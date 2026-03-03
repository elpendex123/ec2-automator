# Production Deployment Checklist

Use this checklist before deploying EC2-Automator to production.

## Pre-Deployment (1-2 days before)

### AWS Account & Billing
- [ ] AWS account created and verified
- [ ] Billing alerts configured (notify at $1, $5, $10)
- [ ] Free Tier limits understood (750 hours EC2, 62k SES emails/month)
- [ ] Budget calculator reviewed
- [ ] Cost anomaly detection enabled

### IAM & Security
- [ ] IAM role `ec2-automator-role` created
- [ ] IAM policy `ec2-automator-policy` attached
- [ ] Instance profile `ec2-automator-profile` created
- [ ] No root account access keys in use
- [ ] MFA enabled on AWS account
- [ ] Password policy enforced (12+ chars, special chars)

### AWS Resources
- [ ] Default VPC confirmed to exist
- [ ] Security group `ec2-automator-sg` created
- [ ] Security group ingress rules configured:
  - [ ] SSH (22) from trusted IPs only
  - [ ] HTTP (80) from 0.0.0.0/0
  - [ ] HTTPS (443) from 0.0.0.0/0
  - [ ] MySQL (3306) if needed
  - [ ] MongoDB (27017) if needed
- [ ] Key pair created for EC2 SSH access
- [ ] Key pair securely stored (encrypted, backed up)

### SES Configuration
- [ ] Sender email verified in SES
- [ ] DKIM configured (optional, for production)
- [ ] SPF/DMARC records added to DNS (optional)
- [ ] Test email successfully sent
- [ ] Production access requested (if needed for volume)
- [ ] Verified email list documented

### Application Code
- [ ] All tests passing (55/55)
- [ ] Code coverage > 80% (achieved 81%)
- [ ] Ruff linting passed (all checks pass)
- [ ] Black formatting verified (all files formatted)
- [ ] No debug/print statements in code
- [ ] No hardcoded credentials in code
- [ ] All TODOs reviewed and addressed
- [ ] Logging configured (JSON format verified)
- [ ] Error handling comprehensive
- [ ] Dependencies pinned in requirements.txt
- [ ] README updated with current info
- [ ] CHANGELOG updated (optional)

### Docker & Container
- [ ] Dockerfile reviewed for security
- [ ] Docker image builds successfully
- [ ] Image scanned for vulnerabilities
- [ ] `.dockerignore` includes:
  - [ ] `.git`
  - [ ] `.env`
  - [ ] `*.pyc`
  - [ ] `__pycache__`
  - [ ] `.pytest_cache`
  - [ ] `htmlcov`
- [ ] Image size reasonable (< 500MB)
- [ ] Health check implemented and tested
- [ ] Environment variables configurable

### Documentation
- [ ] README.md complete and tested
- [ ] AWS_SETUP_GUIDE.md reviewed
- [ ] DEPLOYMENT_GUIDE.md followed
- [ ] DEPLOYMENT_CHECKLIST.md reviewed
- [ ] API documentation auto-generated (Swagger)
- [ ] Architecture diagram available
- [ ] Runbook created for common issues

---

## Day-Of-Deployment

### Final Code Review
- [ ] Code reviewed by second person (if possible)
- [ ] No uncommitted changes
- [ ] Git history clean (`git log --oneline -10`)
- [ ] All commits have meaningful messages
- [ ] Remote branch up-to-date

### Environment Setup
- [ ] Deployment target selected (EC2/Docker/Kubernetes)
- [ ] Environment file (.env) created with production values:
  - [ ] `AWS_REGION=us-east-1` (or appropriate region)
  - [ ] `SES_SENDER_EMAIL=` (verified email)
  - [ ] `NOTIFICATION_EMAIL=` (notifications recipient)
- [ ] Environment file NOT committed to git
- [ ] Environment variables documented in .env.example
- [ ] All required environment variables defined
- [ ] No hardcoded values in application code

### Pre-Deployment Testing

#### Local Testing
- [ ] API starts without errors
- [ ] Health endpoint responds: `GET /health`
- [ ] Options endpoint responds: `GET /options`
- [ ] Launch endpoint accepts request: `POST /launch`
- [ ] Status endpoint tracks tasks: `GET /status/{task_id}`
- [ ] Terminate endpoint works: `DELETE /terminate/{instance_id}`
- [ ] Error handling works (try invalid inputs)
- [ ] Logging outputs JSON format
- [ ] Docker image runs locally
- [ ] All endpoints accessible in container
- [ ] Health check passes in container

#### AWS Testing
- [ ] AWS credentials work (test with `aws sts get-caller-identity`)
- [ ] EC2 API accessible (test with `aws ec2 describe-instances`)
- [ ] SES API accessible (test with `aws ses list-verified-email-addresses`)
- [ ] IAM role attachable to instances
- [ ] Security group rules allow access
- [ ] Can launch test instance manually
- [ ] Can terminate test instance manually
- [ ] Email notification received on test

### Database/External Services (if applicable)
- [ ] Database connection tested
- [ ] Database backups configured
- [ ] Cache warmed up (if using caching)
- [ ] External APIs tested
- [ ] Rate limits checked
- [ ] Webhook receivers ready (if applicable)

### Deployment Execution

#### EC2 + Systemd Deployment
- [ ] EC2 instance launched with correct type and security group
- [ ] SSH access verified
- [ ] System dependencies installed (Python 3.12, git, etc.)
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Environment file configured
- [ ] Systemd service created
- [ ] Service enabled for startup
- [ ] Service started successfully
- [ ] Process running (`ps aux | grep uvicorn`)
- [ ] Port listening (`netstat -tlnp | grep 8000`)
- [ ] Nginx configured and started
- [ ] Reverse proxy working
- [ ] Health check passes

#### Docker Deployment
- [ ] Docker installed and running
- [ ] Image built successfully
- [ ] Container starts without errors
- [ ] Container healthy (health check passes)
- [ ] Environment variables passed correctly
- [ ] Volume mounts working (AWS credentials)
- [ ] Network ports exposed correctly
- [ ] Log output visible (docker logs)
- [ ] Resource limits configured
- [ ] Auto-restart enabled
- [ ] Persistence configured (if needed)

#### Kubernetes Deployment
- [ ] Cluster accessible (`kubectl cluster-info`)
- [ ] Namespace created
- [ ] ConfigMaps/Secrets configured
- [ ] Deployment created
- [ ] Pods running (`kubectl get pods`)
- [ ] Service created
- [ ] Ingress configured (if needed)
- [ ] Health checks passing
- [ ] Logs accessible (`kubectl logs`)
- [ ] Auto-scaling configured (optional)

---

## Post-Deployment (First 24 hours)

### Immediate Verification (First 5 minutes)
- [ ] Application responding to requests
- [ ] Health endpoint returns 200 OK
- [ ] Swagger docs accessible at `/docs`
- [ ] No errors in application logs
- [ ] CPU usage normal (< 50%)
- [ ] Memory usage normal (< 50% of available)
- [ ] Disk space adequate (> 20% free)

### Functional Testing (First 30 minutes)
- [ ] All endpoints return expected responses
- [ ] Error handling working correctly
- [ ] Invalid inputs rejected with 400/422 errors
- [ ] Invalid instance types rejected
- [ ] Invalid app names rejected
- [ ] Missing fields rejected
- [ ] Launch endpoint returns 202 + task_id
- [ ] Status endpoint tracks progress
- [ ] Terminate endpoint works
- [ ] Emails sent successfully
- [ ] Email content correct
- [ ] Logs contain all operations

### Load Testing (If applicable)
- [ ] Load test executed: `ab -n 100 -c 10 http://localhost/health`
- [ ] Response time acceptable (< 1s)
- [ ] No dropped requests
- [ ] No 500 errors under load
- [ ] Memory stable under load
- [ ] CPU stays below 80%

### AWS Resource Monitoring (First hour)
- [ ] EC2 instances appear in console
- [ ] CloudWatch metrics visible
- [ ] No excessive API calls
- [ ] No failed API calls
- [ ] Billing accurate
- [ ] Cost tracking operational
- [ ] No unexpected charges

### Security Verification (First hour)
- [ ] HTTPS working (if configured)
- [ ] TLS certificate valid
- [ ] Firewall rules enforced
- [ ] No direct access to port 8000 (only through reverse proxy)
- [ ] No hardcoded credentials visible in logs
- [ ] Rate limiting working (if configured)
- [ ] CORS configured correctly (if needed)

### Monitoring & Alerting (After 1 hour)
- [ ] CloudWatch dashboards visible
- [ ] Alarms configured and armed
- [ ] Health check endpoint monitored
- [ ] Error rate alert configured
- [ ] High CPU alert configured
- [ ] High memory alert configured
- [ ] Disk space alert configured
- [ ] Daily cost alert configured
- [ ] Test alert received successfully

### Logging & Diagnostics (After 1 hour)
- [ ] All logs captured
- [ ] Log retention configured (7-30 days)
- [ ] Log searching working
- [ ] Error tracking configured
- [ ] Request tracing working
- [ ] Database query logging (if applicable)
- [ ] Slow query detection (if applicable)

---

## First Week Monitoring

### Daily Checks
- [ ] **Day 1:** Application running, no errors
- [ ] **Day 2:** Performance stable, no degradation
- [ ] **Day 3:** Error rate < 1%, success rate > 99%
- [ ] **Day 4:** Cost tracking accurate, no surprises
- [ ] **Day 5:** Backup/recovery plan tested
- [ ] **Day 6:** Load test re-run (if needed)
- [ ] **Day 7:** Documentation updated with learnings

### Weekly Review
- [ ] Error logs reviewed
- [ ] Slow requests analyzed
- [ ] Usage patterns examined
- [ ] Cost projections reviewed
- [ ] Capacity headroom confirmed
- [ ] Performance targets met
- [ ] Security best practices followed
- [ ] Team documentation updated

---

## Long-term Operations (Ongoing)

### Weekly
- [ ] [ ] Review CloudWatch dashboards
- [ ] [ ] Check error rate trends
- [ ] [ ] Review cost trends
- [ ] [ ] Verify backups working
- [ ] [ ] Check security updates available
- [ ] [ ] Review access logs
- [ ] [ ] Confirm health checks passing

### Monthly
- [ ] [ ] Full security audit
- [ ] [ ] Dependency update check
- [ ] [ ] Performance review
- [ ] [ ] Cost optimization review
- [ ] [ ] Capacity planning update
- [ ] [ ] Documentation refresh
- [ ] [ ] Team training/knowledge share

### Quarterly
- [ ] [ ] Disaster recovery drill
- [ ] [ ] Load testing (if high traffic)
- [ ] [ ] Security penetration test
- [ ] [ ] Architecture review
- [ ] [ ] Vendor/service reviews
- [ ] [ ] Budget forecasting
- [ ] [ ] Roadmap planning

### Annually
- [ ] [ ] Complete security audit (third-party)
- [ ] [ ] Compliance review
- [ ] [ ] Major version upgrades
- [ ] [ ] Infrastructure refresh
- [ ] [ ] Cost renegotiation
- [ ] [ ] Disaster recovery test (full)
- [ ] [ ] Strategy review

---

## Rollback Decision Criteria

Rollback if any of these occur:

### Critical Issues (Immediate Rollback)
- [ ] Application completely unavailable
- [ ] Data corruption detected
- [ ] Security breach detected
- [ ] Uncontrolled cost escalation
- [ ] Compliance violation detected

### High Priority Issues (Rollback within 1 hour)
- [ ] Error rate > 10%
- [ ] Response time > 5 seconds
- [ ] Memory leak detected
- [ ] Major feature broken
- [ ] Data loss observed

### Medium Priority Issues (Assess and decide)
- [ ] Error rate > 5% but < 10%
- [ ] Response time 1-5 seconds
- [ ] Minor feature broken
- [ ] Performance degradation
- [ ] Unexpected cost increase

### Rollback Procedure
```bash
# Option 1: Revert to previous code
git reset --hard origin/main
git checkout previous-version-tag
# Rebuild and redeploy

# Option 2: Rollback Docker image
docker pull your-registry/ec2-automator:previous-tag
docker-compose down
docker-compose up -d

# Option 3: Kubernetes rollback
kubectl rollout undo deployment/ec2-automator
```

---

## Sign-Off

Once all items complete:

- **Deployed By:** _________________
- **Approved By:** _________________
- **Date:** _________________
- **Version:** _________________
- **Notes:** _________________________________________________

---

## Contact & Escalation

### Primary Contact
- Name: Enrique Coello
- Email: enrique.coello@gmail.com
- Phone: [if applicable]

### On-Call Escalation
- Level 1 (App Issues): [Team member]
- Level 2 (Infra Issues): [Ops/DevOps]
- Level 3 (AWS Account): [Account owner]

### Emergency Contacts
- AWS Support: [Account ID, Support Plan]
- Alerting Service: [Contact info]

---

See also:
- [AWS Setup Guide](AWS_SETUP_GUIDE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [README](../README.md)
