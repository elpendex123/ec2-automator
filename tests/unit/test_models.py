"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from app.models import (
    LaunchInstanceRequest,
    LaunchInstanceResponse,
    TaskStatus,
    TerminateInstanceResponse,
    InstanceOption,
    ErrorResponse,
)


class TestLaunchInstanceRequest:
    """Test LaunchInstanceRequest model validation."""

    def test_valid_request(self, valid_launch_request):
        """Valid request should pass validation."""
        request = LaunchInstanceRequest(**valid_launch_request)
        assert request.instance_name == "test-instance"
        assert request.instance_type == "t3.micro"
        assert request.app_name == "nginx"
        assert request.owner == "test-team"

    def test_invalid_app_name(self, invalid_launch_request_bad_app):
        """Invalid app name should raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            LaunchInstanceRequest(**invalid_launch_request_bad_app)
        assert "literal_error" in str(exc_info.value)

    def test_invalid_instance_type(self, invalid_launch_request_bad_instance_type):
        """Invalid instance type should raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            LaunchInstanceRequest(**invalid_launch_request_bad_instance_type)
        assert "literal_error" in str(exc_info.value)

    def test_missing_required_field(self, invalid_launch_request_missing_field):
        """Missing required field should raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            LaunchInstanceRequest(**invalid_launch_request_missing_field)
        assert "missing" in str(exc_info.value)

    def test_empty_instance_name(self):
        """Empty instance name should raise validation error."""
        with pytest.raises(ValidationError):
            LaunchInstanceRequest(
                instance_name="",
                instance_type="t3.micro",
                app_name="nginx",
                owner="team",
            )

    def test_instance_type_default(self):
        """Instance type should default to t3.micro."""
        request = LaunchInstanceRequest(
            instance_name="test",
            app_name="nginx",
            owner="team",
        )
        assert request.instance_type == "t3.micro"


class TestLaunchInstanceResponse:
    """Test LaunchInstanceResponse model."""

    def test_valid_response(self):
        """Valid response should be created."""
        response = LaunchInstanceResponse(
            task_id="test-123",
            status="accepted",
            message="Task started",
        )
        assert response.task_id == "test-123"
        assert response.status == "accepted"

    def test_missing_task_id(self):
        """Missing task_id should raise error."""
        with pytest.raises(ValidationError):
            LaunchInstanceResponse(
                status="accepted",
                message="Task started",
            )


class TestTaskStatus:
    """Test TaskStatus model."""

    def test_pending_status(self):
        """Pending status should be valid."""
        status = TaskStatus(
            task_id="test-123",
            status="pending",
        )
        assert status.status == "pending"
        assert status.instance_id is None

    def test_completed_status(self):
        """Completed status with instance_id should be valid."""
        status = TaskStatus(
            task_id="test-123",
            status="completed",
            instance_id="i-1234567890abcdef0",
        )
        assert status.status == "completed"
        assert status.instance_id == "i-1234567890abcdef0"

    def test_failed_status(self):
        """Failed status with error should be valid."""
        status = TaskStatus(
            task_id="test-123",
            status="failed",
            error="Something went wrong",
        )
        assert status.status == "failed"
        assert status.error == "Something went wrong"

    def test_invalid_status(self):
        """Invalid status should raise error."""
        with pytest.raises(ValidationError):
            TaskStatus(
                task_id="test-123",
                status="invalid-status",
            )


class TestTerminateInstanceResponse:
    """Test TerminateInstanceResponse model."""

    def test_valid_response(self):
        """Valid termination response should be created."""
        response = TerminateInstanceResponse(
            message="Instance terminated",
            instance_id="i-1234567890abcdef0",
        )
        assert response.instance_id == "i-1234567890abcdef0"
        assert response.message == "Instance terminated"


class TestInstanceOption:
    """Test InstanceOption model."""

    def test_default_options(self):
        """Default options should include all apps and instance types."""
        options = InstanceOption()
        assert "t3.micro" in options.instance_types
        assert "t3.small" in options.instance_types
        assert "nginx" in options.apps
        assert "mysql" in options.apps
        assert "httpd" in options.apps
        assert "mongo" in options.apps


class TestErrorResponse:
    """Test ErrorResponse model."""

    def test_valid_error(self):
        """Valid error response should be created."""
        error = ErrorResponse(
            error="Bad Request",
            detail="Invalid input",
            status_code=400,
        )
        assert error.error == "Bad Request"
        assert error.status_code == 400

    def test_error_without_detail(self):
        """Error without detail should be valid."""
        error = ErrorResponse(
            error="Server Error",
            status_code=500,
        )
        assert error.detail is None
