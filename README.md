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
7. **Observe** → Complete APM trace linking frontend → API → database operations

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

## Querying APM Correlation Data in Observe

### Frontend RUM Data with APM Traces
```sql
-- Find RUM transactions with APM correlation
FIELDS.custom_correlation_id LIKE "rum-%"
AND FIELDS.trace_id IS NOT NULL
```

### API Span Data with Full APM Context
```sql
-- Find API traces with RUM correlation
FIELDS.correlation.id LIKE "rum-%"
AND FIELDS.trace_id IS NOT NULL
```

### Database Explain Plans with APM Correlation
```sql
-- Find Oracle explain plans linked to APM traces
FIELDS.logs.attributes.LOG_TYPE = "execution_plan_with_correlation" 
AND FIELDS.logs.attributes.CORRELATION_ID LIKE "rum-%"
AND FIELDS.logs.attributes.OTEL_TRACE_ID != "no_trace"
```

### Recent SQL Executions with APM Context
```sql
-- Find SQL executions with full OpenTelemetry context
FIELDS.logs.attributes.LOG_TYPE = "recent_sql_execution"
AND FIELDS.logs.attributes.CORRELATION_ID LIKE "rum-%"
AND FIELDS.logs.attributes.OTEL_TRACE_ID != "no_trace"
```

### Complete End-to-End APM Correlation
```sql
-- Link frontend RUM → API → database with full APM trace context
SELECT 
  rum.trace_id,
  rum.custom_correlation_id,
  api.span_id,
  db.logs.attributes.OTEL_TRACE_ID,
  db.logs.attributes.OTEL_SPAN_ID,
  db.logs.body as execution_plan
FROM rum_transactions rum
JOIN api_spans api ON rum.trace_id = api.trace_id
JOIN database_logs db ON api.correlation_id = db.logs.attributes.CORRELATION_ID
WHERE db.logs.attributes.LOG_TYPE = "execution_plan_with_correlation"
```

