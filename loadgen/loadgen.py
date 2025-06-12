import requests
import time
import os
import random
import json
import uuid
from datetime import datetime, timedelta
from urllib.parse import urljoin

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")

# Load generation configuration
MIN_SLEEP = float(os.getenv("LOADGEN_MIN_SLEEP", "2"))
MAX_SLEEP = float(os.getenv("LOADGEN_MAX_SLEEP", "8"))
ENABLE_MULTI_INSTANCE_LOAD = os.getenv("ENABLE_MULTI_INSTANCE_LOAD", "true").lower() == "true"

# Multi-instance load distribution for production-like scenarios
ORACLE_INSTANCE_WEIGHTS = {
    'primary': {
        'weight': 0.5,  # 50% - OLTP workload
        'workload_types': ['transactional', 'lookup', 'crud'],
        'max_concurrent': 15
    },
    'secondary': {
        'weight': 0.3,  # 30% - Analytics workload  
        'workload_types': ['analytics', 'aggregation', 'reporting'],
        'max_concurrent': 8
    },
    'legacy': {
        'weight': 0.2,  # 20% - Legacy/batch workload
        'workload_types': ['batch', 'complex', 'maintenance'],
        'max_concurrent': 5
    }
}

def wait_for_services():
    """Wait for API service to be ready"""
    services = [
        ("API", API_BASE_URL + "/health")
    ]
    
    for service_name, url in services:
        while True:
            try:
                print(f"[STARTUP] Checking {service_name} at {url}...")
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"[OK] {service_name} is ready!")
                    break
                else:
                    print(f"[ERROR] {service_name} returned {response.status_code}, retrying in 5s...")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] {service_name} not ready ({e}), retrying in 5s...")
            time.sleep(5)
    
    print("[INFO] API service ready! Starting database load generation...")

class DatabaseLoadGenerator:
    """Generates realistic database load across multiple Oracle instances"""
    
    def __init__(self):
        self.session = requests.Session()
        # Set headers to simulate API client
        self.session.headers.update({
            'User-Agent': 'Oracle-Database-LoadGen/2.0',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        })
        
    def generate_correlation_id(self):
        """Generate a unique correlation ID for database operations"""
        trace_id = uuid.uuid4().hex[:16]  # 16 chars for trace
        span_id = uuid.uuid4().hex[:8]    # 8 chars for span
        return f"loadgen-{trace_id}-{span_id}"
    
    def execute_database_operation(self, endpoint, operation_type, target_instance="primary", workload_category="transactional"):
        """Execute a database operation through the API"""
        correlation_id = self.generate_correlation_id()
        
        print(f"[DATABASE] Executing {operation_type} operation on {target_instance} instance")
        print(f"[CORRELATION] Generated correlation ID: {correlation_id}")
        
        # Make direct API call to trigger database operation
        api_url = urljoin(API_BASE_URL, endpoint)
        
        # Set operation context headers
        headers = {
            'X-Database-Operation': operation_type,
            'X-Correlation-ID': correlation_id,
            'X-Target-Instance': target_instance,
            'Content-Type': 'application/json',
            # OpenTelemetry trace context for correlation
            'traceparent': f"00-{uuid.uuid4().hex}-{uuid.uuid4().hex[:16]}-01"
        }
        
        try:
            print(f"[API] Calling {endpoint} -> {target_instance} database")
            
            start_time = time.time()
            response = self.session.get(api_url, headers=headers, timeout=15)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                record_count = data.get('count', 0)
                query_type = data.get('query_type', 'unknown')
                explain_plan = data.get('explain_plan_hint', 'N/A')
                
                print(f"[SUCCESS] Database operation completed: {query_type}")
                print(f"[DATA] Records processed: {record_count}")
                print(f"[PLAN] Execution plan: {explain_plan}")
                print(f"[PERF] Response time: {duration:.3f}s")
                print(f"[FLOW] Load Generator -> API -> {target_instance.upper()} Oracle -> OTEL Collector")
                
                # Verify correlation is present in response
                returned_correlation = data.get('correlation_id')
                if returned_correlation:
                    print(f"[CORRELATION] Correlation preserved: {returned_correlation}")
                else:
                    print("[WARNING] Correlation ID not found in response")
                
                return {
                    'success': True,
                    'correlation_id': correlation_id,
                    'query_type': query_type,
                    'record_count': record_count,
                    'duration': duration,
                    'explain_plan': explain_plan,
                    'target_instance': target_instance
                }
            else:
                print(f"[ERROR] Database operation failed: {response.status_code} - {response.text}")
                return {'success': False, 'correlation_id': correlation_id, 'error': response.status_code, 'target_instance': target_instance}
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            return {'success': False, 'correlation_id': correlation_id, 'error': str(e), 'target_instance': target_instance}

def select_target_instance_for_workload(workload_category):
    """Select optimal Oracle instance based on workload category"""
    # Direct mapping for certain workload types
    workload_to_instance = {
        'transactional': 'primary',
        'lookup': 'primary', 
        'crud': 'primary',
        'analytics': 'secondary',
        'aggregation': 'secondary',
        'reporting': 'secondary',
        'batch': 'legacy',
        'complex': 'legacy',
        'maintenance': 'legacy'
    }
    
    preferred_instance = workload_to_instance.get(workload_category, 'primary')
    
    # Add some randomization to simulate real-world load balancing
    if ENABLE_MULTI_INSTANCE_LOAD:
        # 80% chance to use preferred instance, 20% chance to distribute load
        if random.random() < 0.8:
            return preferred_instance
        else:
            # Weighted random selection across all instances
            rand_val = random.random()
            cumulative_weight = 0
            for instance, config in ORACLE_INSTANCE_WEIGHTS.items():
                cumulative_weight += config['weight']
                if rand_val <= cumulative_weight:
                    return instance
    
    return preferred_instance

def generate_realistic_load():
    """Generate realistic database load across multiple Oracle instances with appropriate workload distribution"""
    
    # Realistic database operations with workload categorization
    database_operations = [
        {
            'endpoint': '/api/employees',
            'operation_type': 'full-table-scan',
            'workload_category': 'lookup',
            'weight': 25,
            'description': 'Employee list retrieval (OLTP - Primary)',
            'category': 'read',
            'preferred_instance': 'primary'
        },
        {
            'endpoint': '/api/employees/high-salary',
            'operation_type': 'index-range-scan', 
            'workload_category': 'transactional',
            'weight': 30,
            'description': 'High salary filter (OLTP - Primary)',
            'category': 'read',
            'preferred_instance': 'primary'
        },
        {
            'endpoint': '/api/analytics/salary-stats',
            'operation_type': 'aggregation-query',
            'workload_category': 'analytics',
            'weight': 20,
            'description': 'Salary analytics (Analytics - Secondary)',
            'category': 'read',
            'preferred_instance': 'secondary'
        },
        {
            'endpoint': '/api/complex-query',
            'operation_type': 'complex-join',
            'workload_category': 'complex',
            'weight': 15,
            'description': 'Complex analysis (Batch - Legacy)',
            'category': 'read',
            'preferred_instance': 'legacy'
        },
        {
            'endpoint': '/api/slow-query',
            'operation_type': 'performance-test',
            'workload_category': 'batch',
            'weight': 10,
            'description': 'Performance stress test (Batch - Legacy)',
            'category': 'read',
            'preferred_instance': 'legacy'
        }
    ]
    
    # Sometimes add INSERT operations (15% chance)
    if random.random() < 0.15:
        database_operations.append({
            'endpoint': '/api/employees',
            'operation_type': 'insert-operation',
            'workload_category': 'crud',
            'weight': 10,
            'description': 'Employee creation (CRUD - Primary)',
            'category': 'write',
            'method': 'POST',
            'preferred_instance': 'primary'
        })
    
    # Select operation based on weights
    total_weight = sum(operation['weight'] for operation in database_operations)
    random_weight = random.randint(1, total_weight)
    
    current_weight = 0
    selected_operation = None
    for operation in database_operations:
        current_weight += operation['weight']
        if random_weight <= current_weight:
            selected_operation = operation
            break
    
    if not selected_operation:
        selected_operation = database_operations[0]  # Fallback
    
    # Determine optimal target instance based on workload
    target_instance = select_target_instance_for_workload(selected_operation['workload_category'])
    
    print(f"\n{'='*80}")
    print(f"[SCENARIO] {selected_operation['description']}")
    print(f"[WORKLOAD] {selected_operation['workload_category'].upper()} -> {target_instance.upper()} instance")
    print(f"[CATEGORY] {selected_operation['category'].upper()} operation")
    print(f"[ROUTING] Workload-optimized routing: {selected_operation['preferred_instance']} -> {target_instance}")
    print(f"{'='*80}")
    
    load_generator = DatabaseLoadGenerator()
    
    # Handle POST requests differently
    if selected_operation.get('method') == 'POST':
        return simulate_employee_creation(load_generator, target_instance, selected_operation['workload_category'])
    else:
        return load_generator.execute_database_operation(
            selected_operation['endpoint'],
            selected_operation['operation_type'],
            target_instance,
            selected_operation['workload_category']
        )

def simulate_employee_creation(load_generator, target_instance, workload_category="crud"):
    """Simulate creating a new employee through the API"""
    correlation_id = load_generator.generate_correlation_id()
    
    print(f"[DATABASE] Executing INSERT operation on {target_instance} instance")
    print(f"[WORKLOAD] Category: {workload_category}")
    print(f"[CORRELATION] Generated correlation ID: {correlation_id}")
    
    # Generate realistic employee data
    first_names = ['Alex', 'Jordan', 'Casey', 'Taylor', 'Morgan', 'Riley', 'Cameron', 'Avery']
    last_names = ['Johnson', 'Williams', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Garcia']
    
    employee_data = {
        'first_name': random.choice(first_names),
        'last_name': random.choice(last_names),
        'salary': round(random.uniform(50000, 95000), 2)
    }
    
    api_url = urljoin(API_BASE_URL, '/api/employees')
    headers = {
        'X-Database-Operation': 'insert-operation',
        'X-Correlation-ID': correlation_id,
        'X-Target-Instance': target_instance,
        'X-Workload-Category': workload_category,
        'X-User-Action': 'employee-create',
        'Content-Type': 'application/json',
        'traceparent': f"00-{uuid.uuid4().hex}-{uuid.uuid4().hex[:16]}-01"
    }
    
    try:
        print(f"[INSERT] Creating employee: {employee_data['first_name']} {employee_data['last_name']} -> {target_instance.upper()} database ({workload_category})")
        
        start_time = time.time()
        response = load_generator.session.post(api_url, json=employee_data, headers=headers, timeout=15)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            employee = data.get('employee', {})
            
            print(f"[SUCCESS] Employee created successfully in {target_instance.upper()} database!")
            print(f"[EMPLOYEE] Employee: {employee.get('first_name')} {employee.get('last_name')} (ID: {employee.get('employee_id')})")
            print(f"[SALARY] Salary: ${employee.get('salary', 0):,.2f}")
            print(f"[PERF] Response time: {duration:.3f}s")
            print(f"[FLOW] Load Generator -> API -> {target_instance.upper()} Oracle ({workload_category}) -> OTEL Collector")
            print(f"[INSTANCE] {target_instance} optimized for {ORACLE_INSTANCE_WEIGHTS[target_instance]['workload_types']}")
            
            return {
                'success': True,
                'correlation_id': correlation_id,
                'query_type': 'employee_insert',
                'duration': duration,
                'employee': employee,
                'target_instance': target_instance
            }
        else:
            print(f"[ERROR] Employee creation failed: {response.status_code} - {response.text}")
            return {'success': False, 'correlation_id': correlation_id, 'error': response.status_code, 'target_instance': target_instance}
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return {'success': False, 'correlation_id': correlation_id, 'error': str(e), 'target_instance': target_instance}

def print_statistics(stats):
    """Print load generation statistics"""
    total_requests = stats['success'] + stats['errors']
    success_rate = (stats['success'] / total_requests * 100) if total_requests > 0 else 0
    avg_duration = (stats['total_duration'] / stats['success']) if stats['success'] > 0 else 0
    
    print(f"\n[STATS] Database Load Generation Statistics:")
    print(f"   Total operations: {total_requests}")
    print(f"   Successful: {stats['success']} ({success_rate:.1f}%)")
    print(f"   Errors: {stats['errors']}")
    print(f"   Average response time: {avg_duration:.3f}s")
    print(f"   Query types: {dict(stats['query_types'])}")
    print(f"   Instance distribution: {dict(stats['instance_distribution'])}")
    print(f"   Correlations generated: {len(stats['correlations'])}")

def main():
    print("[INFO] Starting Multi-Instance Oracle Database Load Generator")
    print("=" * 70)
    print("This load generator creates realistic database workload across:")
    print("- Multiple Oracle database instances (Primary/Secondary)")
    print("- Various operation types (SELECT, INSERT, aggregations)")
    print("- Weighted load distribution with correlation tracking")
    print("- End-to-end correlation: Load Generator -> API -> Oracle -> OTEL")
    print(f"- Load distribution: Primary: {int(ORACLE_INSTANCE_WEIGHTS['primary']['weight'] * 100)}%, Secondary: {int(ORACLE_INSTANCE_WEIGHTS['secondary']['weight'] * 100)}%, Legacy: {int(ORACLE_INSTANCE_WEIGHTS['legacy']['weight'] * 100)}%")
    print("=" * 70)
    
    # Wait for all services to be ready
    wait_for_services()
    
    # Initialize statistics
    stats = {
        'success': 0,
        'errors': 0,
        'total_duration': 0,
        'query_types': {},
        'instance_distribution': {'primary': 0, 'secondary': 0, 'legacy': 0},
        'correlations': set()
    }
    
    operation_count = 0
    
    try:
        while True:
            operation_count += 1
            
            # Generate realistic database load
            result = generate_realistic_load()
            
            # Update statistics
            if result['success']:
                stats['success'] += 1
                stats['total_duration'] += result.get('duration', 0)
                
                query_type = result.get('query_type', 'unknown')
                stats['query_types'][query_type] = stats['query_types'].get(query_type, 0) + 1
                stats['correlations'].add(result['correlation_id'])
                
                # Track instance distribution
                target_instance = result.get('target_instance', 'unknown')
                if target_instance in stats['instance_distribution']:
                    stats['instance_distribution'][target_instance] += 1
                
                print(f"[COUNTER] Total successful operations: {stats['success']}")
            else:
                stats['errors'] += 1
                # Track failed instance distribution
                target_instance = result.get('target_instance', 'unknown')
                if target_instance in stats['instance_distribution']:
                    # Don't count failed operations in instance distribution
                    pass
                print(f"[COUNTER] Total errors: {stats['errors']}")
            
            # Print statistics every 10 operations
            if operation_count % 10 == 0:
                print_statistics(stats)
            
            # Random sleep between operations (realistic database load)
            sleep_time = random.uniform(MIN_SLEEP, MAX_SLEEP)
            print(f"[WAIT] Waiting {sleep_time:.1f}s before next operation...")
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print(f"\n[STOP] Load generation stopped by user")
        print_statistics(stats)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        print_statistics(stats)

if __name__ == "__main__":
    main()