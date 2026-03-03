# Jenkins Job Files

Modular Jenkins jobs for EC2-Automator CI/CD pipeline. Each job is independent and can be run separately.

## Jobs Overview

### 1. `Jenkinsfile.setup`
**Purpose:** Install all dependencies (heavy lifting)
**Run:** Once per session or nightly
**Time:** 2-3 minutes (first run), cached after
**When to use:** Initial setup, dependency updates
**What it does:**
- Upgrades pip
- Installs requirements.txt (FastAPI, Boto3, etc.)
- Installs requirements-dev.txt (pytest, ruff, black, moto)
- Verifies all tools installed

**Run in Jenkins:**
```groovy
// In Jenkins job configuration:
Definition: Pipeline script from SCM
SCM: Git
Branch: master
Script Path: jenkins/Jenkinsfile.setup
```

---

### 2. `Jenkinsfile.lint`
**Purpose:** Code quality checks (fast)
**Run:** Manual trigger after code changes
**Time:** 10-15 seconds
**Prerequisites:** Dependencies installed (run setup first)
**What it does:**
- Runs ruff on app/ and tests/
- Checks Black formatting
- Reports style/error issues

**Run in Jenkins:**
```groovy
Definition: Pipeline script from SCM
Script Path: jenkins/Jenkinsfile.lint
```

**Local equivalent:**
```bash
python3.10 -m ruff check app/ tests/
python3.10 -m black --check app/ tests/
```

---

### 3. `Jenkinsfile.test`
**Purpose:** Run test suite with coverage (fast)
**Run:** Manual trigger after linting passes
**Time:** 30-45 seconds
**Prerequisites:** Dependencies installed (run setup first)
**What it does:**
- Runs pytest (55 tests)
- Generates coverage report (XML + HTML)
- Publishes JUnit test results
- Publishes HTML coverage report to Jenkins

**Run in Jenkins:**
```groovy
Definition: Pipeline script from SCM
Script Path: jenkins/Jenkinsfile.test
```

**Local equivalent:**
```bash
python3.10 -m pytest tests/ -v --cov=app --cov-report=html
```

---

### 4. `Jenkinsfile.build`
**Purpose:** Build Docker image (no push)
**Run:** Manual trigger after tests pass
**Time:** 20-45 seconds
**Prerequisites:** Docker installed, Dockerfile present
**What it does:**
- Builds Docker image with build number tag
- Also tags as 'latest'
- Verifies image works
- Shows image size

**Run in Jenkins:**
```groovy
Definition: Pipeline script from SCM
Script Path: jenkins/Jenkinsfile.build
```

**Local equivalent:**
```bash
docker build -t ec2-automator:latest .
docker run --rm ec2-automator:latest python -c "import app"
```

---

### 5. `Jenkinsfile.push`
**Purpose:** Push Docker image to registry (optional)
**Run:** Manual trigger after build passes (OPTIONAL)
**Time:** 15-30 seconds
**Prerequisites:** Docker credentials configured, image built
**When to use:** Only when ready to deploy to Docker Hub
**What it does:**
- Verifies image exists
- Pushes to Docker registry (currently shows what would happen)
- Requires Docker Hub credentials

**To enable actual push:**
1. Go to Jenkins: Manage Jenkins > Manage Credentials
2. Add Docker Hub credentials (username + token)
3. Set credential ID to: `dockerhub-credentials`
4. Uncomment docker push commands in the stage

**Local equivalent:**
```bash
docker login -u <username> -p <token>
docker push elpendex123/ec2-automator:latest
docker logout
```

---

## Job Execution Workflow

```
┌─────────────────────────────────────────────┐
│ 1. Jenkinsfile.setup (RUN ONCE)            │
│    Install all dependencies                │
│    Time: 2-3 min                          │
│    Frequency: Once per session             │
└──────────────┬──────────────────────────────┘
               │
               ├─────────────────────────────────────────┐
               │                                         │
               ▼                                         ▼
    ┌────────────────────────┐          ┌────────────────────────┐
    │ 2. Jenkinsfile.lint    │          │ (3. Jenkinsfile.test)  │
    │    Code quality checks │          │    Run test suite      │
    │    Time: 10-15 sec     │          │    Time: 30-45 sec     │
    │    Run: After commit   │          │    Run: After lint     │
    └──────────┬─────────────┘          └────────────┬───────────┘
               │                                      │
               └──────────────────┬───────────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │ 4. Jenkinsfile.build     │
                    │    Docker build          │
                    │    Time: 20-45 sec       │
                    │    Run: After tests pass │
                    └──────────────┬───────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │ 5. Jenkinsfile.push      │
                    │    Docker push (optional)│
                    │    Time: 15-30 sec       │
                    │    Run: Manual, if ready │
                    └──────────────────────────┘
```

---

## Recommended Execution Pattern

### First Time (Full Setup)
```
1. Run Jenkinsfile.setup
   └─ Installs everything (~2-3 min)
2. Run Jenkinsfile.lint
   └─ Quick validation (~10-15 sec)
3. Run Jenkinsfile.test
   └─ Run tests (~30-45 sec)
4. Run Jenkinsfile.build
   └─ Docker build (~20-45 sec)

TOTAL: ~4 minutes
```

### Subsequent Times (Fast Cycle)
```
1. Run Jenkinsfile.lint
   └─ Code quality (~10-15 sec)
2. Run Jenkinsfile.test
   └─ Tests + coverage (~30-45 sec)
3. Run Jenkinsfile.build
   └─ Docker build (~20-45 sec)

TOTAL: ~60-90 seconds (vs 4 minutes)
```

### When Deploying
```
1. Run Jenkinsfile.lint
2. Run Jenkinsfile.test
3. Run Jenkinsfile.build
4. Run Jenkinsfile.push  ← Only when ready to deploy
```

---

## Setting Up Jobs in Jenkins

### Create Each Job

For each Jenkinsfile:

1. Click **New Item** in Jenkins
2. Enter job name (e.g., `ec2-automator-lint`)
3. Select **Pipeline**
4. Click **OK**

In **Pipeline** section:
- **Definition:** Pipeline script from SCM
- **SCM:** Git
- **Repository URL:** `https://github.com/elpendex123/ec2-automator.git`
- **Branch:** `*/master`
- **Script Path:** `jenkins/Jenkinsfile.lint` (adjust per job)

Click **Save**

### Manual Triggers

To run a job:
1. Click job name in Jenkins
2. Click **Build Now**
3. Wait for execution
4. Review logs and results

---

## Troubleshooting

### "Module not found" errors
- Run `Jenkinsfile.setup` first to install dependencies
- Check Python is 3.10: `python3.10 --version`

### Docker build fails
- Ensure Docker is installed: `docker --version`
- Run locally first: `docker build -t test .`

### Test failures
- Run locally: `python3.10 -m pytest tests/ -v`
- Check specific test: `python3.10 -m pytest tests/unit/test_models.py -v`

### Lint failures
- Run locally: `python3.10 -m ruff check app/ --fix`
- Format: `python3.10 -m black app/ tests/`

### Push fails
- Verify credentials configured in Jenkins
- Test locally: `docker login` then `docker push ...`

---

## Environment Variables

Set globally in Jenkins or per job:

```groovy
environment {
    DOCKER_REGISTRY = 'docker.io'
    DOCKER_IMAGE = 'elpendex123/ec2-automator'
    DOCKER_TAG = "${BUILD_NUMBER}"
    PYTHON_VERSION = '3.10'
}
```

---

## Performance Summary

| Job | Setup | Subsequent | What It Does |
|-----|-------|-----------|-------------|
| setup | 2-3 min | - | Install deps (once) |
| lint | - | 10-15 sec | Code quality |
| test | - | 30-45 sec | 55 tests + coverage |
| build | - | 20-45 sec | Docker image |
| push | - | 15-30 sec | Docker registry |
| **Total (first)** | **~4 min** | - | Full pipeline |
| **Total (fast)** | - | **~60-90 sec** | Lint+Test+Build |

---

## References

- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [Docker Building Images](https://docs.docker.com/build/)
- [pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
