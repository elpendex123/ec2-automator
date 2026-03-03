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

---

## Python Testing (Advanced)

### Run Tests with Coverage Report
```bash
python3.10 -m pytest tests/ -v --cov=app --cov-report=term-missing
```
**What it does:** Runs all tests with verbose output, shows code coverage with missing line numbers
**Arguments:**
- `-v`: Verbose output showing each test
- `--cov=app`: Measure coverage for app/ directory
- `--cov-report=term-missing`: Show missing lines in terminal

**Expected output:**
```
tests/unit/test_models.py::TestLaunchInstanceRequest::test_valid_request PASSED [10%]
...
======================== 55 passed in 5.44s ========================
Name                         Stmts   Miss  Cover   Missing
app/models.py                  30      0   100%
app/endpoints.py               53     14    74%   68-76, 118-120
TOTAL                         340     64    81%
```

### Run Specific Test Class
```bash
python3.10 -m pytest tests/unit/test_models.py::TestLaunchInstanceRequest -v
```
**What it does:** Runs only tests in a specific class
**Arguments:**
- `::ClassName`: Filter to specific test class

**Expected output:**
```
tests/unit/test_models.py::TestLaunchInstanceRequest::test_valid_request PASSED
tests/unit/test_models.py::TestLaunchInstanceRequest::test_invalid_app_name PASSED
...
======================== 6 passed in 0.45s ========================
```

### Run Tests with Auto-reload on Change
```bash
python3.10 -m pytest tests/ --watch
```
**What it does:** Re-runs tests whenever test files change (requires pytest-watch)
**Expected output:**
```
Test session started
collected 55 items
...
[Re-running on file change...]
```

---

## Code Quality (Linting & Formatting)

### Check Code with Ruff (Show Issues)
```bash
python3.10 -m ruff check app/ tests/
```
**What it does:** Scans code for style/error issues without modifying
**Expected output:**
```
F401 [*] `app.tasks.task_store` imported but unused
 --> app/background.py:6:23
help: Remove unused import: `app.tasks.task_store`
```

### Auto-fix Ruff Issues
```bash
python3.10 -m ruff check app/ tests/ --fix
```
**What it does:** Automatically fixes fixable issues (removing unused imports, etc.)
**Arguments:**
- `--fix`: Apply fixes directly to files

**Expected output:**
```
Found 12 errors (12 fixed, 0 remaining).
```

### Check Code Formatting (Black)
```bash
python3.10 -m black --check app/ tests/
```
**What it does:** Checks if code conforms to Black formatting without modifying
**Expected output:**
```
would reformat app/background.py
would reformat app/models.py
2 files would be reformatted.
```

### Apply Code Formatting (Black)
```bash
python3.10 -m black app/ tests/
```
**What it does:** Automatically formats all code to PEP 8 style
**Expected output:**
```
reformatted app/aws/ec2.py
reformatted app/models.py
All done! 2 files reformatted.
```

---

## Docker (Phase 6+)

### Build Docker Image
```bash
docker build -t ec2-automator:latest .
```
**What it does:** Builds Docker image from Dockerfile in current directory
**Arguments:**
- `-t`: Tag name (image name:version)
- `.`: Build context (current directory)

**Expected output:**
```
Step 1/9 : FROM python:3.12-alpine
Step 2/9 : WORKDIR /app
...
Step 9/9 : CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
Successfully built 281d0e22941b
Successfully tagged ec2-automator:latest
```

### Run Docker Container (Detached)
```bash
docker run -d --name ec2-automator-test -p 8000:8000 \
  -e AWS_REGION=us-east-1 \
  -e SES_SENDER_EMAIL=enrique.coello@gmail.com \
  ec2-automator
```
**What it does:** Runs container in background with environment variables
**Arguments:**
- `-d`: Detached mode (background)
- `--name`: Container name
- `-p 8000:8000`: Port mapping (host:container)
- `-e`: Environment variables
- Last arg: Image name

**Expected output:**
```
f3b44f5219c6...  (Container ID)
```

### Stop Docker Container
```bash
docker stop ec2-automator-test
```
**What it does:** Gracefully stops a running container
**Expected output:**
```
ec2-automator-test
```

### Remove Docker Container
```bash
docker rm ec2-automator-test
```
**What it does:** Removes a stopped container
**Expected output:**
```
ec2-automator-test
```

### View Docker Container Logs
```bash
docker logs ec2-automator-test
```
**What it does:** Shows logs from container stdout/stderr
**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### List Running Containers
```bash
docker ps
```
**What it does:** Shows all running containers
**Expected output:**
```
CONTAINER ID   IMAGE              COMMAND                 CREATED        STATUS
f3b44f521f6    ec2-automator      "uvicorn app.main:a..."  2 minutes ago  Up 2 minutes
```

### Remove Docker Image
```bash
docker rmi ec2-automator:latest
```
**What it does:** Removes a Docker image
**Expected output:**
```
Untagged: ec2-automator:latest
Deleted: sha256:281d0e22941b...
```

---

## Troubleshooting Commands

### Check Port Usage
```bash
lsof -i :8000
```
**What it does:** Shows which process is using port 8000
**Arguments:**
- `-i :PORT`: Check specific port
- Use for any port: `:8001`, `:5432`, etc.

**Expected output:**
```
COMMAND    PID    USER   FD   TYPE DEVICE SIZE NODE NAME
uvicorn  31761 enrique    6u  IPv4 215405      0 TCP *:8000 (LISTEN)
```

### Kill Process Using Port
```bash
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```
Or simpler:
```bash
pkill -f uvicorn
```
**What it does:** Terminates the process using port 8000
**Arguments:**
- `-9`: Force kill signal
- `-f`: Match full command name (not just process name)

**Expected output:**
```
(No output, process terminated)
```

### Check if Port is Free
```bash
lsof -i :8000 2>/dev/null || echo "Port 8000 is free"
```
**What it does:** Checks port availability
**Expected output:**
```
Port 8000 is free
```
Or:
```
COMMAND    PID    USER   FD   TYPE DEVICE SIZE NODE NAME
[process info]
```

### Verify Python Version in Virtual Environment
```bash
python3.10 -c "import sys; print(sys.version)"
```
**What it does:** Shows Python version being used
**Expected output:**
```
3.10.12 (main, ... Linux)
```

### List Installed Packages
```bash
pip list | grep -E "pytest|boto3|fastapi"
```
**What it does:** Shows installed versions of specific packages
**Arguments:**
- `grep -E`: Filter package names with regex

**Expected output:**
```
boto3                 1.36.5
fastapi               0.115.4
pytest                9.0.2
```

### Check if Module Can Be Imported
```bash
python3.10 -c "import moto; print('moto installed')"
```
**What it does:** Tests if a Python module is available
**Expected output:**
```
moto installed
```

---

## AWS CLI (Free Tier)

### Check Free Tier Eligible Instance Types
```bash
aws ec2 describe-instance-types --filters "Name=free-tier-eligible,Values=true" \
  --query 'InstanceTypes[].InstanceType' --output text
```
**What it does:** Lists all Free Tier eligible instance types
**Arguments:**
- `--filters`: Filter by free-tier-eligible
- `--query`: Extract only InstanceType field
- `--output text`: Plain text output

**Expected output:**
```
t3.micro t3.small t4g.micro t4g.small c7i-flex.large m7i-flex.large
```

### List Running EC2 Instances (Table Format)
```bash
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[].{ID:InstanceId,Name:Tags[?Key==`Name`]|[0].Value,Type:InstanceType}' \
  --output table
```
**What it does:** Shows all running instances with ID, Name, and Type in table format
**Expected output:**
```
------------------------------------------
|     DescribeInstances                  |
+--------+----────+---------+------------+
| ID     | Name   | Type    |
+--------+----────+---------+------------+
| i-1234 | web-01 | t3.micro |
+--------+----────+---------+------------+
```

### Terminate Multiple EC2 Instances
```bash
aws ec2 terminate-instances --instance-ids i-123 i-456 i-789
```
**What it does:** Terminates specified instances (saves Free Tier hours)
**Arguments:**
- `--instance-ids`: Space-separated list of instance IDs

**Expected output:**
```
TerminatingInstances:
  - InstanceId: i-123
    CurrentState: shutting-down
```

### Get Instance Types for Free Tier (x86_64 Linux only)
```bash
aws ec2 describe-instance-types --filters \
  "Name=free-tier-eligible,Values=true" \
  "Name=processor-info.valid-architectures,Values=x86_64" \
  --query 'InstanceTypes[].InstanceType' --output text
```
**What it does:** Lists Free Tier x86_64 instance types (filters out ARM types)
**Expected output:**
```
t3.micro t3.small c7i-flex.large m7i-flex.large
```

### List SES Verified Email Addresses
```bash
aws ses list-identities --region us-east-1
```
**What it does:** Shows all verified email addresses in SES
**Arguments:**
- `--region`: SES region

**Expected output:**
```
{
    "Identities": [
        "enrique.coello@gmail.com"
    ]
}
```

### Send Test Email via SES (CLI)
```bash
aws ses send-email --from enrique.coello@gmail.com \
  --to enrique.coello@gmail.com \
  --subject "Test Email" \
  --text "This is a test" \
  --region us-east-1
```
**What it does:** Sends a test email via AWS SES to verify it works
**Expected output:**
```
{
    "MessageId": "000001234567890-abcdef..."
}
```

---

## Git Commands (Advanced)

### Remove File from Git Tracking (Keep Locally)
```bash
git rm --cached CLAUDE.md
```
**What it does:** Stops tracking file without deleting it locally
**Expected output:**
```
rm 'CLAUDE.md'
```

### Add to Gitignore and Commit
```bash
echo "CLAUDE.md" >> .gitignore
git add .gitignore
git commit -m "Add CLAUDE.md to gitignore"
```
**What it does:** Ensures file is never committed in future

### Show What Would Be Committed
```bash
git diff --cached
```
**What it does:** Shows staged changes before committing
**Expected output:**
```
diff --git a/app/main.py b/app/main.py
+new_line_added
-old_line_removed
```

### Revert Last Commit (Keep Changes)
```bash
git reset --soft HEAD~1
```
**What it does:** Undoes last commit but keeps changes staged
**Arguments:**
- `--soft`: Keep changes staged
- `--mixed`: Keep changes unstaged
- `--hard`: Discard changes (danger!)

### View Recent Commits
```bash
git log --oneline -10
```
**What it does:** Shows last 10 commits in one-line format
**Expected output:**
```
4da19ea Phase 6: Docker complete
ae0ad89 Phase 5: Testing complete
a1b2c3d Phase 4: Email integration
...
```

---

## Docker Container Testing (Phase 7+)

### Start Test Container
```bash
docker run -d --name test-api -p 8000:8000 \
  -e AWS_REGION=us-east-1 \
  -e SES_SENDER_EMAIL=enrique.coello@gmail.com \
  elpendex123/ec2-automator:latest

sleep 3 && echo "Container started"
```
**What it does:** Starts containerized API for testing
**Arguments:**
- `-d`: Detached mode (background)
- `--name test-api`: Container name
- `-p 8000:8000`: Port mapping
- `-e`: Environment variables
- `sleep 3`: Wait for startup

**Expected output:**
```
Container started
```

### Test Health Endpoint
```bash
curl -s http://localhost:8000/health | python3.10 -m json.tool
```
**What it does:** Verifies container is running and healthy
**Expected output:**
```json
{
    "status": "healthy",
    "service": "ec2-automator"
}
```

### Test Options Endpoint
```bash
curl -s http://localhost:8000/options | python3.10 -m json.tool
```
**What it does:** Gets available instance types and apps
**Expected output:**
```json
{
    "instance_types": ["t3.micro", "t3.small"],
    "apps": ["nginx", "mysql", "httpd", "mongo"]
}
```

### Test Launch Endpoint (Valid)
```bash
curl -s -X POST http://localhost:8000/launch \
  -H "Content-Type: application/json" \
  -d '{
    "instance_name":"test-01",
    "instance_type":"t3.micro",
    "app_name":"nginx",
    "owner":"test-user"
  }' | python3.10 -m json.tool
```
**What it does:** Tests valid instance launch request
**Expected output:**
```json
{
    "task_id": "uuid-here",
    "status": "accepted",
    "message": "Instance launch initiated..."
}
```

### Test Launch Endpoint (Invalid)
```bash
curl -s -X POST http://localhost:8000/launch \
  -H "Content-Type: application/json" \
  -d '{
    "instance_name":"test-02",
    "instance_type":"t2.large",
    "app_name":"nginx",
    "owner":"test-user"
  }' | python3.10 -m json.tool
```
**What it does:** Tests request validation (invalid instance type)
**Expected output:**
```json
{
    "detail": [
        {
            "type": "literal_error",
            "loc": ["body", "instance_type"],
            "msg": "Input should be 't3.micro' or 't3.small'"
        }
    ]
}
```

### Get Task Status
```bash
curl -s http://localhost:8000/status/<task-id> | python3.10 -m json.tool
```
**What it does:** Checks status of async task
**Arguments:**
- `<task-id>`: Replace with actual task ID from launch response

**Expected output:**
```json
{
    "task_id": "...",
    "status": "pending|running|completed|failed",
    "instance_id": "i-xxx or null",
    "error": null or error message
}
```

### View Container Logs
```bash
docker logs test-api | tail -50
```
**What it does:** Shows recent container logs
**Expected output:**
```
{"timestamp": "...", "level": "INFO", "message": "..."}
[with JSON structured logging]
```

### Stop Test Container
```bash
docker stop test-api && docker rm test-api && echo "Container stopped"
```
**What it does:** Stops and removes container
**Expected output:**
```
Container stopped
```

---

## Jenkins Pipeline Testing (Phase 7+)

### Manually Trigger Jenkins Job
```bash
# Via Jenkins UI: Click job → Build Now
# Or via Jenkins CLI:
java -jar jenkins-cli.jar -s http://localhost:8080 build ec2-automator-lint
```
**What it does:** Manually triggers a Jenkins job
**Expected output:**
```
Scheduled build of ec2-automator-lint for execution
```

### Check Jenkins Job Status
```bash
curl -s http://localhost:8080/job/ec2-automator-lint/lastBuild/api/json | python3.10 -m json.tool
```
**What it does:** Gets last build status via Jenkins API
**Arguments:**
- Replace `ec2-automator-lint` with actual job name
- `lastBuild` returns most recent build

**Expected output:**
```json
{
    "result": "SUCCESS",
    "building": false,
    "number": 1,
    "timestamp": 1234567890000
}
```

### View Jenkins Build Log
```bash
curl -s http://localhost:8080/job/ec2-automator-lint/lastBuild/consoleText
```
**What it does:** Gets full console output of last build
**Expected output:**
```
Started by user enrique
...
Finished: SUCCESS
```

### Verify All 5 Jobs Completed
```bash
for job in "1 - Setup" "2 - Lint" "3 - Test" "4 - Build" "5 - Push"; do
  curl -s "http://localhost:8080/job/ec2-automator/$job/lastBuild/api/json" | \
    python3.10 -c "import json,sys; d=json.load(sys.stdin); print(f'$job: {d[\"result\"]}')"
done
```
**What it does:** Checks result of all 5 pipeline jobs
**Expected output:**
```
1 - Setup: SUCCESS
2 - Lint: SUCCESS
3 - Test: SUCCESS
4 - Build: SUCCESS
5 - Push: SUCCESS
```

---

## Notes
- All AWS commands assume you have AWS CLI configured with credentials
- Replace example values (instance IDs, email addresses, etc.) with actual values
- Port 8000 is the default FastAPI port; adjust if using different port
- Port 8080 is Jenkins default; adjust if using different port
- Docker commands assume Docker is installed and running
- Git commands assume repository is initialized
- Use `python3.10` for consistent Python version (avoid environment issues)
- Always use virtual environments (venv) for Python projects
- Check Free Tier limits regularly: `aws ec2 describe-instances`
- Kill old processes before starting new services: `pkill -f uvicorn`
- Jenkins requires Java and plugins installed before use
- Test container locally before trusting in production
- Full pipeline execution: setup (once) → lint (manual) → test,build,push (auto)
