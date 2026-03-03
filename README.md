# EC2-Automator

A minimalist REST API for provisioning AWS Free Tier EC2 instances.

## Overview

EC2-Automator provides a simple HTTP API to:
- Launch EC2 instances (t3.micro/t3.small) with pre-configured applications
- Terminate instances
- Track provisioning status asynchronously
- Send email notifications on completion

## Tech Stack

- **Language:** Python 3.12+
- **Framework:** FastAPI
- **Cloud SDK:** Boto3
- **Container:** Docker (Alpine)
- **Validation:** Pydantic
- **CI/CD:** Jenkins

## Quick Start

### Prerequisites
- Python 3.12+
- AWS credentials (via IAM Instance Profile or local AWS CLI config)
- Docker (optional, for containerized deployment)

### Installation

```bash
# Clone repository
git clone https://github.com/elpendex123/ec2-automator.git
cd ec2-automator

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp .env.example .env
# Edit .env with your AWS region and SES email
```

### Running Locally

```bash
# Start the API server
uvicorn app.main:app --reload

# API will be available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Running with Docker

```bash
# Build Docker image
docker build -t ec2-automator .

# Run Docker container
docker run -d \
  -p 8000:8000 \
  -e AWS_REGION=us-east-1 \
  -e SES_SENDER_EMAIL=your-email@example.com \
  -v ~/.aws:/root/.aws:ro \
  ec2-automator

# Or use docker-compose
docker-compose up -d

# Stop container
docker-compose down
```

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests with coverage
pytest

# Run specific test file
pytest tests/unit/test_endpoints.py -v
```

## API Endpoints

### Interactive API Documentation
Once running, access interactive API docs at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

All endpoints are documented with request/response schemas, examples, and try-it-out capability.

### GET /health
Health check endpoint for monitoring.

**Response (200 OK):**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### GET /options
Returns available instance types and supported applications.

**Response:**
```json
{
  "instance_types": ["t3.micro", "t3.small"],
  "apps": ["nginx", "mysql", "httpd", "mongo"]
}
```

### POST /launch
Provisions a new EC2 instance asynchronously. Returns `202 Accepted` with task ID.

**Request:**
```json
{
  "instance_name": "web-server-01",
  "instance_type": "t3.micro",
  "app_name": "nginx",
  "owner": "team-member"
}
```

**Response (202 Accepted):**
```json
{
  "task_id": "task-abc123def456",
  "status": "accepted",
  "message": "Instance launch started"
}
```

**Request Validation:**
- `instance_name`: Required, non-empty string
- `instance_type`: Must be "t3.micro" or "t3.small"
- `app_name`: Must be one of: nginx, mysql, httpd, mongo
- `owner`: Required, non-empty string

**Error Responses:**
- `400 Bad Request` - Invalid instance_type or app_name
- `422 Unprocessable Entity` - Missing/invalid request fields

### GET /status/{task_id}
Check the status of an async provisioning task.

**Response:**
```json
{
  "task_id": "task-abc123def456",
  "status": "completed",
  "instance_id": "i-1234567890abcdef0",
  "error": null
}
```

**Possible Status Values:**
- `pending` - Task queued, not yet started
- `running` - Instance provisioning in progress
- `completed` - Instance successfully launched
- `failed` - Instance launch failed (check error field)

**Error Response (404 Not Found):**
```json
{
  "detail": "Task not found"
}
```

### DELETE /terminate/{instance_id}
Terminate an EC2 instance.

**Path Parameter:**
- `instance_id`: EC2 instance ID (e.g., i-1234567890abcdef0)

**Response (200 OK):**
```json
{
  "message": "Termination requested",
  "instance_id": "i-1234567890abcdef0"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Invalid instance ID format"
}
```

## Project Structure

```
ec2-automator/
├── app/                    # Main application package
│   ├── main.py            # FastAPI entry point
│   ├── config.py          # Configuration & AVAILABLE_APPS
│   ├── models.py          # Pydantic models
│   ├── endpoints.py       # Route handlers
│   ├── tasks.py           # Task management
│   ├── background.py      # Background workers
│   ├── aws/               # AWS integration
│   │   ├── ec2.py        # EC2 provisioning
│   │   └── ses.py        # Email notifications
│   ├── utils/             # Utilities
│   └── middleware/        # HTTP middleware
├── tests/                 # Test suite
├── docs/                  # Documentation
├── Dockerfile            # Container definition
├── Jenkinsfile           # CI/CD pipeline
├── requirements.txt      # Dependencies
├── pyproject.toml        # Project config
└── README.md            # This file
```

## AWS Resources

### Supported Instance Types (Free Tier)
- **t3.micro** (2 vCPU, 1 GB RAM) - Recommended
- **t3.small** (2 vCPU, 2 GB RAM) - For demanding workloads

### Supported Applications
- **nginx** - Web server
- **mysql** - Relational database
- **httpd** - Apache HTTP Server
- **mongo** - NoSQL database

### AMI Options
- Amazon Linux 2023 (recommended)
- Ubuntu 22.04 LTS
- Ubuntu 24.04 LTS

## Configuration

Copy `.env.example` to `.env` and configure:

```
AWS_REGION=us-east-1
SES_SENDER_EMAIL=noreply@yourdomain.com
NOTIFICATION_EMAIL=team@yourdomain.com
```

## Security

- **No hardcoded credentials** - Uses AWS IAM Instance Profiles
- **Fail fast** - Errors are raised immediately, not silently ignored
- **Input validation** - All requests validated with Pydantic
- **Minimal permissions** - IAM policy restricted to required actions
- **TLS/SSL** - Use HTTPS in production (reverse proxy with nginx/HAProxy)
- **Rate limiting** - Implement API rate limiting in production (use nginx or API gateway)
- **Authentication** - Add API key/JWT authentication for production deployments

## Logging & Monitoring

### JSON Structured Logging
All logs are output as JSON to stdout for easy parsing and aggregation:

```json
{
  "timestamp": "2026-03-03T10:30:45.123456Z",
  "level": "INFO",
  "message": "GET /options",
  "method": "GET",
  "path": "/options",
  "status_code": 200,
  "duration_ms": 1.23
}
```

### Log Levels
- `DEBUG` - Detailed information for debugging
- `INFO` - General informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors

### Monitoring Recommendations
1. **Log Aggregation** - Send logs to CloudWatch, ELK, or Splunk
2. **Health Checks** - Monitor `/health` endpoint regularly (every 10-30 seconds)
3. **Task Queue Monitoring** - Track pending/running task counts
4. **AWS Resources** - Monitor EC2 instance count and costs
5. **Error Rate** - Alert if error rate exceeds threshold (>5%)
6. **Response Time** - Alert if average response time exceeds 1s

### CloudWatch Integration (Future)
```python
# Can be added for production deployments
import boto3
cloudwatch = boto3.client('cloudwatch')
cloudwatch.put_metric_data(
    Namespace='EC2Automator',
    MetricData=[
        {'MetricName': 'Tasks', 'Value': pending_count}
    ]
)
```

## Development

### Code Quality

```bash
# Lint with ruff
ruff check .

# Format with black
black .

# Run tests with coverage
pytest --cov=app
```

### Contributing

1. Create a feature branch
2. Make changes
3. Run tests and linting
4. Commit with descriptive messages
5. Push to GitHub

## License

MIT

## Utility Scripts

EC2-Automator includes cleanup and testing scripts in the `scripts/` directory:

```bash
# Test API endpoints
bash scripts/test_api.sh

# Clean up local services (uvicorn, systemd, nginx)
bash scripts/cleanup-local-deployment.sh

# Clean up Docker containers and images
bash scripts/cleanup-docker.sh

# Clean up AWS resources (terminate EC2 instances)
bash scripts/cleanup-aws-resources.sh --dry-run       # Preview
bash scripts/cleanup-aws-resources.sh                 # Execute
```

See [scripts/README.md](scripts/README.md) for detailed documentation on all scripts.

## Documentation

### Getting Started
- [README.md](README.md) - Overview and quick start (this file)
- [Project Phases](docs/PROJECT_PHASES.md) - Development phases and timeline

### Deployment & Operations
- [AWS Setup Guide](docs/AWS_SETUP_GUIDE.md) - IAM, SES, VPC, Security Groups
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - EC2, Docker, Kubernetes deployment options
- [Deployment Checklist](docs/DEPLOYMENT_CHECKLIST.md) - Pre/during/post deployment verification

### Reference
- [Commands Reference](docs/COMMANDS_REFERENCE.md) - All commands by technology (AWS, Python, Docker, Jenkins)
- [Issues Log](docs/ISSUES.md) - Known issues and solutions from all phases
- [Project Structure](docs/PROJECT_STRUCTURE.md) - Detailed directory layout
- [Scripts README](scripts/README.md) - Cleanup and testing scripts documentation

### API Documentation
- **Swagger UI:** http://localhost:8000/docs (interactive API docs)
- **ReDoc:** http://localhost:8000/redoc (alternative API documentation)
