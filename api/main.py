from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import oracledb
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict
import json

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource

# Configure OpenTelemetry
resource = Resource.create({
    "service.name": "oracle-api",
    "service.version": "1.0.0",
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Configure OTLP exporter to send to OTEL collector
otlp_exporter = OTLPSpanExporter(
    endpoint="http://otel-collector:4317",
    insecure=True
)

span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = FastAPI(title="Oracle Demo API", description="API for triggering Oracle queries from frontend")

# Instrument FastAPI with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Oracle connection settings
ORACLE_HOST = os.getenv("ORACLE_HOST", "oracle-db")
ORACLE_PORT = int(os.getenv("ORACLE_PORT", "1521"))
ORACLE_SID = os.getenv("ORACLE_SID", "XEPDB1")
ORACLE_USER = os.getenv("ORACLE_USER", "testuser")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "testpass")

conn_str = f"{ORACLE_USER}/{ORACLE_PASSWORD}@{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SID}"

def get_oracle_connection():
    """Get Oracle database connection"""
    try:
        return oracledb.connect(conn_str, mode=oracledb.DEFAULT_AUTH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Oracle Demo API - Ready to trigger database queries!"}

@app.get("/api/employees")
async def get_employees(request: Request):
    """Get employees list - triggers SELECT with explain plan"""
    # Extract correlation ID from headers
    correlation_id = request.headers.get("x-correlation-id", f"api-{datetime.now().isoformat()}")
    user_action = request.headers.get("x-user-action", "employees")
    
    # Add correlation ID to current span
    current_span = trace.get_current_span()
    if current_span:
        current_span.set_attribute("correlation.id", correlation_id)
        current_span.set_attribute("user.action", user_action)
        current_span.set_attribute("observability.layer", "api")
        current_span.set_attribute("database.operation", "select")
    
    connection = get_oracle_connection()
    cursor = connection.cursor()
    
    try:
        # Execute query with optimizer hint and correlation ID for tracking
        query = f"""
        SELECT /*+ FULL(e) */ /* CORRELATION_ID={correlation_id} USER_ACTION={user_action} */
            employee_id, 
            first_name, 
            last_name, 
            salary, 
            hire_date 
        FROM employees e 
        ORDER BY salary DESC
        """
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        employees = []
        for row in rows:
            employee = dict(zip(columns, row))
            # Convert datetime to string for JSON serialization
            if employee.get('HIRE_DATE'):
                employee['HIRE_DATE'] = employee['HIRE_DATE'].isoformat()
            employees.append(employee)
        
        # Add correlation tracking to response
        result = {
            "query_type": "employees_list",
            "explain_plan_hint": "FULL table scan with ORDER BY",
            "count": len(employees),
            "employees": employees,
            "correlation_id": correlation_id,
            "observability": {
                "user_action": user_action,
                "sql_executed": True,
                "table": "employees"
            }
        }
        
        # Add response details to span
        if current_span:
            current_span.set_attribute("response.record_count", len(employees))
            current_span.set_attribute("database.table", "employees")
        
        return result
    
    finally:
        cursor.close()
        connection.close()

@app.get("/api/employees/high-salary")
async def get_high_salary_employees(request: Request):
    """Get high salary employees - triggers INDEX scan"""
    # Extract correlation ID from headers
    correlation_id = request.headers.get("x-correlation-id", f"api-{datetime.now().isoformat()}")
    user_action = request.headers.get("x-user-action", "high-salary")
    
    # Add correlation ID to current span
    current_span = trace.get_current_span()
    if current_span:
        current_span.set_attribute("correlation.id", correlation_id)
        current_span.set_attribute("user.action", user_action)
        current_span.set_attribute("observability.layer", "api")
        current_span.set_attribute("database.operation", "select")
    
    connection = get_oracle_connection()
    cursor = connection.cursor()
    
    try:
        query = f"""
        SELECT /*+ INDEX_RS_ASC(e emp_salary_idx) */ /* CORRELATION_ID={correlation_id} USER_ACTION={user_action} */
            employee_id, 
            first_name, 
            last_name, 
            salary 
        FROM employees e 
        WHERE salary > 60000 
        ORDER BY salary DESC
        """
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        employees = [dict(zip(columns, row)) for row in rows]
        
        # Add correlation tracking to response
        result = {
            "query_type": "high_salary_filter",
            "explain_plan_hint": "INDEX range scan on salary",
            "threshold": 60000,
            "count": len(employees),
            "employees": employees,
            "correlation_id": correlation_id,
            "observability": {
                "user_action": user_action,
                "sql_executed": True,
                "table": "employees"
            }
        }
        
        # Add response details to span
        if current_span:
            current_span.set_attribute("response.record_count", len(employees))
            current_span.set_attribute("database.table", "employees")
        
        return result
    
    finally:
        cursor.close()
        connection.close()

@app.get("/api/analytics/salary-stats")
async def get_salary_analytics():
    """Get salary analytics - triggers aggregation with GROUP BY"""
    connection = get_oracle_connection()
    cursor = connection.cursor()
    
    try:
        query = """
        SELECT /*+ FULL(e) */ 
            TRUNC(hire_date, 'MONTH') as hire_month,
            COUNT(*) as employee_count,
            AVG(salary) as avg_salary,
            MIN(salary) as min_salary,
            MAX(salary) as max_salary
        FROM employees e
        GROUP BY TRUNC(hire_date, 'MONTH')
        ORDER BY hire_month DESC
        """
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        analytics = []
        for row in rows:
            record = dict(zip(columns, row))
            # Convert datetime to string
            if record.get('HIRE_MONTH'):
                record['HIRE_MONTH'] = record['HIRE_MONTH'].isoformat()
            # Round salary values
            if record.get('AVG_SALARY'):
                record['AVG_SALARY'] = round(float(record['AVG_SALARY']), 2)
            analytics.append(record)
        
        return {
            "query_type": "salary_analytics",
            "explain_plan_hint": "FULL scan with GROUP BY aggregation",
            "analytics": analytics
        }
    
    finally:
        cursor.close()
        connection.close()

@app.post("/api/employees")
async def create_employee(employee_data: dict):
    """Create new employee - triggers INSERT with possible index updates"""
    connection = get_oracle_connection()
    cursor = connection.cursor()
    
    try:
        # Generate new employee data
        new_id = random.randint(2000, 9999)
        first_names = ['Alex', 'Jordan', 'Casey', 'Taylor', 'Morgan', 'Riley']
        last_names = ['Johnson', 'Williams', 'Brown', 'Davis', 'Miller', 'Wilson']
        
        first_name = employee_data.get('first_name', random.choice(first_names))
        last_name = employee_data.get('last_name', random.choice(last_names))
        salary = employee_data.get('salary', random.uniform(50000, 90000))
        hire_date = datetime.now()
        
        insert_query = """
        INSERT INTO employees (employee_id, first_name, last_name, salary, hire_date)
        VALUES (:1, :2, :3, :4, :5)
        """
        
        cursor.execute(insert_query, (new_id, first_name, last_name, salary, hire_date))
        connection.commit()
        
        return {
            "query_type": "employee_insert",
            "explain_plan_hint": "INSERT with index maintenance",
            "employee": {
                "employee_id": new_id,
                "first_name": first_name,
                "last_name": last_name,
                "salary": round(salary, 2),
                "hire_date": hire_date.isoformat()
            }
        }
    
    finally:
        cursor.close()
        connection.close()

@app.get("/api/complex-query")
async def run_complex_query():
    """Run complex query - triggers self-join with multiple operations"""
    connection = get_oracle_connection()
    cursor = connection.cursor()
    
    try:
        query = """
        SELECT /*+ USE_NL(e1 e2) */ 
            e1.employee_id,
            e1.first_name || ' ' || e1.last_name as employee_name,
            e1.salary as employee_salary,
            COUNT(e2.employee_id) as higher_paid_colleagues
        FROM employees e1
        LEFT JOIN employees e2 ON e2.salary > e1.salary
        WHERE e1.salary > 50000
        GROUP BY e1.employee_id, e1.first_name, e1.last_name, e1.salary
        ORDER BY e1.salary DESC
        """
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        results = [dict(zip(columns, row)) for row in rows]
        
        return {
            "query_type": "complex_self_join",
            "explain_plan_hint": "Nested loops self-join with aggregation",
            "description": "Shows each employee and count of colleagues earning more",
            "results": results
        }
    
    finally:
        cursor.close()
        connection.close()

@app.get("/api/slow-query")
async def run_slow_query():
    """Run intentionally slow query for performance testing"""
    connection = get_oracle_connection()
    cursor = connection.cursor()
    
    try:
        # Cross join to create a slow query
        query = """
        SELECT /*+ NO_INDEX(e1) NO_INDEX(e2) */ 
            COUNT(*) as cartesian_count
        FROM employees e1, employees e2
        WHERE e1.salary + e2.salary > 100000
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        return {
            "query_type": "slow_cartesian_product",
            "explain_plan_hint": "Cartesian product without indexes",
            "warning": "This query intentionally generates heavy load",
            "result": {"cartesian_count": result[0] if result else 0}
        }
    
    finally:
        cursor.close()
        connection.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        connection = get_oracle_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        cursor.close()
        connection.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}