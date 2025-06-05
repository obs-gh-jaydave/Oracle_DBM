# Oracle Database & Frontend Observability Demo

This demo showcases comprehensive **end-to-end observability** for Oracle databases and frontend applications using OpenTelemetry and Observe Inc's Real User Monitoring (RUM), with **complete correlation tracking** from user interactions to database queries.

## What This Demo Includes

- **End-to-End Correlation**: Track user interactions from frontend → API → database with correlation IDs
- **Oracle Database Monitoring**: SQL execution metrics, explain plans, and performance data with embedded correlation tracking
- **Frontend Observability**: Real User Monitoring with Observe Inc RUM SDK including custom correlation context
- **OpenTelemetry Integration**: Full tracing pipeline with metrics collection and export to Observe
- **Interactive Demo**: Web interface to test various observability scenarios with correlation tracking

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

Key configuration variables:
- `OBSERVE_TENANT_ID`: Your Observe tenant ID (replace with your actual tenant ID)
- `OBSERVE_RUM_BEARER_TOKEN`: Your Frontend RUM bearer token (get from Observe dashboard)
- `OBSERVE_BACKEND_BEARER_TOKEN`: Your Backend/database bearer token (get from Observe dashboard)
- `OBSERVE_RUM_ENVIRONMENT`: Your deployment environment (e.g., 'production', 'staging')
- `OBSERVE_RUM_SERVICE_NAME`: Your application/service name

## What Gets Monitored

### Database Observability (Datadog DBM-style)
- **SQL Execution Metrics**: Real-time execution times, CPU usage, I/O metrics with APM correlation
- **Explain Plans**: Query execution plans with full OpenTelemetry trace/span IDs
- **Oracle-Native Correlation**: Uses `DBMS_SESSION.SET_IDENTIFIER` and `CLIENT_INFO` for production-ready correlation
- **Performance Monitoring**: Buffer cache hit ratios, library cache metrics, shared pool statistics
- **SQL Comment Extraction**: Correlation data embedded in SQL text for reliable tracking
- **Log Types**: 
  - `recent_sql_execution`: SQL statements with APM trace/span IDs and correlation
  - `execution_plan_with_correlation`: Query execution plans linked to APM traces
  - `oracle_session_correlation`: Session-level correlation data from Oracle context
  - `oracle_performance`: Database performance metrics with correlation context

### Frontend Observability (Observe RUM)
- **OpenTelemetry Integration**: Elastic APM RUM SDK with automatic trace context generation
- **Distributed Tracing**: Automatic propagation of trace context to API calls
- **User Journey Tracking**: Complete user interaction correlation with APM traces
- **Performance Monitoring**: Real User Monitoring with Core Web Vitals and response times
- **Error Tracking**: JavaScript errors and exceptions with full trace context
- **Custom Labels**: APM transactions enriched with correlation data and user actions
- **Automatic Instrumentation**: fetch() and XHR calls automatically instrumented with trace headers

### API/Backend Observability (FastAPI + OpenTelemetry)
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

This demo sends correlated data to Observe with the following attributes:

### Frontend RUM Data
- **Custom correlation IDs** in transaction labels with format `rum-{trace_id}-{span_id}`
- **OpenTelemetry trace context** linking user interactions to backend operations
- **User action metadata** showing which demo buttons were clicked

### API Span Data  
- **Distributed traces** with correlation attributes from RUM context
- **Database operation metadata** showing SQL execution details
- **Response metrics** including record counts and query types

### Database Monitoring Data
- **Explain plans** with correlation IDs: `execution_plan_with_correlation`
- **SQL execution logs** with APM trace/span IDs: `recent_sql_execution`  
- **Oracle performance metrics** with correlation context
- **Real OpenTelemetry trace/span IDs** extracted from SQL comments

### Complete APM Correlation
- **End-to-end tracing** from frontend clicks → API calls → Oracle explain plans
- **Full OpenTelemetry context** with 32-character trace IDs and 16-character span IDs
- **Oracle-native correlation** using production-ready database monitoring techniques

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

