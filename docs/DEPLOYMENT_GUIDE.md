# Deployment Guide

This guide covers deploying EC2-Automator to production on AWS or any server environment.

## Table of Contents
1. [Deployment Options](#deployment-options)
2. [EC2 Instance Deployment](#ec2-instance-deployment)
3. [Container Deployment](#container-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Health Checks & Monitoring](#health-checks--monitoring)
6. [Production Hardening](#production-hardening)
7. [Rollback Procedures](#rollback-procedures)
8. [Troubleshooting](#troubleshooting)

---

## Deployment Options

Choose based on your needs:

| Option | Best For | Complexity | Cost | Scaling |
|--------|----------|-----------|------|---------|
| **EC2 + Systemd** | Single server | Low | $15-20/mo | Manual |
| **Docker + Docker Compose** | Single/few servers | Low | $15-20/mo | Manual |
| **ECS (Elastic Container Service)** | AWS-native | Medium | $20-50/mo | Auto |
| **Kubernetes (EKS)** | Multi-region, scaling | High | $50-100/mo | Full auto |
| **Lambda** | Serverless | Medium | Pay per use | Full auto |

---

## EC2 Instance Deployment

### Step 1: Launch EC2 Instance

Launch a dedicated EC2 instance to run the application (not for user provisioning).

```bash
# Launch instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.small \
  --security-groups default \
  --iam-instance-profile Name=ec2-automator-role \
  --key-name your-key-pair \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ec2-automator-api}]'
```

### Step 2: SSH into Instance

```bash
# Get instance public IP
INSTANCE_IP=$(aws ec2 describe-instances \
  --filters Name=tag:Name,Values=ec2-automator-api \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

# SSH into instance
ssh -i your-key.pem ec2-user@$INSTANCE_IP
```

### Step 3: Install Dependencies

```bash
# Update system
sudo yum update -y

# Install Python 3.12
sudo yum install -y python3.12 python3.12-devel

# Install git
sudo yum install -y git

# Install pip
python3.12 -m pip install --upgrade pip

# Install supervisor (for process management)
sudo yum install -y supervisor
```

### Step 4: Clone Repository

```bash
# Clone repo
git clone https://github.com/elpendex123/ec2-automator.git
cd ec2-automator

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Configure Environment

```bash
# Copy environment file
cp .env.example .env

# Edit configuration
nano .env

# Configure:
# AWS_REGION=us-east-1
# SES_SENDER_EMAIL=your-verified-email@example.com
# NOTIFICATION_EMAIL=notifications@example.com
```

### Step 6: Set Up Systemd Service

Create a systemd service for automatic startup and restart.

```bash
# Create service file
sudo nano /etc/systemd/system/ec2-automator.service
```

Paste the following:

```ini
[Unit]
Description=EC2 Automator API Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/ec2-automator
Environment="PATH=/home/ec2-user/ec2-automator/venv/bin"
ExecStart=/home/ec2-user/ec2-automator/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
# Enable on startup
sudo systemctl enable ec2-automator

# Start service
sudo systemctl start ec2-automator

# Check status
sudo systemctl status ec2-automator

# View logs
sudo journalctl -u ec2-automator -f
```

### Step 7: Set Up Nginx Reverse Proxy

```bash
# Install nginx
sudo yum install -y nginx

# Create nginx config
sudo nano /etc/nginx/conf.d/ec2-automator.conf
```

Paste the following:

```nginx
upstream ec2-automator {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name _;
    client_max_body_size 10M;

    location / {
        proxy_pass http://ec2-automator;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and start nginx:

```bash
# Enable on startup
sudo systemctl enable nginx

# Start service
sudo systemctl start nginx

# Check status
sudo systemctl status nginx
```

### Step 8: Test Deployment

```bash
# Test health endpoint
curl http://localhost/health

# Test API endpoint
curl http://localhost/options

# Check logs
sudo journalctl -u ec2-automator -n 50
```

---

## Container Deployment

### Step 1: Build Docker Image

```bash
# Build image
docker build -t ec2-automator:latest .

# Tag for registry
docker tag ec2-automator:latest your-registry/ec2-automator:latest

# Push to registry
docker push your-registry/ec2-automator:latest
```

### Step 2: Deploy with Docker Compose

```bash
# Copy docker-compose.yml
cp docker-compose.yml docker-compose.prod.yml

# Edit for production
nano docker-compose.prod.yml
```

Update configuration:

```yaml
version: '3.8'

services:
  ec2-automator:
    image: your-registry/ec2-automator:latest
    container_name: ec2-automator-api
    ports:
      - "8000:8000"
    environment:
      AWS_REGION: us-east-1
      SES_SENDER_EMAIL: your-verified-email@example.com
      NOTIFICATION_EMAIL: notifications@example.com
    volumes:
      - ~/.aws:/root/.aws:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    container_name: ec2-automator-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - ec2-automator
    restart: unless-stopped
```

### Step 3: Run Containers

```bash
# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f ec2-automator

# Stop services
docker-compose -f docker-compose.prod.yml down
```

### Step 4: SSL/TLS Configuration

```bash
# Install Let's Encrypt certbot
sudo yum install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Update nginx config to use SSL
# (Include SSL certificate paths and redirects)
```

---

## Kubernetes Deployment

### Step 1: Create Kubernetes Manifests

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ec2-automator
  labels:
    app: ec2-automator
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ec2-automator
  template:
    metadata:
      labels:
        app: ec2-automator
    spec:
      serviceAccountName: ec2-automator
      containers:
      - name: ec2-automator
        image: your-registry/ec2-automator:latest
        ports:
        - containerPort: 8000
        env:
        - name: AWS_REGION
          value: "us-east-1"
        - name: SES_SENDER_EMAIL
          valueFrom:
            secretKeyRef:
              name: ec2-automator-secrets
              key: ses-email
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ec2-automator
spec:
  selector:
    app: ec2-automator
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ec2-automator
```

### Step 2: Deploy to EKS

```bash
# Create namespace
kubectl create namespace ec2-automator

# Create secrets
kubectl create secret generic ec2-automator-secrets \
  --from-literal=ses-email=your-email@example.com \
  -n ec2-automator

# Deploy
kubectl apply -f k8s/deployment.yaml -n ec2-automator

# Check status
kubectl get deployments -n ec2-automator
kubectl get pods -n ec2-automator
kubectl get svc -n ec2-automator
```

---

## Health Checks & Monitoring

### Step 1: Set Up Health Checks

EC2-Automator includes a `/health` endpoint for monitoring:

```bash
# Test health endpoint
curl http://localhost/health

# Response
{"status":"ok","version":"1.0.0"}
```

### Step 2: Configure Monitoring

#### CloudWatch (AWS Native)

```bash
# Create CloudWatch alarm for application health
aws cloudwatch put-metric-alarm \
  --alarm-name ec2-automator-health \
  --alarm-description "Alert if API health check fails" \
  --metric-name APIHealth \
  --namespace EC2Automator \
  --statistic Average \
  --period 60 \
  --threshold 1 \
  --comparison-operator LessThanThreshold
```

#### Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ec2-automator'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### Step 3: Log Aggregation

#### CloudWatch Logs

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# Configure logs
sudo nano /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

# Start agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s
```

---

## Production Hardening

### Step 1: Security Updates

```bash
# Enable automatic security updates
sudo yum install -y yum-cron
sudo systemctl enable yum-cron
sudo systemctl start yum-cron
```

### Step 2: Firewall Configuration

```bash
# Configure security group (AWS)
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Block direct API access (port 8000)
aws ec2 revoke-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0
```

### Step 3: Rate Limiting

Add to nginx configuration:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location / {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://ec2-automator;
}
```

### Step 4: API Authentication

For production, add API key authentication:

```bash
# Generate API key
openssl rand -hex 32
# Output: abc123...

# Add to environment
SES_SENDER_EMAIL=your-email@example.com
API_KEY=abc123...
```

Update application to require header:

```python
@app.get("/launch")
def launch(request: LaunchInstanceRequest, api_key: str = Header(...)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... rest of implementation
```

### Step 5: HTTPS/TLS

```bash
# Install Let's Encrypt certificate
sudo certbot certonly --standalone -d your-domain.com

# Configure nginx for HTTPS
sudo nano /etc/nginx/conf.d/ec2-automator.conf

# Add:
# listen 443 ssl;
# ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

# Reload nginx
sudo systemctl reload nginx
```

---

## Rollback Procedures

### If Deployment Fails

#### Container Deployment

```bash
# Rollback to previous image
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Or revert to specific version
docker-compose -f docker-compose.prod.yml down
docker pull your-registry/ec2-automator:v1.0.0
# Update image in docker-compose.yml
docker-compose -f docker-compose.prod.yml up -d
```

#### Kubernetes Deployment

```bash
# Check rollout history
kubectl rollout history deployment/ec2-automator -n ec2-automator

# Rollback to previous version
kubectl rollout undo deployment/ec2-automator -n ec2-automator

# Rollback to specific revision
kubectl rollout undo deployment/ec2-automator -n ec2-automator --to-revision=2
```

#### EC2 + Systemd

```bash
# Stop service
sudo systemctl stop ec2-automator

# Revert code
cd /home/ec2-user/ec2-automator
git reset --hard origin/main

# Restart service
sudo systemctl start ec2-automator

# Check status
sudo systemctl status ec2-automator
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check systemd logs
sudo journalctl -u ec2-automator -n 100

# Check if port is in use
sudo lsof -i :8000

# Test locally
python3.12 -m uvicorn app.main:app --reload
```

### High CPU/Memory Usage

```bash
# Check process stats
ps aux | grep uvicorn

# Check Docker stats
docker stats ec2-automator

# Reduce workers if needed
# Update systemd service ExecStart to limit workers
```

### Database/AWS Connection Issues

```bash
# Test AWS credentials
aws sts get-caller-identity

# Test SES
aws ses send-email \
  --from your-email@example.com \
  --destination ToAddresses=your-email@example.com \
  --message Subject={Data="Test"},Body={Text={Data="Test"}}

# Check security groups
aws ec2 describe-security-groups --group-names ec2-automator-sg
```

### Request Timeouts

```bash
# Increase nginx timeouts
sudo nano /etc/nginx/conf.d/ec2-automator.conf

# Add:
# proxy_connect_timeout 60s;
# proxy_send_timeout 60s;
# proxy_read_timeout 60s;

sudo systemctl reload nginx
```

---

## Next Steps

1. [Complete AWS setup](AWS_SETUP_GUIDE.md)
2. [Review deployment checklist](DEPLOYMENT_CHECKLIST.md)
3. [Test endpoints thoroughly](../README.md#api-endpoints)
4. [Set up monitoring](AWS_SETUP_GUIDE.md#monitoring-recommendations)
5. [Monitor application health](../README.md#logging--monitoring)
