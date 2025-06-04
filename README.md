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

This demo implements complete correlation tracking across all layers:

1. **Frontend Click** → Generates correlation ID (`obs-{timestamp}-{random}`)
2. **RUM Transaction** → Tagged with correlation ID in custom labels and context
3. **API Request** → Correlation ID passed via headers (`X-Correlation-ID`)
4. **API Span** → Enriched with correlation attributes in OpenTelemetry traces
5. **Database Query** → Correlation ID embedded in SQL comments for tracking
6. **OTEL Logs** → Correlation data extracted and captured for analysis in Observe

### Correlation ID Format
- **Pattern**: `obs-{timestamp}-{randomString}`
- **Example**: `obs-1703875200000-abc123def`
- **Visibility**: Available in frontend RUM, API spans, and database logs

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

### Database Observability
- **SQL Execution Metrics**: Execution times, costs, and performance data
- **Explain Plans**: Query execution plans with operation details
- **Correlation Tracking**: SQL queries enriched with correlation IDs from frontend interactions
- **Real-time Monitoring**: Buffer gets, disk reads, and I/O metrics
- **Log Types**: 
  - `recent_sql`: SQL statements with embedded correlation IDs
  - `explain_plan`: Query execution plans linked by SQL_ID

### Frontend Observability
- **User Interaction Tracking**: Page loads, clicks, and user journey correlation
- **API Call Correlation**: HTTP requests tagged with correlation IDs for end-to-end tracing
- **Performance Monitoring**: Load times, response times, and user experience metrics
- **Error Tracking**: JavaScript errors and exceptions with context
- **Custom Context**: Correlation IDs in RUM transaction labels and custom fields

### API/Backend Observability
- **Distributed Tracing**: OpenTelemetry spans with correlation attributes
- **Request Correlation**: API requests enriched with correlation metadata
- **Database Operation Tracking**: SQL operations linked to user actions via correlation IDs

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

## Querying Correlation Data in Observe

### Frontend RUM Data
```sql
-- Find RUM transactions with correlation IDs
FIELDS.custom_correlation_id IS NOT NULL
```

### API Span Data  
```sql
-- Find API traces with correlation
FIELDS.correlation.id IS NOT NULL
```

### Database Log Data
```sql
-- Find SQL queries with correlation IDs
FIELDS.logs.attributes.LOG_TYPE = "recent_sql" 
AND FIELDS.logs.attributes.CORRELATION_ID != "none"
```

### Link Frontend to Database
```sql
-- Correlate frontend actions to database queries
SELECT 
  rum.custom_correlation_id,
  logs.CORRELATION_ID,
  logs.body as sql_query
FROM rum_data rum
JOIN database_logs logs 
ON rum.custom_correlation_id = logs.CORRELATION_ID
```

