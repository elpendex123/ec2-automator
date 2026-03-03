# Jenkins Pipeline Setup Guide

Complete step-by-step guide to configure the modular Jenkins jobs as an automated pipeline.

## Pipeline Flow

```
┌──────────────────────────────────────────────────────────────┐
│ 1. ec2-automator-setup (MANUAL - Run once)                  │
│    └─ Creates artifact: dependencies cached                  │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 │ (Dependencies now available to all jobs)
                 │
    ┌────────────▼──────────────────────────────────────────┐
    │ 2. ec2-automator-lint (MANUAL TRIGGER)                │
    │    └─ Auto-triggers: ec2-automator-test              │
    └────────────┬──────────────────────────────────────────┘
                 │
    ┌────────────▼──────────────────────────────────────────┐
    │ 3. ec2-automator-test (AUTO-TRIGGERED)               │
    │    └─ Auto-triggers: ec2-automator-build             │
    └────────────┬──────────────────────────────────────────┘
                 │
    ┌────────────▼──────────────────────────────────────────┐
    │ 4. ec2-automator-build (AUTO-TRIGGERED)              │
    │    └─ Auto-triggers: ec2-automator-push              │
    └────────────┬──────────────────────────────────────────┘
                 │
    ┌────────────▼──────────────────────────────────────────┐
    │ 5. ec2-automator-push (AUTO-TRIGGERED)               │
    │    └─ Pipeline complete                              │
    └────────────────────────────────────────────────────────┘
```

## Job Creation Order

Create jobs in this order in Jenkins:

1. **ec2-automator-setup** (only runs manually once)
2. **ec2-automator-lint** (triggers test when successful)
3. **ec2-automator-test** (triggers build when successful)
4. **ec2-automator-build** (triggers push when successful)
5. **ec2-automator-push** (end of pipeline)

---

## Step-by-Step Configuration

### Setup Prerequisites

Before creating jobs:
1. Jenkins running (Docker or local)
2. Git plugin installed (default)
3. Pipeline plugin installed
4. SSH/HTTPS access to GitHub configured
5. Post Build Task plugin or Groovy plugin installed (for auto-triggering)

**Install plugins:**
- Go to **Manage Jenkins** > **Manage Plugins** > **Available**
- Search and install:
  - "Parameterized Trigger Plugin" (for triggering other jobs)
  - OR use "Post Build Task" (built-in with Pipeline)

---

## Job 1: ec2-automator-setup

### Configuration

1. **Create Job**
   - Click **New Item**
   - Name: `ec2-automator-setup`
   - Select **Pipeline**
   - Click **OK**

2. **Pipeline Configuration**
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** `https://github.com/elpendex123/ec2-automator.git`
   - **Branch:** `*/master`
   - **Script Path:** `jenkins/Jenkinsfile.setup`

3. **Build Triggers**
   - **Do NOT check any build triggers** (manual only)
   - This is the starting point, only run once

4. **Post-build Actions**
   - **Do NOT add any** (this is first job)

5. **Save**

### How to Run
```
1. Click job: ec2-automator-setup
2. Click "Build Now"
3. Wait for completion (2-3 minutes first time)
4. Review logs
5. Dependencies now cached for other jobs
```

---

## Job 2: ec2-automator-lint

### Configuration

1. **Create Job**
   - Click **New Item**
   - Name: `ec2-automator-lint`
   - Select **Pipeline**
   - Click **OK**

2. **Pipeline Configuration**
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** `https://github.com/elpendex123/ec2-automator.git`
   - **Branch:** `*/master`
   - **Script Path:** `jenkins/Jenkinsfile.lint`

3. **Build Triggers**
   - **Check:** "Poll SCM"
   - **Schedule:** (leave empty - we'll trigger manually)
   - OR leave unchecked and trigger manually

4. **Post-build Actions**
   - Click **Add post-build action**
   - Select **Build other projects** (from Parameterized Trigger Plugin)
   - OR if not available, use **Pipeline: Trigger builds on other projects**

   **Configuration:**
   - **Projects to build:** `ec2-automator-test`
   - **Trigger when build is:** `Stable`
   - Click **Add**

5. **Save**

### How to Run
```
1. Click job: ec2-automator-lint
2. Click "Build Now"
3. Linting runs (~15 sec)
4. If linting PASSES → Automatically triggers ec2-automator-test
5. If linting FAILS → Pipeline stops, no auto-trigger
```

---

## Job 3: ec2-automator-test

### Configuration

1. **Create Job**
   - Click **New Item**
   - Name: `ec2-automator-test`
   - Select **Pipeline**
   - Click **OK**

2. **Pipeline Configuration**
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** `https://github.com/elpendex123/ec2-automator.git`
   - **Branch:** `*/master`
   - **Script Path:** `jenkins/Jenkinsfile.test`

3. **Build Triggers**
   - **Do NOT check any** (will be auto-triggered by lint job)

4. **Post-build Actions**
   - Click **Add post-build action**
   - Select **Build other projects**

   **Configuration:**
   - **Projects to build:** `ec2-automator-build`
   - **Trigger when build is:** `Stable`
   - Click **Add**

5. **Save**

### How to Run
```
Automatically triggered by ec2-automator-lint
1. Tests run (~45 sec)
2. If tests PASS → Automatically triggers ec2-automator-build
3. If tests FAIL → Pipeline stops, no auto-trigger
```

---

## Job 4: ec2-automator-build

### Configuration

1. **Create Job**
   - Click **New Item**
   - Name: `ec2-automator-build`
   - Select **Pipeline**
   - Click **OK**

2. **Pipeline Configuration**
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** `https://github.com/elpendex123/ec2-automator.git`
   - **Branch:** `*/master`
   - **Script Path:** `jenkins/Jenkinsfile.build`

3. **Build Triggers**
   - **Do NOT check any** (will be auto-triggered by test job)

4. **Post-build Actions**
   - Click **Add post-build action**
   - Select **Build other projects**

   **Configuration:**
   - **Projects to build:** `ec2-automator-push`
   - **Trigger when build is:** `Stable`
   - Click **Add**

5. **Save**

### How to Run
```
Automatically triggered by ec2-automator-test
1. Docker image builds (~45 sec)
2. If build SUCCEEDS → Automatically triggers ec2-automator-push
3. If build FAILS → Pipeline stops, no auto-trigger
```

---

## Job 5: ec2-automator-push

### Configuration

1. **Create Job**
   - Click **New Item**
   - Name: `ec2-automator-push`
   - Select **Pipeline**
   - Click **OK**

2. **Pipeline Configuration**
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** `https://github.com/elpendex123/ec2-automator.git`
   - **Branch:** `*/master`
   - **Script Path:** `jenkins/Jenkinsfile.push`

3. **Build Triggers**
   - **Do NOT check any** (will be auto-triggered by build job)

4. **Post-build Actions**
   - **Do NOT add any** (this is final job in pipeline)

5. **Save**

### How to Run
```
Automatically triggered by ec2-automator-build
1. Verifies image and prepares push (~5 sec)
2. Shows what would be pushed (requires credentials for actual push)
3. Pipeline complete
```

---

## Complete Pipeline Execution Example

### First Time Setup

```bash
# Day 1: Run setup once
1. Jenkins: ec2-automator-setup → "Build Now"
   └─ Installs all dependencies (2-3 min)
   └─ Dependencies cached for future jobs

# Dependency installation complete ✓
```

### Daily Development Workflow

```bash
# Day N: Code changes made, ready to deploy
1. Make code changes locally
2. Push to GitHub: git push origin master

3. Jenkins: ec2-automator-lint → "Build Now"
   ├─ Runs ruff checks (15 sec)
   ├─ PASS → Auto-triggers ec2-automator-test
   └─ FAIL → Pipeline stops, you fix code locally

4. Auto-triggered: ec2-automator-test
   ├─ Runs pytest (45 sec)
   ├─ PASS → Auto-triggers ec2-automator-build
   └─ FAIL → Pipeline stops, you fix tests

5. Auto-triggered: ec2-automator-build
   ├─ Docker build (45 sec)
   ├─ PASS → Auto-triggers ec2-automator-push
   └─ FAIL → Pipeline stops, you fix Dockerfile

6. Auto-triggered: ec2-automator-push
   ├─ Verifies push ready (5 sec)
   ├─ Ready for deployment
   └─ Pipeline complete ✓

TOTAL TIME: ~2 minutes from "Build Now" to completion
```

---

## Monitoring Pipeline Execution

### View Pipeline Progress

1. Click **ec2-automator-lint** job
2. Under **Build History**, click latest build number
3. Click **Console Output**
4. Watch in real-time or scroll through logs

### Check Job Chain Execution

In Jenkins **Dashboard**:
- Watch **ec2-automator-lint** complete
- Then **ec2-automator-test** appears in queue
- Then **ec2-automator-build** appears
- Then **ec2-automator-push** appears
- Each auto-triggers the next on success

### Email Notifications

Each job has post-build email notifications:
- **Success:** Email sent with build details
- **Failure:** Email sent with error logs

---

## If Pipeline Fails

### At Lint Stage
```
1. Jenkins shows: ec2-automator-lint FAILED
2. Click job to view "Console Output"
3. Fix code issues locally
4. Commit and push to GitHub
5. Manually trigger ec2-automator-lint again
```

### At Test Stage
```
1. Jenkins shows: ec2-automator-test FAILED
2. Review test output in Console Output
3. Fix test or code locally
4. Commit and push
5. Manually trigger ec2-automator-lint (which will retry from beginning)
```

### At Build Stage
```
1. Jenkins shows: ec2-automator-build FAILED
2. Check Dockerfile or Docker issues
3. Verify Docker installed: docker --version
4. Fix and commit locally
5. Manually trigger ec2-automator-lint
```

---

## Quick Reference: Configuration Summary

| Job | Trigger Type | Auto-triggers | Script Path |
|-----|--------------|---------------|------------|
| setup | Manual only | None | jenkins/Jenkinsfile.setup |
| lint | Manual | ec2-automator-test | jenkins/Jenkinsfile.lint |
| test | Auto (from lint) | ec2-automator-build | jenkins/Jenkinsfile.test |
| build | Auto (from test) | ec2-automator-push | jenkins/Jenkinsfile.build |
| push | Auto (from build) | None | jenkins/Jenkinsfile.push |

---

## Typical Execution Flow

```
YOUR ACTION:
│
├─ Run setup ONCE
│  └─ Dependencies installed ✓
│
└─ For each code change:
   ├─ Commit and push to GitHub
   ├─ Click "Build Now" on ec2-automator-lint
   │
   └─ AUTOMATIC CHAIN:
      ├─ Lint runs → if PASS
      ├─ Test runs → if PASS
      ├─ Build runs → if PASS
      ├─ Push runs → if PASS
      └─ Pipeline complete ✓

TOTAL TIME: 10-15 seconds + 90 seconds = ~2 minutes
```

---

## Troubleshooting Pipeline Configuration

### "Projects to build" not showing in Post-build

**Problem:** Can't find "Build other projects" option

**Solution:**
1. Go to **Manage Jenkins** > **Manage Plugins**
2. Search: "Parameterized Trigger Plugin"
3. Install it
4. Restart Jenkins (safe restart recommended)
5. Re-open job configuration
6. "Build other projects" should now appear

### Job not auto-triggering

**Problem:** Job completes but doesn't trigger next job

**Reasons:**
1. Post-build action not configured
2. Trigger set to wrong project name
3. Previous job failed (check trigger condition is "Stable")

**Fix:**
1. Click job **Configure**
2. Scroll to **Post-build Actions**
3. Verify **"Build other projects"** exists
4. Verify correct project name (exact match, case-sensitive)
5. Verify **"Trigger when build is"** = **"Stable"** (not "Unstable")
6. Click **Save**

### Dependencies not available in test job

**Problem:** Test job says "pytest not found"

**Solution:**
1. Run setup job again
2. OR manually run: `python3.10 -m pip install -r requirements-dev.txt`

---

## Optional: Jenkins Web UI Dashboard View

After all jobs configured, create a view to see pipeline:

1. Click **+** or **New View**
2. Select **Pipeline View** (if plugin installed)
3. Name: `EC2-Automator Pipeline`
4. Add jobs in order:
   - ec2-automator-setup
   - ec2-automator-lint
   - ec2-automator-test
   - ec2-automator-build
   - ec2-automator-push
5. Click **Save**

Now you can see the full pipeline in one view!

---

## Summary

**Setup:**
1. Create 5 jobs using the configurations above
2. Configure auto-triggering between jobs (lint→test→build→push)
3. Only manual trigger on setup and lint jobs

**Daily Usage:**
1. Code changes → git push
2. Jenkins: Click ec2-automator-lint "Build Now"
3. Wait ~2 minutes for full pipeline to complete
4. Check email for success/failure notification

**Time Savings:**
- **First time:** ~4 minutes (includes setup)
- **Subsequent:** ~90 seconds per deploy (just lint→test→build→push)
