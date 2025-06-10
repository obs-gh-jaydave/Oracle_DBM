import requests
import time
import os
import random
import json
import uuid
from datetime import datetime, timedelta
from urllib.parse import urljoin

# API and Frontend configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://frontend-observability:80")

# Load generation configuration
MIN_SLEEP = float(os.getenv("LOADGEN_MIN_SLEEP", "2"))
MAX_SLEEP = float(os.getenv("LOADGEN_MAX_SLEEP", "8"))
ENABLE_FRONTEND_SIMULATION = os.getenv("ENABLE_FRONTEND_SIMULATION", "true").lower() == "true"

def wait_for_services():
    """Wait for API and frontend services to be ready"""
    services = [
        ("API", API_BASE_URL + "/health"),
        ("Frontend", FRONTEND_BASE_URL)
    ]
    
    for service_name, url in services:
        while True:
            try:
                print(f"Checking {service_name} at {url}...")
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"[OK] {service_name} is ready!")
                    break
                else:
                    print(f"[ERROR] {service_name} returned {response.status_code}, retrying in 5s...")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] {service_name} not ready ({e}), retrying in 5s...")
            time.sleep(5)
    
    print("[INFO] All services are ready! Starting load generation...")

class RUMSimulator:
    """Simulates Real User Monitoring (RUM) interactions"""
    
    def __init__(self):
        self.session = requests.Session()
        # Set headers to simulate a real browser with RUM SDK
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Oracle-LoadGen/1.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
    def generate_correlation_id(self):
        """Generate a RUM-style correlation ID"""
        # Simulate what the RUM SDK would generate
        trace_id = uuid.uuid4().hex[:12]  # 12 chars like RUM trace
        span_id = uuid.uuid4().hex[:8]    # 8 chars like RUM span
        return f"rum-{trace_id}-{span_id}"
    
    def simulate_frontend_interaction(self, endpoint, user_action):
        """Simulate a user interaction through the frontend that triggers API calls"""
        correlation_id = self.generate_correlation_id()
        
        print(f"[USER] Simulating user action: {user_action}")
        print(f"[CORRELATION] Generated correlation ID: {correlation_id}")
        
        # Step 1: Simulate frontend page load/interaction
        if ENABLE_FRONTEND_SIMULATION:
            try:
                # Simulate loading the frontend page first
                frontend_response = self.session.get(FRONTEND_BASE_URL, timeout=10)
                print(f"[FRONTEND] Frontend page loaded: {frontend_response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"[WARNING] Frontend interaction failed: {e}")
        
        # Step 2: Make the API call with RUM-style headers
        api_url = urljoin(API_BASE_URL, endpoint)
        
        # Simulate RUM SDK headers and correlation context
        headers = {
            'X-User-Action': user_action,
            'X-Correlation-ID': correlation_id,
            'Content-Type': 'application/json',
            # Simulate RUM trace context headers
            'elastic-apm-traceparent': f"00-{uuid.uuid4().hex}-{uuid.uuid4().hex[:16]}-01",
            'X-Observe-Rum-Id': correlation_id
        }
        
        try:
            print(f"[API] Making API call to {endpoint} with correlation {correlation_id}")
            
            start_time = time.time()
            response = self.session.get(api_url, headers=headers, timeout=15)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                record_count = data.get('count', 0)
                query_type = data.get('query_type', 'unknown')
                explain_plan = data.get('explain_plan_hint', 'N/A')
                
                print(f"[SUCCESS] API Success: {query_type}")
                print(f"[DATA] Records returned: {record_count}")
                print(f"[PLAN] Explain plan: {explain_plan}")
                print(f"[PERF] Response time: {duration:.3f}s")
                print(f"[FLOW] Correlation flow: RUM -> API -> Oracle -> OTEL Collector")
                
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
                    'explain_plan': explain_plan
                }
            else:
                print(f"[ERROR] API Error: {response.status_code} - {response.text}")
                return {'success': False, 'correlation_id': correlation_id, 'error': response.status_code}
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            return {'success': False, 'correlation_id': correlation_id, 'error': str(e)}

def generate_realistic_load():
    """Generate realistic user interactions that create full RUM → API → Oracle correlation"""
    
    # Weighted list of API endpoints that users would interact with
    api_scenarios = [
        {
            'endpoint': '/api/employees',
            'user_action': 'view-employees',
            'weight': 30,
            'description': 'User views employee list (FULL table scan)'
        },
        {
            'endpoint': '/api/employees/high-salary',
            'user_action': 'filter-high-salary',
            'weight': 25,
            'description': 'User filters high salary employees (INDEX scan)'
        },
        {
            'endpoint': '/api/analytics/salary-stats',
            'user_action': 'view-analytics',
            'weight': 20,
            'description': 'User views salary analytics (GROUP BY aggregation)'
        },
        {
            'endpoint': '/api/complex-query',
            'user_action': 'complex-analysis',
            'weight': 10,
            'description': 'User runs complex analysis (Self-join)'
        },
        {
            'endpoint': '/api/slow-query',
            'user_action': 'performance-test',
            'weight': 5,
            'description': 'User triggers performance test (Cartesian product)'
        }
    ]
    
    # Sometimes simulate employee creation (POST requests)
    if random.random() < 0.15:  # 15% chance
        api_scenarios.append({
            'endpoint': '/api/employees',
            'user_action': 'create-employee',
            'weight': 10,
            'description': 'User creates new employee (INSERT operation)',
            'method': 'POST'
        })
    
    # Select scenario based on weights
    total_weight = sum(scenario['weight'] for scenario in api_scenarios)
    random_weight = random.randint(1, total_weight)
    
    current_weight = 0
    selected_scenario = None
    for scenario in api_scenarios:
        current_weight += scenario['weight']
        if random_weight <= current_weight:
            selected_scenario = scenario
            break
    
    if not selected_scenario:
        selected_scenario = api_scenarios[0]  # Fallback
    
    print(f"\n{'='*60}")
    print(f"[SCENARIO] {selected_scenario['description']}")
    print(f"{'='*60}")
    
    rum_simulator = RUMSimulator()
    
    # Handle POST requests differently
    if selected_scenario.get('method') == 'POST':
        return simulate_employee_creation(rum_simulator)
    else:
        return rum_simulator.simulate_frontend_interaction(
            selected_scenario['endpoint'],
            selected_scenario['user_action']
        )

def simulate_employee_creation(rum_simulator):
    """Simulate creating a new employee through the API"""
    correlation_id = rum_simulator.generate_correlation_id()
    
    print(f"[USER] Simulating user action: create-employee")
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
        'X-User-Action': 'create-employee',
        'X-Correlation-ID': correlation_id,
        'Content-Type': 'application/json',
        'elastic-apm-traceparent': f"00-{uuid.uuid4().hex}-{uuid.uuid4().hex[:16]}-01",
        'X-Observe-Rum-Id': correlation_id
    }
    
    try:
        print(f"[CREATE] Creating employee: {employee_data['first_name']} {employee_data['last_name']}")
        
        start_time = time.time()
        response = rum_simulator.session.post(api_url, json=employee_data, headers=headers, timeout=15)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            employee = data.get('employee', {})
            
            print(f"[SUCCESS] Employee created successfully!")
            print(f"[EMPLOYEE] Employee: {employee.get('first_name')} {employee.get('last_name')} (ID: {employee.get('employee_id')})")
            print(f"[SALARY] Salary: ${employee.get('salary', 0):,.2f}")
            print(f"[PERF] Response time: {duration:.3f}s")
            print(f"[FLOW] Correlation flow: RUM -> API -> Oracle -> OTEL Collector")
            
            return {
                'success': True,
                'correlation_id': correlation_id,
                'query_type': 'employee_insert',
                'duration': duration,
                'employee': employee
            }
        else:
            print(f"[ERROR] Employee creation failed: {response.status_code} - {response.text}")
            return {'success': False, 'correlation_id': correlation_id, 'error': response.status_code}
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return {'success': False, 'correlation_id': correlation_id, 'error': str(e)}

def print_statistics(stats):
    """Print load generation statistics"""
    total_requests = stats['success'] + stats['errors']
    success_rate = (stats['success'] / total_requests * 100) if total_requests > 0 else 0
    avg_duration = (stats['total_duration'] / stats['success']) if stats['success'] > 0 else 0
    
    print(f"\n[STATS] Load Generation Statistics:")
    print(f"   Total requests: {total_requests}")
    print(f"   Successful: {stats['success']} ({success_rate:.1f}%)")
    print(f"   Errors: {stats['errors']}")
    print(f"   Average response time: {avg_duration:.3f}s")
    print(f"   Query types: {dict(stats['query_types'])}")
    print(f"   Correlations generated: {len(stats['correlations'])}")

def main():
    print("[INFO] Starting Enhanced RUM-Integrated Load Generator")
    print("=" * 60)
    print("This load generator simulates real user interactions with:")
    print("- Frontend page loads (optional)")
    print("- RUM correlation ID generation")
    print("- API calls with proper tracing headers")
    print("- End-to-end correlation: RUM -> API -> Oracle -> OTEL")
    print("=" * 60)
    
    # Wait for all services to be ready
    wait_for_services()
    
    # Initialize statistics
    stats = {
        'success': 0,
        'errors': 0,
        'total_duration': 0,
        'query_types': {},
        'correlations': set()
    }
    
    request_count = 0
    
    try:
        while True:
            request_count += 1
            
            # Generate realistic user interaction
            result = generate_realistic_load()
            
            # Update statistics
            if result['success']:
                stats['success'] += 1
                stats['total_duration'] += result.get('duration', 0)
                
                query_type = result.get('query_type', 'unknown')
                stats['query_types'][query_type] = stats['query_types'].get(query_type, 0) + 1
                stats['correlations'].add(result['correlation_id'])
                
                print(f"[COUNTER] Total successful interactions: {stats['success']}")
            else:
                stats['errors'] += 1
                print(f"[COUNTER] Total errors: {stats['errors']}")
            
            # Print statistics every 10 requests
            if request_count % 10 == 0:
                print_statistics(stats)
            
            # Random sleep between interactions (realistic user behavior)
            sleep_time = random.uniform(MIN_SLEEP, MAX_SLEEP)
            print(f"[WAIT] Waiting {sleep_time:.1f}s before next interaction...")
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print(f"\n[STOP] Load generation stopped by user")
        print_statistics(stats)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        print_statistics(stats)

if __name__ == "__main__":
    main()