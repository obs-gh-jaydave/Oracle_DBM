import oracledb
import time
import os
import random
from datetime import datetime, timedelta

host = os.getenv("ORACLE_HOST", "oracle-db")
port = int(os.getenv("ORACLE_PORT", "1521"))
sid  = os.getenv("ORACLE_SID", "XEPDB1")
user = os.getenv("ORACLE_USER", "testuser")
pwd  = os.getenv("ORACLE_PASSWORD", "testpass")

# Build the DSN (connect string) for 'thin' mode:
conn_str = f"{user}/{pwd}@{host}:{port}/{sid}"

def wait_for_connection():
    """Keep retrying until we can connect to the database."""
    while True:
        try:
            print("Attempting to connect to Oracle...")
            conn = oracledb.connect(conn_str, mode=oracledb.DEFAULT_AUTH)
            print("Connected to Oracle!")
            return conn
        except oracledb.OperationalError as ex:
            err_msg = str(ex)
            if "ORA-01033" in err_msg:
                print("DB is still initializing (ORA-01033). Will retry in 5s...")
            elif "ORA-12514" in err_msg or "ORA-12541" in err_msg or "ORA-12543" in err_msg:
                print("Listener or service not ready. Will retry in 5s...")
            else:
                print(f"Got an OperationalError: {err_msg}")
            time.sleep(5)
        except Exception as ex:
            print(f"Unexpected exception: {ex}, retrying in 5s...")
            time.sleep(5)

def generate_load(cursor):
    """Execute various types of queries to generate different explain plans"""
    queries = [
        # Full table scan with sorting
        """
        SELECT /*+ FULL(e) */ *
        FROM employees e
        ORDER BY salary DESC
        """,
        
        # Range scan with filtering
        """
        SELECT /*+ INDEX_RS_ASC(e) */ *
        FROM employees e
        WHERE salary BETWEEN 50000 AND 80000
        """,
        
        # Aggregation with grouping
        """
        SELECT /*+ FULL(e) */ 
            TRUNC(hire_date, 'MONTH') as hire_month,
            AVG(salary) as avg_salary,
            COUNT(*) as employee_count
        FROM employees e
        GROUP BY TRUNC(hire_date, 'MONTH')
        HAVING COUNT(*) > 0
        """,
        
        # Complex filtering with multiple conditions
        """
        SELECT /*+ FULL(e) */ *
        FROM employees e
        WHERE (salary > 65000 OR hire_date < SYSDATE - 200)
        AND last_name LIKE 'S%'
        """,
        
        # Self-join query
        """
        SELECT /*+ USE_NL(e1 e2) */ 
            e1.employee_id, 
            e1.first_name,
            e1.salary,
            e2.salary as colleague_salary
        FROM employees e1
        JOIN employees e2 ON e1.salary < e2.salary
        WHERE e1.salary > 50000
        """
    ]
    
    try:
        # Execute a random query
        query = random.choice(queries)
        print(f"\nExecuting query:\n{query.strip()}")
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"Query returned {len(results)} rows")
        
        # Sometimes insert new data to keep the table growing
        if random.random() < 0.2:  # 20% chance
            new_id = random.randint(1004, 9999)
            first_names = ['Michael', 'Sarah', 'David', 'Lisa', 'Robert', 'Emma']
            last_names = ['Brown', 'Wilson', 'Taylor', 'Anderson', 'Thomas']
            salary = random.uniform(50000, 90000)
            hire_date = datetime.now() - timedelta(days=random.randint(0, 365))
            
            insert_query = """
            INSERT INTO employees (employee_id, first_name, last_name, salary, hire_date)
            VALUES (:1, :2, :3, :4, :5)
            """
            cursor.execute(insert_query, 
                         (new_id, 
                          random.choice(first_names),
                          random.choice(last_names),
                          salary,
                          hire_date))
            cursor.execute("COMMIT")
            print(f"Inserted new employee with ID {new_id}")
            
    except Exception as e:
        print(f"Error executing query: {e}")

def main():
    connection = wait_for_connection()
    cursor = connection.cursor()
    
    print("Starting enhanced load generator...")
    
    while True:
        generate_load(cursor)
        # Random sleep between 2-5 seconds
        sleep_time = random.uniform(2, 5)
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()