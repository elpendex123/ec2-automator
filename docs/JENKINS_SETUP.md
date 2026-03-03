# Jenkins CI/CD Setup Guide

This guide explains how to set up Jenkins for EC2-Automator continuous integration and deployment pipeline.

## Overview

The Jenkins pipeline automates:
1. **Lint** - Code quality checks with ruff
2. **Test** - Unit and integration tests with pytest
3. **Build** - Docker image creation
4. **Push** - Push to Docker registry (optional, on master branch)
5. **Notifications** - Email alerts on success/failure

## Prerequisites

- Jenkins 2.400+ installed and running
- Jenkins plugins:
  - Pipeline (workflow-aggregator)
  - Email Extension Plugin
  - HTML Publisher Plugin
  - JUnit Plugin
- Docker installed on Jenkins agent
- Python 3.10 installed on Jenkins agent
- Git plugin (usually comes with Jenkins)

## Jenkins Setup Steps

### 1. Install Jenkins

#### Using Docker (Recommended for Local Testing)
```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(which docker):/usr/bin/docker \
  jenkins/jenkins:lts
```

Then access Jenkins at: `http://localhost:8080`

#### Get Initial Admin Password
```bash
docker logs jenkins | grep "Please use the following password to proceed to installation"
```

### 2. Install Required Plugins

1. Go to **Manage Jenkins** > **Manage Plugins**
2. Search and install:
   - Pipeline
   - Email Extension Plugin
   - HTML Publisher Plugin
   - JUnit Plugin
   - Git (if not present)
   - Docker (for Docker agent support)

3. Click **Install without restart**

### 3. Configure System Settings

#### Email Configuration

1. Go to **Manage Jenkins** > **Configure System**
2. Scroll to **Extended Email Notification**
3. Configure SMTP:

**Using Gmail:**
```
SMTP server: smtp.gmail.com
SMTP port: 587
Use SMTP Authentication: ✓ (checked)
Username: your-email@gmail.com
Password: your-app-password (not regular password)
Use TLS: ✓ (checked)
```

**For Other Email Providers:**
- Gmail: smtp.gmail.com:587
- Office 365: smtp.office365.com:587
- Custom: Your organization's SMTP server

4. Test email configuration:
   - Click "Test Configuration"
   - Check "Send Test E-mail To":
   - Enter test email address
   - Click "Test"

#### Global Configuration

1. **System Admin E-mail Address**: Set to `enrique.coello@gmail.com`
2. **Jenkins URL**: Set to your Jenkins URL (e.g., `http://localhost:8080/`)

### 4. Create Pipeline Job

#### Option A: Using Jenkins UI

1. Click **New Item**
2. Enter job name: `ec2-automator`
3. Select **Pipeline**
4. Click **OK**

5. In **Pipeline** section, select:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/elpendex123/ec2-automator.git`
   - Branch: `master`
   - Script Path: `Jenkinsfile`

6. Click **Save**

#### Option B: Using Jenkins Configuration as Code (Advanced)

Create a `jenkins.yaml`:
```yaml
jobs:
  - script: |
      pipelineJob('ec2-automator') {
        definition {
          cpsScm {
            scm {
              git {
                remote {
                  url('https://github.com/elpendex123/ec2-automator.git')
                  name('origin')
                  refspec('+refs/heads/*:refs/remotes/origin/*')
                }
                branches('*/master')
                browser {
                  github {
                    repoUrl('https://github.com/elpendex123/ec2-automator')
                  }
                }
                doGenerateSubmoduleConfigurations(false)
                extensions([])
              }
            }
            scriptPath('Jenkinsfile')
          }
        }
      }
```

### 5. Configure Credentials (For Docker Push)

1. Go to **Manage Jenkins** > **Manage Credentials**
2. Click **System** > **Global credentials**
3. Click **Add Credentials**

**For Docker Hub:**
- **Kind:** Username with password
- **Username:** your-dockerhub-username
- **Password:** Your Docker Hub token (not password)
- **ID:** `dockerhub-credentials`

4. Click **Create**

5. In Jenkinsfile, uncomment the docker push commands:
```groovy
withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
    sh 'docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}'
    sh 'docker logout'
}
```

### 6. Configure Environment Variables

1. Go to job **Configure**
2. Scroll to **Pipeline** section
3. Under **Script**, add environment variables:
```groovy
environment {
    NOTIFICATION_EMAIL = 'enrique.coello@gmail.com'
    AWS_REGION = 'us-east-1'
}
```

Or configure at Jenkins level:
- **Manage Jenkins** > **Configure System** > **Global properties** > **Environment variables**

## Jenkinsfile Overview

### Pipeline Structure

```groovy
pipeline {
    agent any                    // Run on any available agent
    environment { }              // Define variables
    options { }                  // Configure pipeline behavior
    stages { }                   // Execution stages
    post { }                     // Post-execution hooks
}
```

### Stages Breakdown

#### Checkout Stage
- Clones the repository
- Checks out the specified branch

#### Lint Stage
```bash
python3.10 -m ruff check app/ tests/ --output-format=github
```
- Scans code for style/error issues
- Uses GitHub output format for better UI integration
- Fails if style issues found

#### Test Stage
```bash
python3.10 -m pytest tests/ -v --cov=app --cov-report=xml --cov-report=html
```
- Runs all unit and integration tests
- Generates XML report for JUnit plugin
- Generates HTML coverage report
- Publishes coverage to Jenkins UI

#### Build Stage
```bash
docker build -t ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG} .
```
- Builds Docker image with build number as tag
- Also tags as 'latest'
- No push (dry run)

#### Push Stage
```bash
docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
```
- Only runs on master branch
- Pushes to Docker registry
- Requires Docker credentials configured

### Post Sections

#### Always
- Runs regardless of result
- Cleans workspace: `cleanWs()`

#### Success
- Sends success email
- Includes build details and links

#### Failure
- Sends failure email
- Includes error logs for debugging

#### Unstable
- Runs if tests pass but with warnings
- Notifies of potential issues

## Testing Jenkinsfile Locally

### Validate Jenkinsfile Syntax

Without Jenkins installed:
```bash
# Use groovy-lint (requires Groovy installed)
groovy-lint Jenkinsfile
```

With Jenkins CLI:
```bash
java -jar jenkins-cli.jar -s http://localhost:8080 declarative-linter < Jenkinsfile
```

### Test Individual Stages

Run individual stage commands locally:

**Test Lint Stage:**
```bash
python3.10 -m pip install ruff
python3.10 -m ruff check app/ tests/
```

**Test Test Stage:**
```bash
python3.10 -m pip install -r requirements-dev.txt
python3.10 -m pytest tests/ -v --cov=app
```

**Test Build Stage:**
```bash
docker build -t ec2-automator:test .
```

## Running the Pipeline

### Manual Trigger

1. Go to job **ec2-automator**
2. Click **Build Now**
3. Monitor build progress in **Console Output**

### Webhook Trigger (GitHub Integration)

1. Go to GitHub repository > **Settings** > **Webhooks**
2. Click **Add webhook**
3. **Payload URL:** `http://jenkins-url/github-webhook/`
4. **Content type:** `application/json`
5. **Events:** Push events
6. Click **Add webhook**

Now pushes to GitHub automatically trigger Jenkins builds.

### Scheduled Builds

1. Go to job **Configure**
2. Under **Build Triggers**, select **Build periodically**
3. Enter cron schedule:
   - `H H * * *` - Daily at midnight
   - `H H(0-6) * * *` - Daily early morning
   - `H H * * MON` - Weekly on Monday

## Troubleshooting

### Build Fails at Lint Stage

**Issue:** `ruff: command not found`
- **Solution:** Ensure Python 3.10 is installed on Jenkins agent
- Run: `python3.10 -m pip install ruff`

### Build Fails at Test Stage

**Issue:** `pytest: No such file or directory`
- **Solution:** Install dev dependencies first
- Add to agent setup: `python3.10 -m pip install -r requirements-dev.txt`

### Docker Build Fails

**Issue:** `docker: command not found`
- **Solution:** Docker not installed on agent
- Install Docker on Jenkins agent machine

### Email Notifications Not Sending

**Issue:** Emails not received
- **Troubleshooting:**
  1. Check **Manage Jenkins** > **System Log** for errors
  2. Verify SMTP credentials: Click "Test Configuration"
  3. Check spam folder
  4. Verify recipient email in Jenkinsfile

### Docker Push Fails

**Issue:** `denied: requested access to the resource is denied`
- **Solution:** Docker credentials not configured correctly
  1. Verify credentials in Jenkins
  2. Test locally: `docker login -u username -p token`
  3. Ensure correct registry URL

### Pipeline Hangs

**Issue:** Build doesn't complete
- **Solution:** Check for interactive prompts
  1. Review logs: **Console Output**
  2. Add timeout to Jenkinsfile (already included)
  3. Check Docker daemon availability

## Pipeline Monitoring

### View Build Logs

1. Click job name
2. Click build number (e.g., `#45`)
3. Click **Console Output**

### View Coverage Report

1. Click build number
2. Scroll to **Coverage Report**
3. Click **index.html** link

### View Test Results

1. Click build number
2. Scroll to **Test Result**
3. View passed/failed tests

### Jenkins Metrics

Track over time:
- Test pass rate
- Build duration trends
- Code coverage improvement
- Build success rate

## Best Practices

1. **Keep Jenkinsfile in Source Control**
   - Jenkinsfile is versioned with code
   - Changes tracked in Git

2. **Use Declarative Pipeline**
   - More readable than scripted pipeline
   - Better error messages
   - Easier to maintain

3. **Fail Fast**
   - Lint before test before build
   - Skip expensive builds if lint fails

4. **Test Locally First**
   - Run stages locally before committing
   - Ensure scripts work before pushing

5. **Monitor Build Duration**
   - Optimize slow stages
   - Cache dependencies when possible
   - Consider parallel stages for independent tests

6. **Clean Credentials**
   - Never hardcode credentials in Jenkinsfile
   - Use Jenkins credentials store
   - Rotate credentials regularly

7. **Email Best Practices**
   - Include build details in emails
   - Link to console output
   - Clear subject line with status

## Advanced Configuration

### Parallel Stages

```groovy
parallel {
    stage('Unit Tests') {
        steps { sh 'pytest tests/unit/' }
    }
    stage('Integration Tests') {
        steps { sh 'pytest tests/integration/' }
    }
}
```

### Conditional Stages

```groovy
stage('Push') {
    when {
        branch 'master'
        expression { currentBuild.result == null }
    }
    steps { sh 'docker push ...' }
}
```

### Retry on Failure

```groovy
stage('Push') {
    steps {
        retry(3) {
            sh 'docker push ...'
        }
    }
}
```

### Timeout for Stages

```groovy
stage('Test') {
    options {
        timeout(time: 10, unit: 'MINUTES')
    }
    steps { sh 'pytest ...' }
}
```

## References

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [Email Extension Plugin](https://plugins.jenkins.io/email-ext/)
- [Docker Plugin](https://plugins.jenkins.io/docker-workflow/)
