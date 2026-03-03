# EC2-Automator: Project Phases

## Overview
This document outlines the development phases for building the EC2-Automator REST API for provisioning AWS Free Tier EC2 instances.

---

## Phase 1: Project Setup & Dependencies
**Goal:** Initialize project structure and install all required dependencies.

### Tasks
- [ ] Initialize Python project structure
  - Create `src/` directory
  - Create `app/` submodules for modular code
  - Create `tests/` directory for unit tests

- [ ] Set up dependency management
  - Create `requirements.txt` with all dependencies
  - Create `requirements-dev.txt` for dev tools (pytest, ruff, black)

- [ ] Create configuration files
  - `.gitignore` (Python, Docker, IDE files)
  - `pyproject.toml` for build metadata
  - `.env.example` for environment variables

### Dependencies to Install
```
fastapi==0.109.0+
uvicorn[standard]==0.27.0+
pydantic==2.5.0+
boto3==1.34.0+
python-dotenv==1.0.0+
```

### Dev Dependencies
```
pytest==7.4.0+
pytest-asyncio==0.23.0+
ruff==0.1.0+
black==23.12.0+
```

### Deliverables
- Project directory structure in place
- `requirements.txt` and `requirements-dev.txt` created
- `.gitignore` and `pyproject.toml` configured

---

## Phase 2: FastAPI Application Core
**Goal:** Build the core FastAPI application with request/response models and basic endpoints.

### Tasks
- [ ] Create Pydantic models for validation
  - `LaunchInstanceRequest` model
  - `LaunchInstanceResponse` model
  - `InstanceOption` model

- [ ] Implement logging with JSON formatting
  - Configure Python `logging` module
  - JSON output to stdout
  - Request/response logging middleware

- [ ] Build REST endpoints
  - `GET /options` - List available instance types and apps
  - `POST /launch` - Launch instance (returns 202 Accepted with task_id)
  - `DELETE /terminate/{instance_id}` - Terminate instance
  - `GET /status/{task_id}` - Check async task status

- [ ] Error handling framework
  - HTTPException wrapping
  - Error response formatting
  - Validation error responses

### Deliverables
- `app/main.py` with FastAPI app initialization
- `app/models.py` with Pydantic models
- `app/logging_config.py` with JSON logging setup
- `app/endpoints.py` with all route handlers
- Health check endpoint implemented

---

## Phase 3: AWS Integration - EC2 & Tagging
**Goal:** Integrate AWS EC2 provisioning and implement instance tagging.

### Tasks
- [ ] Configure Boto3 client
  - Create EC2 client using IAM instance profile
  - Handle AWS region configuration
  - Error handling for ClientError

- [ ] Implement EC2 instance launch
  - Call `ec2.create_instances()` with proper parameters
  - Include UserData scripts from `AVAILABLE_APPS`
  - Set instance type and AMI validation

- [ ] Implement instance tagging
  - Apply Name, Owner, CreatedBy tags
  - Use TagSpecifications during launch

- [ ] Implement instance termination
  - Stop instances with `ec2.stop_instances()`
  - Terminate with `ec2.terminate_instances()`

### Deliverables
- `app/aws_ec2.py` with EC2 operations
- `app/config.py` with AVAILABLE_APPS dictionary
- Instance launch logic with tagging
- Instance termination logic

---

## Phase 4: AWS Integration - Email Notifications (SES)
**Goal:** Implement email notifications using AWS SES.

### Tasks
- [ ] Configure SES client
  - Create SES client using IAM instance profile
  - Set region configuration
  - Verify sender email in SES

- [ ] Implement send_notification function
  - Accept subject, body, recipient parameters
  - Handle SES errors and retry logic
  - Log email send status

- [ ] Integrate notifications into EC2 workflow
  - Send success email after instance launch
  - Send failure email if launch fails
  - Include instance details in email body

### Deliverables
- `app/aws_ses.py` with SES operations
- Email template functions
- Integration into background task workflow

---

## Phase 5: Asynchronous Task Queue & Background Workers
**Goal:** Implement asynchronous task execution with task ID tracking.

### Tasks
- [ ] Set up task tracking system
  - In-memory task store (simple dict with task_id -> status)
  - Task status: pending, running, completed, failed

- [ ] Create background worker
  - Use `asyncio` for async EC2 operations
  - Background task executes: launch instance -> send email
  - Update task status in store

- [ ] Implement async endpoints
  - `POST /launch` returns 202 with task_id immediately
  - `GET /status/{task_id}` returns current task status
  - Task details include: status, instance_id, errors

- [ ] Error handling in background tasks
  - Catch exceptions during EC2 launch
  - Catch exceptions during email send
  - Log detailed error messages

### Deliverables
- `app/tasks.py` with task management
- `app/background.py` with background worker logic
- Task store implementation
- Status endpoint implementation

---

## Phase 6: Docker & Containerization
**Goal:** Create Docker image for the application.

### Tasks
- [ ] Create Dockerfile
  - Base: `python:3.12-alpine`
  - Multi-stage if needed
  - Install dependencies
  - Expose port 8000
  - Health check included

- [ ] Create docker-compose.yml (optional)
  - Local development setup
  - Port mapping
  - Environment variables

- [ ] Build and test Docker image locally
  - Build image
  - Run container
  - Test endpoints with curl

### Deliverables
- `Dockerfile` optimized for Alpine
- `.dockerignore` file
- Docker image builds successfully
- Container runs and responds to requests

---

## Phase 7: Jenkins CI/CD Pipeline ✅
**Goal:** Set up automated testing, building, and deployment.
**Status:** COMPLETE

### Tasks
- [x] Create modular Jenkinsfiles (5 jobs)
  - `Jenkinsfile.setup` - Install dependencies (run once)
  - `Jenkinsfile.lint` - Code quality checks (ruff)
  - `Jenkinsfile.test` - Test suite (pytest)
  - `Jenkinsfile.build` - Docker image build
  - `Jenkinsfile.push` - Docker registry push

- [x] Configure auto-triggering between jobs
  - setup → lint (manual)
  - lint → test (auto on success)
  - test → build (auto on success)
  - build → push (auto on success)

- [x] Test pipeline end-to-end
  - All 5 jobs executed successfully
  - Docker image built and verified
  - API endpoints tested and working
  - Container deployment tested

### Deliverables
- `jenkins/` directory with 5 modular Jenkinsfiles
- `jenkins/README.md` - Job descriptions
- `jenkins/PIPELINE_SETUP.md` - Configuration guide
- `jenkins/QUICK_CONFIG.md` - Quick reference
- Jenkins pipeline executing successfully
- Docker container tested and verified

### Issues Fixed
- Issue #13: Missing NOTIFICATION_EMAIL env var
- Issue #14: Pip dependency conflicts (pytest/pytest-asyncio)
- Issue #15: pytest-asyncio plugin incompatibility
- Issue #16: Missing HTML Publisher Jenkins plugin
- Issue #17: Modular job chain execution optimization

---

## Phase 8: Documentation & Deployment
**Goal:** Comprehensive testing of all components.

### Tasks
- [ ] Unit tests
  - Test Pydantic models validation
  - Test endpoint request/response handling
  - Test error conditions
  - Mock AWS calls with moto library

- [ ] Integration tests
  - Test full launch workflow (without AWS)
  - Test termination workflow
  - Test task status tracking

- [ ] Code quality
  - Run ruff linter
  - Run black formatter
  - Achieve high test coverage

### Deliverables
- `tests/` directory with test files
- Test coverage report
- All tests passing
- Code passes linting

---

## Phase 9: Documentation & Deployment
**Goal:** Complete documentation and prepare for production deployment.

### Tasks
- [ ] Create API documentation
  - OpenAPI/Swagger docs (FastAPI built-in)
  - README.md with setup instructions
  - Deployment guide

- [ ] AWS setup documentation
  - IAM role creation steps
  - SES email verification steps
  - VPC/Security group configuration

- [ ] Deployment checklist
  - Environment variables required
  - AWS credentials setup
  - Docker registry setup
  - Jenkins configuration

- [ ] Monitoring & Logging setup
  - CloudWatch integration (future)
  - Log aggregation setup
  - Health check configuration

### Deliverables
- Complete README.md
- API documentation
- AWS setup guide
- Deployment checklist

---

## Summary Timeline
| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: Setup & Dependencies | 1-2 hours | Pending |
| Phase 2: FastAPI Core | 3-4 hours | Pending |
| Phase 3: EC2 Integration | 2-3 hours | Pending |
| Phase 4: SES Integration | 1-2 hours | Pending |
| Phase 5: Async Tasks | 2-3 hours | Pending |
| Phase 6: Docker | 1-2 hours | Pending |
| Phase 7: Jenkins CI/CD | 2-3 hours | Pending |
| Phase 8: Testing & QA | 3-4 hours | Pending |
| Phase 9: Docs & Deploy | 2-3 hours | Pending |

---

## Critical Path
1. Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 (Core API)
2. Phase 6 (Docker) - parallel with Phase 5
3. Phase 7 (Jenkins) - after Phase 6
4. Phase 8 & 9 (Testing/Docs) - ongoing throughout

---

## Notes
- Each phase builds on previous phases
- AWS resources should be created/configured before starting Phase 3
- Testing (Phase 8) should happen incrementally, not just at the end
- Documentation should be updated as code is written
