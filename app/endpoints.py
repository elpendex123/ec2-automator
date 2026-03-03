"""API endpoint handlers."""

from fastapi import APIRouter, HTTPException, status
from app.logging_config import logger
from app.models import (
    LaunchInstanceRequest,
    LaunchInstanceResponse,
    TaskStatus,
    TerminateInstanceResponse,
    ErrorResponse,
)
from app.tasks import task_store, create_task, get_task

router = APIRouter(tags=["Instances"])


@router.post(
    "/launch",
    response_model=LaunchInstanceResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def launch_instance(request: LaunchInstanceRequest):
    """Launch a new EC2 instance asynchronously.

    Args:
        request: LaunchInstanceRequest with instance details

    Returns:
        LaunchInstanceResponse with task_id for tracking

    Raises:
        HTTPException: If request validation fails
    """
    try:
        logger.info(
            f"Launching instance: {request.instance_name} ({request.instance_type}) with {request.app_name}"
        )

        # Create async task
        task_id = create_task(
            instance_name=request.instance_name,
            instance_type=request.instance_type,
            app_name=request.app_name,
            owner=request.owner,
        )

        logger.info(f"Task created: {task_id}")

        return LaunchInstanceResponse(
            task_id=task_id,
            status="accepted",
            message=f"Instance launch initiated. Track with task_id: {task_id}",
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error in launch_instance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to launch instance",
        )


@router.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get the status of an async task.

    Args:
        task_id: Task identifier

    Returns:
        TaskStatus with current status and details

    Raises:
        HTTPException: If task not found
    """
    try:
        logger.info(f"Checking status for task: {task_id}")

        task = get_task(task_id)

        if not task:
            logger.warning(f"Task not found: {task_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )

        return TaskStatus(
            task_id=task_id,
            status=task.get("status", "unknown"),
            instance_id=task.get("instance_id"),
            error=task.get("error"),
            created_at=task.get("created_at"),
            completed_at=task.get("completed_at"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task status",
        )


@router.delete("/terminate/{instance_id}")
async def terminate_instance(instance_id: str):
    """Terminate an EC2 instance.

    Args:
        instance_id: EC2 instance ID (e.g., i-1234567890abcdef0)

    Returns:
        TerminateInstanceResponse confirming termination request

    Raises:
        HTTPException: If instance_id is invalid
    """
    try:
        if not instance_id.startswith("i-"):
            logger.warning(f"Invalid instance ID format: {instance_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid instance ID format (must start with 'i-')",
            )

        logger.info(f"Terminating instance: {instance_id}")

        # Actual termination will be implemented in Phase 3
        # For now, just log and return success response

        return TerminateInstanceResponse(
            message=f"Instance {instance_id} termination requested",
            instance_id=instance_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error terminating instance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to terminate instance",
        )
