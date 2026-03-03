"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.tasks import clear_tasks


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_task_store():
    """Clear task store before each test."""
    clear_tasks()
    yield
    clear_tasks()


@pytest.fixture
def mock_ec2_client():
    """Mock boto3 EC2 client."""
    with patch("app.aws.ec2.get_ec2_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_ses_client():
    """Mock boto3 SES client."""
    with patch("app.aws.ses.get_ses_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_create_instance():
    """Mock EC2 instance creation."""
    with patch("app.aws.ec2.create_instance") as mock:
        mock.return_value = "i-1234567890abcdef0"
        yield mock


@pytest.fixture
def mock_send_email():
    """Mock SES email sending."""
    with patch("app.aws.ses.send_email") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_launch_success_email():
    """Mock launch success email."""
    with patch("app.aws.ses.send_launch_success_email") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_launch_failure_email():
    """Mock launch failure email."""
    with patch("app.aws.ses.send_launch_failure_email") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def valid_launch_request():
    """Valid launch instance request body."""
    return {
        "instance_name": "test-instance",
        "instance_type": "t3.micro",
        "app_name": "nginx",
        "owner": "test-team",
    }


@pytest.fixture
def invalid_launch_request_bad_app():
    """Launch request with invalid app name."""
    return {
        "instance_name": "test-instance",
        "instance_type": "t3.micro",
        "app_name": "invalid-app",
        "owner": "test-team",
    }


@pytest.fixture
def invalid_launch_request_bad_instance_type():
    """Launch request with invalid instance type."""
    return {
        "instance_name": "test-instance",
        "instance_type": "t2.large",
        "app_name": "nginx",
        "owner": "test-team",
    }


@pytest.fixture
def invalid_launch_request_missing_field():
    """Launch request with missing required field."""
    return {
        "instance_name": "test-instance",
        "instance_type": "t3.micro",
    }
