"""Integration tests for EC2 operations with moto mocking."""

import pytest
from unittest.mock import patch
from botocore.exceptions import ClientError

from app.aws.ec2 import (
    create_instance,
    terminate_instance,
    get_instance_status,
    validate_instance_type,
    validate_app_name,
)


class TestValidation:
    """Test validation functions."""

    def test_validate_instance_type_valid(self):
        """Valid instance type should return True."""
        assert validate_instance_type("t3.micro") is True
        assert validate_instance_type("t3.small") is True

    def test_validate_instance_type_invalid(self):
        """Invalid instance type should return False."""
        assert validate_instance_type("t2.large") is False
        assert validate_instance_type("invalid") is False

    def test_validate_app_name_valid(self):
        """Valid app name should return True."""
        assert validate_app_name("nginx") is True
        assert validate_app_name("mysql") is True
        assert validate_app_name("httpd") is True
        assert validate_app_name("mongo") is True

    def test_validate_app_name_invalid(self):
        """Invalid app name should return False."""
        assert validate_app_name("invalid-app") is False
        assert validate_app_name("postgres") is False


class TestCreateInstance:
    """Test EC2 instance creation."""

    def test_create_instance_success(self, mock_ec2_client):
        """Successful instance creation should return instance ID."""
        # Mock the EC2 response
        mock_ec2_client.run_instances.return_value = {
            "Instances": [{"InstanceId": "i-1234567890abcdef0"}]
        }

        with patch("app.aws.ec2.get_ec2_client", return_value=mock_ec2_client):
            instance_id = create_instance(
                instance_name="test-instance",
                instance_type="t3.micro",
                app_name="nginx",
                owner="test-team",
            )

        assert instance_id == "i-1234567890abcdef0"
        mock_ec2_client.run_instances.assert_called_once()

    def test_create_instance_invalid_type(self):
        """Invalid instance type should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            create_instance(
                instance_name="test",
                instance_type="t2.large",
                app_name="nginx",
                owner="team",
            )
        assert "Invalid instance type" in str(exc_info.value)

    def test_create_instance_invalid_app(self):
        """Invalid app name should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            create_instance(
                instance_name="test",
                instance_type="t3.micro",
                app_name="invalid-app",
                owner="team",
            )
        assert "Invalid app name" in str(exc_info.value)

    def test_create_instance_with_tags(self, mock_ec2_client):
        """Instance should be created with proper tags."""
        mock_ec2_client.run_instances.return_value = {"Instances": [{"InstanceId": "i-test"}]}

        with patch("app.aws.ec2.get_ec2_client", return_value=mock_ec2_client):
            create_instance(
                instance_name="web-server",
                instance_type="t3.micro",
                app_name="nginx",
                owner="devops-team",
            )

        # Verify tags were included in call
        call_args = mock_ec2_client.run_instances.call_args
        assert "TagSpecifications" in call_args.kwargs
        tags = call_args.kwargs["TagSpecifications"][0]["Tags"]
        tag_dict = {tag["Key"]: tag["Value"] for tag in tags}
        assert tag_dict["Name"] == "web-server"
        assert tag_dict["Owner"] == "devops-team"
        assert tag_dict["CreatedBy"] == "AutomatorAPI"

    def test_create_instance_with_userdata(self, mock_ec2_client):
        """Instance should be created with UserData script."""
        mock_ec2_client.run_instances.return_value = {"Instances": [{"InstanceId": "i-test"}]}

        with patch("app.aws.ec2.get_ec2_client", return_value=mock_ec2_client):
            create_instance(
                instance_name="test",
                instance_type="t3.micro",
                app_name="nginx",
                owner="team",
            )

        call_args = mock_ec2_client.run_instances.call_args
        assert "UserData" in call_args.kwargs
        assert "nginx" in call_args.kwargs["UserData"]

    def test_create_instance_aws_error(self, mock_ec2_client):
        """AWS API error should raise ClientError."""
        error_response = {
            "Error": {"Code": "InsufficientInstanceCapacity", "Message": "No capacity"}
        }
        mock_ec2_client.run_instances.side_effect = ClientError(error_response, "RunInstances")

        with patch("app.aws.ec2.get_ec2_client", return_value=mock_ec2_client):
            with pytest.raises(ClientError):
                create_instance(
                    instance_name="test",
                    instance_type="t3.micro",
                    app_name="nginx",
                    owner="team",
                )


class TestTerminateInstance:
    """Test EC2 instance termination."""

    def test_terminate_instance_success(self, mock_ec2_client):
        """Successful termination should return True."""
        mock_ec2_client.stop_instances.return_value = {}
        mock_ec2_client.terminate_instances.return_value = {}

        with patch("app.aws.ec2.get_ec2_client", return_value=mock_ec2_client):
            result = terminate_instance("i-1234567890abcdef0")

        assert result is True
        mock_ec2_client.stop_instances.assert_called_once()
        mock_ec2_client.terminate_instances.assert_called_once()

    def test_terminate_invalid_id(self):
        """Invalid instance ID should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            terminate_instance("invalid-id")
        assert "Invalid instance ID format" in str(exc_info.value)

    def test_terminate_instance_aws_error(self, mock_ec2_client):
        """AWS API error should raise ClientError."""
        error_response = {"Error": {"Code": "InvalidInstanceID.NotFound", "Message": "Not found"}}
        mock_ec2_client.stop_instances.side_effect = ClientError(error_response, "StopInstances")

        with patch("app.aws.ec2.get_ec2_client", return_value=mock_ec2_client):
            with pytest.raises(ClientError):
                terminate_instance("i-1234567890abcdef0")


class TestGetInstanceStatus:
    """Test getting instance status."""

    def test_get_instance_status_success(self, mock_ec2_client):
        """Valid instance should return status details."""
        mock_ec2_client.describe_instances.return_value = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-test",
                            "State": {"Name": "running"},
                            "InstanceType": "t3.micro",
                            "PublicIpAddress": "1.2.3.4",
                            "PrivateIpAddress": "10.0.0.1",
                            "LaunchTime": "2026-03-03T00:00:00Z",
                        }
                    ]
                }
            ]
        }

        with patch("app.aws.ec2.get_ec2_client", return_value=mock_ec2_client):
            status = get_instance_status("i-test")

        assert status["instance_id"] == "i-test"
        assert status["state"] == "running"
        assert status["public_ip"] == "1.2.3.4"

    def test_get_instance_status_not_found(self, mock_ec2_client):
        """Nonexistent instance should return None."""
        mock_ec2_client.describe_instances.return_value = {"Reservations": []}

        with patch("app.aws.ec2.get_ec2_client", return_value=mock_ec2_client):
            status = get_instance_status("i-nonexistent")

        assert status is None
