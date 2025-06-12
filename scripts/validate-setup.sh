#!/bin/bash

# Quick Setup Validation Script
# This script quickly checks if all Oracle instances are properly configured

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_success() { echo -e "${GREEN}${NC} $1"; }
log_error() { echo -e "${RED}${NC} $1"; }
log_warning() { echo -e "${YELLOW}${NC} $1"; }

echo "🔍 Oracle Multi-Instance Setup Validation"
echo "========================================"

errors=0

# Check containers
echo ""
echo "Container Status:"
for container in oracle-db-primary oracle-db-secondary oracle-db-legacy otel-collector; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}"; then
        log_success "$container is running"
    else
        log_error "$container is not running"
        ((errors++))
    fi
done

# Check database connectivity
echo ""
echo "Database Connectivity:"

# Use arrays instead of associative arrays for better compatibility
instances=(
    "primary:oracle-db-primary:YourSecurePassword123"
    "secondary:oracle-db-secondary:YourSecurePassword456" 
    "legacy:oracle-db-legacy:YourSecurePassword789"
)

for instance_config in "${instances[@]}"; do
    IFS=':' read -r instance host password <<< "$instance_config"
    if docker exec -i $host sqlplus -S system/$password@localhost:1521/xepdb1 <<< "SELECT 1 FROM DUAL; EXIT;" >/dev/null 2>&1; then
        log_success "$instance instance is accessible"
    else
        log_error "$instance instance is not accessible"
        ((errors++))
    fi
done

# Check monitoring users
echo ""
echo "Monitoring Users:"
for instance_config in "${instances[@]}"; do
    IFS=':' read -r instance host password <<< "$instance_config"
    if docker exec -i $host sqlplus -S otel_monitor/OtelMonitorPassword123@localhost:1521/xepdb1 <<< "SELECT COUNT(*) FROM v\$session WHERE rownum <= 1; EXIT;" >/dev/null 2>&1; then
        log_success "$instance OTEL_MONITOR user is working"
    else
        log_error "$instance OTEL_MONITOR user is not working"
        ((errors++))
    fi
done

# Check test schemas
echo ""
echo "Test Schemas:"
for instance_config in "${instances[@]}"; do
    IFS=':' read -r instance host password <<< "$instance_config"
    count=$(docker exec -i $host sqlplus -S testuser/YourSecurePassword123@localhost:1521/xepdb1 <<EOF 2>/dev/null | tail -1 | tr -d ' \n'
SET PAGESIZE 0
SET FEEDBACK OFF
SET HEADING OFF
SELECT COUNT(*) FROM employees;
EXIT;
EOF
)
    if [[ "$count" -ge "3" ]]; then
        log_success "$instance TESTUSER schema has $count employee records"
    else
        log_error "$instance TESTUSER schema is missing or has no data"
        ((errors++))
    fi
done

# Check OTEL collector
echo ""
echo "OTEL Collector:"
if docker logs otel-collector --since 30s 2>/dev/null | grep -q "Everything is ready"; then
    log_success "OTEL collector is running and ready"
else
    log_warning "OTEL collector may still be starting up"
fi

# Check for oracle_correlation_plan logs
if docker logs otel-collector --since 2m 2>/dev/null | grep -q "oracle_correlation_plan"; then
    log_success "oracle_correlation_plan logs are being generated"
else
    log_warning "oracle_correlation_plan logs not found (may need more time or activity)"
fi

echo ""
echo "========================================"
if [[ $errors -eq 0 ]]; then
    log_success "🎉 All systems are properly configured!"
    echo ""
    echo "You can access:"
    echo "  Frontend Demo: http://localhost:8081"
    echo "  Prometheus Metrics: http://localhost:9464/metrics"
    echo "  API: http://localhost:8000"
    echo ""
    echo "To generate activity and see correlation logs, visit the frontend demo."
else
    log_error "Found $errors issues"
    echo ""
    echo "To fix setup issues, run:"
    echo "  ./scripts/init-database.sh"
    echo ""
    echo "If containers aren't running:"
    echo "  docker compose up -d"
    echo "  # Wait 3-4 minutes for databases to initialize"
    echo "  ./scripts/validate-setup.sh"
    exit 1
fi