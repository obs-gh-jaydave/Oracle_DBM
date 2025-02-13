ALTER SESSION SET CONTAINER = XEPDB1;

-- Drop existing user if exists (to allow clean restarts)
BEGIN
    EXECUTE IMMEDIATE 'DROP USER testuser CASCADE';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -1918 THEN  -- ORA-01918: user does not exist
            RAISE;
        END IF;
END;
/

-- Create the testuser with proper privileges
CREATE USER testuser IDENTIFIED BY "testpass"
    DEFAULT TABLESPACE USERS
    TEMPORARY TABLESPACE TEMP;

-- Grant necessary privileges
GRANT CREATE SESSION TO testuser;
GRANT CONNECT, RESOURCE TO testuser;
GRANT UNLIMITED TABLESPACE TO testuser;

-- Switch to testuser schema
ALTER SESSION SET CURRENT_SCHEMA = testuser;

-- Create the employees table
CREATE TABLE employees (
    employee_id    NUMBER(6),
    first_name     VARCHAR2(20),
    last_name      VARCHAR2(25),
    salary         NUMBER(8,2),
    hire_date      DATE
);

-- Insert initial data
INSERT INTO employees VALUES (1001, 'John', 'Doe', 60000, SYSDATE - 100);
INSERT INTO employees VALUES (1002, 'Jane', 'Smith', 65000, SYSDATE - 200);
INSERT INTO employees VALUES (1003, 'Alice', 'Johnson', 75000, SYSDATE - 300);

-- Ensure changes are committed
COMMIT;

-- Create an index to support our queries
CREATE INDEX emp_salary_idx ON employees(salary);
CREATE INDEX emp_hire_date_idx ON employees(hire_date);