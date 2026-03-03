"""Integration tests for SES email operations with moto mocking."""

import pytest
from unittest.mock import patch
from botocore.exceptions import ClientError

from app.aws.ses import (
    send_email,
    send_launch_success_email,
    send_launch_failure_email,
)


class TestSendEmail:
    """Test generic email sending."""

    def test_send_email_success(self, mock_ses_client):
        """Valid email should be sent successfully."""
        mock_ses_client.send_email.return_value = {"MessageId": "test-message-id-123"}

        with patch("app.aws.ses.get_ses_client", return_value=mock_ses_client):
            result = send_email(
                recipient="test@example.com",
                subject="Test Subject",
                body_text="Test body",
            )

        assert result is True
        mock_ses_client.send_email.assert_called_once()

    def test_send_email_with_html(self, mock_ses_client):
        """Email with HTML should include both text and HTML."""
        mock_ses_client.send_email.return_value = {"MessageId": "test-id"}

        with patch("app.aws.ses.get_ses_client", return_value=mock_ses_client):
            send_email(
                recipient="test@example.com",
                subject="Test",
                body_text="Plain text",
                body_html="<html>HTML</html>",
            )

        call_args = mock_ses_client.send_email.call_args
        message = call_args.kwargs["Message"]
        assert "Text" in message["Body"]
        assert "Html" in message["Body"]

    def test_send_email_invalid_recipient(self):
        """Invalid email should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            send_email(
                recipient="invalid-email",
                subject="Test",
                body_text="Test",
            )
        assert "Invalid email address" in str(exc_info.value)

    def test_send_email_empty_subject(self):
        """Empty subject should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            send_email(
                recipient="test@example.com",
                subject="",
                body_text="Test",
            )
        assert "Subject cannot be empty" in str(exc_info.value)

    def test_send_email_empty_body(self):
        """Empty body should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            send_email(
                recipient="test@example.com",
                subject="Test",
                body_text="",
            )
        assert "Email body cannot be empty" in str(exc_info.value)

    def test_send_email_aws_error(self, mock_ses_client):
        """AWS API error should raise ClientError."""
        error_response = {
            "Error": {
                "Code": "MessageRejected",
                "Message": "Email address not verified",
            }
        }
        mock_ses_client.send_email.side_effect = ClientError(error_response, "SendEmail")

        with patch("app.aws.ses.get_ses_client", return_value=mock_ses_client):
            with pytest.raises(ClientError):
                send_email(
                    recipient="test@example.com",
                    subject="Test",
                    body_text="Test",
                )


class TestLaunchSuccessEmail:
    """Test success notification emails."""

    def test_send_launch_success_email(self, mock_send_email):
        """Success email should be sent with instance details."""
        with patch("app.aws.ses.send_email", return_value=True) as mock:
            result = send_launch_success_email(
                recipient="test@example.com",
                instance_name="test-instance",
                instance_id="i-test-id",
                instance_type="t3.micro",
                app_name="nginx",
                owner="test-team",
            )

        assert result is True
        mock.assert_called_once()
        call_args = mock.call_args
        # Check positional arguments: recipient, subject, body_text, body_html
        assert call_args[0][0] == "test@example.com"
        assert "test-instance" in call_args[0][1]  # subject

    def test_success_email_contains_instance_details(self):
        """Success email content should include instance details."""
        with patch("app.aws.ses.send_email", return_value=True) as mock:
            send_launch_success_email(
                recipient="test@example.com",
                instance_name="web-server-01",
                instance_id="i-1234567890abcdef0",
                instance_type="t3.small",
                app_name="mysql",
                owner="dba-team",
            )

            call_args = mock.call_args
            # Arguments are: recipient, subject, body_text, body_html
            subject = call_args[0][1]
            body_text = call_args[0][2]

            assert "web-server-01" in subject or "web-server-01" in body_text
            assert "i-1234567890abcdef0" in body_text
            assert "mysql" in body_text
            assert "dba-team" in body_text


class TestLaunchFailureEmail:
    """Test failure notification emails."""

    def test_send_launch_failure_email(self):
        """Failure email should be sent with error details."""
        with patch("app.aws.ses.send_email", return_value=True) as mock:
            result = send_launch_failure_email(
                recipient="test@example.com",
                instance_name="test-instance",
                error_message="Instance type not available",
                owner="test-team",
            )

        assert result is True
        mock.assert_called_once()

    def test_failure_email_contains_error_details(self):
        """Failure email should include error message."""
        error_msg = "Insufficient capacity in availability zone"

        with patch("app.aws.ses.send_email", return_value=True) as mock:
            send_launch_failure_email(
                recipient="test@example.com",
                instance_name="test-instance",
                error_message=error_msg,
                owner="team",
            )

            call_args = mock.call_args
            # Arguments are: recipient, subject, body_text, body_html
            body_text = call_args[0][2]
            assert error_msg in body_text
