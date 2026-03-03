"""Pydantic models for request/response validation."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class InstanceOption(BaseModel):
    """Available instance type and app options."""

    instance_types: List[str] = Field(
        default=["t3.micro", "t3.small"],
        description="Available EC2 instance types",
    )
    apps: List[str] = Field(
        default=["nginx", "mysql", "httpd", "mongo"],
        description="Available applications to install",
    )


class LaunchInstanceRequest(BaseModel):
    """Request body for launching an EC2 instance."""

    instance_name: str = Field(
        ..., min_length=1, max_length=255, description="Name of the instance"
    )
    instance_type: Literal["t3.micro", "t3.small"] = Field(
        default="t3.micro", description="EC2 instance type"
    )
    app_name: Literal["nginx", "mysql", "httpd", "mongo"] = Field(
        ..., description="Application to install on the instance"
    )
    owner: str = Field(
        ..., min_length=1, max_length=255, description="Owner/team name"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "instance_name": "web-server-01",
                "instance_type": "t3.micro",
                "app_name": "nginx",
                "owner": "team-member",
            }
        }


class LaunchInstanceResponse(BaseModel):
    """Response body for instance launch request."""

    task_id: str = Field(..., description="Async task ID for tracking")
    status: str = Field(default="accepted", description="Initial task status")
    message: str = Field(..., description="Response message")


class TaskStatus(BaseModel):
    """Task status response."""

    task_id: str = Field(..., description="Task identifier")
    status: Literal["pending", "running", "completed", "failed"] = Field(
        ..., description="Current task status"
    )
    instance_id: Optional[str] = Field(
        default=None, description="EC2 instance ID (if completed)"
    )
    error: Optional[str] = Field(default=None, description="Error message (if failed)")
    created_at: Optional[str] = Field(default=None, description="Task creation time")
    completed_at: Optional[str] = Field(default=None, description="Task completion time")


class TerminateInstanceResponse(BaseModel):
    """Response body for instance termination."""

    message: str = Field(..., description="Response message")
    instance_id: str = Field(..., description="Instance ID being terminated")


class ErrorResponse(BaseModel):
    """Error response body."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional error details")
    status_code: int = Field(..., description="HTTP status code")
