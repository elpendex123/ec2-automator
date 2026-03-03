"""AWS SES email notifications."""

import os
from typing import Optional
import boto3
from botocore.exceptions import ClientError

from app.logging_config import logger


def get_ses_client():
    """Get Boto3 SES client.

    Uses AWS credentials from environment variables or IAM instance profile.

    Returns:
        boto3.client: SES client

    Raises:
        Exception: If AWS credentials not configured
    """
    region = os.getenv("SES_REGION", "us-east-1")
    try:
        client = boto3.client("ses", region_name=region)
        logger.info(f"SES client initialized for region: {region}")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize SES client: {str(e)}")
        raise


def send_email(
    recipient: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
) -> bool:
    """Send email via AWS SES.

    Args:
        recipient: Email address to send to
        subject: Email subject
        body_text: Plain text email body
        body_html: Optional HTML email body

    Returns:
        bool: True if successful, False if failed

    Raises:
        ValueError: If recipient or subject is invalid
        ClientError: If AWS API call fails
    """
    if not recipient or "@" not in recipient:
        raise ValueError(f"Invalid email address: {recipient}")

    if not subject or not subject.strip():
        raise ValueError("Subject cannot be empty")

    if not body_text or not body_text.strip():
        raise ValueError("Email body cannot be empty")

    sender = os.getenv("SES_SENDER_EMAIL", "noreply@yourdomain.com")

    try:
        ses = get_ses_client()

        # Build message body
        message_body = {"Text": {"Data": body_text, "Charset": "UTF-8"}}

        if body_html:
            message_body["Html"] = {"Data": body_html, "Charset": "UTF-8"}

        logger.info(f"Sending email to {recipient}: {subject}")

        response = ses.send_email(
            Source=sender,
            Destination={"ToAddresses": [recipient]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": message_body,
            },
        )

        message_id = response["MessageId"]
        logger.info(f"Email sent successfully: {message_id} to {recipient}")

        return True

    except ValueError as e:
        logger.error(f"Validation error in send_email: {str(e)}")
        raise
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_msg = e.response["Error"]["Message"]
        logger.error(f"AWS SES error: {error_code} - {error_msg}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error sending email: {str(e)}")
        raise


def send_launch_success_email(
    recipient: str,
    instance_name: str,
    instance_id: str,
    instance_type: str,
    app_name: str,
    owner: str,
) -> bool:
    """Send success email after instance launch.

    Args:
        recipient: Email address to send to
        instance_name: Name of the launched instance
        instance_id: AWS instance ID
        instance_type: Instance type (t3.micro, etc)
        app_name: Application installed
        owner: Instance owner

    Returns:
        bool: True if successful
    """
    subject = f"EC2 Instance Launch Success: {instance_name}"

    body_text = f"""
Instance Launch Successful

Instance Details:
  Name: {instance_name}
  Instance ID: {instance_id}
  Instance Type: {instance_type}
  Application: {app_name}
  Owner: {owner}

Your instance is now running and the application is being installed.
You can access it through the AWS EC2 console.

---
EC2-Automator API
"""

    body_html = f"""
<html>
<body style="font-family: Arial, sans-serif;">
  <h2 style="color: #2ecc71;">Instance Launch Successful</h2>
  <p>Your EC2 instance has been successfully created and is now running.</p>

  <h3>Instance Details:</h3>
  <ul>
    <li><strong>Name:</strong> {instance_name}</li>
    <li><strong>Instance ID:</strong> <code>{instance_id}</code></li>
    <li><strong>Instance Type:</strong> {instance_type}</li>
    <li><strong>Application:</strong> {app_name}</li>
    <li><strong>Owner:</strong> {owner}</li>
  </ul>

  <p>Your instance is now running and the application is being installed.</p>
  <p>You can access it through the <a href="https://console.aws.amazon.com/ec2/">AWS EC2 console</a>.</p>

  <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
  <p style="color: #666; font-size: 12px;">EC2-Automator API</p>
</body>
</html>
"""

    return send_email(recipient, subject, body_text, body_html)


def send_launch_failure_email(
    recipient: str,
    instance_name: str,
    error_message: str,
    owner: str,
) -> bool:
    """Send failure email if instance launch fails.

    Args:
        recipient: Email address to send to
        instance_name: Requested instance name
        error_message: Error description
        owner: Instance owner

    Returns:
        bool: True if successful
    """
    subject = f"EC2 Instance Launch Failed: {instance_name}"

    body_text = f"""
Instance Launch Failed

Request Details:
  Instance Name: {instance_name}
  Owner: {owner}

Error:
{error_message}

Please check your request parameters and try again.
For more details, check the EC2-Automator logs.

---
EC2-Automator API
"""

    body_html = f"""
<html>
<body style="font-family: Arial, sans-serif;">
  <h2 style="color: #e74c3c;">Instance Launch Failed</h2>
  <p>Unfortunately, your EC2 instance launch request could not be completed.</p>

  <h3>Request Details:</h3>
  <ul>
    <li><strong>Instance Name:</strong> {instance_name}</li>
    <li><strong>Owner:</strong> {owner}</li>
  </ul>

  <h3 style="color: #e74c3c;">Error:</h3>
  <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
{error_message}
  </pre>

  <p>Please check your request parameters and try again.</p>
  <p>For more details, check the EC2-Automator logs.</p>

  <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
  <p style="color: #666; font-size: 12px;">EC2-Automator API</p>
</body>
</html>
"""

    return send_email(recipient, subject, body_text, body_html)
