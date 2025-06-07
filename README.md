# Oracle Database & Frontend Observability Demo

This demo showcases comprehensive **end-to-end observability** for Oracle databases and frontend applications using OpenTelemetry and Observe Inc's Real User Monitoring (RUM), with **complete correlation tracking** from user interactions to database queries.

## **NEW: Production-Ready Oracle Metrics **

This demo now includes **47 comprehensive Oracle database metrics** that provide enterprise-grade monitoring equivalent to Database Monitoring solution, with full descriptions and production-ready attributes for multi-instance deployments.

## What This Demo Includes

### **Enterprise Oracle Database Monitoring**
- **47 Production-Ready Metrics**: Session, memory, storage, performance, I/O, and transaction metrics
- **Multi-Instance Support**: Production-ready attributes for environment, datacenter, region identification
- **Comprehensive Descriptions**: Every metric includes detailed descriptions for observability teams
- **Real-Time Collection**: 10-second collection intervals with proper cardinality management

### **End-to-End Correlation & Tracing**
- **Complete Correlation Tracking**: Track user interactions from frontend → API → database with correlation IDs
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
   colima start --arch x86_64 --memory 4
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

## **Oracle Database Metrics (47 Production Metrics)**

This demo implements comprehensive Oracle database monitoring with metrics.

### **Metric Collection Summary**
- **Total Metrics**: 47 time series
- **Collection Frequency**: Every 10 seconds
- **Data Points per Hour**: 16,920 (47 × 360)
- **Cardinality**: Production-safe with proper attribute management
- **Backend Integration**: Full Observe compatibility with descriptions and metadata

### **Metric Categories**

#### **1. Session Metrics (6 data points)**
```
oracle.sessions.active    - Active user sessions connected to database
oracle.sessions.total     - Total user sessions (active + inactive)
```
**Attributes**: `oracle.metric.category="sessions"`, `oracle.metric.type="connection_metrics"`

#### **2. Memory Metrics (3 data points)**
```
oracle.memory.sga_size    - System Global Area size in MB (shared memory for caching)
```
**Attributes**: `oracle.memory.component="sga"`, `oracle.metric.type="memory_metrics"`

#### **3. Storage Metrics (16 data points - 4 tablespaces × 2 metrics × 2 series)**
```
oracle.tablespace.size    - Total allocated tablespace size in MB
oracle.tablespace.used    - Used storage space in tablespace in MB
```
**Monitored Tablespaces**: SYSTEM, SYSAUX, UNDOTBS1, USERS
**Attributes**: `TABLESPACE_NAME`, `oracle.storage.type="permanent"`

#### **4. Performance Metrics (3 data points)**
```
oracle.performance.metric - Database performance indicators:
  • buffer_cache_hit_ratio     - Buffer cache efficiency percentage
  • library_cache_hit_ratio    - Library cache efficiency percentage  
  • shared_pool_free_percent   - Shared pool free memory percentage
```
**Attributes**: `oracle.performance.component="cache_efficiency"`

#### **5. Wait Event Metrics (10 data points)**
```
oracle.wait_events.time   - Time spent waiting for database events (performance bottlenecks)
```
**Top Wait Events Monitored**:
- `resmgr:cpu quantum` (Scheduler)
- `library cache lock` (Concurrency)
- `db file sequential read` (User I/O)
- `cursor: pin S wait on X` (Concurrency)

**Attributes**: `WAIT_EVENT`, `WAIT_CLASS`, `oracle.performance.impact="high"`

#### **6. I/O & Transaction Metrics (9 data points)**
```
oracle.io.physical_reads     - Physical disk read operations count
oracle.io.physical_writes    - Physical disk write operations count  
oracle.redo.size_bytes       - Redo log data size (transaction volume)
```
**Attributes**: `oracle.io.direction`, `oracle.transaction.component="redo_log"`

### **Production-Ready Attributes**

#### **Resource-Level Attributes (All Metrics)**
Applied to every metric via OpenTelemetry resource processor:
```yaml
oracle.instance.name: "XEPDB1"           # Unique instance identifier
oracle.database.name: "XE"               # Database name
oracle.host: "oracle-db"                 # Database host
oracle.port: "1521"                      # Database port
oracle.version: "21c"                    # Oracle version
oracle.edition: "express"                # Edition (express/standard/enterprise)
environment: "development"               # Environment (dev/staging/prod)
datacenter: "local"                      # Datacenter location
region: "us-west-1"                      # Geographic region
service.name: "oracle-database"          # Service name for grouping
service.version: "21.3.0.0.0"           # Oracle service version
deployment.environment: "dev"            # Deployment environment
```

#### **Multi-Instance Production Setup**
For production deployments with multiple Oracle instances, update these attributes:

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

### **Enterprise Oracle Database Monitoring (47 Metrics)**
- **Session Management**: Active/total user sessions with connection metrics
- **Memory Utilization**: SGA (System Global Area) size and efficiency monitoring  
- **Storage Management**: Tablespace size, usage, and capacity planning for all tablespaces
- **Performance Bottlenecks**: Top 10 wait events with time spent and impact classification
- **I/O Operations**: Physical read/write operations and transaction log volume
- **Cache Efficiency**: Buffer cache, library cache, and shared pool performance ratios
- **SQL Execution Metrics**: Real-time execution times, CPU usage, I/O metrics with APM correlation
- **Explain Plans**: Query execution plans with full OpenTelemetry trace/span IDs

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

### Frontend RUM Integration Examples
- Live examples of all three RUM integration methods (sync, async, bundler)
- Interactive buttons to generate observability data with correlation IDs
- Simulated user interactions with correlation context
- Real-time feedback on data being sent to Observe

### Observability Data Flow Testing
- **End-to-End Correlation**: Click buttons to see correlation IDs flow from frontend → API → database
- **Performance Testing**: Scenarios to test different SQL execution patterns
- **Error Simulation**: Generate errors with correlation context for debugging

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
- **47 comprehensive Oracle metrics** covering sessions, memory, storage, performance, I/O, and transactions
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

**Deploy this solution in your environment and gain enterprise-grade Oracle database observability with full correlation tracking and comprehensive metric collection that scales from development to production.**