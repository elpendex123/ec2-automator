# Jenkins Configuration Quick Reference

Copy-paste configuration for each job.

---

## Job 1: ec2-automator-setup

```
Job Name: ec2-automator-setup
Type: Pipeline
Definition: Pipeline script from SCM
SCM: Git
Repository URL: https://github.com/elpendex123/ec2-automator.git
Branch: */master
Script Path: jenkins/Jenkinsfile.setup

Build Triggers: NONE (manual only)
Post-build Actions: NONE

Notes:
- Run once per session
- Creates cached dependencies
- No auto-trigger needed
```

---

## Job 2: ec2-automator-lint

```
Job Name: ec2-automator-lint
Type: Pipeline
Definition: Pipeline script from SCM
SCM: Git
Repository URL: https://github.com/elpendex123/ec2-automator.git
Branch: */master
Script Path: jenkins/Jenkinsfile.lint

Build Triggers: NONE (manual trigger)
Post-build Actions:
  ✓ Build other projects
    - Projects to build: ec2-automator-test
    - Trigger when build is: Stable
```

---

## Job 3: ec2-automator-test

```
Job Name: ec2-automator-test
Type: Pipeline
Definition: Pipeline script from SCM
SCM: Git
Repository URL: https://github.com/elpendex123/ec2-automator.git
Branch: */master
Script Path: jenkins/Jenkinsfile.test

Build Triggers: NONE (auto-triggered by lint)
Post-build Actions:
  ✓ Build other projects
    - Projects to build: ec2-automator-build
    - Trigger when build is: Stable
```

---

## Job 4: ec2-automator-build

```
Job Name: ec2-automator-build
Type: Pipeline
Definition: Pipeline script from SCM
SCM: Git
Repository URL: https://github.com/elpendex123/ec2-automator.git
Branch: */master
Script Path: jenkins/Jenkinsfile.build

Build Triggers: NONE (auto-triggered by test)
Post-build Actions:
  ✓ Build other projects
    - Projects to build: ec2-automator-push
    - Trigger when build is: Stable
```

---

## Job 5: ec2-automator-push

```
Job Name: ec2-automator-push
Type: Pipeline
Definition: Pipeline script from SCM
SCM: Git
Repository URL: https://github.com/elpendex123/ec2-automator.git
Branch: */master
Script Path: jenkins/Jenkinsfile.push

Build Triggers: NONE (auto-triggered by build)
Post-build Actions: NONE (final job)
```

---

## Pipeline Trigger Chain

```
setup (manual)
  ↓
lint (manual) → test → build → push
```

---

## How to Use

### First Time
```
1. Jenkins → ec2-automator-setup → Build Now
   Wait for completion (dependencies installed)
2. Ready for normal workflow
```

### Normal Workflow
```
1. Make code changes, git push
2. Jenkins → ec2-automator-lint → Build Now
3. Automatic chain runs: lint → test → build → push
4. Check email for results
```

### Time per Deploy
```
First run:  ~4 minutes (includes setup)
Subsequent: ~90 seconds (just pipeline)
```

---

## What Each Job Does

| Job | Time | Action | Auto-next |
|-----|------|--------|-----------|
| setup | 2-3m | Install deps | - |
| lint | 15s | Ruff check | test |
| test | 45s | Pytest | build |
| build | 45s | Docker image | push |
| push | 5s | Verify push | - |

---

## Required Jenkins Plugins

- Pipeline (workflow-aggregator) - usually built-in
- Git - usually built-in
- **Parameterized Trigger Plugin** - must install
  - Go to: Manage Jenkins → Manage Plugins
  - Search: "Parameterized Trigger Plugin"
  - Install and restart

---

## Post-build Action: "Build other projects"

If you don't see this option:

1. Manage Jenkins → Manage Plugins
2. Search: "Parameterized Trigger"
3. Install: "Parameterized Trigger Plugin"
4. Restart Jenkins
5. Re-open job config → should see option now

---

## Trigger Condition

**Always set to:** "Stable"

This means:
- ✓ If previous job PASSES → auto-trigger next
- ✗ If previous job FAILS → do NOT auto-trigger

---

## Manual Trigger

To manually run any job:

1. Click job name
2. Click "Build Now"
3. Wait for execution
4. View logs: Click build number → Console Output

---

## View Build History

1. Click job name
2. Look at "Build History" section
3. Click build number to view logs
4. Check "Console Output" for details

---

## Prevent Duplicate Runs

**Important:** Only manually trigger **ec2-automator-lint**

Do NOT manually trigger:
- ec2-automator-test (triggered by lint)
- ec2-automator-build (triggered by test)
- ec2-automator-push (triggered by build)

If you manually trigger test, it will:
1. Run test
2. Trigger build
3. Trigger push

This wastes time since you didn't run lint first.

---

## Reset Pipeline

To start over:

```
1. Stop any running builds
2. Optionally run ec2-automator-setup again
3. Trigger ec2-automator-lint to restart pipeline
```

---

## Debug Pipeline Issues

If pipeline stops:

```
1. Find which job failed
2. Click job → Console Output
3. Read error message
4. Fix locally (code/tests/docker)
5. Commit and push
6. Click ec2-automator-lint → Build Now
```

---

## Email Notifications

Each job sends email on:
- ✓ SUCCESS (no errors, all checks pass)
- ✗ FAILURE (errors or test failures)

Configure email in:
- Manage Jenkins → Configure System
- Extended Email Notification
- Set SMTP and recipient

---

## Summary

```
Jobs to Create: 5
Manual triggers: 2 (setup, lint)
Auto-triggered: 3 (test, build, push)

Time investment: ~15 min to set up
Time savings: ~90 seconds per deploy
Total pipeline: Setup once, then 2-min deploys
```
