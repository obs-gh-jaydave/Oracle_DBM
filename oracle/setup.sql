ALTER SESSION SET CONTAINER = XEPDB1;

-- Create monitoring user
CREATE USER otel_monitor IDENTIFIED BY "YourSecurePassword123";

GRANT CREATE SESSION TO otel_monitor;

GRANT SELECT ON V_$SESSION TO otel_monitor;
GRANT SELECT ON V_$SQL TO otel_monitor;
GRANT SELECT ON V_$SQL_PLAN TO otel_monitor;
GRANT SELECT ON V_$SQL_PLAN_STATISTICS_ALL TO otel_monitor;
GRANT SELECT ON V_$SQL_MONITOR TO otel_monitor;

-- Additional grants for metrics
GRANT SELECT ON V_$SYSSTAT TO otel_monitor;
GRANT SELECT ON V_$OSSTAT TO otel_monitor;
GRANT SELECT ON V_$SGA TO otel_monitor;
GRANT SELECT ON V_$PGASTAT TO otel_monitor;
GRANT SELECT ON V_$SYSTEM_EVENT TO otel_monitor;
GRANT SELECT ON DBA_DATA_FILES TO otel_monitor;
GRANT SELECT ON DBA_FREE_SPACE TO otel_monitor;
GRANT SELECT ON V_$LIBRARYCACHE TO otel_monitor;
GRANT SELECT ON V_$SGASTAT TO otel_monitor;

-- Grant privileges for testuser to use DBMS_SESSION and correlation context
GRANT EXECUTE ON DBMS_SESSION TO testuser;
GRANT EXECUTE ON DBMS_APPLICATION_INFO TO testuser;

-- Grant testuser access to system views needed for correlation tracking
GRANT SELECT ON V_$SESSION TO testuser;
GRANT SELECT ON V_$SQL TO testuser;
