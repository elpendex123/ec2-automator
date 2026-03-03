#!/bin/bash

################################################################################
# EC2-Automator Docker Cleanup Script
# Purpose: Stop and remove Docker containers and images
# Usage: bash scripts/cleanup-docker.sh
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
REMOVE_IMAGES=false

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
Usage: bash scripts/cleanup-docker.sh [OPTIONS]

Options:
    --dry-run           Show what would be deleted without making changes
    --force             Skip confirmation prompts
    --remove-images     Also remove Docker images (in addition to containers)
    -h, --help          Show this help message

Examples:
    # Show what would be deleted (safe)
    bash scripts/cleanup-docker.sh --dry-run

    # Stop and remove containers (default)
    bash scripts/cleanup-docker.sh

    # Stop containers and remove images
    bash scripts/cleanup-docker.sh --remove-images

    # Without confirmation (dangerous!)
    bash scripts/cleanup-docker.sh --force

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
        --remove-images)
            REMOVE_IMAGES=true
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

print_header "EC2-Automator Docker Cleanup"

# Check Docker is installed and running
if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Install it from https://docs.docker.com/install/"
    exit 1
fi

if ! docker ps > /dev/null 2>&1; then
    print_error "Docker daemon not running or permission denied"
    echo "Try: sudo service docker start"
    echo "Or:  docker ps (to check permissions)"
    exit 1
fi

print_success "Docker is installed and running"
echo ""

# Check for ec2-automator containers
print_info "Checking for ec2-automator containers..."
EC2_CONTAINERS=$(docker ps -a --filter "ancestor=ec2-automator:*" --filter "name=*ec2*" -q || true)

if [ -z "$EC2_CONTAINERS" ]; then
    print_success "No ec2-automator containers found"
else
    print_warning "Found ec2-automator container(s):"
    docker ps -a --filter "ancestor=ec2-automator:*" --filter "name=*ec2*" --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"
    echo ""

    CONTAINER_COUNT=$(echo "$EC2_CONTAINERS" | wc -l)

    if [ "$DRY_RUN" = true ]; then
        print_info "[DRY RUN] Would stop and remove $CONTAINER_COUNT container(s)"
        echo "$EC2_CONTAINERS" | while read -r container_id; do
            docker inspect "$container_id" --format='  - {{.Name}} ({{.State.Status}})'
        done
    else
        # Confirm removal
        if [ "$FORCE" = false ]; then
            echo ""
            print_warning "This will STOP and REMOVE $CONTAINER_COUNT container(s)"
            read -p "Are you sure? Type 'yes' to confirm: " -r
            if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
                print_info "Cancelled - no containers removed"
                exit 0
            fi
        fi

        # Stop containers
        print_info "Stopping containers..."
        echo "$EC2_CONTAINERS" | while read -r container_id; do
            docker stop "$container_id" 2>/dev/null || true
        done
        print_success "Containers stopped"

        # Remove containers
        print_info "Removing containers..."
        docker rm $EC2_CONTAINERS > /dev/null 2>&1 || true
        print_success "Containers removed"
        echo ""
    fi
fi

# Check for running containers (all)
print_info "Checking for any running containers..."
RUNNING=$(docker ps -q || true)

if [ ! -z "$RUNNING" ]; then
    print_warning "Found running containers:"
    docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"
    print_info "Note: Run docker stop <container_id> to stop specific containers"
else
    print_success "No running containers"
fi
echo ""

# Check for ec2-automator images
print_info "Checking for ec2-automator images..."
EC2_IMAGES=$(docker images "ec2-automator*" -q || true)

if [ -z "$EC2_IMAGES" ]; then
    print_success "No ec2-automator images found"
else
    print_warning "Found ec2-automator image(s):"
    docker images "ec2-automator*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
    echo ""

    if [ "$REMOVE_IMAGES" = true ]; then
        IMAGE_COUNT=$(echo "$EC2_IMAGES" | wc -l)

        if [ "$DRY_RUN" = true ]; then
            print_info "[DRY RUN] Would remove $IMAGE_COUNT image(s)"
            echo "$EC2_IMAGES" | while read -r image_id; do
                docker inspect "$image_id" --format='  - {{.RepoTags}}'
            done
        else
            # Confirm removal
            if [ "$FORCE" = false ]; then
                echo ""
                print_warning "This will REMOVE $IMAGE_COUNT Docker image(s)"
                read -p "Are you sure? Type 'yes' to confirm: " -r
                if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
                    print_info "Cancelled - no images removed"
                    exit 0
                fi
            fi

            print_info "Removing Docker images..."
            docker rmi $EC2_IMAGES > /dev/null 2>&1 || true
            print_success "Docker images removed"
        fi
    else
        print_info "Use --remove-images to remove Docker images"
    fi
    echo ""
fi

# Check Docker volumes (orphaned)
print_info "Checking for orphaned Docker volumes..."
ORPHANED_VOLUMES=$(docker volume ls -q --filter dangling=true || true)

if [ -z "$ORPHANED_VOLUMES" ]; then
    print_success "No orphaned Docker volumes found"
else
    print_warning "Found orphaned volume(s):"
    docker volume ls --filter dangling=true
    print_info "To clean up: docker volume prune"
fi
echo ""

# Check Docker networks (orphaned)
print_info "Checking for orphaned Docker networks..."
ORPHANED_NETWORKS=$(docker network ls --filter dangling=true -q || true)

if [ -z "$ORPHANED_NETWORKS" ]; then
    print_success "No orphaned Docker networks found"
else
    print_warning "Found orphaned network(s):"
    docker network ls --filter dangling=true
    print_info "To clean up: docker network prune"
fi
echo ""

# Docker disk usage
print_info "Docker disk usage:"
docker system df || print_warning "Could not retrieve Docker disk usage"
echo ""

# Summary
print_header "Docker Cleanup Summary"

if [ "$DRY_RUN" = true ]; then
    print_warning "DRY RUN - No changes made"
    print_info "Run without --dry-run to perform actual cleanup"
else
    if [ ! -z "$EC2_CONTAINERS" ]; then
        print_success "✓ Containers stopped and removed"
    else
        print_info "✓ No containers to clean up"
    fi

    if [ "$REMOVE_IMAGES" = true ] && [ ! -z "$EC2_IMAGES" ]; then
        print_success "✓ Images removed"
    elif [ ! -z "$EC2_IMAGES" ]; then
        print_info "✓ Images still present (use --remove-images to delete)"
    fi
fi

echo ""
print_info "Additional cleanup commands:"
print_info "  - Remove all stopped containers: docker container prune"
print_info "  - Remove dangling images:       docker image prune"
print_info "  - Remove unused images:         docker image prune -a"
print_info "  - Clean up volumes:              docker volume prune"
print_info "  - Full system cleanup:           docker system prune -a"
echo ""

print_success "Docker cleanup script completed"
