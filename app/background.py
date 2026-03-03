"""Background task workers for async operations."""

import asyncio
from app.logging_config import logger
from app.tasks import task_store, update_task
from app.aws.ec2 import create_instance, get_instance_status


async def launch_instance_worker(
    task_id: str,
    instance_name: str,
    instance_type: str,
    app_name: str,
    owner: str,
) -> None:
    """Background worker to launch an EC2 instance.

    This runs asynchronously and updates task status as it progresses.

    Args:
        task_id: Task identifier
        instance_name: Name for the instance
        instance_type: EC2 instance type
        app_name: Application to install
        owner: Owner/team name
    """
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

    except ValueError as e:
        logger.error(f"Validation error in worker: {str(e)}")
        update_task(task_id, "failed", error=str(e))

    except Exception as e:
        logger.error(f"Error in launch_instance_worker for {task_id}: {str(e)}")
        update_task(task_id, "failed", error=str(e))


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
