-- Connect to the pluggable database (required for Oracle XE)
ALTER SESSION SET CONTAINER = xepdb1;

-- Ensure we're in the correct container
SHOW CON_NAME;

-- Drop existing monitoring user if exists (for clean restarts)
BEGIN
    EXECUTE IMMEDIATE 'DROP USER otel_monitor CASCADE';
    DBMS_OUTPUT.PUT_LINE('Dropped existing otel_monitor user');
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE = -1918 THEN  -- ORA-01918: user does not exist
            DBMS_OUTPUT.PUT_LINE('otel_monitor user does not exist, proceeding...');
        ELSE
            DBMS_OUTPUT.PUT_LINE('Error dropping otel_monitor: ' || SQLERRM);
            RAISE;
        END IF;
END;
/

-- Create monitoring user for OpenTelemetry Collector
-- Using consistent password across all Oracle instances
CREATE USER otel_monitor IDENTIFIED BY "OtelMonitorPassword123";

-- Grant basic connection privileges
GRANT CREATE SESSION TO otel_monitor;

-- Grant access to session and SQL monitoring views
GRANT SELECT ON V_$SESSION TO otel_monitor;
GRANT SELECT ON V_$SQL TO otel_monitor;
GRANT SELECT ON V_$SQL_PLAN TO otel_monitor;
GRANT SELECT ON V_$SQL_PLAN_STATISTICS_ALL TO otel_monitor;
GRANT SELECT ON V_$SQL_MONITOR TO otel_monitor;

-- Grant access to system statistics and performance views
GRANT SELECT ON V_$SYSSTAT TO otel_monitor;
GRANT SELECT ON V_$OSSTAT TO otel_monitor;
GRANT SELECT ON V_$SGA TO otel_monitor;
GRANT SELECT ON V_$PGASTAT TO otel_monitor;
GRANT SELECT ON V_$SYSTEM_EVENT TO otel_monitor;
GRANT SELECT ON V_$LIBRARYCACHE TO otel_monitor;
GRANT SELECT ON V_$SGASTAT TO otel_monitor;

-- Grant access to storage and tablespace views
GRANT SELECT ON DBA_DATA_FILES TO otel_monitor;
GRANT SELECT ON DBA_FREE_SPACE TO otel_monitor;

-- Verify user creation
SELECT username, account_status FROM dba_users WHERE username = 'OTEL_MONITOR';

-- Create testuser if it doesn't exist (ensures consistency across all instances)
BEGIN
    EXECUTE IMMEDIATE 'DROP USER testuser CASCADE';
    DBMS_OUTPUT.PUT_LINE('Dropped existing testuser');
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE = -1918 THEN  -- ORA-01918: user does not exist
            DBMS_OUTPUT.PUT_LINE('testuser does not exist, proceeding...');
        ELSE
            DBMS_OUTPUT.PUT_LINE('Error dropping testuser: ' || SQLERRM);
        END IF;
END;
/

-- Create testuser
BEGIN
    EXECUTE IMMEDIATE 'CREATE USER testuser IDENTIFIED BY "YourSecurePassword123" DEFAULT TABLESPACE USERS TEMPORARY TABLESPACE TEMP';
    DBMS_OUTPUT.PUT_LINE('Created testuser successfully');
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Error creating testuser: ' || SQLERRM);
        RAISE;
END;
/

-- Grant privileges for testuser to use DBMS_SESSION and correlation context
GRANT CREATE SESSION TO testuser;
GRANT CONNECT, RESOURCE TO testuser;
GRANT UNLIMITED TABLESPACE TO testuser;
GRANT EXECUTE ON DBMS_SESSION TO testuser;
GRANT EXECUTE ON DBMS_APPLICATION_INFO TO testuser;
GRANT SELECT ON V_$SESSION TO testuser;
GRANT SELECT ON V_$SQL TO testuser;

-- Final verification
SELECT 'SETUP COMPLETE - Users created:' AS status FROM dual;
SELECT username, account_status FROM dba_users WHERE username IN ('OTEL_MONITOR', 'TESTUSER');

-- Commit all changes
COMMIT;

-- Output completion message
BEGIN
    DBMS_OUTPUT.PUT_LINE('=================================');
    DBMS_OUTPUT.PUT_LINE('Oracle setup.sql completed successfully');
    DBMS_OUTPUT.PUT_LINE('OTEL_MONITOR and TESTUSER created');
    DBMS_OUTPUT.PUT_LINE('All privileges granted');
    DBMS_OUTPUT.PUT_LINE('=================================');
END;
/
