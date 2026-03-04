# diagrams - AWS Infrastructure as Code Diagrams

**diagrams** (mingrammer/diagrams) is a Python library for programmatically creating cloud architecture diagrams. Perfect for documenting deployment topologies and AWS infrastructure.

## Overview

diagrams generates professional AWS architecture diagrams by writing Python code instead of using GUI tools. The diagrams are created programmatically, making them:
- Version controllable
- Reproducible
- Easy to update
- Suitable for CI/CD integration

## Installation

```bash
# Install diagrams library
pip install diagrams==0.23.3

# Install Graphviz (required for diagram rendering)
sudo apt-get install graphviz graphviz-dev

# Verify installation
python -c "import diagrams; print('diagrams installed')"
which dot  # Should show Graphviz is installed
```

## Quick Start

```bash
# Generate all diagrams
python generate_architecture.py

# View generated PNG files
ls -lh *.png
```

## What It Generates

### 1. ec2_automator_architecture.png
**High-level system architecture showing all components and relationships**

Structure:
```
┌─────────────────────────────────────────────────────┐
│  Docker Container (FastAPI Application)             │
│  ┌────────────────┐  ┌────────────────────┐        │
│  │ FastAPI Router │→ │ Pydantic Models    │        │
│  └────────────────┘  └────────────────────┘        │
│                            ↓                        │
│  ┌────────────────┐  ┌────────────────┐           │
│  │ Task Store     │← │ Background     │           │
│  └────────────────┘  │ Worker         │           │
│                      └────────────────┘           │
└─────────────────────────────────────────────────────┘
            ↓                    ↓
    ┌──────────────┐    ┌──────────────┐
    │ EC2 Boto3    │    │ SES Boto3    │
    └──────────────┘    └──────────────┘
            ↓                    ↓
    ┌──────────────┐    ┌──────────────┐
    │ EC2 Instances│    │ Email Service│
    │ (Managed)    │    │ (Notifications)
    └──────────────┘    └──────────────┘
```

**Components Shown**:
- Docker container running FastAPI
- FastAPI endpoints and routers
- Pydantic validation models
- In-memory task store
- Background workers
- EC2 provisioning (boto3)
- SES email notifications (boto3)
- AWS infrastructure (VPC, Security Groups, IAM)

### 2. deployment_flow.png
**Instance launch workflow from request to completion**

Sequence:
```
User Request
    ↓
API Endpoint (/launch)
    ↓
Pydantic Validation
    ↓
Task Creation
    ├→ Immediate: Return HTTP 202
    └→ Parallel: Launch Background Worker
           ↓
        EC2 Client (run_instances)
           ↓
        New EC2 Instance Created
           ↓
        Boto3 SES (send_email)
           ↓
        Success/Failure Email
           ↓
        Update Task Status
```

**Shows**:
- Immediate HTTP 202 response path
- Asynchronous background task execution
- EC2 instance provisioning
- Email notification flow
- Task status updates

### 3. free_tier_topology.png
**Free tier eligible AWS resources and limits**

Structure:
```
EC2-Automator Host
  └─ t3.micro (FREE)
       ├─ Default VPC
       │   ├─ t3.micro OR t3.small (managed instances)
       │   ├─ Amazon Linux 2023, Ubuntu 22.04, Ubuntu 24.04
       │   └─ Security Group (Ports 22, 80, 443, 3306, 27017)
       ├─ SES Email Service (62,000/day FREE)
       └─ CloudWatch Logs (optional)
```

**Key Information**:
- t3.micro and t3.small instance options
- Supported AMIs (Amazon Linux 2023, Ubuntu)
- Security group rules
- Free tier email limits
- IAM instance profile

## How It Works

diagrams uses AWS CDK-like Python syntax to define architecture:

```python
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2
from diagrams.aws.integration import SES

with Diagram("My Architecture", show=False):
    web = EC2("webserver")
    db = RDS("database")
    email = SES("email")

    web >> db
    web >> email
```

**Syntax**:
- `with Diagram(...)`: Context manager for diagram
- `with Cluster(...)`: Group related components
- `>>`: Connection arrow (shows data flow)
- `[item1, item2]`: Multiple connections

## Component Library

### Compute
```python
from diagrams.aws.compute import EC2, Lambda, ECS
```

### Storage
```python
from diagrams.aws.storage import S3, EBS, EFS
```

### Database
```python
from diagrams.aws.database import RDS, DynamoDB, ElastiCache
```

### Networking
```python
from diagrams.aws.network import VPC, ALB, Route53
```

### Integration
```python
from diagrams.aws.integration import SQS, SNS, SES
```

### Security
```python
from diagrams.aws.security import IAM, KMS, SecretsManager
```

### Containers
```python
from diagrams.onprem.container import Docker
```

### Version Control
```python
from diagrams.onprem.vcs import Github, Gitlab
```

## Advanced Usage

### Custom Labels

```python
server = EC2("web server\nProduction")
# Label appears under icon

db = RDS("PostgreSQL\n15.2")
```

### Custom Connections

```python
from diagrams import Edge

web >> Edge(label="HTTPS") >> db
web >> Edge(label="Query", style="dashed") >> cache
```

### Edge Attributes

```python
# Different styles
Edge(style="dotted")
Edge(style="bold")
Edge(style="dashed")

# Labels
Edge(label="data flow")
Edge(label="secure", color="red")
```

### Nested Clusters

```python
with Diagram("Complex"):
    with Cluster("Region 1"):
        with Cluster("AZ 1"):
            instance = EC2("server")
        with Cluster("AZ 2"):
            backup = EC2("backup")
```

## For EC2-Automator

### What It Shows Well ✅
- Docker container running on EC2
- AWS service dependencies (EC2, SES, IAM)
- VPC and networking setup
- Free tier resource eligibility
- Deployment workflow (request → response → email)
- Component relationships

### What It Doesn't Show ❌
- Internal module dependencies (use pydeps instead)
- Class hierarchies (use pyreverse instead)
- Sequence diagrams (use PlantUML instead)
- Code-level details

## Workflow Integration

### 1. Architecture Reviews
```bash
# Update diagram when infrastructure changes
python uml/diagrams/generate_architecture.py

# Review changes in PR
git diff uml/diagrams/
```

### 2. Documentation
```bash
# Embed diagrams in README
![Architecture](uml/diagrams/ec2_automator_architecture.png)
```

### 3. CI/CD Pipeline
```yaml
# GitHub Actions
- name: Generate architecture diagrams
  run: python uml/diagrams/generate_architecture.py

- name: Upload diagrams
  uses: actions/upload-artifact@v2
  with:
    name: diagrams
    path: uml/diagrams/*.png
```

## Troubleshooting

### diagrams module not found
```bash
pip install diagrams --upgrade
python -c "import diagrams; print('OK')"
```

### Graphviz not found
```bash
# Install Graphviz
sudo apt-get install graphviz graphviz-dev

# Verify
which dot
dot -V
```

### PNG generation fails
```bash
# Check Graphviz installation
python -c "from diagrams import Diagram; print('OK')"

# Try with explicit export
export PATH="/usr/bin:$PATH"
python generate_architecture.py
```

### Java errors
```bash
# Graphviz may need Java for rendering
java -version
sudo apt-get install default-jre
```

### Low resolution output
```python
# Increase DPI in diagram generation
# Note: diagrams library doesn't have built-in DPI settings
# PNG quality depends on system Graphviz configuration
```

## Comparison with Other Tools

| Feature | diagrams | PlantUML | pydeps | pyreverse |
|---------|----------|----------|--------|-----------|
| AWS icons | ✅ | ⚠️ | ❌ | ❌ |
| Python code | ✅ | ❌ | ❌ | ❌ |
| Architecture | ✅ | ✅ | ❌ | ❌ |
| Dependency graphs | ❌ | ❌ | ✅ | ✅ |
| Class diagrams | ❌ | ✅ | ❌ | ✅ |
| Sequence diagrams | ❌ | ✅ | ❌ | ❌ |
| Professional icons | ✅ | ❌ | ❌ | ❌ |

## References

- [diagrams GitHub](https://github.com/mingrammer/diagrams)
- [diagrams Documentation](https://diagrams.mingrammer.com)
- [AWS Icons](https://diagrams.mingrammer.com/docs/reference/aws)
- [Graphviz Documentation](https://graphviz.org)

---

**Tool Type**: Infrastructure as Code Diagrams
**License**: MIT
**Requires**: Python 3.6+, Graphviz
