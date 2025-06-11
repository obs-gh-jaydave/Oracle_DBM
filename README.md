# Oracle Database & Frontend Observability Demo

This demo showcases comprehensive **end-to-end observability** for Oracle databases and frontend applications using OpenTelemetry and Observe Inc's Real User Monitoring (RUM), with **complete correlation tracking** from user interactions to database queries.

## **NEW: Production-Ready Oracle Metrics (Oracle XE Compatible)**

This demo now includes **15 comprehensive Oracle database metrics** that provide enterprise-grade monitoring with full Oracle XE compatibility, complete descriptions, and production-ready attributes for multi-instance deployments. All metrics have been tested and verified working with Oracle Express Edition (XE).

## What This Demo Includes

### **Enterprise Oracle Database Monitoring**
- **15 Production-Ready Metrics**: Session, memory, storage, performance, I/O, and transaction metrics
- **Oracle XE Compatibility**: All queries tested and verified compatible with Oracle Express Edition
- **Multi-Instance Support**: Production-ready attributes for environment, datacenter, region identification
- **Comprehensive Descriptions**: Every metric includes detailed descriptions for observability teams
- **Real-Time Collection**: 10-second collection intervals with proper cardinality management

### **End-to-End Correlation & Tracing**
- **Complete Correlation Tracking**: Track user interactions from frontend → API → database with correlation IDs
- **OpenTelemetry Span Attributes**: Correlation data set as span attributes instead of HTTP headers for APM visibility
- **Oracle-Native Integration**: SQL execution metrics, explain plans, and performance data with embedded correlation tracking
- **OpenTelemetry Standard**: Full distributed tracing pipeline with metrics collection and export to Observe

### **Frontend & API Observability**
- **Real User Monitoring**: Observe Inc RUM SDK with custom correlation context
- **FastAPI Integration**: Automatic OpenTelemetry instrumentation with correlation propagation
- **Interactive Demo Interface**: Web interface to test various observability scenarios

## Architecture

- **Oracle XE Database**: Running with test data and monitoring user for SQL query capture
- **FastAPI Backend**: REST API with OpenTelemetry instrumentation and correlation ID injection
- **OTEL Collector**: Collecting database metrics, traces, and logs with correlation ID extraction
- **Frontend Application**: Web demo with RUM integration and correlation ID generation
- **Nginx Web Server**: Serving the frontend demo with environment variable substitution

## End-to-End Correlation Flow

This demo implements complete **OpenTelemetry-native correlation tracking** across all layers:

1. **Frontend Click** → RUM SDK generates OpenTelemetry trace context automatically
2. **RUM Transaction** → Creates APM trace with correlation ID and custom labels
3. **API Request** → Receives trace context via distributed tracing headers (no manual headers needed)
4. **API Span** → Extracts correlation from OpenTelemetry trace/span IDs
5. **Database Query** → Embeds full OpenTelemetry context + correlation in SQL comments
6. **OTEL Collector** → Extracts real APM trace/span IDs and correlation from SQL text
7. **Observe** → Dashboards, monitors & explorers linking frontend → API → database operations

### Correlation ID Format
- **Pattern**: `rum-{trace_id_12_chars}-{span_id_8_chars}`
- **Example**: `rum-498f7f4d8c70-3fc5f9b6`
- **Full APM Context**: Includes 32-char OpenTelemetry trace ID and 16-char span ID
- **Visibility**: Available in frontend RUM, API spans, and database explain plans with full APM correlation

## Quick Start

When running locally, it will take some time for everything to launch and work.

### Prerequisites for Running on Apple Silicon

If you're using Apple Silicon, follow these steps:

1. Install Colima:
   ```bash
   brew install colima
   ```

2. Start Colima with specific architecture and memory settings:
   ```bash
   colima start --arch x86_64 --memory 8
   ```

### Running the Demo

1. Build and run all containers:
   ```bash
   docker compose build --no-cache
   docker compose up
   ```

2. Access the frontend demo:
   ```
   http://localhost:8081
   ```

3. View Prometheus metrics:
   ```
   http://localhost:9464/metrics
   ```

These steps ensure compatibility and proper setup for running the application on Apple Silicon machines.

## **Oracle Database Metrics (15 Production Metrics - Oracle XE Compatible)**

This demo implements comprehensive Oracle database monitoring with Oracle Express Edition (XE) compatibility. All metrics have been tested and verified to work with Oracle XE constraints.

### **Metric Collection Summary**
- **Total Metrics**: 15 time series (Oracle XE compatible)
- **Collection Frequency**: Every 10 seconds
- **Data Points per Hour**: 5,400 (15 × 360)
- **Cardinality**: Production-safe with proper attribute management
- **Backend Integration**: Full Observe compatibility with descriptions and metadata
- **Oracle XE Compatibility**: All queries verified compatible with Oracle Express Edition limitations

### **Metric Categories (Oracle XE Compatible)**

#### **1. Session Metrics (3 metrics)**
```
oracle.sessions.active    - Active user sessions connected to database
oracle.sessions.total     - Total user sessions (active + inactive)  
oracle.memory.sga_size    - System Global Area size in MB (shared memory for caching)
```
**Attributes**: `oracle.metric.category="sessions"`, `oracle.metric.type="connection_metrics"`

#### **2. Storage Metrics (8 metrics - 4 tablespaces × 2 metrics)**
```
oracle.tablespace.size    - Total allocated tablespace size in MB
oracle.tablespace.used    - Used storage space in tablespace in MB
```
**Monitored Tablespaces**: SYSTEM, SYSAUX, UNDOTBS1, USERS (Oracle XE default tablespaces)
**Attributes**: `TABLESPACE_NAME`, `oracle.storage.type="permanent"`

#### **3. Performance Metrics (3 metrics)**
```
oracle.performance.metric - Database performance indicators:
  • buffer_cache_hit_ratio     - Buffer cache efficiency percentage
  • library_cache_hit_ratio    - Library cache efficiency percentage  
  • shared_pool_free_percent   - Shared pool free memory percentage
```
**Attributes**: `oracle.performance.component="cache_efficiency"`

#### **4. I/O & Transaction Metrics (3 metrics)**
```
oracle.io.physical_reads     - Physical disk read operations count
oracle.io.physical_writes    - Physical disk write operations count  
oracle.redo.size_bytes       - Redo log data size (transaction volume)
```
**Attributes**: `oracle.io.direction`, `oracle.transaction.component="redo_log"`

### **Oracle XE Compatibility Notes**
- **Removed ECID column references**: Oracle XE doesn't support ECID (Execution Context ID) 
- **v$sql instead of v$sql_monitor**: Oracle XE doesn't include v$sql_monitor view
- **Simplified column references**: Using `parsing_schema_name` instead of `username` for XE compatibility
- **Wait events limited**: Oracle XE has fewer wait events, focusing on most common ones
- **Tablespace monitoring**: Limited to default XE tablespaces (SYSTEM, SYSAUX, UNDOTBS1, USERS)

### **Production-Ready Attributes (Dynamic Configuration)**

#### **Resource-Level Attributes (All Metrics)**
All attributes are now **dynamically configured via environment variables** instead of hardcoded values:

```yaml
# OTEL Collector Configuration (collector-config.yaml)
processors:
  resourcedetection:
    detectors: [env, system, docker, ec2, ecs, gcp, azure]
    
  resource:
    attributes:
      # Oracle Instance Identification
      - key: oracle.instance.name
        value: "${ORACLE_INSTANCE_NAME}"        # From environment
        action: upsert
      - key: oracle.database.name
        value: "${ORACLE_DATABASE_NAME}"        # From environment
        action: upsert
      - key: oracle.host
        value: "${ORACLE_HOST}"                 # From environment
        action: upsert
      - key: oracle.port
        value: "${ORACLE_PORT}"                 # From environment
        action: upsert
      - key: oracle.version
        value: "${ORACLE_VERSION}"              # From environment
        action: upsert
      - key: oracle.edition
        value: "${ORACLE_EDITION}"              # From environment
        action: upsert
      
      # Environment & Deployment Configuration
      - key: environment
        value: "${ENVIRONMENT}"                 # From environment
        action: upsert
      - key: datacenter
        value: "${DATACENTER}"                  # From environment
        action: upsert
      - key: region
        value: "${REGION}"                      # From environment
        action: upsert
      - key: service.name
        value: "${SERVICE_NAME}"                # From environment
        action: upsert
      - key: service.version
        value: "${SERVICE_VERSION}"             # From environment
        action: upsert
      - key: deployment.environment
        value: "${DEPLOYMENT_ENVIRONMENT}"      # From environment
        action: upsert
      
      # Deployment Tracking
      - key: deployment.id
        value: "${DEPLOYMENT_ID}"               # Auto-generated in CI/CD
        action: upsert
      - key: deployment.timestamp
        value: "${DEPLOYMENT_TIMESTAMP}"        # Auto-generated in CI/CD
        action: upsert
```

#### **Automatic Resource Detection**
The collector automatically detects:
- **Infrastructure**: Cloud provider (AWS/GCP/Azure), region, availability zone
- **Container**: Docker container information, Kubernetes metadata
- **System**: Hostname, operating system, hardware information

#### **Environment-Specific Configuration Files**
Use different `.env` files for each environment:

- `.env` - Development (default)
- `.env.production` - Production template
- `.env.staging` - Staging template

#### **Automatic Deployment Tracking**
Use the included script to auto-generate deployment information:

```bash
# Run before deployment (manual or CI/CD)
./scripts/generate-deployment-info.sh

# This auto-generates:
# - deployment.id (Git commit SHA)
# - deployment.timestamp (ISO 8601 timestamp) 
# - environment (auto-detected from hostname/CI)
# - region (auto-detected from cloud metadata)
# - datacenter (availability zone)
```

#### **Multi-Instance Production Setup**
For production deployments with multiple Oracle instances, update environment variables:

```bash
# Primary Production Instance
ORACLE_INSTANCE_NAME=PROD01
ORACLE_DATABASE_NAME=PRODDB
ORACLE_HOST=prod-oracle-01.company.com
ENVIRONMENT=production
DATACENTER=datacenter-east
REGION=us-east-1

# Secondary/DR Instance  
ORACLE_INSTANCE_NAME=PROD02
ORACLE_HOST=prod-oracle-02.company.com
ENVIRONMENT=production
DATACENTER=datacenter-west
REGION=us-west-2

# Staging Environment
ORACLE_INSTANCE_NAME=STAG01
ENVIRONMENT=staging
```

#### **Dashboard Organization**
- **By Environment**: Separate prod/staging/dev dashboards using `environment` attribute
- **By Instance**: Monitor specific databases using `oracle.instance.name`
- **By Category**: Group metrics using `oracle.metric.category` (sessions, memory, storage, performance, io)
- **By Impact**: Focus on critical events using `oracle.performance.impact="high"`

#### **Alerting Precision**
- Target specific environments: `environment="production"`
- Monitor critical components: `oracle.performance.impact="high"`  
- Track by service tier: `oracle.edition="enterprise"`
- Regional monitoring: `region="us-east-1"`

### **Sample Metric Output**
```
oracle_sessions_active{
  oracle.metric.category="sessions",
  oracle.metric.type="connection_metrics", 
  oracle.monitoring.level="instance",
  oracle.instance.name="XEPDB1",
  environment="development"
} 2

oracle_tablespace_size{
  oracle.metric.category="storage",
  oracle.storage.type="permanent",
  TABLESPACE_NAME="SYSTEM",
  oracle.instance.name="XEPDB1"
} 272

oracle_wait_events_time{
  oracle.metric.category="performance",
  oracle.performance.impact="high",
  WAIT_EVENT="library cache lock",
  WAIT_CLASS="Concurrency"
} 14.22
```

This comprehensive metric collection transforms your Oracle monitoring from basic health checks into enterprise-grade database observability that scales across multiple instances, environments, and geographic regions.

## Frontend Observability Setup

The demo includes three different methods to implement Observe Inc RUM:

### Method 1: Synchronous Script Tags

Add directly to your HTML `<head>`:

```html
<script src="https://assets.observeinc.com/dist/bundles/apm-rum.umd.min.js" crossorigin></script>
<script>
  elasticApm.init({
        environment: '<YOUR_ENVIRONMENT>',
        serviceName: '<YOUR_SERVICE_NAME>',
        serverUrlPrefix: '?environment=<YOUR_ENVIRONMENT>&serviceName=<YOUR_SERVICE_NAME>',
        serverUrl: 'https://<YOUR_TENANT_ID>.collect.observe-staging.com/v1/http/rum',
        breakdownMetrics: true,
        distributedTracingOrigins: ['*'],
        distributedTracingHeaderName: 'X-Observe-Rum-Id',
        propagateTracestate: true,
        logLevel: 'error',
        session:true,
        apiVersion: 2,
        apmRequest({ xhr }) {
            xhr.setRequestHeader('Authorization', 'Bearer <YOUR_RUM_BEARER_TOKEN>')
            return true
        }
  })
</script>
```

### Method 2: Asynchronous Loading

For non-blocking script loading:

```html
<script>
  ;(function(d, s, c) {
    var j = d.createElement(s),
      t = d.getElementsByTagName(s)[0]

    j.src = 'https://assets.observeinc.com/dist/bundles/apm-rum.umd.min.js'
    j.onload = function() {elasticApm.init(c)}
    t.parentNode.insertBefore(j, t)
  })(document, 'script', {
            environment: '<YOUR_ENVIRONMENT>',
            serviceName: '<YOUR_SERVICE_NAME>',
            serverUrlPrefix: '?environment=<YOUR_ENVIRONMENT>&serviceName=<YOUR_SERVICE_NAME>',
            serverUrl: 'https://<YOUR_TENANT_ID>.collect.observe-staging.com/v1/http/rum',
            breakdownMetrics: true,
            distributedTracingOrigins: ['*'],
            distributedTracingHeaderName: 'X-Observe-Rum-Id',
            propagateTracestate: true,
            logLevel: 'error',
            session:true,
            apiVersion: 2,
            apmRequest({ xhr }) {
                xhr.setRequestHeader('Authorization', 'Bearer <YOUR_RUM_BEARER_TOKEN>')
                return true
            }
        })
</script>
```

### Method 3: NPM/Bundler Integration

Install the package:

```bash
npm install @elastic/apm-rum --save
```

Initialize in your application:

```javascript
import { init as initApm } from '@elastic/apm-rum';

initApm({
  environment: '<YOUR_ENVIRONMENT>',
  serviceName: '<YOUR_SERVICE_NAME>',
  serverUrlPrefix: '?environment=<YOUR_ENVIRONMENT>&serviceName=<YOUR_SERVICE_NAME>',
  serverUrl: 'https://<YOUR_TENANT_ID>.collect.observe-staging.com/v1/http/rum',
  breakdownMetrics: true,
  distributedTracingOrigins: ['*'],
  distributedTracingHeaderName: 'X-Observe-Rum-Id',
  propagateTracestate: true,
  logLevel: 'error',
  session:true,
  apiVersion: 2,
  apmRequest({ xhr }) {
    xhr.setRequestHeader('Authorization', 'Bearer <YOUR_RUM_BEARER_TOKEN>')
    return true
  }
});
```

## Configuration

The demo uses environment variables configured in `.env` file. Copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
```

### **Core Configuration Variables**
- `OBSERVE_TENANT_ID`: Your Observe tenant ID (replace with your actual tenant ID)
- `OBSERVE_RUM_BEARER_TOKEN`: Your Frontend RUM bearer token (get from Observe dashboard)
- `OBSERVE_BACKEND_BEARER_TOKEN`: Your Backend/database bearer token (get from Observe dashboard)
- `OBSERVE_RUM_ENVIRONMENT`: Your deployment environment (e.g., 'production', 'staging')
- `OBSERVE_RUM_SERVICE_NAME`: Your application/service name

### **Oracle Instance Configuration (Production)**
For production deployments with multiple Oracle instances:

```bash
# Oracle Instance Identification
ORACLE_INSTANCE_NAME=PRODDB1          # Unique instance identifier
ORACLE_DATABASE_NAME=PRODDB           # Database name
ORACLE_HOST=prod-oracle-01.company.com # Database host
ORACLE_PORT=1521                       # Database port
ORACLE_VERSION=19c                     # Oracle version (19c, 21c, etc.)
ORACLE_EDITION=enterprise             # Oracle edition (express, standard, enterprise)

# Environment & Deployment
ENVIRONMENT=production                 # Environment (development, staging, production)
DATACENTER=datacenter-east            # Datacenter location
REGION=us-east-1                      # Geographic region
DEPLOYMENT_ENV=prod                   # Deployment environment
```

### **Multi-Environment Setup Examples**

#### **Production Environment**
```bash
ORACLE_INSTANCE_NAME=PROD01
ENVIRONMENT=production
DATACENTER=aws-us-east-1a
REGION=us-east-1
ORACLE_EDITION=enterprise
```

#### **Staging Environment**
```bash
ORACLE_INSTANCE_NAME=STAG01
ENVIRONMENT=staging
DATACENTER=aws-us-west-2b
REGION=us-west-2
ORACLE_EDITION=standard
```

#### **Development Environment**
```bash
ORACLE_INSTANCE_NAME=DEV01
ENVIRONMENT=development
DATACENTER=local
REGION=us-west-1
ORACLE_EDITION=express
```

These environment variables automatically populate the resource-level attributes for all Oracle metrics, enabling proper instance identification and multi-environment monitoring.

## What Gets Monitored

### **Enterprise Oracle Database Monitoring (15 Oracle XE Compatible Metrics)**
- **Session Management**: Active/total user sessions with connection metrics
- **Memory Utilization**: SGA (System Global Area) size monitoring  
- **Storage Management**: Tablespace size, usage, and capacity planning for Oracle XE tablespaces
- **Cache Efficiency**: Buffer cache, library cache, and shared pool performance ratios
- **I/O Operations**: Physical read/write operations and transaction log volume
- **SQL Execution Metrics**: Real-time execution times, CPU usage, I/O metrics with APM correlation (Oracle XE compatible)
- **Explain Plans**: Query execution plans with full OpenTelemetry trace/span IDs
- **Oracle Session Correlation**: ECID session correlation and CLIENT_INFO tracking

### **Frontend Observability (Observe RUM)**
- **OpenTelemetry Integration**: Elastic APM RUM SDK with automatic trace context generation
- **Distributed Tracing**: Automatic propagation of trace context to API calls
- **User Journey Tracking**: Complete user interaction correlation with APM traces
- **Performance Monitoring**: Real User Monitoring with Core Web Vitals and response times
- **Error Tracking**: JavaScript errors and exceptions with full trace context
- **Custom Labels**: APM transactions enriched with correlation data and user actions

### **API/Backend Observability (FastAPI + OpenTelemetry)**
- **Automatic Instrumentation**: FastAPI automatically instrumented with OpenTelemetry
- **Trace Context Propagation**: Receives and processes RUM trace context from frontend
- **Span Attributes**: Correlation data set as OpenTelemetry span attributes for APM visibility
- **Oracle Integration**: Embeds APM trace/span IDs directly in SQL comments for correlation
- **Span Enrichment**: API spans enriched with correlation attributes and database metadata
- **Database Operation Tracking**: Every SQL operation linked to originating APM trace/span
- **Error Correlation**: API errors linked to frontend user actions via trace context

## Demo Features

The interactive demo at `http://localhost:8081` includes:

### Oracle Database API Calls (with Correlation Tracking)
- **Get All Employees**: Triggers FULL table scan with correlation ID embedding
- **High Salary Filter**: Uses INDEX range scan with correlation tracking
- **Salary Analytics**: GROUP BY aggregation with correlation context
- **Add New Employee**: INSERT operation with correlation ID propagation
- **Complex Join Query**: Self-join operations with end-to-end tracing
- **Slow Query**: Performance testing with correlation tracking

### Enhanced RUM-Integrated Load Generator
The demo now includes an **automated load generator** that simulates realistic user interactions:

#### **Realistic User Behavior Simulation**
- **Frontend Page Load Simulation**: Simulates loading the frontend before making API calls
- **RUM-Style Correlation ID Generation**: Creates correlation IDs in `rum-{trace_id_12_chars}-{span_id_8_chars}` format
- **Weighted Scenario Selection**: Realistic distribution of user actions based on typical usage patterns:
  - 30% - View employee list (FULL table scan)
  - 25% - Filter high salary employees (INDEX scan)
  - 20% - View salary analytics (GROUP BY aggregation)
  - 10% - Run complex analysis (Self-join)
  - 5% - Trigger performance test (Cartesian product)
  - 15% chance - Create new employee (INSERT operation)

#### **Load Generation Configuration**
- **Frequency**: 3-10 second intervals between requests (configurable via environment variables)
- **Volume**: Approximately 9-10 requests per minute, 540-600 requests per hour
- **Headers**: Proper RUM trace context headers (`elastic-apm-traceparent`, `X-Observe-Rum-Id`)
- **Environment Variables**:
  ```bash
  LOADGEN_MIN_SLEEP=3          # Minimum wait time between requests
  LOADGEN_MAX_SLEEP=10         # Maximum wait time between requests
  ENABLE_FRONTEND_SIMULATION=true  # Enable frontend page load simulation
  ```

#### **Comprehensive Observability Data Generation**
- **End-to-End Correlation**: Each request generates correlation data flowing from RUM -> API -> Oracle -> OTEL Collector
- **Explain Plan Generation**: Automatically creates Oracle execution plans with embedded correlation IDs
- **Performance Metrics**: Tracks response times, record counts, and query types
- **Statistics Tracking**: Real-time statistics every 10 requests including success rates and query type distribution

#### **Production-Ready Logging**
- **Structured Logging**: Clean, professional log output with categorized prefixes ([INFO], [CORRELATION], [SUCCESS], [ERROR])
- **Correlation Tracking**: Logs correlation ID preservation across all layers
- **Performance Monitoring**: Response time tracking and query execution metrics
- **Error Handling**: Graceful error handling with detailed error logging

### Frontend RUM Integration Examples
- Live examples of all three RUM integration methods (sync, async, bundler)
- Interactive buttons to generate observability data with correlation IDs
- Simulated user interactions with correlation context
- Real-time feedback on data being sent to Observe

### Observability Data Flow Testing
- **Automated Load Generation**: Continuous generation of realistic observability data
- **End-to-End Correlation**: Correlation IDs flow from simulated frontend interactions -> API -> database
- **Performance Testing**: Multiple scenarios testing different SQL execution patterns
- **Error Simulation**: Generate errors with correlation context for debugging
- **Statistics Dashboard**: Real-time load generation statistics and correlation tracking

## What You'll See in Observe

This demo sends comprehensive Oracle database metrics and correlated observability data to Observe with rich metadata and descriptions.

### **Oracle Database Metrics in Observe**

#### **Metric Organization**
All Oracle metrics appear in Observe with the following structure:
- **Metric Names**: `oracle.sessions.active`, `oracle.tablespace.size`, `oracle.wait_events.time`, etc.
- **Descriptions**: Every metric includes comprehensive descriptions explaining what it measures
- **Categories**: Organized by `oracle.metric.category` (sessions, memory, storage, performance, io, transactions)
- **Resource Attributes**: Instance identification via `oracle.instance.name`, `environment`, `datacenter`, `region`

#### **Sample Observe Data Structure**
```json
{
  "FIELDS": {
    "name": "oracle.tablespace.used",
    "value": 269.31,
    "type": "gauge",
    "time_unix_nano": 1749318959938110700
  },
  "EXTRA": {
    "description": "Used storage space in Oracle tablespace in megabytes - indicates actual data consumption",
    "attributes": {
      "TABLESPACE_NAME": "SYSTEM",
      "oracle.metric.category": "storage",
      "oracle.storage.type": "permanent",
      "oracle.monitoring.level": "tablespace"
    },
    "resource": {
      "oracle.instance.name": "XEPDB1",
      "oracle.database.name": "XE", 
      "environment": "development",
      "datacenter": "local",
      "region": "us-west-1",
      "service.name": "oracle-database"
    }
  }
}
```

#### **Dashboard Organization Examples**
1. **Environment Overview**: Filter all metrics by `environment="production"`
2. **Instance Health**: Group by `oracle.instance.name` for per-database views
3. **Regional Monitoring**: Use `region` and `datacenter` for geographic dashboards
4. **Performance Focus**: Filter by `oracle.performance.impact="high"` for critical events
5. **Storage Management**: Monitor `oracle.tablespace.*` metrics with `TABLESPACE_NAME` breakdown

### **End-to-End Correlation Data**

This demo also sends correlated observability data across all layers:

#### **Data Types Exported**
- **Frontend RUM**: Custom correlation IDs, OpenTelemetry trace context, user action metadata
- **API Spans**: Distributed traces with correlation attributes and database operation metadata
- **Database Logs**: Execution plans, SQL execution logs, and performance metrics with correlation
- **Complete APM Correlation**: End-to-end tracing from frontend → API → database with full OpenTelemetry context

## How Correlation Works Across Layers

This section explains the technical implementation of end-to-end correlation from frontend to database explain plans.

### Layer 1: Frontend RUM (Elastic APM SDK)

**Location**: `frontend/clean.html`

1. **Automatic Trace Generation**:
   ```javascript
   // RUM SDK automatically generates OpenTelemetry trace context
   const transaction = elasticApm.startTransaction(`oracle-${userAction}`, 'user-action');
   ```

2. **Custom Correlation Labels**:
   ```javascript
   transaction.addLabels({
       custom_correlation_id: correlationId,  // rum-{trace}-{span} format
       custom_user_action: userAction,
       custom_frontend_timestamp: Date.now()
   });
   ```

3. **Automatic Distributed Tracing**:
   ```javascript
   // RUM SDK automatically adds trace headers to fetch() calls
   fetch(apiUrl, {
       method: 'GET',
       headers: { 'Content-Type': 'application/json' }
       // elastic-apm-traceparent header added automatically
   });
   ```

### Layer 2: FastAPI Backend (OpenTelemetry APM)

**Location**: `api/main.py`

1. **Automatic Trace Context Reception**:
   ```python
   # FastAPI OpenTelemetry instrumentation automatically receives trace context
   current_span = trace.get_current_span()
   trace_id = format(current_span.get_span_context().trace_id, '032x')
   span_id = format(current_span.get_span_context().span_id, '016x')
   ```

2. **Correlation ID Generation from APM Context**:
   ```python
   def extract_correlation_from_request(request: Request):
       # Extract correlation from OpenTelemetry trace context (from RUM)
       if current_span and current_span.get_span_context().trace_id != 0:
           correlation_id = f"rum-{trace_id[:12]}-{span_id[:8]}"
           
       # Set correlation_id as span attribute for APM visibility
       if current_span:
           current_span.set_attribute("correlation_id", correlation_id)
           current_span.set_attribute("user_action", user_action)
           current_span.set_attribute("observability.correlation_source", "rum_trace_context")
   ```

3. **SQL Comment Embedding**:
   ```python
   # Embed full APM context in SQL comments for Oracle correlation
   query = f"""
   SELECT /*+ FULL(e) */ /* correlation_id={correlation_id} 
                            user_action={user_action} 
                            otel_trace_id={trace_id} 
                            otel_span_id={span_id} */
   FROM employees e ORDER BY salary DESC
   """
   ```

### Layer 3: Oracle Database Integration

**Location**: `api/main.py` - `execute_with_correlation()`

1. **Oracle-Native Session Correlation**:
   ```python
   # Set Oracle CLIENT_INFO with structured correlation data
   client_info = f"otel_trace={trace_id},otel_span={span_id},correlation={correlation_id}"
   cursor.execute("BEGIN DBMS_APPLICATION_INFO.SET_CLIENT_INFO(:1); END;", [client_info])
   
   # Set Oracle client identifier as backup
   cursor.execute("BEGIN DBMS_SESSION.SET_IDENTIFIER(:1); END;", [correlation_id])
   ```

2. **SQL Execution with Embedded Context**:
   ```python
   # Execute SQL with both session context AND embedded comments
   cursor.execute(query)  # Contains APM trace/span IDs in comments
   ```

### Layer 4: OTEL Collector (Database Monitoring)

**Location**: `otel-collector/collector-config.yaml`

1. **Explain Plan Correlation Extraction**:
   ```yaml
   # Extract correlation and OpenTelemetry context from SQL text comments
   NVL(REGEXP_SUBSTR(sql.sql_text, 'correlation_id=([^ \*/]+)', 1, 1, NULL, 1), 'no_correlation') AS CORRELATION_ID,
   NVL(REGEXP_SUBSTR(sql.sql_text, 'otel_trace_id=([^ \*/]+)', 1, 1, NULL, 1), 'no_trace') AS OTEL_TRACE_ID,
   NVL(REGEXP_SUBSTR(sql.sql_text, 'otel_span_id=([^ \*/]+)', 1, 1, NULL, 1), 'no_span') AS OTEL_SPAN_ID,
   ```

2. **Explain Plan Capture with APM Context**:
   ```yaml
   # Query v$sql and v$sql_plan with correlation extraction
   SELECT sql.sql_id, p.operation, p.options, p.object_name,
          CORRELATION_ID, OTEL_TRACE_ID, OTEL_SPAN_ID
   FROM v$sql sql
   JOIN v$sql_plan p ON sql.sql_id = p.sql_id
   WHERE sql.parsing_schema_name = 'TESTUSER'
   ```

3. **Data Export to Observe**:
   ```yaml
   logs:
     - body_column: EXECUTION_PLAN
       attribute_columns: [SQL_ID, CORRELATION_ID, OTEL_TRACE_ID, OTEL_SPAN_ID, USER_ACTION]
   ```

### Complete Correlation Flow Example

1. **User clicks "Get All Employees"** → RUM generates trace `498f7f4d8c70f0b3d8ef243ed48eb913`
2. **Frontend sends API request** → Automatically includes `elastic-apm-traceparent` header
3. **FastAPI receives trace context** → Extracts correlation: `rum-498f7f4d8c70-3fc5f9b6`
4. **API embeds in SQL** → `/* correlation_id=rum-498f7f4d8c70-3fc5f9b6 otel_trace_id=498f7f4d8c70f0b3d8ef243ed48eb913 */`
5. **Oracle stores SQL** → SQL text persists in `v$sql` with embedded correlation
6. **OTEL Collector extracts** → Regex extracts correlation from SQL comments
7. **Observe receives** → Creates dashboards & monitors linking frontend → API → database explain plan

### Why This Approach Works in Production

- **No dependency on short-lived sessions** - correlation embedded in persistent SQL text
- **OpenTelemetry standard compliance** - uses proper distributed tracing headers  
- **Oracle-native techniques** - leverages `DBMS_SESSION` and `CLIENT_INFO` for production reliability
- **Fallback mechanisms** - multiple correlation methods ensure data capture
- **Performance optimized** - minimal overhead on database operations
- **Oracle XE compatibility** - all 15 metrics verified compatible with Oracle Express Edition
- **15 comprehensive Oracle metrics** covering sessions, memory, storage, performance, I/O, and transactions
- **Oracle XE constraint handling** - uses v$sql instead of v$sql_monitor, removes ECID dependencies
- **Span attributes implementation** - correlation data set as OpenTelemetry span attributes for APM visibility
- **10-second collection intervals** providing real-time database health insights
- **Production-safe cardinality** with proper attribute management
- **Resource-level attributes** for instance, environment, datacenter, and region identification
- **Scalable architecture** supporting unlimited Oracle instances across geographic regions
- **Environment separation** with proper production/staging/development classification
- **Comprehensive descriptions** for every metric, enabling self-service observability
- **Complete correlation tracking** from frontend user clicks to database explain plans
- **OpenTelemetry standard compliance** ensuring compatibility with any observability backend
- **Oracle-native integration** using production-proven database monitoring techniques
- **Rich contextual data** enabling precise alerting and sophisticated dashboard organization
- **Containerized architecture** with Docker Compose for easy deployment
- **Environment variable configuration** for seamless multi-environment setup
- **Comprehensive documentation** covering installation, configuration, and operation
- **Example configurations** for production, staging, and development environments

## Recent Updates

### **Enhanced RUM-Integrated Load Generator (Latest)**
- **Automated User Simulation**: Complete transformation from database-direct tool to frontend interaction simulator
- **Realistic User Behavior**: Weighted scenario selection mimicking actual user patterns with frontend page loads
- **RUM Correlation Generation**: Proper `rum-{trace}-{span}` correlation ID format with OpenTelemetry trace context
- **Professional Logging**: Structured log output with categorized prefixes, no visual elements for production clarity
- **Configurable Load Patterns**: Environment variable control of request frequency and simulation options
- **End-to-End Validation**: Verified correlation flow from simulated frontend through to Oracle database explain plans

### **Docker Compose Caching Optimizations**
- **Persistent Oracle Data**: Added volumes for database data and configuration to prevent reinitialization
- **Build Cache Optimization**: Enhanced build contexts with base image caching for faster rebuilds
- **Restart Policies**: Added `unless-stopped` restart policies for service reliability
- **Resource Limits**: Implemented memory and CPU limits to prevent resource contention
- **Optimized Health Checks**: Reduced frequency and improved timeout settings for better performance

### **Span Attributes Implementation**
- **OpenTelemetry Span Attributes**: Correlation data now set as span attributes instead of HTTP headers
- **APM Visibility**: `correlation_id`, `user_action`, and `observability.correlation_source` attributes added to spans
- **Endpoint-Specific Attributes**: Each API endpoint includes `api.endpoint`, `api.method`, and `observability.layer` attributes
- **Enhanced Traceability**: Correlation data visible in FastAPI APM layer payload for better observability

### **Production Deployment Ready**
This solution provides enterprise-grade Oracle database observability with:
- **Oracle XE to Enterprise Edition compatibility** - works across all Oracle editions
- **Complete end-to-end correlation** from simulated user interactions to database explain plans
- **OpenTelemetry standard compliance** for any observability backend
- **15 production-ready metrics** with comprehensive descriptions and attributes
- **Span attributes implementation** providing APM visibility of correlation data
- **Automated load generation** creating realistic observability data continuously
- **Container persistence** maintaining database state and correlation data across restarts

**Deploy this solution in your environment and gain enterprise-grade Oracle database observability with full correlation tracking, automated load generation, and comprehensive metric collection that scales from development to production.**