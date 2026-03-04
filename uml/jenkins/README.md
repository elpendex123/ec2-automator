# Jenkins CI/CD Integration for UML Diagrams

Automated UML diagram generation integrated into Jenkins CI/CD pipeline.

## Overview

This directory contains scripts and configuration for automatically generating all UML diagrams whenever code changes are detected.

**Files**:
- `generate_all_diagrams.sh` - Master script that runs all diagram generators
- `Jenkinsfile.diagrams` - Jenkins pipeline configuration

## Quick Start

### Manual Generation (Local Testing)

```bash
# Make script executable
chmod +x uml/jenkins/generate_all_diagrams.sh

# Run all diagram generators
bash uml/jenkins/generate_all_diagrams.sh
```

### Automated Generation (Jenkins)

1. Create Jenkins job pointing to `Jenkinsfile.diagrams`
2. Configure build trigger (polling SCM or webhook)
3. Job automatically generates diagrams on code changes

## Installation

### Option 1: Using GitHub Webhook (Recommended)

**Step 1**: Create Jenkins job
```
New Item → Pipeline → Name: "EC2-Automator-Diagrams"
Pipeline section:
  - Definition: Pipeline script from SCM
  - SCM: Git
  - Repository: (your repo URL)
  - Script path: uml/jenkins/Jenkinsfile.diagrams
```

**Step 2**: Configure GitHub webhook
```
GitHub repo → Settings → Webhooks → Add webhook
- Payload URL: https://jenkins.example.com/github-webhook/
- Content type: application/json
- Events: Let me select individual events
  ✓ Push events
  ✓ Pull requests
- Active: ✓
```

**Step 3**: Configure Jenkins GitHub integration
```
Jenkins → Manage Jenkins → Configure System
- GitHub section:
  - API URL: https://api.github.com
  - Credentials: (add token)
  - Test connection
```

### Option 2: Poll SCM (Simpler)

**Step 1**: Create Jenkins job (same as above)

**Step 2**: Configure polling
```
Jenkins job → Build Triggers:
  ✓ Poll SCM
  - Schedule: H/15 * * * *  (every 15 minutes)
```

### Option 3: Docker-based Agent

For reliability, use Docker container with pre-installed tools:

```Dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip \
    default-jre \
    plantuml \
    graphviz \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    pylint==3.0.3 \
    py2puml==0.9.0 \
    pydeps==1.12.8 \
    diagrams==0.23.3 \
    plantuml==0.3.0
```

## Dependencies

### System Requirements

```bash
# Java runtime (for PlantUML)
sudo apt-get install default-jre

# PlantUML
sudo apt-get install plantuml

# Graphviz (for pydeps and diagrams)
sudo apt-get install graphviz graphviz-dev
```

### Python Requirements

```bash
pip install -r requirements-dev.txt

# Or individually:
pip install pylint==3.0.3
pip install py2puml==0.9.0
pip install pydeps==1.12.8
pip install diagrams==0.23.3
pip install plantuml==0.3.0
```

## What the Pipeline Does

### Stage 1: Initialize
- Checkout code from SCM
- Clear previous artifacts
- Set environment variables

### Stage 2: Setup Dependencies
- Install system packages (Java, PlantUML, Graphviz)
- Verify installations

### Stage 3: Install Python Dependencies
- Install Python packages from requirements-dev.txt
- Verify each tool is available

### Stage 4: Generate Diagrams
```
Runs: bash uml/jenkins/generate_all_diagrams.sh

Which runs:
  1. pyreverse (pylint)
  2. py2puml
  3. pydeps
  4. PlantUML
  5. diagrams (mingrammer)
```

### Stage 5: Verify Outputs
- Count generated files
- Verify minimum file count
- List all generated diagrams

### Stage 6: Archive Artifacts
- Save PNG, SVG, and PUML files
- Make available in Jenkins UI
- Attach to email notifications

### Stage 7: Update Documentation (Optional)
- Copy diagrams to docs directory
- Only runs on main branch

## Pipeline Output

### Success Case
```
✓ All diagram generation completed successfully!

Next steps:
  1. Review generated diagrams
  2. Embed in documentation
  3. Commit and push
```

### Failure Case
```
✗ Some diagram generation failed

Troubleshooting:
  1. Check dependencies
  2. Run individual tools for details
```

## Notifications

### Email Configuration

By default, emails sent to:
- Developers who made commits
- User who triggered the build

**Recipient Options**:
```groovy
// recipients: [developers(), requestor(), culprits()]
```

**Email Content**:
- Build number and status
- Git commit information
- Artifact locations
- Troubleshooting steps
- PNG attachments (success only)

### Custom Recipients

Edit Jenkinsfile to add specific emails:
```groovy
emailext(
    subject: "...",
    body: "...",
    to: 'admin@example.com, team@example.com'
)
```

## Artifact Management

### Storage

Generated files stored in Jenkins workspace:
```
Jenkins_Home/
  jobs/
    EC2-Automator-Diagrams/
      builds/
        N/
          archive/
            uml/
              pyreverse/*.png
              plantuml/*.png, *.svg
              py2puml/*.png, *.svg
              pydeps/*.svg
              diagrams/*.png
```

### Retention Policy

By default:
- Keep last 30 builds
- Delete artifacts after 30 days
- Keep fingerprints for change tracking

### Accessing Artifacts

1. **From Jenkins UI**:
   - Click build → "Artifacts"
   - Download individual files or ZIP

2. **From Command Line**:
   ```bash
   curl -u user:token \
     http://jenkins.example.com/job/EC2-Automator-Diagrams/lastSuccessfulBuild/artifact/uml/pyreverse/classes_diagram.png
   ```

3. **Via Jenkins API**:
   ```bash
   curl -u user:token \
     http://jenkins.example.com/job/EC2-Automator-Diagrams/lastSuccessfulBuild/api/json
   ```

## Troubleshooting

### Build Fails on Checkout
```
Error: Permission denied

Solution:
  - Check Git credentials in Jenkins
  - Verify SSH key or token is valid
  - Check repository access
```

### Missing Dependencies
```
Error: plantuml: command not found

Solution:
  - Run: apt-get install plantuml
  - Or use Docker container with pre-installed tools
```

### Graphviz Issues
```
Error: Can't find Graphviz installation

Solution:
  - Install: apt-get install graphviz graphviz-dev
  - Verify: which dot
  - Rebuild Docker image
```

### Java Runtime Errors
```
Error: java: command not found

Solution:
  - Install: apt-get install default-jre
  - Verify: java -version
```

### Python Module Errors
```
Error: ModuleNotFoundError: No module named 'diagrams'

Solution:
  - Run: pip install -r requirements-dev.txt
  - Or: pip install diagrams
```

### Build Timeout
```
Error: Build timed out after 10 minutes

Solution:
  - Increase timeout in Jenkinsfile:
    timeout(time: 15, unit: 'MINUTES')
  - Or optimize generation scripts
  - Check for slow system calls
```

### Disk Space Issues
```
Error: No space left on device

Solution:
  - Delete old builds: Manage Jenkins → Delete
  - Reduce artifact retention
  - Clean workspace: cleanWs()
  - Check disk: df -h
```

## Debugging

### View Build Log

```bash
# Full log
curl -u user:token \
  http://jenkins.example.com/job/EC2-Automator-Diagrams/lastBuild/consoleText

# Last 100 lines
curl -u user:token \
  http://jenkins.example.com/job/EC2-Automator-Diagrams/lastBuild/consoleText | tail -100
```

### Run Script Manually

```bash
# SSH to Jenkins agent
ssh jenkins-agent

# Run script
cd /var/jenkins_home/workspace/EC2-Automator-Diagrams
bash uml/jenkins/generate_all_diagrams.sh
```

### Check Dependencies

```bash
# Test each tool
pyreverse --version
plantuml -version
py2puml --help
pydeps --version
python -c "import diagrams"
```

## Best Practices

1. **Run locally first** - Test script on dev machine before committing
2. **Monitor disk usage** - Keep old builds under control
3. **Test on every commit** - Catch issues early
4. **Use version control** - Keep Jenkinsfile and scripts in git
5. **Automate notifications** - Know when builds fail
6. **Archive artifacts** - Make diagrams available to team
7. **Document changes** - Update README when modifying pipeline
8. **Use Docker agents** - Ensure consistent environment

## Integration with Documentation

### Option 1: Automatic Copy to Docs

Edit Jenkinsfile:
```groovy
sh '''
    cp -r uml/ docs/architecture/
    git config user.name "Jenkins"
    git config user.email "jenkins@example.com"
    git add docs/
    git commit -m "Update diagrams [skip ci]"
    git push origin main
'''
```

### Option 2: Manual Integration

1. Download artifacts from Jenkins
2. Copy to `docs/architecture/`
3. Commit and push to repository

### Option 3: Embed in README

```markdown
## Architecture Diagrams

![System Architecture](uml/pyreverse/classes_diagram.png)

### Instance Launch Flow

![Launch Sequence](uml/plantuml/sequence_launch.png)

### Dependencies

![Module Dependencies](uml/pydeps/dependencies.svg)
```

## Advanced Configuration

### Build Parameters

Add input parameters to pipeline:

```groovy
parameters {
    string(name: 'MAX_BUILDS_TO_KEEP', defaultValue: '30')
    booleanParam(name: 'UPDATE_DOCS', defaultValue: false)
    choice(name: 'TOOL_SUBSET', choices: ['all', 'quick', 'detailed'])
}
```

### Conditional Execution

```groovy
stage('Generate Diagrams') {
    when {
        // Only run on main branch or tags
        anyOf {
            branch 'main'
            tag "v*"
        }
    }
    steps {
        sh 'bash uml/jenkins/generate_all_diagrams.sh'
    }
}
```

### Parallel Execution

```groovy
parallel {
    stage('pyreverse') {
        steps {
            sh 'cd uml/pyreverse && bash generate.sh'
        }
    }
    stage('PlantUML') {
        steps {
            sh 'cd uml/plantuml && bash generate.sh'
        }
    }
    stage('diagrams') {
        steps {
            sh 'cd uml/diagrams && python generate_architecture.py'
        }
    }
}
```

## References

- [Jenkins Pipeline Documentation](https://jenkins.io/doc/book/pipeline/)
- [Jenkins GitHub Integration](https://plugins.jenkins.io/github/)
- [Jenkins Email Extension Plugin](https://plugins.jenkins.io/email-ext/)
- [Jenkins Artifact Manager](https://jenkins.io/doc/book/managing/artifacts/)

---

**Last Updated**: 2026-03-03
**Maintained By**: EC2-Automator Team
