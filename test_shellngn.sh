#!/usr/bin/env bash
"""
DEBT Business Remote Access (Shellngn Pro) Test Script
Verifies Shellngn Pro Docker setup and business remote access functionality
"""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

test_docker_availability() {
    log_info "Testing Docker availability..."
    
    if command -v docker &> /dev/null; then
        log_success "Docker command is available"
        docker --version
        return 0
    else
        log_error "Docker is not installed or not in PATH"
        return 1
    fi
}

test_docker_service() {
    log_info "Testing Docker service status..."
    
    if docker info &> /dev/null; then
        log_success "Docker service is running"
        return 0
    else
        log_error "Docker service is not running or accessible"
        log_info "Try: sudo systemctl start docker"
        return 1
    fi
}

test_shellngn_image() {
    log_info "Testing DEBT Shellngn Pro Business Remote Access image availability..."
    
    if docker pull shellngn/pro &> /dev/null; then
        log_success "DEBT Shellngn Pro business remote access image pulled successfully"
        return 0
    else
        log_error "Failed to pull DEBT Shellngn Pro business access image"
        return 1
    fi
}

test_shellngn_container() {
    log_info "Testing DEBT Shellngn Pro business remote access container startup..."
    
    # Stop any existing container
    docker stop shellngn 2>/dev/null || true
    docker rm shellngn 2>/dev/null || true
    
    # Create business data directory
    mkdir -p ./shellngn-data
    
    # Start business remote access container
    if docker run -d --name shellngn -p 8080:8080 -v "$(pwd)/shellngn-data:/data" shellngn/pro; then
        sleep 5  # Wait for container to initialize
        
        if docker ps | grep -q "shellngn"; then
            log_success "DEBT Shellngn Pro business remote access started successfully"
            log_info "Business Remote Access Portal: http://localhost:8080"
            return 0
        else
            log_error "DEBT Shellngn Pro business container failed to start properly"
            docker logs shellngn
            return 1
        fi
    else
        log_error "Failed to start DEBT Shellngn Pro business container"
        return 1
    fi
}

test_shellngn_connectivity() {
    log_info "Testing DEBT Shellngn Pro business interface connectivity..."
    
    # Test if business portal port 8080 is responding
    if command -v curl &> /dev/null; then
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 | grep -q "200\|30[0-9]"; then
            log_success "DEBT Shellngn Pro business interface is responding"
            return 0
        else
            log_warning "DEBT Shellngn Pro business interface not yet ready (may need more time to initialize)"
            return 1
        fi
    else
        log_warning "curl not available for DEBT business connectivity test"
        return 1
    fi
}

cleanup_test_container() {
    log_info "Cleaning up test container..."
    docker stop shellngn 2>/dev/null || true
    docker rm shellngn 2>/dev/null || true
    log_success "Test container cleaned up"
}

show_usage_instructions() {
    echo ""
    echo "================================================"
    echo "DEBT Shellngn Pro Business Remote Access Usage:"
    echo "================================================"
    echo ""
    echo "🚀 Start DEBT Business Remote Access:"
    echo "   docker run -d --name shellngn -p 8080:8080 -v \$(pwd)/shellngn-data:/data shellngn/pro"
    echo ""
    echo "🌐 Access Business Portal:"
    echo "   http://localhost:8080"
    echo ""
    echo "🛑 Stop Business Remote Access:"
    echo "   docker stop shellngn && docker rm shellngn"
    echo ""
    echo "📋 View Business Logs:"
    echo "   docker logs shellngn"
    echo ""
    echo "📁 Business Data Persistence:"
    echo "   Business data is stored in ./shellngn-data directory"
    echo ""
    echo "🔧 Business Remote Access Features:"
    echo "   • SSH/Telnet Access to Business Servers"
    echo "   • SFTP File Transfer for Business Documents"
    echo "   • VNC/RDP Remote Desktop for Business Applications"
    echo "   • Multi-session Business Connection Management"
    echo "   • Business Device & Identity Management"
    echo "   • Web-based Business Interface (No installation required)"
    echo ""
}

main() {
    echo "Testing DEBT Shellngn Pro Business Remote Access setup..."
    echo "========================================================"
    
    tests=(
        test_docker_availability
        test_docker_service
        test_shellngn_image
        test_shellngn_container
        test_shellngn_connectivity
    )
    
    passed=0
    total=${#tests[@]}
    
    for test in "${tests[@]}"; do
        if $test; then
            ((passed++))
        fi
        echo ""
    done
    
    echo "========================================================"
    echo "DEBT Business Remote Access Test Results: $passed/$total tests passed"
    
    if [ $passed -eq $total ]; then
        log_success "All DEBT Shellngn Pro business tests passed! Ready for business remote access."
        show_usage_instructions
    else
        log_error "Some DEBT business remote access tests failed. Please check setup."
        if [ $passed -gt 2 ]; then
            show_usage_instructions
        fi
    fi
    
    # Cleanup
    cleanup_test_container
}

main "$@"