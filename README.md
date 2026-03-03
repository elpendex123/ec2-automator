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
Provisions a new EC2 instance asynchronously.

**Request:**
```json
{
  "instance_name": "web-server-01",
  "instance_type": "t3.micro",
  "app_name": "nginx",
  "owner": "team-member"
}
```

**Response:**
```json
{
  "task_id": "task-abc123def456",
  "status": "accepted",
  "message": "Instance launch started"
}
```

### GET /status/{task_id}
Check the status of an async provisioning task.

**Response:**
```json
{
  "task_id": "task-abc123def456",
  "status": "completed",
  "instance_id": "i-1234567890abcdef0"
}
```

### DELETE /terminate/{instance_id}
Terminate an EC2 instance.

**Response:**
```json
{
  "message": "Termination requested",
  "instance_id": "i-1234567890abcdef0"
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

## Documentation

- [Project Phases](docs/PROJECT_PHASES.md) - Development phases and timeline
- [Commands Reference](docs/COMMANDS_REFERENCE.md) - All commands by technology
- [Project Structure](docs/PROJECT_STRUCTURE.md) - Detailed directory layout
- [Issues Log](docs/ISSUES.md) - Known issues and solutions
