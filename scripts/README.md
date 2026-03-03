# EC2-Automator Scripts

Utility scripts for managing EC2-Automator development and deployment.

## Available Scripts

### 1. cleanup-aws-resources.sh

Clean up AWS resources including EC2 instances.

**Purpose:** Terminate EC2 instances to avoid excessive charges and stay within Free Tier limits.

**Usage:**
```bash
# View what would be deleted (dry run)
bash scripts/cleanup-aws-resources.sh --dry-run

# Delete with confirmation
bash scripts/cleanup-aws-resources.sh

# Delete without confirmation (dangerous!)
bash scripts/cleanup-aws-resources.sh --force
```

**Features:**
- ✅ Lists all running and stopped EC2 instances
- ✅ Displays instance IDs, types, and names
- ✅ Terminates instances with confirmation
- ✅ Waits for termination to complete
- ✅ Checks security groups
- ✅ Provides AWS console links for further cleanup
- ✅ Dry-run mode to preview changes

**Requirements:**
- AWS CLI installed and configured
- AWS credentials with EC2 permissions

**Example Output:**
```
========================================
EC2-Automator AWS Resource Cleanup
========================================

[INFO] Checking AWS credentials...
[SUCCESS] AWS credentials verified (Account: 903609216629)

[INFO] Checking for running EC2 instances...

[WARNING] Found running EC2 instances:

Instance ID          Type         Name
==================== ============ ========================
i-0d7570b79cd362c57 t3.micro     test-nginx-01
i-03fad9b0176faeb11 t3.small     test-mysql-01

[INFO] Terminating EC2 instances...
[SUCCESS] Termination request sent for 2 instance(s)
[SUCCESS] All instances terminated
```

---

### 2. cleanup-local-deployment.sh

Clean up local development deployments (uvicorn, systemd, nginx).

**Purpose:** Stop and clean up local services running on your development machine.

**Usage:**
```bash
# Stop all services
bash scripts/cleanup-local-deployment.sh

# Stop only specific service
bash scripts/cleanup-local-deployment.sh --uvicorn
bash scripts/cleanup-local-deployment.sh --systemd
bash scripts/cleanup-local-deployment.sh --nginx
```

**Features:**
- ✅ Stops uvicorn API server processes
- ✅ Stops systemd ec2-automator service
- ✅ Stops nginx reverse proxy
- ✅ Frees port 8000 and 80
- ✅ Individual service control
- ✅ Verifies all services are stopped
- ✅ Reports free/busy ports

**Available Options:**
- `-a, --all` - Stop all services (default)
- `-u, --uvicorn` - Stop only uvicorn
- `-s, --systemd` - Stop only systemd service
- `-n, --nginx` - Stop only nginx
- `-h, --help` - Show help

**Example Output:**
```
========================================
EC2-Automator Local Deployment Cleanup
========================================

[INFO] Checking for uvicorn processes...
[WARNING] Found uvicorn process(es):
  1234   root   /usr/bin/python3.10 -m uvicorn app.main:app

[INFO] Stopping uvicorn...
[SUCCESS] All uvicorn processes stopped

[INFO] Checking for nginx...
[WARNING] Found nginx process
[INFO] Stopping nginx...
[SUCCESS] nginx stopped

[INFO] Checking for processes on port 8000...
[SUCCESS] No processes listening on port 8000

[SUCCESS] ✓ Uvicorn stopped
[SUCCESS] ✓ Nginx stopped

[INFO] Free ports:
[INFO] - Port 8000: FREE
[INFO] - Port 80:   FREE
```

---

### 3. cleanup-docker.sh

Clean up Docker containers and images.

**Purpose:** Stop and remove Docker containers to free up disk space and system resources.

**Usage:**
```bash
# View what would be deleted (dry run)
bash scripts/cleanup-docker.sh --dry-run

# Stop and remove containers
bash scripts/cleanup-docker.sh

# Also remove Docker images
bash scripts/cleanup-docker.sh --remove-images

# Without confirmation (dangerous!)
bash scripts/cleanup-docker.sh --force
```

**Features:**
- ✅ Lists ec2-automator containers
- ✅ Stops running containers
- ✅ Removes containers
- ✅ Lists Docker images
- ✅ Optionally removes images
- ✅ Checks for orphaned volumes
- ✅ Checks for orphaned networks
- ✅ Reports Docker disk usage
- ✅ Dry-run mode to preview changes

**Available Options:**
- `--dry-run` - Show changes without applying them
- `--force` - Skip confirmation prompts
- `--remove-images` - Also remove Docker images
- `-h, --help` - Show help

**Example Output:**
```
========================================
EC2-Automator Docker Cleanup
========================================

[SUCCESS] Docker is installed and running

[INFO] Checking for ec2-automator containers...
[WARNING] Found ec2-automator container(s):
CONTAINER ID   IMAGE              STATUS         NAMES
7faba252c630   ec2-automator      Up 2 minutes   ec2-automator-api

[INFO] Stopping containers...
[SUCCESS] Containers stopped

[INFO] Removing containers...
[SUCCESS] Containers removed

[INFO] Docker disk usage:
Images       1      313MB
Containers   0      0B
Local Volumes 0     0B

[SUCCESS] ✓ Containers stopped and removed
```

---

## Quick Reference

### Cleanup All Resources

Run cleanup scripts in this order:

```bash
# 1. Stop local services
bash scripts/cleanup-local-deployment.sh

# 2. Remove Docker containers
bash scripts/cleanup-docker.sh

# 3. Terminate AWS resources (use --dry-run first!)
bash scripts/cleanup-aws-resources.sh --dry-run
bash scripts/cleanup-aws-resources.sh
```

### Cleanup Specific Environment

**For Local Development:**
```bash
bash scripts/cleanup-local-deployment.sh --all
```

**For Docker Testing:**
```bash
bash scripts/cleanup-docker.sh
```

**For AWS Testing:**
```bash
bash scripts/cleanup-aws-resources.sh --dry-run
```

### Safety Tips

1. **Always use `--dry-run` first** to see what will be deleted
2. **Confirm before deleting** (don't use `--force` unless necessary)
3. **Back up important data** before cleanup
4. **Check AWS billing** after cleanup to confirm charges stop
5. **Monitor Free Tier usage** regularly

---

## Troubleshooting

### AWS Script Issues

**Problem:** "AWS CLI not found"
```bash
# Install AWS CLI
pip install awscli
aws configure  # Configure with credentials
```

**Problem:** "AWS credentials not configured"
```bash
aws configure
# Enter your Access Key ID and Secret Access Key
```

**Problem:** Permission denied
```bash
# Check AWS IAM permissions (need EC2 termination rights)
aws iam get-user
```

### Local Deployment Script Issues

**Problem:** "Permission denied" for sudo commands
```bash
# Run with sudo
sudo bash scripts/cleanup-local-deployment.sh

# Or add user to sudo without password (if appropriate)
sudo usermod -aG sudo $USER
```

**Problem:** Port still in use after cleanup
```bash
# Check what's using the port
lsof -i :8000

# Force kill the process
kill -9 <PID>
```

### Docker Script Issues

**Problem:** "Docker daemon not running"
```bash
# Start Docker
sudo service docker start
sudo dockerd  # Or manually start
```

**Problem:** "Permission denied while connecting to Docker daemon"
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or use sudo
sudo bash scripts/cleanup-docker.sh
```

**Problem:** Cannot remove image (still in use)
```bash
# Stop all containers first
docker stop $(docker ps -aq)

# Then remove images
bash scripts/cleanup-docker.sh --remove-images
```

---

## Other Scripts

### test_api.sh

Test API endpoints locally.

**Usage:**
```bash
bash scripts/test_api.sh
```

---

## Safety Notes

⚠️ **WARNING:** These scripts perform destructive operations:
- **cleanup-aws-resources.sh** - Terminates EC2 instances (cannot be undone easily)
- **cleanup-local-deployment.sh** - Stops running services
- **cleanup-docker.sh** - Removes containers (data may be lost)

**Always:**
1. Use `--dry-run` first to preview changes
2. Confirm before deleting
3. Back up important data
4. Test in non-production environments first

---

## Free Tier Monitoring

After running cleanup, monitor your AWS usage:

- **EC2:** https://console.aws.amazon.com/ec2/v2/home#Instances:
  - Check for any running instances
  - Verify no unexpected charges

- **SES:** https://console.aws.amazon.com/ses/home#verified-senders:
  - Monitor email sending volume
  - Ensure under sandbox limits if applicable

- **Billing:** https://console.aws.amazon.com/billing/home
  - Check estimated monthly costs
  - Set up cost anomaly detection
  - Enable billing alerts

---

## Contributing

To add or modify scripts:
1. Use consistent error handling
2. Add color output for clarity
3. Include help text (`--help`)
4. Add dry-run capability where applicable
5. Document with examples
6. Update this README

---

## License

MIT - See LICENSE file for details
