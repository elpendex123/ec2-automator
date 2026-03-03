"""AWS EC2 provisioning and management."""

import os
from typing import Optional
import boto3
from botocore.exceptions import ClientError

from app.logging_config import logger
from app.config import AVAILABLE_APPS, DEFAULT_AMI, DEFAULT_REGION, INSTANCE_TYPES


def get_ec2_client():
    """Get Boto3 EC2 client.

    Uses AWS credentials from environment variables or IAM instance profile.

    Returns:
        boto3.client: EC2 client

    Raises:
        Exception: If AWS credentials not configured
    """
    region = os.getenv("AWS_REGION", DEFAULT_REGION)
    try:
        client = boto3.client("ec2", region_name=region)
        logger.info(f"EC2 client initialized for region: {region}")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize EC2 client: {str(e)}")
        raise


def validate_instance_type(instance_type: str) -> bool:
    """Validate instance type is in allowed list.

    Args:
        instance_type: Instance type to validate (e.g., t3.micro)

    Returns:
        bool: True if valid, False otherwise
    """
    return instance_type in INSTANCE_TYPES


def validate_app_name(app_name: str) -> bool:
    """Validate app name is in available apps.

    Args:
        app_name: Application name to validate

    Returns:
        bool: True if valid, False otherwise
    """
    return app_name in AVAILABLE_APPS


def create_instance(
    instance_name: str,
    instance_type: str,
    app_name: str,
    owner: str,
) -> Optional[str]:
    """Create and launch an EC2 instance.

    Args:
        instance_name: Name for the instance
        instance_type: EC2 instance type (t3.micro, t3.small)
        app_name: Application to install (nginx, mysql, httpd, mongo)
        owner: Owner/team name

    Returns:
        str: Instance ID if successful, None if failed

    Raises:
        ValueError: If inputs are invalid
        ClientError: If AWS API call fails
    """
    # Validate inputs
    if not validate_instance_type(instance_type):
        raise ValueError(f"Invalid instance type: {instance_type}")

    if not validate_app_name(app_name):
        raise ValueError(f"Invalid app name: {app_name}")

    try:
        ec2 = get_ec2_client()

        # Get UserData script for app
        user_data = AVAILABLE_APPS.get(app_name)

        # Create instance
        logger.info(
            f"Creating EC2 instance: {instance_name} ({instance_type}) with {app_name}"
        )

        response = ec2.run_instances(
            ImageId=DEFAULT_AMI,
            MinCount=1,
            MaxCount=1,
            InstanceType=instance_type,
            UserData=user_data,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "Name", "Value": instance_name},
                        {"Key": "Owner", "Value": owner},
                        {"Key": "CreatedBy", "Value": "AutomatorAPI"},
                    ],
                }
            ],
        )

        instance_id = response["Instances"][0]["InstanceId"]
        logger.info(
            f"Instance created successfully: {instance_id} (Name: {instance_name})"
        )

        return instance_id

    except ValueError as e:
        logger.error(f"Validation error in create_instance: {str(e)}")
        raise
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_msg = e.response["Error"]["Message"]
        logger.error(f"AWS error creating instance: {error_code} - {error_msg}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_instance: {str(e)}")
        raise


def terminate_instance(instance_id: str) -> bool:
    """Terminate an EC2 instance.

    Args:
        instance_id: EC2 instance ID (e.g., i-1234567890abcdef0)

    Returns:
        bool: True if successful, False otherwise

    Raises:
        ValueError: If instance_id format is invalid
        ClientError: If AWS API call fails
    """
    if not instance_id.startswith("i-"):
        raise ValueError(f"Invalid instance ID format: {instance_id}")

    try:
        ec2 = get_ec2_client()

        logger.info(f"Terminating instance: {instance_id}")

        # First stop the instance
        ec2.stop_instances(InstanceIds=[instance_id])
        logger.info(f"Instance stopped: {instance_id}")

        # Then terminate it
        ec2.terminate_instances(InstanceIds=[instance_id])
        logger.info(f"Instance terminated: {instance_id}")

        return True

    except ValueError as e:
        logger.error(f"Validation error in terminate_instance: {str(e)}")
        raise
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_msg = e.response["Error"]["Message"]
        logger.error(f"AWS error terminating instance: {error_code} - {error_msg}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in terminate_instance: {str(e)}")
        raise


def get_instance_status(instance_id: str) -> Optional[dict]:
    """Get current status of an EC2 instance.

    Args:
        instance_id: EC2 instance ID

    Returns:
        dict: Instance details or None if not found

    Raises:
        ClientError: If AWS API call fails
    """
    try:
        ec2 = get_ec2_client()
        response = ec2.describe_instances(InstanceIds=[instance_id])

        if response["Reservations"]:
            instance = response["Reservations"][0]["Instances"][0]
            return {
                "instance_id": instance["InstanceId"],
                "state": instance["State"]["Name"],
                "instance_type": instance["InstanceType"],
                "public_ip": instance.get("PublicIpAddress"),
                "private_ip": instance.get("PrivateIpAddress"),
                "launch_time": str(instance["LaunchTime"]),
            }
        return None

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.warning(f"AWS error getting instance status: {error_code}")
        return None
    except Exception as e:
        logger.error(f"Error getting instance status: {str(e)}")
        return None
