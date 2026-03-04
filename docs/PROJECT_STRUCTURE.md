# Project Structure

Complete directory and file structure for EC2-Automator project.

```
dark_wolf_senior_software_engineer/
├── .git/                              # Git repository (local only)
├── .github/                           # GitHub-specific files
│   └── workflows/                     # GitHub Actions (if using)
│       └── ci-cd.yml                  # CI/CD workflow
├── .gitignore                         # Git ignore rules
├── .env.example                       # Example environment variables
├── CLAUDE.md                          # Project specification
├── Dockerfile                         # Docker image definition
├── Jenkinsfile                        # Jenkins pipeline definition
├── docker-compose.yml                 # Docker Compose for local dev
├── requirements.txt                   # Python dependencies
├── requirements-dev.txt               # Python dev dependencies
├── pyproject.toml                     # Python project metadata
├── README.md                          # Project README
│
├── app/                               # Main application package
│   ├── __init__.py                    # Package initialization
│   ├── main.py                        # FastAPI app entry point
│   ├── config.py                      # Configuration (AVAILABLE_APPS, settings)
│   ├── models.py                      # Pydantic models for validation
│   ├── logging_config.py              # JSON logging configuration
│   ├── endpoints.py                   # Route handlers (GET, POST, DELETE)
│   ├── tasks.py                       # Task management (task store, status)
│   ├── background.py                  # Background worker logic
│   │
│   ├── aws/                           # AWS integration modules
│   │   ├── __init__.py
│   │   ├── ec2.py                     # EC2 provisioning & termination
│   │   ├── ses.py                     # Email notifications via SES
│   │   └── credentials.py             # AWS credential handling
│   │
│   ├── utils/                         # Utility modules
│   │   ├── __init__.py
│   │   ├── validators.py              # Input validation helpers
│   │   ├── formatters.py              # Response formatting helpers
│   │   └── errors.py                  # Custom exception classes
│   │
│   └── middleware/                    # Custom middleware
│       ├── __init__.py
│       └── logging.py                 # Request/response logging
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── conftest.py                    # Pytest fixtures & configuration
│   │
│   ├── unit/                          # Unit tests
│   │   ├── __init__.py
│   │   ├── test_models.py             # Pydantic model validation
│   │   ├── test_endpoints.py          # Endpoint logic tests
│   │   └── test_utils.py              # Utility function tests
│   │
│   ├── integration/                   # Integration tests
│   │   ├── __init__.py
│   │   ├── test_ec2_workflow.py       # Full EC2 launch workflow
│   │   ├── test_ses_workflow.py       # Email notification workflow
│   │   └── test_task_management.py    # Task tracking workflow
│   │
│   └── fixtures/                      # Test data & mocks
│       ├── mock_aws.py                # Moto mocks for AWS
│       ├── sample_requests.py         # Sample API requests
│       └── sample_responses.py        # Sample API responses
│
├── docs/                              # Project documentation
│   ├── PROJECT_PHASES.md              # Development phases breakdown
│   ├── PROJECT_STRUCTURE.md           # This file
│   ├── ISSUES.md                      # Issues & problems log
│   ├── COMMANDS_REFERENCE.md          # Commands by technology
│   ├── API_DOCUMENTATION.md           # API endpoint documentation
│   ├── AWS_SETUP.md                   # AWS resource setup guide
│   ├── DEPLOYMENT.md                  # Deployment procedures
│   └── TROUBLESHOOTING.md             # Common issues & solutions
│
├── uml/                               # UML Diagrams & Architecture
│   ├── README.md                      # Diagram generation guide
│   ├── TESTING.md                     # Testing procedures
│   ├── pyreverse/                     # Class & package diagrams
│   ├── plantuml/                      # Professional UML diagrams
│   ├── py2puml/                       # Auto-generated class diagrams
│   ├── pydeps/                        # Dependency graphs
│   ├── diagrams/                      # AWS architecture diagrams
│   ├── mermaid/                       # GitHub-native diagrams
│   └── jenkins/                       # CI/CD auto-generation pipeline
│
├── scripts/                           # Utility scripts
│   ├── setup_aws.sh                   # AWS infrastructure setup
│   ├── setup_jenkins.sh               # Jenkins configuration
│   ├── setup_local.sh                 # Local development setup
│   ├── deploy.sh                      # Deployment script
│   └── test_api.sh                    # API endpoint testing
│
├── iac/                               # Infrastructure as Code (optional)
│   ├── terraform/                     # Terraform configurations
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   └── cloudformation/                # CloudFormation templates
│       └── ec2-automator.yaml
│
└── .docker/                           # Docker related files
    ├── .dockerignore
    └── entrypoint.sh                  # Container entrypoint script
```

---

## Directory Descriptions

### Root Level
- **CLAUDE.md** - Project specification with all requirements
- **Dockerfile** - Container image definition
- **Jenkinsfile** - CI/CD pipeline stages
- **docker-compose.yml** - Local development environment
- **requirements.txt** - Python package dependencies
- **pyproject.toml** - Python project configuration

### `/app`
Main application source code organized by concern:
- **main.py** - FastAPI application setup, middleware, app initialization
- **config.py** - Static configuration (AVAILABLE_APPS, settings)
- **models.py** - Pydantic request/response models
- **endpoints.py** - Route handlers for all API endpoints
- **tasks.py** - Task store and task management logic
- **background.py** - Background worker for async EC2 launch

#### `/app/aws`
AWS SDK integration:
- **ec2.py** - EC2 instance provisioning, termination, tagging
- **ses.py** - Email notifications via AWS SES
- **credentials.py** - IAM instance profile credential handling

#### `/app/utils`
Helper utilities:
- **validators.py** - Input validation functions
- **formatters.py** - Response/error formatting
- **errors.py** - Custom exception classes

#### `/app/middleware`
HTTP middleware:
- **logging.py** - Request/response logging to JSON stdout

### `/tests`
Test suite organized by test type:
- **conftest.py** - Pytest configuration and shared fixtures
- **unit/** - Tests for individual functions/classes
- **integration/** - Tests for complete workflows
- **fixtures/** - Mock data and reusable test fixtures

### `/docs`
Comprehensive documentation:
- **PROJECT_PHASES.md** - Development phases and timeline
- **ISSUES.md** - Issues tracking log
- **COMMANDS_REFERENCE.md** - Commands organized by technology
- **API_DOCUMENTATION.md** - OpenAPI spec and endpoint docs
- **AWS_SETUP.md** - Step-by-step AWS resource setup
- **DEPLOYMENT.md** - Production deployment procedures

### `/scripts`
Automated setup and deployment:
- **setup_aws.sh** - Creates IAM roles, policies, security groups
- **setup_jenkins.sh** - Jenkins job and credential configuration
- **deploy.sh** - Deployment to production

### `/uml`
Architecture visualization and UML diagrams:
- **README.md** - Comprehensive guide to 6 professional diagram generation tools
- **TESTING.md** - Testing procedures and verification checklist
- **pyreverse/** - Auto-generated class and package diagrams (4 PNG files)
- **plantuml/** - 5 professional UML diagram types (10 PNG + SVG files)
  - Sequence diagrams (instance launch workflow)
  - Activity diagrams (background task processing)
  - Component diagrams (architecture relationships)
  - Deployment diagrams (AWS infrastructure)
  - Class diagrams (Pydantic models)
- **pydeps/** - Module dependency analysis (3 interactive SVG graphs)
- **diagrams/** - AWS architecture diagrams (Python code generation)
- **mermaid/** - GitHub-native markdown diagrams (auto-renders in GitHub)
- **jenkins/** - Jenkins pipeline for automatic diagram generation on code changes

### `/iac` (Optional)
Infrastructure as Code:
- **terraform/** - Terraform modules for AWS resources
- **cloudformation/** - CloudFormation templates

---

## File Creation Order

When starting implementation, create files in this order:

1. **Core Config**
   - `app/__init__.py`
   - `app/config.py` (with AVAILABLE_APPS)
   - `requirements.txt`

2. **Models & Validation**
   - `app/models.py`
   - `app/utils/validators.py`

3. **Logging Setup**
   - `app/logging_config.py`
   - `app/middleware/logging.py`

4. **FastAPI App**
   - `app/main.py`
   - `app/endpoints.py`

5. **AWS Integration**
   - `app/aws/__init__.py`
   - `app/aws/ec2.py`
   - `app/aws/ses.py`

6. **Async Tasks**
   - `app/tasks.py`
   - `app/background.py`

7. **Testing**
   - `tests/conftest.py`
   - `tests/unit/test_models.py`
   - `tests/unit/test_endpoints.py`

8. **Docker**
   - `Dockerfile`
   - `docker-compose.yml`

9. **CI/CD**
   - `Jenkinsfile`

10. **Documentation**
    - `README.md`
    - `docs/*.md` files

11. **Architecture & Diagrams**
    - `uml/` - UML diagram generation system with 6 professional tools
    - `uml/README.md` - Comprehensive diagram generation guide
    - `uml/pyreverse/` - Auto-generated class & package diagrams
    - `uml/plantuml/` - 5 professional UML diagram types (sequence, activity, component, deployment, class)
    - `uml/pydeps/` - Module dependency analysis and visualization
    - `uml/diagrams/` - AWS architecture diagrams
    - `uml/mermaid/` - GitHub-native markdown diagrams
    - `uml/jenkins/` - Jenkins CI/CD pipeline for automatic diagram generation

---

## File Size Estimates

| File | Estimated Size | Notes |
|------|----------------|-------|
| `app/main.py` | 150-200 lines | FastAPI app, routes init |
| `app/endpoints.py` | 100-150 lines | 3 endpoints, error handling |
| `app/models.py` | 50-80 lines | 3-4 Pydantic models |
| `app/aws/ec2.py` | 100-150 lines | EC2 provisioning logic |
| `app/aws/ses.py` | 50-80 lines | Email notification logic |
| `app/tasks.py` | 60-100 lines | Task store, status tracking |
| `app/background.py` | 80-120 lines | Background worker logic |
| `tests/` | 400-600 lines total | Unit + integration tests |
| `Dockerfile` | 20-30 lines | Lightweight Alpine-based |
| `Jenkinsfile` | 30-50 lines | 4 stages + post actions |

---

## Key Naming Conventions

- **Files:** `snake_case.py`
- **Directories:** `lowercase`
- **Classes:** `PascalCase`
- **Functions:** `snake_case()`
- **Constants:** `UPPER_CASE`
- **Private methods:** `_private_method()`
- **Pydantic models:** Suffix with `Request` or `Response` (e.g., `LaunchInstanceRequest`)

---

## Ignored Files (in .gitignore)

```
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.ruff_cache/
.env
.venv/
venv/
env/
*.log
.DS_Store
.vscode/
.idea/
*.egg-info/
dist/
build/
.coverage
htmlcov/
```

---

## Dependencies Tree

```
FastAPI (web framework)
├── Pydantic (validation)
├── Uvicorn (ASGI server)
└── Starlette (async support)

Boto3 (AWS SDK)
├── botocore
├── jmespath
└── s3transfer

pytest (testing)
├── pytest-asyncio
└── pytest-cov

Development tools:
├── ruff (linting)
├── black (formatting)
└── moto (AWS mocking)
```

