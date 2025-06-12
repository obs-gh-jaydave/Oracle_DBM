#!/bin/bash

# Database Initialization and Validation Script
# This script ensures all Oracle instances are properly set up with schemas and monitoring users

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MAX_RETRIES=10
RETRY_DELAY=30
INSTANCES=("primary" "secondary" "legacy")

# Database connection details
declare -A DB_HOSTS=([primary]="oracle-db-primary" [secondary]="oracle-db-secondary" [legacy]="oracle-db-legacy")
declare -A DB_PORTS=([primary]="1521" [secondary]="1521" [legacy]="1521")
declare -A DB_PASSWORDS=([primary]="YourSecurePassword123" [secondary]="YourSecurePassword456" [legacy]="YourSecurePassword789")

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
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

wait_for_database() {
    local instance=$1
    local host=${DB_HOSTS[$instance]}
    local port=${DB_PORTS[$instance]}
    local password=${DB_PASSWORDS[$instance]}
    
    log "Waiting for Oracle $instance instance to be ready..."
    
    for i in $(seq 1 $MAX_RETRIES); do
        if docker exec -i $host sqlplus -S system/$password@localhost:$port/xepdb1 <<EOF >/dev/null 2>&1
SELECT 1 FROM DUAL;
EXIT;
EOF
        then
            log_success "Oracle $instance instance is ready"
            return 0
        fi
        
        log "Attempt $i/$MAX_RETRIES failed, waiting ${RETRY_DELAY}s..."
        sleep $RETRY_DELAY
    done
    
    log_error "Oracle $instance instance failed to become ready after $MAX_RETRIES attempts"
    return 1
}

check_user_exists() {
    local instance=$1
    local host=${DB_HOSTS[$instance]}
    local password=${DB_PASSWORDS[$instance]}
    local username=$2
    
    docker exec -i $host sqlplus -S system/$password@localhost:1521/xepdb1 <<EOF 2>/dev/null
SET PAGESIZE 0
SET FEEDBACK OFF
SET VERIFY OFF
SET HEADING OFF
SELECT COUNT(*) FROM dba_users WHERE username = UPPER('$username');
EXIT;
EOF
}

check_table_exists() {
    local instance=$1
    local host=${DB_HOSTS[$instance]}
    local password=${DB_PASSWORDS[$instance]}
    local owner=$2
    local table=$3
    
    docker exec -i $host sqlplus -S system/$password@localhost:1521/xepdb1 <<EOF 2>/dev/null
SET PAGESIZE 0
SET FEEDBACK OFF
SET VERIFY OFF
SET HEADING OFF
SELECT COUNT(*) FROM dba_tables WHERE owner = UPPER('$owner') AND table_name = UPPER('$table');
EXIT;
EOF
}

create_monitoring_user() {
    local instance=$1
    local host=${DB_HOSTS[$instance]}
    local password=${DB_PASSWORDS[$instance]}
    
    log "Creating OTEL_MONITOR user in $instance instance..."
    
    docker exec -i $host sqlplus -S system/$password@localhost:1521/xepdb1 <<EOF
SET ECHO OFF
SET FEEDBACK OFF

-- Drop existing user if exists
BEGIN
    EXECUTE IMMEDIATE 'DROP USER otel_monitor CASCADE';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -1918 THEN
            NULL;
        END IF;
END;
/

-- Create monitoring user
CREATE USER otel_monitor IDENTIFIED BY "OtelMonitorPassword123";
GRANT CREATE SESSION TO otel_monitor;
GRANT SELECT ON V_\$SESSION TO otel_monitor;
GRANT SELECT ON V_\$SQL TO otel_monitor;
GRANT SELECT ON V_\$SQL_PLAN TO otel_monitor;
GRANT SELECT ON V_\$SQL_PLAN_STATISTICS_ALL TO otel_monitor;
GRANT SELECT ON V_\$SQL_MONITOR TO otel_monitor;
GRANT SELECT ON V_\$SYSSTAT TO otel_monitor;
GRANT SELECT ON V_\$OSSTAT TO otel_monitor;
GRANT SELECT ON V_\$SGA TO otel_monitor;
GRANT SELECT ON V_\$PGASTAT TO otel_monitor;
GRANT SELECT ON V_\$SYSTEM_EVENT TO otel_monitor;
GRANT SELECT ON V_\$LIBRARYCACHE TO otel_monitor;
GRANT SELECT ON V_\$SGASTAT TO otel_monitor;
GRANT SELECT ON DBA_DATA_FILES TO otel_monitor;
GRANT SELECT ON DBA_FREE_SPACE TO otel_monitor;
GRANT SELECT ON V_\$SYSMETRIC TO otel_monitor;
GRANT SELECT ON V_\$LOG_HISTORY TO otel_monitor;
GRANT SELECT ON V_\$PARAMETER TO otel_monitor;
GRANT SELECT ON V_\$TRANSACTION TO otel_monitor;
GRANT SELECT ON DBA_TAB_PRIVS TO otel_monitor;

COMMIT;
EXIT;
EOF
}

create_test_user() {
    local instance=$1
    local host=${DB_HOSTS[$instance]}
    local password=${DB_PASSWORDS[$instance]}
    
    log "Creating TESTUSER in $instance instance..."
    
    docker exec -i $host sqlplus -S system/$password@localhost:1521/xepdb1 <<EOF
SET ECHO OFF
SET FEEDBACK OFF

-- Drop existing user if exists
BEGIN
    EXECUTE IMMEDIATE 'DROP USER testuser CASCADE';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -1918 THEN
            NULL;
        END IF;
END;
/

-- Create test user
CREATE USER testuser IDENTIFIED BY "YourSecurePassword123" 
    DEFAULT TABLESPACE USERS 
    TEMPORARY TABLESPACE TEMP;

GRANT CREATE SESSION TO testuser;
GRANT CONNECT, RESOURCE TO testuser;
GRANT UNLIMITED TABLESPACE TO testuser;
GRANT EXECUTE ON DBMS_SESSION TO testuser;
GRANT EXECUTE ON DBMS_APPLICATION_INFO TO testuser;
GRANT SELECT ON V_\$SESSION TO testuser;
GRANT SELECT ON V_\$SQL TO testuser;

COMMIT;
EXIT;
EOF
}

create_test_schema() {
    local instance=$1
    local host=${DB_HOSTS[$instance]}
    local password=${DB_PASSWORDS[$instance]}
    
    log "Creating test schema in $instance instance..."
    
    docker exec -i $host sqlplus -S testuser/YourSecurePassword123@localhost:1521/xepdb1 <<EOF
SET ECHO OFF
SET FEEDBACK OFF

-- Drop existing table if exists
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE employees CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -942 THEN
            NULL;
        END IF;
END;
/

-- Create employees table
CREATE TABLE employees (
    employee_id    NUMBER(6),
    first_name     VARCHAR2(20),
    last_name      VARCHAR2(25),
    salary         NUMBER(8,2),
    hire_date      DATE
);

-- Insert sample data
INSERT INTO employees VALUES (1001, 'John', 'Doe', 60000, SYSDATE - 100);
INSERT INTO employees VALUES (1002, 'Jane', 'Smith', 65000, SYSDATE - 200);
INSERT INTO employees VALUES (1003, 'Alice', 'Johnson', 75000, SYSDATE - 300);

-- Add load generation sample data
INSERT INTO employees VALUES (2001, 'Bob', 'Wilson', 55000, SYSDATE - 50);
INSERT INTO employees VALUES (2002, 'Carol', 'Brown', 70000, SYSDATE - 150);
INSERT INTO employees VALUES (2003, 'David', 'Miller', 80000, SYSDATE - 250);
INSERT INTO employees VALUES (2004, 'Emma', 'Davis', 65000, SYSDATE - 75);
INSERT INTO employees VALUES (2005, 'Frank', 'Garcia', 72000, SYSDATE - 125);
INSERT INTO employees VALUES (2006, 'Grace', 'Rodriguez', 68000, SYSDATE - 175);
INSERT INTO employees VALUES (2007, 'Henry', 'Martinez', 85000, SYSDATE - 225);

COMMIT;

-- Create indexes for performance
CREATE INDEX emp_salary_idx ON employees(salary);
CREATE INDEX emp_hire_date_idx ON employees(hire_date);

-- Create Oracle context for OpenTelemetry correlation tracking
CREATE OR REPLACE CONTEXT OTEL_CTX USING DBMS_SESSION ACCESSED GLOBALLY;

COMMIT;
EXIT;
EOF
}

validate_setup() {
    local instance=$1
    local host=${DB_HOSTS[$instance]}
    local password=${DB_PASSWORDS[$instance]}
    local errors=0
    
    log "Validating setup for $instance instance..."
    
    # Check OTEL_MONITOR user
    local otel_count=$(check_user_exists $instance "otel_monitor" | tr -d ' \n')
    if [[ "$otel_count" != "1" ]]; then
        log_error "OTEL_MONITOR user not found in $instance"
        ((errors++))
    else
        log_success "OTEL_MONITOR user exists in $instance"
    fi
    
    # Check TESTUSER
    local test_count=$(check_user_exists $instance "testuser" | tr -d ' \n')
    if [[ "$test_count" != "1" ]]; then
        log_error "TESTUSER not found in $instance"
        ((errors++))
    else
        log_success "TESTUSER exists in $instance"
    fi
    
    # Check employees table
    local table_count=$(check_table_exists $instance "testuser" "employees" | tr -d ' \n')
    if [[ "$table_count" != "1" ]]; then
        log_error "EMPLOYEES table not found in $instance"
        ((errors++))
    else
        log_success "EMPLOYEES table exists in $instance"
    fi
    
    # Test OTEL_MONITOR connectivity
    if docker exec -i $host sqlplus -S otel_monitor/OtelMonitorPassword123@localhost:1521/xepdb1 <<EOF >/dev/null 2>&1
SELECT COUNT(*) FROM v\$session WHERE rownum <= 1;
EXIT;
EOF
    then
        log_success "OTEL_MONITOR can query v\$session in $instance"
    else
        log_error "OTEL_MONITOR cannot query v\$session in $instance"
        ((errors++))
    fi
    
    # Check data count
    local data_count=$(docker exec -i $host sqlplus -S testuser/YourSecurePassword123@localhost:1521/xepdb1 <<EOF 2>/dev/null
SET PAGESIZE 0
SET FEEDBACK OFF
SET VERIFY OFF
SET HEADING OFF
SELECT COUNT(*) FROM employees;
EXIT;
EOF
    )
    data_count=$(echo $data_count | tr -d ' \n')
    
    if [[ "$data_count" -ge "3" ]]; then
        log_success "EMPLOYEES table has $data_count records in $instance"
    else
        log_error "EMPLOYEES table has insufficient data in $instance (found: $data_count)"
        ((errors++))
    fi
    
    return $errors
}

setup_instance() {
    local instance=$1
    local host=${DB_HOSTS[$instance]}
    
    log "Setting up Oracle $instance instance ($host)..."
    
    # Wait for database to be ready
    if ! wait_for_database $instance; then
        return 1
    fi
    
    # Create users and schema
    create_monitoring_user $instance
    create_test_user $instance
    create_test_schema $instance
    
    # Validate setup
    if validate_setup $instance; then
        log_success "Oracle $instance instance setup completed successfully"
        return 0
    else
        log_error "Oracle $instance instance setup validation failed"
        return 1
    fi
}

main() {
    log "Starting Oracle Database Initialization and Validation..."
    log "This script will ensure all Oracle instances have proper schemas and monitoring users"
    
    local total_errors=0
    
    # Check if containers are running
    for instance in "${INSTANCES[@]}"; do
        local host=${DB_HOSTS[$instance]}
        if ! docker ps --format '{{.Names}}' | grep -q "^${host}$"; then
            log_error "Container $host is not running. Please start with: docker compose up -d"
            ((total_errors++))
        fi
    done
    
    if [[ $total_errors -gt 0 ]]; then
        log_error "Some containers are not running. Exiting."
        exit 1
    fi
    
    # Setup each instance
    for instance in "${INSTANCES[@]}"; do
        if ! setup_instance $instance; then
            ((total_errors++))
        fi
        echo ""
    done
    
    # Final validation
    log "Running final validation across all instances..."
    for instance in "${INSTANCES[@]}"; do
        if ! validate_setup $instance >/dev/null; then
            ((total_errors++))
        fi
    done
    
    echo ""
    if [[ $total_errors -eq 0 ]]; then
        log_success "All Oracle instances are properly configured!"
        log_success "OTEL_MONITOR users created with monitoring privileges"
        log_success "TESTUSER created with sample data"
        log_success "All databases ready for monitoring"
        echo ""
        log "You can now access:"
        log "  Frontend: http://localhost:8081"
        log "  Prometheus: http://localhost:9464/metrics"
        log "  API: http://localhost:8000"
    else
        log_error "Setup completed with $total_errors errors"
        log_error "Please check the logs above and retry setup"
        exit 1
    fi
}

# Allow script to be sourced for testing
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi