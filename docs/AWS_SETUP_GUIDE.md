# AWS Setup Guide

This guide provides step-by-step instructions for configuring AWS resources needed to run EC2-Automator.

## Table of Contents
1. [IAM Role & Policy](#iam-role--policy)
2. [SES Configuration](#ses-configuration)
3. [VPC & Security Groups](#vpc--security-groups)
4. [EC2 Free Tier Limits](#ec2-free-tier-limits)
5. [Testing Your Setup](#testing-your-setup)
6. [Troubleshooting](#troubleshooting)

---

## IAM Role & Policy

### Step 1: Create IAM Role for EC2

The application requires an IAM role to launch instances and send emails.

#### Via AWS Console

1. Go to **IAM → Roles → Create role**
2. Choose **AWS service** as trusted entity
3. Select **EC2** service
4. Click **Next**
5. Name the role: `ec2-automator-role`
6. Click **Create role**

#### Via AWS CLI

```bash
# Create trust policy document
cat > trust-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name ec2-automator-role \
  --assume-role-policy-document file://trust-policy.json
```

### Step 2: Create IAM Policy

The role needs a policy with minimal permissions for EC2 and SES operations.

#### Via AWS Console

1. Go to **IAM → Policies → Create policy**
2. Click **JSON** tab
3. Paste the policy below:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances",
        "ec2:TerminateInstances",
        "ec2:DescribeInstances",
        "ec2:CreateTags"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    }
  ]
}
```

4. Click **Next**
5. Name: `ec2-automator-policy`
6. Click **Create policy**

#### Via AWS CLI

```bash
# Create policy document
cat > ec2-automator-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances",
        "ec2:TerminateInstances",
        "ec2:DescribeInstances",
        "ec2:CreateTags"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# Create policy
aws iam create-policy \
  --policy-name ec2-automator-policy \
  --policy-document file://ec2-automator-policy.json
```

### Step 3: Attach Policy to Role

#### Via AWS Console

1. Go to **IAM → Roles → ec2-automator-role**
2. Click **Attach policies**
3. Search for `ec2-automator-policy`
4. Check the box and click **Attach policy**

#### Via AWS CLI

```bash
aws iam attach-role-policy \
  --role-name ec2-automator-role \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/ec2-automator-policy
```

Replace `ACCOUNT_ID` with your AWS account ID. Find it with:
```bash
aws sts get-caller-identity --query Account --output text
```

### Step 4: Create Instance Profile

The instance profile is used to attach the role to EC2 instances.

#### Via AWS Console

1. Go to **IAM → Roles → ec2-automator-role**
2. Note the role ARN
3. When launching the instance, select this role in **Advanced Details → IAM instance profile**

#### Via AWS CLI

```bash
# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name ec2-automator-profile

# Add role to instance profile
aws iam add-role-to-instance-profile \
  --instance-profile-name ec2-automator-profile \
  --role-name ec2-automator-role
```

---

## SES Configuration

### Step 1: Verify Email Address

EC2-Automator sends emails via AWS SES. You must verify your email address first.

#### Via AWS Console

1. Go to **SES → Email addresses**
2. Click **Verify a New Email Address**
3. Enter your email: `enrique.coello@gmail.com`
4. Click **Verify This Email Address**
5. Check your email inbox for verification link
6. Click the link to confirm

#### Via AWS CLI

```bash
# Request verification
aws ses verify-email-identity --email-address enrique.coello@gmail.com

# Check status
aws ses list-verified-email-addresses
```

### Step 2: Configure Email in .env

Update your `.env` file with the verified email:

```bash
# Edit .env
SES_SENDER_EMAIL=enrique.coello@gmail.com
NOTIFICATION_EMAIL=enrique.coello@gmail.com
```

### Step 3: Request Production Access (Optional)

By default, SES is in **sandbox mode**, which means:
- ✓ You can send emails to verified addresses
- ✗ You cannot send to unverified addresses
- ⚠ Limited to 200 emails per 24 hours

For production, request **production access**:

1. Go to **SES → Sending statistics**
2. Click **Edit your account details**
3. Describe your use case
4. Submit for review (usually approved within 24 hours)

### Step 4: Test Email Sending

```bash
# Test with AWS CLI
aws ses send-email \
  --from enrique.coello@gmail.com \
  --destination ToAddresses=enrique.coello@gmail.com \
  --message Subject={Data="Test Email",Charset=UTF-8},Body={Text={Data="Test",Charset=UTF-8}}
```

Or use the API:

```bash
curl -X POST http://localhost:8000/launch \
  -H "Content-Type: application/json" \
  -d '{
    "instance_name": "test-email",
    "instance_type": "t3.micro",
    "app_name": "nginx",
    "owner": "admin"
  }'
```

---

## VPC & Security Groups

### Step 1: Use Default VPC

EC2-Automator works with the **default VPC** - no custom VPC needed.

Verify default VPC exists:

```bash
aws ec2 describe-vpcs --filters Name=isDefault,Values=true
```

### Step 2: Create/Update Security Group

The security group controls inbound/outbound access to instances.

#### Via AWS Console

1. Go to **EC2 → Security Groups**
2. Click **Create security group**
3. Name: `ec2-automator-sg`
4. Description: "Security group for EC2-Automator instances"
5. VPC: Select your default VPC
6. Add inbound rules:

| Type | Protocol | Port | Source | Purpose |
|------|----------|------|--------|---------|
| SSH | TCP | 22 | 0.0.0.0/0 | Instance management |
| HTTP | TCP | 80 | 0.0.0.0/0 | Web server |
| HTTPS | TCP | 443 | 0.0.0.0/0 | Secure web |
| MySQL | TCP | 3306 | 0.0.0.0/0 | Database access |
| MongoDB | TCP | 27017 | 0.0.0.0/0 | NoSQL access |

7. Click **Create security group**

#### Via AWS CLI

```bash
# Create security group
SG_ID=$(aws ec2 create-security-group \
  --group-name ec2-automator-sg \
  --description "Security group for EC2-Automator instances" \
  --query 'GroupId' \
  --output text)

# Add SSH inbound rule
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# Add HTTP inbound rule
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Add HTTPS inbound rule
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Add MySQL inbound rule
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 3306 \
  --cidr 0.0.0.0/0

# Add MongoDB inbound rule
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 27017 \
  --cidr 0.0.0.0/0

echo "Security group created: $SG_ID"
```

### Step 3: Update Configuration

The security group is used when launching instances via the API.

---

## EC2 Free Tier Limits

### Instance Types & Limits

**Free Tier includes 750 hours per month of:**
- `t3.micro` (2 vCPU, 1 GB RAM) - Recommended
- `t3.small` (2 vCPU, 2 GB RAM) - For demanding workloads

**Limits:**
- Maximum 1 instance running simultaneously (to stay within 750 hours)
- Storage: 30 GB EBS per month
- Data transfer: 100 GB free per month

### Monitoring Your Usage

```bash
# Check running instances
aws ec2 describe-instances \
  --filters Name=instance-state-name,Values=running \
  --query 'Reservations[].Instances[].[InstanceId,InstanceType,LaunchTime]'

# Calculate hours used
aws ec2 describe-instances \
  --query 'Reservations[].Instances[].[InstanceId,InstanceType,State.Name,LaunchTime]' \
  --output table
```

### Cost Optimization

1. **Terminate unused instances immediately**
   ```bash
   aws ec2 terminate-instances --instance-ids i-1234567890abcdef0
   ```

2. **Set up billing alerts**
   - Go to **AWS Billing → Billing preferences**
   - Enable "Receive Billing Alerts"
   - Set alert threshold to $1.00

3. **Monitor with CloudWatch**
   - Track EC2 instance count
   - Alert if cost exceeds threshold

---

## Testing Your Setup

### Step 1: Verify IAM Role

```bash
# Get current AWS identity
aws sts get-caller-identity

# Check role permissions
aws iam get-role --role-name ec2-automator-role
aws iam list-role-policies --role-name ec2-automator-role
```

### Step 2: Test SES Configuration

```bash
# Send test email
aws ses send-email \
  --from enrique.coello@gmail.com \
  --destination ToAddresses=enrique.coello@gmail.com \
  --message Subject={Data="Test Email",Charset=UTF-8},Body={Text={Data="Test from EC2-Automator",Charset=UTF-8}}

# List verified emails
aws ses list-verified-email-addresses
```

### Step 3: Test Security Group

```bash
# Describe security group
aws ec2 describe-security-groups \
  --group-names ec2-automator-sg \
  --query 'SecurityGroups[0].IpPermissions'
```

### Step 4: Launch Test Instance

```bash
# Via EC2-Automator API
curl -X POST http://localhost:8000/launch \
  -H "Content-Type: application/json" \
  -d '{
    "instance_name": "test-setup",
    "instance_type": "t3.micro",
    "app_name": "nginx",
    "owner": "admin"
  }'

# Via AWS CLI (for manual testing)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.micro \
  --security-groups ec2-automator-sg \
  --iam-instance-profile Name=ec2-automator-profile \
  --key-name your-key-pair \
  --user-data file://userdata.sh
```

---

## Troubleshooting

### Problem: "Unable to locate credentials"

**Cause:** Application cannot find AWS credentials.

**Solutions:**
1. For EC2 instances: Attach IAM role with proper permissions
2. For local development: Configure AWS CLI
   ```bash
   aws configure
   # Enter your Access Key ID and Secret Access Key
   ```
3. For Docker: Mount credentials
   ```bash
   docker run -v ~/.aws:/root/.aws:ro ec2-automator
   ```

### Problem: "User is not authorized to perform: ec2:RunInstances"

**Cause:** IAM policy doesn't include required permissions.

**Solution:** Verify policy is attached:
```bash
aws iam list-attached-role-policies --role-name ec2-automator-role
```

If missing, attach the policy:
```bash
aws iam attach-role-policy \
  --role-name ec2-automator-role \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/ec2-automator-policy
```

### Problem: "Email address not verified"

**Cause:** Sender email not verified in SES.

**Solution:** Verify email address:
```bash
aws ses verify-email-identity --email-address enrique.coello@gmail.com
```

Then confirm verification link in your email inbox.

### Problem: Instance launches but email not received

**Cause 1:** SES in sandbox mode, email goes to spam

**Solution:**
- Check spam/junk folder
- Request SES production access
- Add sender to contacts

**Cause 2:** Email not verified in SES

**Solution:** Verify the email address again

### Problem: "The security group ... is not a valid security group"

**Cause:** Security group doesn't exist or is in wrong VPC.

**Solution:** Create security group in default VPC:
```bash
aws ec2 create-security-group \
  --group-name ec2-automator-sg \
  --description "EC2-Automator security group"
```

### Problem: Free Tier limit exceeded

**Cause:** Running too many instances or using non-Free Tier instance type.

**Solutions:**
1. Terminate unused instances immediately
   ```bash
   aws ec2 terminate-instances --instance-ids i-xxxxxxxxx
   ```
2. Use only t3.micro or t3.small
3. Monitor usage with CloudWatch
4. Set up billing alerts

---

## Next Steps

1. [Configure the application](../README.md#configuration)
2. [Run the API server](../README.md#running-locally)
3. [Test API endpoints](../README.md#api-endpoints)
4. [Deploy with Docker](../README.md#running-with-docker)
5. [Set up Jenkins CI/CD](../jenkins/PIPELINE_SETUP.md)
