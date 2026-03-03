"""FastAPI application entry point."""

import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.logging_config import logger
from app.models import InstanceOption

# Create FastAPI app
app = FastAPI(
    title="EC2-Automator",
    description="REST API for provisioning AWS Free Tier EC2 instances",
    version="0.1.0",
)


# Middleware for request/response logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests and outgoing responses."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Log request
    logger.info(
        f"{request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
        },
    )

    # Process request
    response = await call_next(request)

    # Log response
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        },
    )

    return response


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ec2-automator"}


# Get available options endpoint
@app.get("/options", response_model=InstanceOption, tags=["Options"])
async def get_options():
    """Get available instance types and applications.

    Returns:
        InstanceOption: List of available instance types and apps
    """
    logger.info("Fetching available instance types and applications")
    return InstanceOption()


# Will be imported from endpoints.py
from app.endpoints import router  # noqa: E402, F401

app.include_router(router)
