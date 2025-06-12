ALTER SESSION SET CONTAINER = XEPDB1;

-- Show current container for verification
SHOW CON_NAME;

-- Note: TESTUSER should already exist from setup.sql
-- This script focuses on creating the schema objects
-- Verify testuser exists
BEGIN
    DECLARE
        user_count NUMBER;
    BEGIN
        SELECT COUNT(*) INTO user_count FROM dba_users WHERE username = 'TESTUSER';
        IF user_count = 0 THEN
            DBMS_OUTPUT.PUT_LINE('ERROR: TESTUSER does not exist! Run setup.sql first.');
            RAISE_APPLICATION_ERROR(-20001, 'TESTUSER not found');
        ELSE
            DBMS_OUTPUT.PUT_LINE('TESTUSER exists, proceeding with schema creation...');
        END IF;
    END;
END;
/

-- Switch to testuser schema
ALTER SESSION SET CURRENT_SCHEMA = testuser;

-- Create the employees table (drop first if exists for clean restarts)
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE employees CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -942 THEN  -- ORA-00942: table or view does not exist
            RAISE;
        END IF;
END;
/

-- Create the employees table
CREATE TABLE employees (
    employee_id    NUMBER(6),
    first_name     VARCHAR2(20),
    last_name      VARCHAR2(25),
    salary         NUMBER(8,2),
    hire_date      DATE
);

-- Insert initial data with error handling
BEGIN
    INSERT INTO employees VALUES (1001, 'John', 'Doe', 60000, SYSDATE - 100);
    INSERT INTO employees VALUES (1002, 'Jane', 'Smith', 65000, SYSDATE - 200);
    INSERT INTO employees VALUES (1003, 'Alice', 'Johnson', 75000, SYSDATE - 300);
    
    -- Add more sample data for better load testing
    INSERT INTO employees VALUES (2001, 'Bob', 'Wilson', 55000, SYSDATE - 50);
    INSERT INTO employees VALUES (2002, 'Carol', 'Brown', 70000, SYSDATE - 150);
    INSERT INTO employees VALUES (2003, 'David', 'Miller', 80000, SYSDATE - 250);
    INSERT INTO employees VALUES (2004, 'Emma', 'Davis', 65000, SYSDATE - 75);
    INSERT INTO employees VALUES (2005, 'Frank', 'Garcia', 72000, SYSDATE - 125);
    INSERT INTO employees VALUES (2006, 'Grace', 'Rodriguez', 68000, SYSDATE - 175);
    INSERT INTO employees VALUES (2007, 'Henry', 'Martinez', 85000, SYSDATE - 225);
    
    DBMS_OUTPUT.PUT_LINE('Inserted ' || SQL%ROWCOUNT || ' employee records');
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Error inserting data: ' || SQLERRM);
        RAISE;
END;
/

-- Ensure changes are committed
COMMIT;

-- Create an index to support our queries
CREATE INDEX emp_salary_idx ON employees(salary);
CREATE INDEX emp_hire_date_idx ON employees(hire_date);

-- Create Oracle context for OpenTelemetry correlation tracking
CREATE OR REPLACE CONTEXT OTEL_CTX USING DBMS_SESSION ACCESSED GLOBALLY;

-- Grant additional privileges for OpenTelemetry correlation tracking
-- (These may have been attempted in setup.sql but testuser didn't exist yet)
GRANT EXECUTE ON DBMS_SESSION TO testuser;
GRANT EXECUTE ON DBMS_APPLICATION_INFO TO testuser;
GRANT SELECT ON V_$SESSION TO testuser;
GRANT SELECT ON V_$SQL TO testuser;

-- Verify all grants were successful
SELECT grantee, privilege, table_name 
FROM dba_tab_privs 
WHERE grantee = 'TESTUSER' 
  AND table_name IN ('V_$SESSION', 'V_$SQL')
ORDER BY table_name;

-- Final verification and completion message
BEGIN
    DECLARE
        emp_count NUMBER;
    BEGIN
        SELECT COUNT(*) INTO emp_count FROM employees;
        DBMS_OUTPUT.PUT_LINE('=================================');
        DBMS_OUTPUT.PUT_LINE('Schema creation completed successfully');
        DBMS_OUTPUT.PUT_LINE('EMPLOYEES table created with ' || emp_count || ' records');
        DBMS_OUTPUT.PUT_LINE('Indexes created: emp_salary_idx, emp_hire_date_idx');
        DBMS_OUTPUT.PUT_LINE('OTEL context created');
        DBMS_OUTPUT.PUT_LINE('Database ready for monitoring');
        DBMS_OUTPUT.PUT_LINE('=================================');
    END;
END;
/