#!/bin/bash

################################################################################
# EC2-Automator Local Deployment Cleanup Script
# Purpose: Stop local uvicorn, systemd services, and nginx
# Usage: bash scripts/cleanup-local-deployment.sh
################################################################################

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
Usage: bash scripts/cleanup-local-deployment.sh [OPTIONS]

Options:
    -a, --all               Stop all services (default)
    -u, --uvicorn           Stop only uvicorn processes
    -s, --systemd           Stop only systemd service
    -n, --nginx             Stop only nginx
    -h, --help              Show this help message

Examples:
    # Stop all services
    bash scripts/cleanup-local-deployment.sh

    # Stop only uvicorn
    bash scripts/cleanup-local-deployment.sh --uvicorn

    # Stop only systemd service
    bash scripts/cleanup-local-deployment.sh --systemd

    # Stop only nginx
    bash scripts/cleanup-local-deployment.sh --nginx

EOF
}

# Defaults
STOP_UVICORN=false
STOP_SYSTEMD=false
STOP_NGINX=false
STOP_ALL=true

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--all)
            STOP_UVICORN=true
            STOP_SYSTEMD=true
            STOP_NGINX=true
            STOP_ALL=true
            shift
            ;;
        -u|--uvicorn)
            STOP_UVICORN=true
            STOP_ALL=false
            shift
            ;;
        -s|--systemd)
            STOP_SYSTEMD=true
            STOP_ALL=false
            shift
            ;;
        -n|--nginx)
            STOP_NGINX=true
            STOP_ALL=false
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

# If no specific option given, stop all
if [ "$STOP_ALL" = true ]; then
    STOP_UVICORN=true
    STOP_SYSTEMD=true
    STOP_NGINX=true
fi

print_header "EC2-Automator Local Deployment Cleanup"

# Stop uvicorn processes
if [ "$STOP_UVICORN" = true ]; then
    print_info "Checking for uvicorn processes..."

    UVICORN_PIDS=$(pgrep -f "uvicorn.*app.main:app" || true)

    if [ -z "$UVICORN_PIDS" ]; then
        print_success "No uvicorn processes found"
    else
        print_warning "Found uvicorn process(es):"
        echo "$UVICORN_PIDS" | while read -r pid; do
            ps -p "$pid" -o pid,cmd --no-headers
        done

        echo ""
        print_info "Stopping uvicorn..."
        echo "$UVICORN_PIDS" | xargs kill -9 2>/dev/null || true
        sleep 1

        # Verify stopped
        REMAINING=$(pgrep -f "uvicorn.*app.main:app" || true)
        if [ -z "$REMAINING" ]; then
            print_success "All uvicorn processes stopped"
        else
            print_error "Failed to stop some uvicorn processes"
        fi
    fi
    echo ""
fi

# Stop systemd service
if [ "$STOP_SYSTEMD" = true ]; then
    print_info "Checking for systemd ec2-automator service..."

    if systemctl is-active --quiet ec2-automator 2>/dev/null; then
        print_warning "Found active ec2-automator service"
        print_info "Stopping systemd service..."
        sudo systemctl stop ec2-automator 2>/dev/null || true
        sleep 1

        if systemctl is-active --quiet ec2-automator 2>/dev/null; then
            print_error "Failed to stop ec2-automator service"
        else
            print_success "ec2-automator service stopped"
        fi
    else
        print_success "ec2-automator service not running"
    fi
    echo ""
fi

# Stop nginx
if [ "$STOP_NGINX" = true ]; then
    print_info "Checking for nginx..."

    if command -v nginx &> /dev/null; then
        if pgrep -x "nginx" > /dev/null; then
            print_warning "Found nginx process"
            print_info "Stopping nginx..."
            sudo systemctl stop nginx 2>/dev/null || sudo nginx -s stop 2>/dev/null || true
            sleep 1

            if pgrep -x "nginx" > /dev/null; then
                print_warning "nginx still running, attempting force stop..."
                sudo pkill -9 nginx 2>/dev/null || true
                sleep 1
            fi

            if pgrep -x "nginx" > /dev/null; then
                print_error "Failed to stop nginx"
            else
                print_success "nginx stopped"
            fi
        else
            print_success "nginx not running"
        fi
    else
        print_info "nginx not installed"
    fi
    echo ""
fi

# Check for any remaining processes on port 8000
print_info "Checking for processes on port 8000..."
PORT_PROCESSES=$(lsof -i :8000 2>/dev/null || true)

if [ -z "$PORT_PROCESSES" ]; then
    print_success "No processes listening on port 8000"
else
    print_warning "Found process(es) on port 8000:"
    echo "$PORT_PROCESSES" | tail -n +2

    print_info "Attempting to kill processes on port 8000..."
    PIDS=$(lsof -i :8000 -t 2>/dev/null || true)
    if [ ! -z "$PIDS" ]; then
        echo "$PIDS" | xargs kill -9 2>/dev/null || true
        sleep 1

        REMAINING=$(lsof -i :8000 2>/dev/null || true)
        if [ -z "$REMAINING" ]; then
            print_success "Port 8000 is now free"
        else
            print_error "Failed to free port 8000"
        fi
    fi
fi
echo ""

# Check for any remaining processes on port 80
print_info "Checking for processes on port 80..."
PORT_80_PROCESSES=$(lsof -i :80 2>/dev/null || true)

if [ -z "$PORT_80_PROCESSES" ]; then
    print_success "No processes listening on port 80"
else
    print_warning "Found process(es) on port 80 (nginx or reverse proxy):"
    echo "$PORT_80_PROCESSES" | tail -n +2
fi
echo ""

# Summary
print_header "Local Deployment Cleanup Summary"

print_info "Status:"
if [ "$STOP_UVICORN" = true ]; then
    if ! pgrep -f "uvicorn.*app.main:app" > /dev/null 2>&1; then
        print_success "✓ Uvicorn stopped"
    else
        print_error "✗ Uvicorn still running"
    fi
fi

if [ "$STOP_SYSTEMD" = true ]; then
    if ! systemctl is-active --quiet ec2-automator 2>/dev/null; then
        print_success "✓ Systemd service stopped"
    else
        print_warning "✗ Systemd service still running"
    fi
fi

if [ "$STOP_NGINX" = true ]; then
    if ! pgrep -x "nginx" > /dev/null 2>&1; then
        print_success "✓ Nginx stopped"
    else
        print_warning "✗ Nginx still running"
    fi
fi

echo ""
print_info "Free ports:"
print_info "- Port 8000: $(lsof -i :8000 > /dev/null 2>&1 && echo "BUSY" || echo "FREE")"
print_info "- Port 80:   $(lsof -i :80 > /dev/null 2>&1 && echo "BUSY" || echo "FREE")"
echo ""

print_success "Local deployment cleanup completed"
