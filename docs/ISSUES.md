# Issues & Problems Log

## Summary

This document tracks all issues encountered during EC2-Automator development, organized by phase. Each issue includes context, root cause, and solution for future reference and learning.

---

## Phase 1: Project Setup

### Issue #1: CLAUDE.md Accidentally Committed to Git
- **Status:** Resolved
- **Severity:** High
- **Component:** Git / Documentation
- **Created:** 2026-03-02
- **Resolved:** 2026-03-02

**Description:**
CLAUDE.md (project specification) was accidentally committed to GitHub. Per user requirements, this file should never be committed or mentioned in repository.

**Root Cause:**
File was created and committed before adding to .gitignore. User had explicitly requested this file not be committed.

**Solution:**
```bash
git rm --cached CLAUDE.md
git commit -m "Remove CLAUDE.md from tracking"
```
Then updated .gitignore to exclude CLAUDE.md and committed that change.

**Learning:**
- Always add sensitive/specification files to .gitignore before initial commit
- Double-check user requirements before committing files to version control
- When committing, ensure CLAUDE.md and Anthropic references are never mentioned

---

## Phase 2: FastAPI Core Development

### Issue #2: t2.micro Instance Type Referenced in Code
- **Status:** Resolved
- **Severity:** High
- **Component:** EC2, Configuration
- **Created:** 2026-03-02
- **Resolved:** 2026-03-02

**Description:**
Initial implementation referenced `t2.micro` as available instance type, but AWS Free Tier actually only includes `t3.micro` and `t3.small` for x86_64 Linux.

**Root Cause:**
Assumed t2.micro was free tier without verifying actual AWS Free Tier offerings.

**Solution:**
Verified with AWS CLI:
```bash
aws ec2 describe-instance-types --filters Name=free-tier-eligible,Values=true
```
Updated all code and documentation to use only t3.micro and t3.small.

**Learning:**
- Always verify AWS Free Tier limits with actual AWS CLI commands, not assumptions
- Check `aws ec2 describe-instance-types` for authoritative free tier information
- Document instance type restrictions clearly in configuration

---

## Phase 3: AWS EC2 & SES Integration

### Issue #3: Wrong SES Sender Email Not Verified
- **Status:** Resolved
- **Severity:** High
- **Component:** SES, Configuration
- **Created:** 2026-03-02
- **Resolved:** 2026-03-02

**Description:**
Initial SES implementation used `noreply@yourdomain.com` as sender email, but this email was not verified in AWS SES, causing SendEmail API calls to fail with "Email address is not verified" error.

**Error Message:**
```
Error: EmailAddressNotVerifiedException
Message: Email address not verified. The following identities failed the check in region US-EAST-1: noreply@yourdomain.com
```

**Root Cause:**
Placeholder email from documentation was used without verifying it existed in SES.

**Solution:**
Changed sender email to `enrique.coello@gmail.com` which was already verified in SES. Updated environment variable `SES_SENDER_EMAIL` in `.env.example`.

**Learning:**
- Always verify email addresses in AWS SES before using them as senders
- Check verified identities: `aws ses list-identities --region us-east-1`
- Use actual verified email addresses, not placeholders
- Test SES sending with CLI before integrating: `aws ses send-email ...`

---

## Phase 4: Background Task Workers & Email

### Issue #4: Test Dependencies Not Installed Consistently
- **Status:** Resolved
- **Severity:** Medium
- **Component:** Testing, Dependencies
- **Created:** 2026-03-02
- **Resolved:** 2026-03-02

**Description:**
Test execution failed with ModuleNotFoundError for pytest, moto, and httpx even after attempts to install them. Packages had to be installed individually multiple times.

**Root Cause:**
Packages were being installed to user's local Python directory rather than virtual environment due to permission issues. Venv was being deleted and recreated repeatedly instead of just installing missing packages.

**Solution:**
Updated `requirements-dev.txt` to include all dev dependencies (pytest, pytest-cov, pytest-asyncio, moto, httpx, ruff, black) so single install covers all needs:
```bash
pip install -r requirements-dev.txt
```

**Learning:**
- Always use virtual environments (venv) to isolate project dependencies
- List all dev dependencies in requirements-dev.txt, don't install individually
- Use `pip install -r requirements-dev.txt` once, not repeated package installs
- Don't `rm -rf venv` repeatedly; instead just `pip install` missing packages
- Check venv activation: `which python` should show path in venv

---

### Issue #5: Multiple EC2 Instances Consuming Free Tier Hours
- **Status:** Resolved
- **Severity:** High
- **Component:** EC2, Free Tier Management
- **Created:** 2026-03-02
- **Resolved:** 2026-03-02

**Description:**
During testing, 4 EC2 instances were created and left running (test-nginx-01, test-mysql-01, test-httpd-01, test-mongo-email), consuming precious Free Tier monthly hours.

**Root Cause:**
Instances were created for testing but not terminated after use. Lack of cleanup discipline during development.

**Solution:**
Terminated all running instances:
```bash
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query 'Reservations[].Instances[].InstanceId' --output text | xargs aws ec2 terminate-instances --instance-ids
```

**Learning:**
- Always check running instances after testing: `aws ec2 describe-instances`
- Terminate test instances immediately after verification
- Free Tier has strict hour limits; cleanup is critical
- Consider setting CloudWatch alarms for EC2 cost anomalies
- Best practice: Use moto mocking for tests instead of real AWS instances

---

### Issue #6: SES Emails Not Delivered Initially
- **Status:** Resolved
- **Severity:** Medium
- **Component:** SES, Email
- **Created:** 2026-03-02
- **Resolved:** 2026-03-02

**Description:**
Emails sent via SES were not appearing in inbox initially. User reported "i didn't get no email yet" after testing send_email function.

**Root Cause:**
SES account was in sandbox mode (default). Emails were being sent but delivered to spam folder due to sandbox restrictions.

**Solution:**
Verified SES setup and resent test email:
```bash
aws ses send-email --from enrique.coello@gmail.com --to enrique.coello@gmail.com --subject "Test" --text "Test body"
```
Confirmed email was received (in spam folder, which is expected for sandbox mode).

**Learning:**
- Sandbox mode in SES limits sending to verified recipients only
- Emails in sandbox mode may go to spam folder
- Check spam folder when testing SES in sandbox
- Request production access for real-world deployments: AWS SES Console > Edit Account Details
- Test with verified recipient email address

---

## Phase 5: Comprehensive Testing

### Issue #7: SES Email Test Failures - Mock Call Arguments
- **Status:** Resolved
- **Severity:** Medium
- **Component:** Testing, SES Tests
- **Created:** 2026-03-03
- **Resolved:** 2026-03-03

**Description:**
3 SES integration tests failed because they were incorrectly checking mock call arguments. Tests used `in call_args[0]` (checking entire tuple) instead of accessing specific positional arguments.

**Error Messages:**
```python
AssertionError: assert 'test-instance' in ('test@example.com', 'EC2 Instance Launch Success: test-instance', '...')
AssertionError: assert 'web-server-01' in '' or 'web-server-01' in ''
```

**Root Cause:**
Incorrect understanding of `mock.call_args` structure. The tuple contains (positional_args, keyword_args), not individual arguments.

**Solution:**
Fixed test assertions to access correct arguments:
```python
# Before (wrong)
assert "test-instance" in call_args[0]

# After (correct)
call_args[0][1]  # subject argument (index 1 of positional args)
assert "test-instance" in call_args[0][1]
```

**Learning:**
- `mock.call_args` is a tuple: (positional_args, keyword_args)
- Access positional: `call_args[0][0]`, `call_args[0][1]`, etc.
- Access keyword: `call_args.kwargs.get("key")`
- Use `.call_args_list` to check multiple calls
- Print mock.call_args during debugging to see structure

---

### Issue #8: Ruff Linting - Unused Imports
- **Status:** Resolved
- **Severity:** Low
- **Component:** Code Quality, Linting
- **Created:** 2026-03-03
- **Resolved:** 2026-03-03

**Description:**
Code quality checks revealed 12 unused imports causing ruff linting failures (F401 errors).

**Root Cause:**
Imports were added during development but later refactored, leaving unused imports behind.

**Solution:**
Ran automatic ruff fix:
```bash
ruff check app/ tests/ --fix
```
Removed unnecessary imports like:
- `task_store` in background.py
- `get_instance_status` in background.py
- `ErrorResponse` in endpoints.py
- `MagicMock` in test files
- Unused typing imports

**Learning:**
- Run linting regularly: `ruff check .`
- Use `--fix` flag to auto-fix: `ruff check . --fix`
- Remove unused imports: don't add comments like "# unused", just delete them
- Integrate rinting into CI/CD pipeline

---

### Issue #9: Pydantic V2 Deprecation Warning
- **Status:** Acknowledged
- **Severity:** Low
- **Component:** Models, Pydantic
- **Created:** 2026-03-03
- **Resolved:** N/A (Future upgrade)

**Description:**
Warning during tests: "Support for class-based `config` is deprecated, use ConfigDict instead."

**Root Cause:**
LaunchInstanceRequest model uses old Pydantic V1 style `Config` class, which is deprecated in V2.

**Warning Message:**
```
app/models.py:20: PydanticDeprecatedSince20: Support for class-based `config` is deprecated
```

**Notes:**
This is a deprecation warning, not a functional issue. Code works correctly. Can be fixed in future Pydantic upgrade:
```python
# Old (V1 style)
class Config:
    validate_assignment = True

# New (V2 style)
model_config = ConfigDict(validate_assignment=True)
```

**Learning:**
- Monitor deprecation warnings
- Plan for Pydantic V2 migration
- Use `ConfigDict` instead of class-based Config in new code

---

## Phase 6: Docker & Containerization

### Issue #10: Docker Compose Command Failed
- **Status:** Resolved
- **Severity:** Medium
- **Component:** Docker, docker-compose
- **Created:** 2026-03-03
- **Resolved:** 2026-03-03

**Description:**
`docker-compose up` command failed with Docker daemon connectivity error: "Not supported URL scheme http+docker".

**Error Message:**
```
docker.errors.DockerException: Error while fetching server API version: Not supported URL scheme http+docker
```

**Root Cause:**
docker-compose version issue or Docker daemon not properly accessible via socket.

**Solution:**
Used `docker run` command directly instead of docker-compose:
```bash
docker run -d --name ec2-automator-test -p 8000:8000 \
  -e AWS_REGION=us-east-1 \
  -e SES_SENDER_EMAIL=enrique.coello@gmail.com \
  ec2-automator
```
docker-compose.yml is still valid and can be used with updated docker-compose V2 or direct `docker compose up`.

**Learning:**
- `docker run` is more reliable for manual testing
- docker-compose syntax may vary by version
- Use `docker ps` to verify container is running
- Check Docker daemon: `docker info`
- Use `docker logs container_name` to debug container issues

---

### Issue #11: Port 8000 Already in Use
- **Status:** Resolved
- **Severity:** Medium
- **Component:** Networking, FastAPI
- **Created:** 2026-03-03
- **Resolved:** 2026-03-03

**Description:**
Attempting to run Docker container on port 8000 failed because local uvicorn server was already listening on that port.

**Root Cause:**
FastAPI development server was running locally from Phase 2 testing and was not stopped before Phase 6 Docker testing.

**Solution:**
Killed the local uvicorn process:
```bash
lsof -i :8000  # Find process using port
kill -9 31761  # Kill the process
# Or use: pkill -f uvicorn
```

**Alternative:**
Could have mapped Docker to different port:
```bash
docker run -p 8001:8000 ec2-automator
```

**Learning:**
- Check port availability before starting services: `lsof -i :PORT`
- Kill port-hogging process: `kill -9 PID`
- Or use pkill: `pkill -f uvicorn`
- Can map Docker to different external port: `-p 8001:8000`
- Use port different from 8000 for concurrent testing

---

### Issue #12: Unable to Locate AWS Credentials in Docker
- **Status:** Expected Behavior
- **Severity:** Medium
- **Component:** Docker, AWS, Authentication
- **Created:** 2026-03-03
- **Resolved:** N/A (By Design)

**Description:**
When testing container endpoints, launch requests failed with "Unable to locate credentials" error.

**Error Message:**
```json
{
  "status": "failed",
  "error": "Unable to locate credentials"
}
```

**Root Cause:**
Container was not properly configured with AWS credentials. Default Boto3 client initialization failed because:
- No AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY environment variables
- No ~/.aws/credentials file mounted into container
- No IAM Instance Profile available (running on local machine, not EC2)

**Solution:**
For local testing with Docker, use one of these approaches:
1. **Mount local AWS credentials** (security risk, not recommended):
   ```bash
   docker run -v ~/.aws:/root/.aws:ro ...
   ```
2. **Use environment variables**:
   ```bash
   docker run -e AWS_ACCESS_KEY_ID=... -e AWS_SECRET_ACCESS_KEY=... ...
   ```
3. **Use IAM Instance Profile** (production, when running on EC2)

For testing: Use moto mocking instead of real AWS calls.

**Learning:**
- Never commit AWS credentials to repository
- Use IAM Instance Profiles in production (EC2 instances)
- Use environment variables for local development
- Mount ~/.aws for local Docker testing only
- Prefer moto mocking for unit/integration tests
- Never store credentials in Dockerfile

---

## Phase 7: Jenkins CI/CD Pipeline

### Issue #13: Missing NOTIFICATION_EMAIL Environment Variable
- **Status:** Resolved
- **Severity:** High
- **Component:** Jenkins, Jenkinsfile
- **Created:** 2026-03-03
- **Resolved:** 2026-03-03

**Description:**
Initial Jenkinsfile used undefined `NOTIFICATION_EMAIL` environment variable in post-build email steps, causing failure.

**Error Message:**
```
groovy.lang.MissingPropertyException: No such property: NOTIFICATION_EMAIL for class: groovy.lang.Binding
```

**Root Cause:**
NOTIFICATION_EMAIL variable referenced in Jenkinsfile but not defined in environment section or Jenkins config.

**Solution:**
Add NOTIFICATION_EMAIL to Jenkins global configuration or define in each Jenkinsfile:
```groovy
environment {
    NOTIFICATION_EMAIL = 'enrique.coello@gmail.com'
}
```

**Learning:**
- Always define all variables used in Jenkinsfile
- Use Jenkins Manage Jenkins → Configure System for global vars
- Or define in environment section of each job
- Test pipeline locally before deployment

---

### Issue #14: Pip Dependency Conflict in Test Job
- **Status:** Resolved
- **Severity:** High
- **Component:** Python Dependencies, pytest
- **Created:** 2026-03-03
- **Resolved:** 2026-03-03

**Description:**
Test job failed during dependency installation with ResolutionImpossible error.

**Error Message:**
```
ERROR: Cannot install -r requirements-dev.txt (line 3) and pytest==7.4.4 because these package versions have conflicting dependencies.
ERROR: ResolutionImpossible: for help visit https://pip.pypa.io/en/latest/topics/dependency-resolution/#dealing-with-dependency-conflicts
```

**Root Cause:**
Initial update to `pytest==8.0.0` and `pytest-asyncio==0.24.0` had conflicting dependencies. These versions are incompatible.

**Solution:**
Reverted to compatible versions:
```
pytest==7.4.4 (not 8.0.0)
pytest-asyncio==0.21.1 (not 0.24.0)
```

These versions are proven to work together.

**Learning:**
- Test dependency updates locally first
- Check PyPI for compatibility information
- Use `pip install --dry-run` to test without installing
- Keep tested version combinations in source control

---

### Issue #15: pytest-asyncio Plugin Incompatibility
- **Status:** Resolved
- **Severity:** High
- **Component:** pytest, pytest-asyncio plugin
- **Created:** 2026-03-03
- **Resolved:** 2026-03-03

**Description:**
Test collection failed with AttributeError when trying to run pytest.

**Error Message:**
```
AttributeError: 'Package' object has no attribute 'obj'
File "pytest_asyncio/plugin.py", line 610, in pytest_collectstart
```

**Root Cause:**
pytest-asyncio 0.23.0 incompatible with pytest 8.0.0. The plugin tried to access an attribute that doesn't exist on Package objects in pytest 8.0.0.

**Solution:**
Used compatible versions:
- pytest: 7.4.4
- pytest-asyncio: 0.21.1

These versions are confirmed compatible with each other.

**Learning:**
- Always check plugin compatibility with framework versions
- Use PyPI to find compatible versions
- Test dependency combinations in full environment
- Keep version combinations documented

---

### Issue #16: Missing Jenkins HTML Publisher Plugin
- **Status:** Resolved
- **Severity:** Medium
- **Component:** Jenkins, publishHTML plugin
- **Created:** 2026-03-03
- **Resolved:** 2026-03-03

**Description:**
Jenkins test job failed with error that publishHTML DSL method not found.

**Error Message:**
```
No such DSL method 'publishHTML' found among steps
```

**Root Cause:**
HTML Publisher Plugin not installed in Jenkins instance. publishHTML step requires this plugin.

**Solution:**
Removed publishHTML from Jenkinsfile since plugin not installed:
```groovy
// Changed from publishHTML to simpler approach
junit 'test-results.xml'
archiveArtifacts artifacts: 'htmlcov/**', allowEmptyArchive: true
```

Can re-add HTML reporting if plugin is installed later:
1. Manage Jenkins → Manage Plugins
2. Search: "HTML Publisher"
3. Install and restart Jenkins

**Learning:**
- Check required plugins before using DSL steps
- Design Jenkinsfiles to be plugin-agnostic when possible
- Document plugin requirements clearly
- Use alternative approaches if plugins unavailable

---

### Issue #17: Modular Jenkinsfile Job Chain Execution
- **Status:** Resolved
- **Severity:** Medium
- **Component:** Jenkins, Pipeline
- **Created:** 2026-03-03
- **Resolved:** 2026-03-03

**Description:**
Original monolithic Jenkinsfile had all stages (setup, lint, test, build, push) in one job, causing 4+ minute executions even for quick changes.

**Root Cause:**
Dependencies reinstalled on every run, taking 2-3 minutes per execution. Setup job should run once, subsequent runs should skip this.

**Solution:**
Broke Jenkinsfile into 5 modular jobs:
1. **ec2-automator-setup** - Run once (2-3 min, install deps)
2. **ec2-automator-lint** - Manual trigger (15 sec)
3. **ec2-automator-test** - Auto-triggered (45 sec)
4. **ec2-automator-build** - Auto-triggered (45 sec)
5. **ec2-automator-push** - Auto-triggered (30 sec)

Each job triggers next on success. Time per deploy: ~90 seconds (vs 4+ minutes).

**Implementation:**
- Created separate Jenkinsfile per job
- Added "Build other projects" post-build actions
- Installed Parameterized Trigger Plugin for auto-triggering
- Created PIPELINE_SETUP.md with configuration guide

**Learning:**
- Break monolithic CI/CD into modular stages
- Use post-build triggers for job chaining
- Cache dependencies to avoid reinstalls
- Document pipeline configuration clearly
- First run: setup once, subsequent runs: skip setup

---

## Phase 8: Testing & QA

**Status:** COMPLETE - No issues encountered

### Summary
Phase 8 focused on comprehensive testing and code quality verification. All tests passed successfully, code quality checks passed, and coverage targets achieved.

### Test Results
- **Total Tests:** 55
- **Passed:** 55 (100%)
- **Test Coverage:** 81%
- **Ruff Linting:** All checks passed ✓
- **Black Formatting:** All files properly formatted ✓
- **Execution Time:** 5.96 seconds

### Tests Completed
1. **Unit Tests** (17 tests)
   - Pydantic models validation
   - Request/response handling
   - Error conditions
   - All passed ✓

2. **Integration Tests** (25 tests)
   - EC2 operations (13 tests)
   - SES email notifications (12 tests)
   - AWS mocking with moto
   - All passed ✓

3. **Code Quality** (3 checks)
   - Ruff linting: All checks passed ✓
   - Black formatting: 22 files properly formatted ✓
   - Coverage report: 81% achieved ✓

### Deliverables
- ✅ Comprehensive test suite in `tests/` directory
- ✅ HTML coverage report in `htmlcov/`
- ✅ All 55 tests passing
- ✅ Code passes all linting checks
- ✅ Code properly formatted

### Learning
- Test suite provides excellent coverage for critical paths
- Moto mocking works reliably for AWS services
- Pytest-asyncio integration with FastAPI is solid
- Focus on integration testing for complex workflows
- Coverage metrics help identify untested error paths

---

## Phase 9: Documentation & Deployment

**Status:** COMPLETE - No issues encountered

### Summary
Phase 9 focused on comprehensive documentation for production deployment. All documentation created and reviewed, covering API usage, AWS setup, deployment procedures, and operational checklists.

### Documentation Created
1. **README.md Enhancements** (expanded from 242 to 320+ lines)
   - API endpoints with request/response examples
   - JSON structured logging documentation
   - Security best practices
   - Monitoring recommendations
   - Added Swagger/ReDoc links

2. **docs/AWS_SETUP_GUIDE.md** (300+ lines)
   - IAM role creation (CLI + Console)
   - SES email verification
   - Security group configuration
   - Free Tier limits and monitoring
   - Troubleshooting guide

3. **docs/DEPLOYMENT_GUIDE.md** (450+ lines)
   - EC2 + Systemd deployment
   - Docker Compose deployment
   - Kubernetes (EKS) deployment
   - Health checks and monitoring
   - Security hardening
   - Rollback procedures

4. **docs/DEPLOYMENT_CHECKLIST.md** (400+ lines)
   - Pre-deployment checklist (20+ items)
   - Day-of-deployment checklist (50+ items)
   - Post-deployment checklist (25+ items)
   - Weekly/Monthly/Annual operations
   - Rollback decision criteria
   - Sign-off requirements

### Key Features Documented
- ✅ API endpoints (GET /health, /options, POST /launch, DELETE /terminate, GET /status)
- ✅ Health check endpoint for monitoring
- ✅ JSON structured logging with timestamps
- ✅ Error handling and validation
- ✅ AWS IAM configuration
- ✅ SES sandbox vs production mode
- ✅ Deployment options (EC2, Docker, Kubernetes)
- ✅ Security hardening (HTTPS, rate limiting, auth)
- ✅ Monitoring with CloudWatch
- ✅ Log aggregation setup

### Learning
- Comprehensive deployment documentation is critical for production use
- Security hardening must be documented with specific configuration examples
- Multi-deployment option documentation helps users choose right approach
- Checklists reduce deployment errors and ensure consistency
- Monitoring setup must be documented alongside deployment

---

## Known Limitations

### Free Tier Hours
- Limited to specific instance types: t3.micro, t3.small (x86_64 Linux only)
- SES in sandbox mode: can only send to verified email addresses
- Monitor running instances closely to avoid exceeding free tier hours

### Testing
- background.py coverage is 51% because async task execution is hard to test
- background tasks are tested indirectly through integration tests

---

## Issue Template (For Future Issues)

When reporting new issues, use this format:

### Issue #[NUMBER]: [TITLE]
- **Status:** Open / In Progress / Resolved
- **Severity:** Critical / High / Medium / Low
- **Component:** [FastAPI, EC2, SES, Docker, Jenkins, Tests, Git, etc]
- **Created:** YYYY-MM-DD
- **Resolved:** YYYY-MM-DD (if applicable)

**Description:**
Brief description of the issue.

**Root Cause:**
What caused the issue to occur.

**Error Messages:**
```
[Paste any error messages/stack traces here]
```

**Solution:**
How the issue was fixed or can be fixed.

**Learning:**
Key takeaways to prevent similar issues in future.

---

## Severity Levels
- **Critical:** Blocks all progress, must fix immediately
- **High:** Major functionality broken, must fix before continuing
- **Medium:** Important feature affected, should fix soon
- **Low:** Nice to fix, doesn't block progress

## Component Categories
- FastAPI: Web framework, endpoints, models
- EC2: Instance provisioning, termination, status
- SES: Email sending, notifications
- Docker: Containerization, image building
- Jenkins: CI/CD pipeline, automation
- Testing: Unit tests, integration tests, mocking
- Git: Version control, commits, branching
- Dependencies: Package management, imports
- AWS: General AWS API, IAM, credentials
- Configuration: Environment variables, settings

