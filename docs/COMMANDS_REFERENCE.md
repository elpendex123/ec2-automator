# Commands Reference

This document lists all commands executed during development, organized by technology. Each command includes what it does and expected output.

---

## Python

### pip / Package Management

#### Install Dependencies
```bash
pip install -r requirements.txt
```
**What it does:** Installs all Python dependencies listed in requirements.txt
**Expected output:**
```
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 pydantic-2.5.0 boto3-1.34.0 ...
```

#### Install Dev Dependencies
```bash
pip install -r requirements-dev.txt
```
**What it does:** Installs development dependencies (pytest, ruff, black)
**Expected output:**
```
Successfully installed pytest-7.4.0 pytest-asyncio-0.23.0 ruff-0.1.0 black-23.12.0 ...
```

#### Freeze Current Dependencies
```bash
pip freeze > requirements.txt
```
**What it does:** Exports currently installed packages to requirements.txt
**Expected output:**
```
(No output, file is written)
```

---

### Testing

#### Run All Tests
```bash
pytest
```
**What it does:** Runs all tests in the tests/ directory
**Expected output:**
```
collected 24 items

tests/test_endpoints.py::test_get_options PASSED
tests/test_ec2.py::test_create_instance PASSED
...
======================== 24 passed in 2.34s ========================
```

#### Run Tests with Coverage
```bash
pytest --cov=app tests/
```
**What it does:** Runs tests and reports code coverage
**Expected output:**
```
collected 24 items
...
======================== 24 passed in 2.45s ========================
Name                  Stmts   Miss  Cover
app/__init__.py            1      0   100%
app/main.py              45      2    96%
...
TOTAL                    200     12    94%
```

#### Run Specific Test File
```bash
pytest tests/test_endpoints.py -v
```
**What it does:** Runs tests in a specific file with verbose output
**Expected output:**
```
tests/test_endpoints.py::test_get_options PASSED
tests/test_endpoints.py::test_launch_instance PASSED
tests/test_endpoints.py::test_terminate_instance PASSED
======================== 3 passed in 0.54s ========================
```

---

### Code Quality

#### Lint with Ruff
```bash
ruff check .
```
**What it does:** Checks code for style and error issues
**Expected output:**
```
(No output if all OK, or list of issues):
app/main.py:15:1: F401 imported but unused: `json`
app/aws_ec2.py:22:80: E501 line too long (92 > 79)
```

#### Format Code with Black
```bash
black .
```
**What it does:** Automatically formats code to PEP 8 style
**Expected output:**
```
reformatted app/main.py
reformatted app/aws_ec2.py
All done! 2 files reformatted.
```

#### Check Formatting Only (Black)
```bash
black --check .
```
**What it does:** Checks if code needs formatting without modifying
**Expected output:**
```
would reformat app/main.py
would reformat app/aws_ec2.py
2 files would be reformatted.
```

---

### Running Application

#### Run FastAPI Server Directly
```bash
uvicorn app.main:app --reload
```
**What it does:** Starts the FastAPI development server with auto-reload
**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete
```

#### Run with Specific Port
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```
**What it does:** Starts FastAPI server on specific host/port
**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

---

## Docker

### Build Commands

#### Build Docker Image
```bash
docker build -t ec2-automator:latest .
```
**What it does:** Builds a Docker image from Dockerfile
**Expected output:**
```
[+] Building 15.3s (10/10) FINISHED
=> [internal] load build definition from Dockerfile                       0.0s
=> [1/8] FROM python:3.12-alpine                                         2.1s
...
=> exporting to image                                                     0.8s
=> => naming to docker.io/library/ec2-automator:latest                   0.0s
```

#### Build with Build Arguments
```bash
docker build -t ec2-automator:v1.0 --build-arg VERSION=1.0 .
```
**What it does:** Builds image with build-time arguments
**Expected output:**
```
[+] Building 12.5s (10/10) FINISHED
...
```

---

### Run Commands

#### Run Container Interactively
```bash
docker run -it -p 8000:8000 ec2-automator:latest
```
**What it does:** Runs container in interactive mode, maps port 8000
**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started server process [1]
INFO:     Application startup complete
```

#### Run Container in Background
```bash
docker run -d -p 8000:8000 --name ec2-api ec2-automator:latest
```
**What it does:** Runs container in detached mode with a name
**Expected output:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```
(Container ID)

#### Run with Environment Variables
```bash
docker run -d -p 8000:8000 -e AWS_REGION=us-east-1 ec2-automator:latest
```
**What it does:** Runs container with environment variables
**Expected output:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

---

### Inspection & Management

#### View Running Containers
```bash
docker ps
```
**What it does:** Lists running containers
**Expected output:**
```
CONTAINER ID   IMAGE                  COMMAND                  STATUS
a1b2c3d4e5f6   ec2-automator:latest   "uvicorn app.main:a..."  Up 2 minutes
```

#### View Container Logs
```bash
docker logs a1b2c3d4e5f6
```
**What it does:** Shows logs from running container
**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
INFO:     127.0.0.1:55432 - "GET /options HTTP/1.1" 200 OK
```

#### Stop Container
```bash
docker stop ec2-api
```
**What it does:** Stops a running container
**Expected output:**
```
ec2-api
```

#### Remove Container
```bash
docker rm ec2-api
```
**What it does:** Removes a stopped container
**Expected output:**
```
ec2-api
```

#### Remove Image
```bash
docker rmi ec2-automator:latest
```
**What it does:** Removes a Docker image
**Expected output:**
```
Untagged: ec2-automator:latest
Deleted: sha256:a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

---

### Docker Compose

#### Start Services
```bash
docker-compose up -d
```
**What it does:** Starts all services defined in docker-compose.yml in background
**Expected output:**
```
Creating ec2-automator ... done
```

#### Stop Services
```bash
docker-compose down
```
**What it does:** Stops and removes containers
**Expected output:**
```
Stopping ec2-automator ... done
Removing ec2-automator ... done
Removing network docker_default
```

---

## AWS CLI

### EC2 Commands

#### List EC2 Instances
```bash
aws ec2 describe-instances --region us-east-1
```
**What it does:** Lists all EC2 instances in a region
**Expected output:**
```
{
    "Reservations": [
        {
            "Instances": [
                {
                    "InstanceId": "i-1234567890abcdef0",
                    "InstanceType": "t3.micro",
                    "State": {"Name": "running"},
                    ...
                }
            ]
        }
    ]
}
```

#### Get Specific Instance Details
```bash
aws ec2 describe-instances --instance-ids i-1234567890abcdef0 --region us-east-1
```
**What it does:** Gets details for a specific instance
**Expected output:**
```
JSON output with instance details
```

#### Create Security Group
```bash
aws ec2 create-security-group --group-name ec2-automator --description "Security group for EC2-Automator" --region us-east-1
```
**What it does:** Creates a security group
**Expected output:**
```
{
    "GroupId": "sg-1234567890abcdef0"
}
```

#### Authorize Ingress Rules
```bash
aws ec2 authorize-security-group-ingress --group-id sg-1234567890abcdef0 --protocol tcp --port 22 --cidr 0.0.0.0/0 --region us-east-1
```
**What it does:** Adds inbound rule to security group
**Expected output:**
```
{
    "Return": true
}
```

---

### IAM Commands

#### Create IAM Role
```bash
aws iam create-role --role-name EC2-Automator-Role --assume-role-policy-document file://trust-policy.json
```
**What it does:** Creates an IAM role
**Expected output:**
```
{
    "Role": {
        "RoleName": "EC2-Automator-Role",
        "Arn": "arn:aws:iam::123456789012:role/EC2-Automator-Role",
        ...
    }
}
```

#### Attach Policy to Role
```bash
aws iam attach-role-policy --role-name EC2-Automator-Role --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess
```
**What it does:** Attaches a policy to a role
**Expected output:**
```
(No output if successful)
```

#### Create Instance Profile
```bash
aws iam create-instance-profile --instance-profile-name EC2-Automator-Profile
```
**What it does:** Creates an instance profile
**Expected output:**
```
{
    "InstanceProfile": {
        "InstanceProfileName": "EC2-Automator-Profile",
        "Arn": "arn:aws:iam::123456789012:instance-profile/EC2-Automator-Profile",
        ...
    }
}
```

#### Add Role to Instance Profile
```bash
aws iam add-role-to-instance-profile --instance-profile-name EC2-Automator-Profile --role-name EC2-Automator-Role
```
**What it does:** Adds a role to an instance profile
**Expected output:**
```
(No output if successful)
```

---

### SES Commands

#### Verify Email Address
```bash
aws ses verify-email-identity --email-address noreply@yourdomain.com --region us-east-1
```
**What it does:** Verifies an email address for sending via SES
**Expected output:**
```
(No output if successful)
```

#### List Verified Identities
```bash
aws ses list-identities --region us-east-1
```
**What it does:** Lists all verified email addresses/domains
**Expected output:**
```
{
    "Identities": ["noreply@yourdomain.com"]
}
```

---

## Git Commands

### Setup & Configuration

#### Initialize Repository
```bash
git init
```
**What it does:** Initializes a new Git repository
**Expected output:**
```
Initialized empty Git repository in /path/to/project/.git/
```

#### Add Remote
```bash
git remote add origin https://github.com/user/ec2-automator.git
```
**What it does:** Adds a remote repository
**Expected output:**
```
(No output if successful)
```

---

### Basic Operations

#### Check Status
```bash
git status
```
**What it does:** Shows current branch and uncommitted changes
**Expected output:**
```
On branch main
Changes to be committed:
  modified:   app/main.py
Changes not staged for commit:
  modified:   requirements.txt
```

#### Add Files to Staging
```bash
git add .
```
**What it does:** Stages all modified files
**Expected output:**
```
(No output if successful)
```

#### Commit Changes
```bash
git commit -m "Add EC2 provisioning endpoint"
```
**What it does:** Commits staged changes
**Expected output:**
```
[main a1b2c3d] Add EC2 provisioning endpoint
 2 files changed, 45 insertions(+), 3 deletions(-)
```

#### Push to Remote
```bash
git push origin main
```
**What it does:** Pushes commits to remote repository
**Expected output:**
```
Counting objects: 3, done.
Delta compression using up to 4 threads.
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 287 bytes | 287.00 KiB/s, done.
Total 3 (delta 2), reused 0 (delta 0)
To github.com:user/ec2-automator.git
   a1b2c3d..e5f6g7h main -> main
```

---

## cURL / HTTP Testing

### GET Requests

#### Get Available Options
```bash
curl http://localhost:8000/options
```
**What it does:** Fetches list of available instance types and apps
**Expected output:**
```json
{
    "instance_types": ["t3.micro", "t3.small"],
    "apps": ["nginx", "mysql", "httpd", "mongo"]
}
```

#### Get Task Status
```bash
curl http://localhost:8000/status/task-123
```
**What it does:** Checks status of async task
**Expected output:**
```json
{
    "task_id": "task-123",
    "status": "completed",
    "instance_id": "i-1234567890abcdef0"
}
```

---

### POST Requests

#### Launch Instance
```bash
curl -X POST http://localhost:8000/launch \
  -H "Content-Type: application/json" \
  -d '{
    "instance_name": "web-server-01",
    "instance_type": "t3.micro",
    "app_name": "nginx",
    "owner": "team-member"
  }'
```
**What it does:** Launches a new EC2 instance asynchronously
**Expected output:**
```json
{
    "task_id": "task-abc123",
    "status": "accepted",
    "message": "Instance launch started"
}
```

---

### DELETE Requests

#### Terminate Instance
```bash
curl -X DELETE http://localhost:8000/terminate/i-1234567890abcdef0
```
**What it does:** Terminates an EC2 instance
**Expected output:**
```json
{
    "message": "Termination requested",
    "instance_id": "i-1234567890abcdef0"
}
```

---

## Jenkins

### Local Testing

#### Run Jenkinsfile Locally (with Jenkins CLI)
```bash
java -jar jenkins-cli.jar -s http://localhost:8080 declarative-linter < Jenkinsfile
```
**What it does:** Validates Jenkinsfile syntax
**Expected output:**
```
Jenkinsfile validated successfully
```

---

## Notes
- All AWS commands assume you have AWS CLI configured with credentials
- Replace example values (instance IDs, email addresses, etc.) with actual values
- Port 8000 is the default FastAPI port; adjust if using different port
- Docker commands assume Docker is installed and running
- Git commands assume repository is initialized
