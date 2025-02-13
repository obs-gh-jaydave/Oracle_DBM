ALTER SESSION SET CONTAINER = XEPDB1;

-- Create monitoring user
CREATE USER otel_monitor IDENTIFIED BY "YourSecurePassword123";

GRANT CREATE SESSION TO otel_monitor;

GRANT SELECT ON V_$SESSION TO otel_monitor;
GRANT SELECT ON V_$SQL TO otel_monitor;
GRANT SELECT ON V_$SQL_PLAN TO otel_monitor;

GRANT SELECT ON V_$SQL_PLAN_STATISTICS_ALL TO otel_monitor;
GRANT SELECT ON V_$SQL_MONITOR TO otel_monitor;
