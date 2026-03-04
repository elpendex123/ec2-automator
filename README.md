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
├── tests/                 # Test suite (55 tests, 81% coverage)
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                  # Documentation (8 files, 5000+ lines)
│   ├── PROJECT_PHASES.md
│   ├── COMMANDS_REFERENCE.md
│   ├── ISSUES.md
│   ├── AWS_SETUP_GUIDE.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── PROJECT_STRUCTURE.md
│   └── JENKINS_SETUP.md
├── uml/                   # UML Diagrams & Architecture Visualization
│   ├── README.md          # UML generation guide (6 tools, 17+ diagrams)
│   ├── TESTING.md         # Testing procedures for diagram tools
│   ├── pyreverse/         # Auto-generated class & package diagrams
│   ├── plantuml/          # 5 professional UML diagram types
│   ├── py2puml/           # Auto-generated PlantUML from Python code
│   ├── pydeps/            # Module dependency graphs
│   ├── diagrams/          # AWS architecture diagrams
│   ├── mermaid/           # GitHub-native markdown diagrams
│   └── jenkins/           # Jenkins pipeline for diagram auto-generation
├── jenkins/               # Jenkins CI/CD pipeline
│   ├── Jenkinsfile.setup  # Install dependencies (run once)
│   ├── Jenkinsfile.lint   # Code quality checks (manual)
│   ├── Jenkinsfile.test   # Run test suite (auto-triggered)
│   ├── Jenkinsfile.build  # Build Docker image (auto-triggered)
│   ├── Jenkinsfile.push   # Push to registry (auto-triggered)
│   ├── README.md          # Job descriptions
│   ├── PIPELINE_SETUP.md  # Configuration guide
│   └── QUICK_CONFIG.md    # Quick reference
├── scripts/               # Utility scripts
│   ├── test_api.sh        # Test API endpoints
│   ├── cleanup-aws-resources.sh      # Terminate EC2 instances
│   ├── cleanup-local-deployment.sh   # Stop local services
│   ├── cleanup-docker.sh  # Remove Docker containers
│   └── README.md          # Scripts documentation
├── Dockerfile             # Container definition (Alpine, Python 3.12)
├── docker-compose.yml     # Docker Compose for local dev
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── pyproject.toml         # Project configuration
├── .gitignore            # Git ignore rules
├── .env.example          # Environment variables template
└── README.md             # This file
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
- **[README.md](README.md)** (this file) - Project overview, quick start, tech stack, API endpoints, security, monitoring, and logging

- **[docs/PROJECT_PHASES.md](docs/PROJECT_PHASES.md)** - Development phases 1-9, deliverables, timeline, and critical path
  - Phase 1: Setup & Dependencies
  - Phase 2: FastAPI Core
  - Phase 3: EC2 Integration
  - Phase 4: SES Integration
  - Phase 5: Async Tasks
  - Phase 6: Docker & Containerization
  - Phase 7: Jenkins CI/CD ✅
  - Phase 8: Testing & QA ✅
  - Phase 9: Documentation & Deployment ✅

### Deployment & Operations
- **[docs/AWS_SETUP_GUIDE.md](docs/AWS_SETUP_GUIDE.md)** (536 lines) - Complete AWS resource setup
  - IAM role and policy creation (CLI + Console)
  - SES email verification and sandbox configuration
  - VPC and security group setup with inbound rules
  - Free Tier limits and cost monitoring
  - Troubleshooting guide (7 common issues)

- **[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** (682 lines) - Multi-option deployment procedures
  - EC2 + Systemd deployment (with systemd service file)
  - Docker Compose production deployment
  - Kubernetes (EKS) deployment (with manifests)
  - Health checks and monitoring setup (CloudWatch, Prometheus)
  - Production hardening (security, firewall, rate limiting, TLS)
  - Rollback procedures for all deployment types
  - Troubleshooting common deployment issues

- **[docs/DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md)** (393 lines) - Comprehensive deployment verification
  - Pre-deployment checklist (32 items: AWS account, IAM, SES, code, Docker)
  - Day-of-deployment checklist (50+ items: testing, execution)
  - Post-deployment verification (25+ items: first 24 hours)
  - Weekly/monthly/annual operations checklists
  - Rollback decision criteria
  - Sign-off requirements

### Reference
- **[docs/COMMANDS_REFERENCE.md](docs/COMMANDS_REFERENCE.md)** (1600+ lines) - All development commands
  - Python: pip, pytest, ruff, black commands
  - AWS: IAM, SES, EC2, CloudWatch CLI commands
  - Docker: build, run, compose, cleanup commands
  - Git: clone, commit, push, branch commands
  - Jenkins: job trigger and monitoring commands
  - Cleanup scripts: test_api.sh, cleanup-*.sh commands
  - Phase 9 deployment commands and monitoring

- **[docs/ISSUES.md](docs/ISSUES.md)** (770 lines) - Known issues and solutions
  - Phase 1-7 issues with root causes and solutions
  - Issue template for future issues
  - Severity levels (Critical, High, Medium, Low)
  - Known limitations and Free Tier constraints
  - Troubleshooting guidance

- **[docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** - Detailed directory layout and file descriptions

- **[jenkins/README.md](jenkins/README.md)** - Jenkins pipeline documentation
  - 5 modular jobs: setup, lint, test, build, push
  - Job descriptions and timing expectations
  - Workflow diagrams and performance metrics
  - Troubleshooting guide

- **[jenkins/PIPELINE_SETUP.md](jenkins/PIPELINE_SETUP.md)** - Step-by-step Jenkins configuration
  - Detailed setup for each of 5 jobs
  - Auto-triggering configuration with Parameterized Trigger Plugin
  - Full pipeline execution examples

- **[jenkins/QUICK_CONFIG.md](jenkins/QUICK_CONFIG.md)** - Quick reference for Jenkins configuration

- **[scripts/README.md](scripts/README.md)** - Utility scripts documentation
  - cleanup-aws-resources.sh - Terminate EC2 instances
  - cleanup-local-deployment.sh - Stop local services
  - cleanup-docker.sh - Remove Docker containers
  - test_api.sh - Test API endpoints

### Architecture & Diagrams
- **[uml/README.md](uml/README.md)** - UML diagram generation guide
  - 6 professional diagram tools with examples
  - 17+ generated diagrams (class, sequence, component, deployment, dependency)
  - Installation and usage for each tool
  - CI/CD integration via Jenkins pipeline

### API Documentation
- **Swagger UI:** http://localhost:8000/docs - Interactive API documentation with try-it-out capability
- **ReDoc:** http://localhost:8000/redoc - Alternative API documentation format
- **OpenAPI Schema:** http://localhost:8000/openapi.json - Machine-readable API specification
