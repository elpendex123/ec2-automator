"""Unit tests for API endpoints."""

from fastapi import status


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Health check should return healthy status."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ec2-automator"


class TestOptionsEndpoint:
    """Test GET /options endpoint."""

    def test_get_options(self, client):
        """GET /options should return available options."""
        response = client.get("/options")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "instance_types" in data
        assert "apps" in data
        assert "t3.micro" in data["instance_types"]
        assert "t3.small" in data["instance_types"]
        assert "nginx" in data["apps"]
        assert "mysql" in data["apps"]
        assert "httpd" in data["apps"]
        assert "mongo" in data["apps"]


class TestLaunchEndpoint:
    """Test POST /launch endpoint."""

    def test_launch_valid_request(self, client, valid_launch_request, mock_create_instance):
        """Valid launch request should return 202 Accepted."""
        response = client.post("/launch", json=valid_launch_request)
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "accepted"
        assert "Instance launch initiated" in data["message"]

    def test_launch_invalid_app(self, client, invalid_launch_request_bad_app):
        """Invalid app name should return 422."""
        response = client.post("/launch", json=invalid_launch_request_bad_app)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_launch_invalid_instance_type(self, client, invalid_launch_request_bad_instance_type):
        """Invalid instance type should return 422."""
        response = client.post("/launch", json=invalid_launch_request_bad_instance_type)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_launch_missing_field(self, client, invalid_launch_request_missing_field):
        """Missing required field should return 422."""
        response = client.post("/launch", json=invalid_launch_request_missing_field)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_launch_empty_instance_name(self, client):
        """Empty instance name should return 422."""
        request = {
            "instance_name": "",
            "instance_type": "t3.micro",
            "app_name": "nginx",
            "owner": "team",
        }
        response = client.post("/launch", json=request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestStatusEndpoint:
    """Test GET /status/{task_id} endpoint."""

    def test_get_status_valid_task(self, client, valid_launch_request, mock_create_instance):
        """Valid task_id should return status."""
        # First create a task
        launch_response = client.post("/launch", json=valid_launch_request)
        task_id = launch_response.json()["task_id"]

        # Then check status
        response = client.get(f"/status/{task_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["task_id"] == task_id
        assert "status" in data

    def test_get_status_nonexistent_task(self, client):
        """Nonexistent task_id should return 404."""
        response = client.get("/status/nonexistent-task-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTerminateEndpoint:
    """Test DELETE /terminate/{instance_id} endpoint."""

    def test_terminate_valid_instance(self, client, mock_ec2_client):
        """Valid instance ID should return success."""
        response = client.delete("/terminate/i-1234567890abcdef0")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "i-1234567890abcdef0" in data["instance_id"]

    def test_terminate_invalid_instance_id(self, client):
        """Invalid instance ID format should return 400."""
        response = client.delete("/terminate/invalid-id")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data

    def test_terminate_malformed_instance_id(self, client):
        """Malformed instance ID should return 400."""
        response = client.delete("/terminate/ec2-1234567890abcdef0")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestRequestValidation:
    """Test request validation across endpoints."""

    def test_launch_with_extra_fields(self, client, valid_launch_request):
        """Extra fields in request should be ignored (by Pydantic)."""
        request = {**valid_launch_request, "extra_field": "should_be_ignored"}
        response = client.post("/launch", json=request)
        assert response.status_code == status.HTTP_202_ACCEPTED

    def test_launch_with_wrong_json_type(self, client):
        """Wrong JSON type for field should return 422."""
        request = {
            "instance_name": "test",
            "instance_type": "t3.micro",
            "app_name": "nginx",
            "owner": 12345,  # Should be string
        }
        response = client.post("/launch", json=request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
