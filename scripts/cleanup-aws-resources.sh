#!/bin/bash

################################################################################
# EC2-Automator AWS Cleanup Script
# Purpose: Terminate all EC2 instances and clean up AWS resources
# Usage: bash scripts/cleanup-aws-resources.sh
################################################################################

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DRY_RUN=false
FORCE=false

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_usage() {
    cat << EOF
Usage: bash scripts/cleanup-aws-resources.sh [OPTIONS]

Options:
    --dry-run       Show what would be deleted without making changes
    --force         Skip confirmation prompts
    -h, --help      Show this help message

Examples:
    # Show what would be deleted (safe)
    bash scripts/cleanup-aws-resources.sh --dry-run

    # Delete with confirmation (default)
    bash scripts/cleanup-aws-resources.sh

    # Delete without confirmation (dangerous!)
    bash scripts/cleanup-aws-resources.sh --force

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main cleanup process
print_header "EC2-Automator AWS Resource Cleanup"

# Check AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI not found. Install it with: pip install awscli"
    exit 1
fi

# Check AWS credentials
print_info "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured or invalid"
    echo "Configure with: aws configure"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
print_success "AWS credentials verified (Account: $ACCOUNT_ID)"
echo ""

# List running EC2 instances
print_info "Checking for running EC2 instances..."
RUNNING_INSTANCES=$(aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=running" \
    --query 'Reservations[].Instances[].[InstanceId,InstanceType,Tags[?Key==`Name`].Value|[0]]' \
    --output text)

if [ -z "$RUNNING_INSTANCES" ]; then
    print_success "No running EC2 instances found"
    echo ""
else
    echo ""
    print_warning "Found running EC2 instances:"
    echo ""
    echo "Instance ID          Type         Name"
    echo "==================== ============ ========================"
    echo "$RUNNING_INSTANCES" | while read -r instance_id instance_type instance_name; do
        printf "%-20s %-12s %s\n" "$instance_id" "$instance_type" "${instance_name:-<no name>}"
    done
    echo ""

    # Get instance IDs
    INSTANCE_IDS=$(echo "$RUNNING_INSTANCES" | awk '{print $1}')
    INSTANCE_COUNT=$(echo "$INSTANCE_IDS" | wc -l)

    if [ "$DRY_RUN" = true ]; then
        print_info "[DRY RUN] Would terminate $INSTANCE_COUNT instance(s)"
        echo "$INSTANCE_IDS" | sed 's/^/  - /'
        echo ""
    else
        # Confirm termination
        if [ "$FORCE" = false ]; then
            echo ""
            print_warning "This will TERMINATE $INSTANCE_COUNT EC2 instance(s)"
            read -p "Are you sure? Type 'yes' to confirm: " -r
            if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
                print_info "Cancelled - no instances terminated"
                exit 0
            fi
        fi

        # Terminate instances
        echo ""
        print_info "Terminating EC2 instances..."
        aws ec2 terminate-instances --instance-ids $INSTANCE_IDS --output text > /dev/null
        print_success "Termination request sent for $INSTANCE_COUNT instance(s)"

        # Wait for termination
        print_info "Waiting for instances to terminate (this may take 1-2 minutes)..."
        aws ec2 wait instance-terminated --instance-ids $INSTANCE_IDS
        print_success "All instances terminated"
        echo ""
    fi
fi

# List stopped EC2 instances
print_info "Checking for stopped EC2 instances..."
STOPPED_INSTANCES=$(aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=stopped" \
    --query 'Reservations[].Instances[].[InstanceId,InstanceType,Tags[?Key==`Name`].Value|[0]]' \
    --output text)

if [ -z "$STOPPED_INSTANCES" ]; then
    print_success "No stopped EC2 instances found"
    echo ""
else
    echo ""
    print_warning "Found stopped EC2 instances:"
    echo ""
    echo "Instance ID          Type         Name"
    echo "==================== ============ ========================"
    echo "$STOPPED_INSTANCES" | while read -r instance_id instance_type instance_name; do
        printf "%-20s %-12s %s\n" "$instance_id" "$instance_type" "${instance_name:-<no name>}"
    done
    echo ""

    STOPPED_IDS=$(echo "$STOPPED_INSTANCES" | awk '{print $1}')
    STOPPED_COUNT=$(echo "$STOPPED_IDS" | wc -l)

    if [ "$DRY_RUN" = true ]; then
        print_info "[DRY RUN] Would terminate $STOPPED_COUNT stopped instance(s)"
        echo "$STOPPED_IDS" | sed 's/^/  - /'
        echo ""
    else
        # Confirm termination
        if [ "$FORCE" = false ]; then
            print_warning "This will TERMINATE $STOPPED_COUNT stopped instance(s)"
            read -p "Are you sure? Type 'yes' to confirm: " -r
            if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
                print_info "Cancelled - no instances terminated"
            else
                print_info "Terminating stopped instances..."
                aws ec2 terminate-instances --instance-ids $STOPPED_IDS --output text > /dev/null
                print_success "Termination request sent for $STOPPED_COUNT instance(s)"
                echo ""
            fi
        fi
    fi
fi

# Check VPC and Security Groups
print_info "Checking Security Groups..."
CUSTOM_SGS=$(aws ec2 describe-security-groups \
    --query 'SecurityGroups[?GroupName==`ec2-automator-sg`].[GroupId,GroupName]' \
    --output text)

if [ -z "$CUSTOM_SGS" ]; then
    print_success "No custom security groups found"
else
    print_info "Found custom security group: ec2-automator-sg"
    print_info "(Note: Delete manually if needed - security groups are reusable)"
fi
echo ""

# Summary
print_header "Cleanup Summary"

if [ "$DRY_RUN" = true ]; then
    print_warning "DRY RUN - No changes made"
    print_info "Run without --dry-run to perform actual cleanup"
else
    if [ ! -z "$RUNNING_INSTANCES" ] || [ ! -z "$STOPPED_INSTANCES" ]; then
        print_success "AWS resources cleanup completed"
    else
        print_info "No AWS resources to clean up"
    fi
fi

echo ""
print_info "Free Tier Status:"
print_info "- EC2: Check usage at https://console.aws.amazon.com/ec2/v2/home#Instances:"
print_info "- SES: Check usage at https://console.aws.amazon.com/ses/home#verified-senders:"
print_info "- Billing: Check costs at https://console.aws.amazon.com/billing/home"
echo ""

print_success "AWS cleanup script completed"
