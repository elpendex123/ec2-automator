"""Background task workers for async operations."""

import os
import asyncio
from app.logging_config import logger
from app.tasks import task_store, update_task
from app.aws.ec2 import create_instance, get_instance_status
from app.aws.ses import send_launch_success_email, send_launch_failure_email


async def launch_instance_worker(
    task_id: str,
    instance_name: str,
    instance_type: str,
    app_name: str,
    owner: str,
) -> None:
    """Background worker to launch an EC2 instance.

    This runs asynchronously and updates task status as it progresses.
    Sends email notifications on success or failure.

    Args:
        task_id: Task identifier
        instance_name: Name for the instance
        instance_type: EC2 instance type
        app_name: Application to install
        owner: Owner/team name
    """
    # Get notification email from environment
    notification_email = os.getenv(
        "NOTIFICATION_EMAIL", "enrique.coello@gmail.com"
    )

    try:
        # Update task status to running
        update_task(task_id, "running")
        logger.info(f"Starting background worker for task: {task_id}")

        # Create the instance (this calls AWS API)
        instance_id = create_instance(
            instance_name=instance_name,
            instance_type=instance_type,
            app_name=app_name,
            owner=owner,
        )

        # Update task with instance ID
        update_task(task_id, "completed", instance_id=instance_id)
        logger.info(
            f"Task completed successfully: {task_id} (Instance: {instance_id})"
        )

        # Send success email
        try:
            send_launch_success_email(
                recipient=notification_email,
                instance_name=instance_name,
                instance_id=instance_id,
                instance_type=instance_type,
                app_name=app_name,
                owner=owner,
            )
            logger.info(f"Success email sent to {notification_email}")
        except Exception as e:
            logger.error(f"Failed to send success email: {str(e)}")

    except ValueError as e:
        logger.error(f"Validation error in worker: {str(e)}")
        update_task(task_id, "failed", error=str(e))

        # Send failure email
        try:
            send_launch_failure_email(
                recipient=notification_email,
                instance_name=instance_name,
                error_message=str(e),
                owner=owner,
            )
            logger.info(f"Failure email sent to {notification_email}")
        except Exception as email_err:
            logger.error(f"Failed to send failure email: {str(email_err)}")

    except Exception as e:
        logger.error(f"Error in launch_instance_worker for {task_id}: {str(e)}")
        update_task(task_id, "failed", error=str(e))

        # Send failure email
        try:
            send_launch_failure_email(
                recipient=notification_email,
                instance_name=instance_name,
                error_message=str(e),
                owner=owner,
            )
            logger.info(f"Failure email sent to {notification_email}")
        except Exception as email_err:
            logger.error(f"Failed to send failure email: {str(email_err)}")


def start_background_task(
    task_id: str,
    instance_name: str,
    instance_type: str,
    app_name: str,
    owner: str,
) -> None:
    """Start a background task without waiting for completion.

    Args:
        task_id: Task identifier
        instance_name: Name for the instance
        instance_type: EC2 instance type
        app_name: Application to install
        owner: Owner/team name
    """
    # Create and schedule the coroutine without awaiting
    asyncio.create_task(
        launch_instance_worker(
            task_id=task_id,
            instance_name=instance_name,
            instance_type=instance_type,
            app_name=app_name,
            owner=owner,
        )
    )
