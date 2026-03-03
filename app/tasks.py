"""Task management for asynchronous instance provisioning."""

import uuid
from datetime import datetime
from typing import Dict, Optional
from app.config import AVAILABLE_APPS

# In-memory task store
# task_id -> {status, instance_id, error, created_at, completed_at, details}
task_store: Dict[str, dict] = {}


def create_task(
    instance_name: str,
    instance_type: str,
    app_name: str,
    owner: str,
) -> str:
    """Create a new async task for instance provisioning.

    Args:
        instance_name: Name of the instance
        instance_type: EC2 instance type (t3.micro or t3.small)
        app_name: Application to install (nginx, mysql, httpd, mongo)
        owner: Owner/team name

    Returns:
        str: Task ID for tracking

    Raises:
        ValueError: If app_name not in AVAILABLE_APPS
    """
    if app_name not in AVAILABLE_APPS:
        raise ValueError(f"Unsupported application: {app_name}")

    task_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    task_store[task_id] = {
        "status": "pending",
        "instance_name": instance_name,
        "instance_type": instance_type,
        "app_name": app_name,
        "owner": owner,
        "instance_id": None,
        "error": None,
        "created_at": now,
        "completed_at": None,
    }

    return task_id


def get_task(task_id: str) -> Optional[dict]:
    """Get task details by ID.

    Args:
        task_id: Task identifier

    Returns:
        dict: Task details or None if not found
    """
    return task_store.get(task_id)


def update_task(
    task_id: str,
    status: str,
    instance_id: Optional[str] = None,
    error: Optional[str] = None,
) -> bool:
    """Update task status.

    Args:
        task_id: Task identifier
        status: New status (pending, running, completed, failed)
        instance_id: EC2 instance ID (if launched)
        error: Error message (if failed)

    Returns:
        bool: True if updated, False if task not found
    """
    if task_id not in task_store:
        return False

    task = task_store[task_id]
    task["status"] = status

    if instance_id:
        task["instance_id"] = instance_id

    if error:
        task["error"] = error

    if status in ["completed", "failed"]:
        task["completed_at"] = datetime.utcnow().isoformat()

    return True


def clear_tasks() -> None:
    """Clear all tasks (for testing)."""
    task_store.clear()
