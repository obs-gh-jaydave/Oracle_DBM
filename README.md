# Oracle Database & Frontend Observability Demo

This demo showcases comprehensive **end-to-end observability** for Oracle databases and frontend applications using OpenTelemetry and Observe Inc's Real User Monitoring (RUM), with **complete correlation tracking** from user interactions to database queries.

## Production-Ready Multi-Instance Oracle Monitoring

This demo now includes **40+ comprehensive Oracle database metrics** and **critical DBA logs** that provide enterprise-grade monitoring with full Oracle XE compatibility, complete descriptions, and production-ready attributes for multi-instance deployments.

## Data Volume & Cost Estimates for Production

### **Metrics (DPM - Data Points per Minute)**

**Per Oracle Instance:**
- **Oracle Database Metrics**: 50+ metrics collected every 10 seconds = **300 DPM**
- **Host/Infrastructure Metrics**: 25+ metrics collected every 30 seconds = **50 DPM**
- **Application Traces**: ~100 traces/hour = **~2 traces/minute**

**Total per Instance: ~350 DPM**

**Scaling Examples:**
- **Single Instance**: 350 DPM = **21,000 DPH** (Data Points per Hour)
- **3 Instances (Demo)**: 1,050 DPM = **63,000 DPH**
- **10 Production Instances**: 3,500 DPM = **210,000 DPH**
- **50 Enterprise Instances**: 17,500 DPM = **1,050,000 DPH**

### **Logs & Traces Volume**

**Per Oracle Instance (with active workload):**
- **Execution Plan Logs**: ~50 logs/hour @ 500 bytes each = **25 KB/hour**
- **Expensive SQL Logs**: ~20 logs/hour @ 300 bytes each = **6 KB/hour**
- **DBA Alert Logs**: ~10 logs/hour @ 200 bytes each = **2 KB/hour**
- **Blocking Session Logs**: ~5 logs/hour @ 400 bytes each = **2 KB/hour**
- **Application Traces**: ~100 traces/hour @ 2KB each = **200 KB/hour**

**Total Log Volume per Instance: ~235 KB/hour = ~5.6 MB/day**

### **Production Cost Estimates (Observe/Similar Platforms)**

**Monthly Estimates:**
- **Single Instance**: 504,000 DPH × 24h × 30d = **~363M data points/month + ~170MB logs**
- **10 Instances**: **~3.6B data points/month + ~1.7GB logs**
- **50 Instances**: **~18B data points/month + ~8.5GB logs**

**Typical Observability Platform Costs:**
- **Metrics**: $0.10-0.30 per 1M data points/month
- **Logs**: $2-5 per GB/month  
- **Traces**: $1-3 per GB/month

**Example Monthly Costs (10 Oracle Instances):**
- **Metrics**: 3.6B points × $0.20/1M = **~$720/month**
- **Logs**: 1.7GB × $3/GB = **~$5/month**
- **Traces**: 6GB × $2/GB = **~$12/month**
- **Total**: **~$737/month for 10 Oracle instances**

## What This Demo Includes

### Multi-Instance Oracle Architecture
- **3 Oracle Database Instances**: Primary (production-style), Secondary (development-style), Legacy (testing-style)
- **Comprehensive DBA Metrics**: 40+ production-ready metrics including critical alerting metrics
- **Advanced Performance Monitoring**: Wait events, tablespace usage, connection limits, long-running transactions
- **Oracle XE Compatibility**: All queries tested and verified compatible with Oracle Express Edition
- **Multi-Instance Support**: Production-ready attributes for environment, datacenter, region identification
- **Real-Time Collection**: 10-second collection intervals with proper cardinality management

### Critical DBA Alerting Metrics
- **Tablespace Usage**: With CRITICAL/WARNING/OK alert levels (>90% = CRITICAL)
- **Wait Events Performance**: Average wait times for top Oracle wait events
- **Connection Pool Health**: Session limit percentage monitoring
- **Long-Running Transactions**: Duration-based alerting for blocking transactions
- **Redo Log Switch Frequency**: I/O load and sizing issue detection

### Performance & Troubleshooting Logs
- **Expensive SQL Queries** (`oracle_expensive_sql`): Queries taking >5 seconds with performance impact classification
- **Blocking Sessions** (`oracle_blocking_sessions`): Real-time blocking session detection with severity levels
- **Execution Plans** (`oracle_correlation_plan`): Oracle execution plans with OpenTelemetry trace/span correlation
- **Alert Log Simulation**: Critical Oracle error monitoring with severity classification

### End-to-End Correlation & Tracing
- **Complete Correlation Tracking**: Track user interactions from frontend → API → database with correlation IDs
- **OpenTelemetry Span Attributes**: Correlation data set as span attributes instead of HTTP headers for APM visibility
- **Oracle-Native Integration**: SQL execution metrics, explain plans, and performance data with embedded correlation tracking
- **OpenTelemetry Standard**: Full distributed tracing pipeline with metrics collection and export to Observe

### Frontend & API Observability
- **Real User Monitoring**: Observe Inc RUM SDK with custom correlation context
- **FastAPI Integration**: Automatic OpenTelemetry instrumentation with correlation propagation
- **Interactive Demo Interface**: Web interface to test various observability scenarios

## Architecture

- **3 Oracle XE Databases**: Primary (1521), Secondary (1522), Legacy (1523) with test data and monitoring users
- **FastAPI Backend**: REST API with OpenTelemetry instrumentation and correlation ID injection
- **OTEL Collector**: Collecting database metrics, traces, and logs with correlation ID extraction
- **Frontend Application**: Web demo with RUM integration and correlation ID generation
- **Nginx Web Server**: Serving the frontend demo with environment variable substitution
- **Load Generator**: Automated realistic user behavior simulation with RUM correlation

## Quick Start (Automated Setup)

### Prerequisites for Running on Apple Silicon

If you're using Apple Silicon, follow these steps:

1. Install Colima:
   ```bash
   brew install colima
   ```

2. Start Colima with specific architecture and memory settings:
   ```bash
   colima start --arch x86_64 --memory 20
   ```

### Running the Demo

**🚀 Fully Automated Setup - Zero Manual Configuration Required!**

1. **Clone and start** (everything is automated):
   ```bash
   git clone <repo>
   cd oracle-otel-demo
   docker compose up -d
   ```

2. **Wait for initialization** (~3-4 minutes for all databases):
   ```bash
   # Watch the logs - wait for all instances to show "Database opened."
   docker compose logs -f oracle-db-primary oracle-db-secondary oracle-db-legacy
   ```

3. **Validate setup** (recommended):
   ```bash
   # Quick validation script to ensure everything is working
   ./scripts/validate-setup.sh
   ```

4. **Access the demo**:
   ```
   Frontend Demo: http://localhost:8081
   Prometheus Metrics: http://localhost:9464/metrics
   API Docs: http://localhost:8000/docs
   ```

### What's Automatically Configured

**3 Oracle Database Instances** with different configurations:
- **Primary Instance** (oracle-db-primary:1521) - Production-style OLTP workload
- **Secondary Instance** (oracle-db-secondary:1522) - Development/Analytics workload  
- **Legacy Instance** (oracle-db-legacy:1523) - Batch/Reporting workload

**Database Users & Schemas** created automatically in all instances:
- **OTEL_MONITOR users** with comprehensive monitoring privileges for 40+ metrics
- **TESTUSER with employees table** containing sample data (3-14 records per instance)
- **All necessary indexes** (emp_salary_idx, emp_hire_date_idx) for optimal performance
- **Oracle correlation context** setup for OpenTelemetry tracking

**Multi-Instance Monitoring** with proper correlation:
- **oracle_correlation_plan logs** generated from all three database instances
- **Distinct resource attributes** for each instance (PROD-ORACLE-01, DEV-ORACLE-02, LEGACY-ORACLE-03)
- **40+ Oracle metrics per instance** immediately available in Prometheus
- **Real-time correlation tracking** from frontend through API to database execution plans

**Load Generation & Activity**:
- **Automated load generator** creates realistic multi-instance workload
- **Primary database**: 70% of load (production simulation)
- **Secondary database**: 30% of load (development/reporting)
- **Correlation tracking** embedded in all generated SQL queries

### Troubleshooting & Validation

**Automated Fix Scripts** - Use these if you encounter any issues:

```bash
# Complete database initialization with retry logic and validation
./scripts/init-database.sh

# Quick validation of all components (recommended after startup)
./scripts/validate-setup.sh

# Check container status
docker compose ps

# View specific database logs
docker compose logs oracle-db-primary
docker compose logs oracle-db-secondary 
docker compose logs oracle-db-legacy
```

**Validation Script Output** - What to expect from `./scripts/validate-setup.sh`:
```
Container Status:
✓ oracle-db-primary is running
✓ oracle-db-secondary is running  
✓ oracle-db-legacy is running
✓ otel-collector is running

Database Connectivity:
✓ primary instance is accessible
✓ secondary instance is accessible
✓ legacy instance is accessible

Monitoring Users:
✓ primary OTEL_MONITOR user is working
✓ secondary OTEL_MONITOR user is working
✓ legacy OTEL_MONITOR user is working

Test Schemas:
✓ primary TESTUSER schema has 14 employee records
✓ secondary TESTUSER schema has 3 employee records
✓ legacy TESTUSER schema has 3 employee records
```

**Common Issues & Solutions:**

| Issue | Solution | Command |
|-------|----------|---------|
| Containers not starting | Restart containers | `docker compose down && docker compose up -d` |
| Database initialization failed | Run setup script | `./scripts/init-database.sh` |
| Missing users/schemas | Run setup script | `./scripts/init-database.sh` |
| No OTEL metrics appearing | Validate setup | `./scripts/validate-setup.sh` |
| Oracle correlation logs missing | Wait or generate activity | Visit http://localhost:8081 |
| Apple Silicon compatibility | Use x86_64 architecture | `colima start --arch x86_64 --memory 20` |

**Complete Reset** (if needed):
```bash
# Reset everything with fresh databases
docker compose down -v
docker compose up -d
# Wait 3-4 minutes for initialization
./scripts/validate-setup.sh
```

**Expected Results After Setup:**
- All 3 Oracle instances running and accessible
- OTEL_MONITOR users created with monitoring privileges in all databases
- TESTUSER schemas with employees table and sample data
- oracle_correlation_plan logs being generated from all three instances
- 40+ Oracle metrics per instance available at http://localhost:9464/metrics
- Load generator creating realistic cross-instance database activity

## Production Oracle Metrics (40+ Metrics - Oracle XE Compatible)

### **Metric Collection Summary**
- **Total Metrics**: 40+ time series across 3 database instances
- **Collection Frequency**: Every 10 seconds (Oracle), Every 30 seconds (Host)
- **Data Points per Minute**: ~350 DPM per Oracle instance
- **Cardinality**: Production-safe with proper attribute management
- **Backend Integration**: Full Observe compatibility with descriptions and metadata
- **Oracle XE Compatibility**: All queries verified compatible with Oracle Express Edition limitations

### **Critical DBA Metrics Categories**

#### Alerting-Priority Metrics
```
oracle.tablespace.usage_percent     - Tablespace usage with CRITICAL/WARNING levels
oracle.wait_events.average_time_ms  - Wait event performance monitoring
oracle.connections.limit_percent    - Session pool health monitoring
oracle.transactions.duration_minutes - Long-running transaction detection
oracle.redo.switches_per_hour       - Redo log switching frequency
```

#### Core Performance Metrics
```
oracle.sessions.active              - Active user sessions
oracle.sessions.total               - Total user sessions
oracle.memory.sga_size              - System Global Area size
oracle.performance.buffer_cache_hit_ratio - Buffer cache efficiency
oracle.performance.library_cache_hit_ratio - Library cache efficiency
oracle.performance.shared_pool_free_percent - Shared pool memory
```

#### Storage & I/O Metrics
```
oracle.tablespace.size              - Tablespace allocated size
oracle.tablespace.used              - Tablespace used space
oracle.io.physical_reads            - Physical disk reads
oracle.io.physical_writes           - Physical disk writes
oracle.redo.size_bytes              - Redo log transaction volume
```

#### Lock & Contention Metrics
```
oracle.locks.deadlocks_total        - Deadlock detection
oracle.locks.waits_total            - Lock wait frequency
oracle.locks.blocked_sessions       - Currently blocked sessions
oracle.locks.wait_time_seconds      - Lock wait duration by type
```

### **Alert Level Integration**
All critical metrics include alert levels:
- **CRITICAL**: Immediate attention required (e.g., >90% tablespace usage)
- **WARNING**: Monitoring recommended (e.g., >80% tablespace usage)
- **OK**: Normal operation

### **Sample Metric with Alerting**
```
oracle_tablespace_usage_percent{
  ALERT_LEVEL="CRITICAL",
  TABLESPACE_NAME="SYSTEM",
  FREE_SIZE_MB="2.63",
  TOTAL_SIZE_MB="272",
  oracle_alerting_priority="critical"
} 99.03
```

## DBA Performance & Troubleshooting Logs

### **Log Types with Production Value**

#### Expensive SQL Detection (`oracle_expensive_sql`)
- **Purpose**: Identify queries taking >5 seconds for performance tuning
- **Attributes**: SQL_ID, execution time, CPU time, buffer gets, performance impact level
- **Value**: Proactive performance optimization and bottleneck identification

#### Blocking Session Analysis (`oracle_blocking_sessions`)
- **Purpose**: Real-time detection of blocking sessions >30 seconds
- **Attributes**: Blocker/blocked session details, wait event, duration, severity
- **Value**: Immediate troubleshooting of production performance issues

#### Execution Plan Correlation (`oracle_correlation_plan`)
- **Purpose**: Link database execution plans to application traces
- **Attributes**: Full execution plan with OpenTelemetry trace/span IDs
- **Value**: End-to-end performance analysis from user click to database operation

## End-to-End Correlation Flow

This demo implements complete **OpenTelemetry-native correlation tracking** across all layers:

1. **Frontend Click** → RUM SDK generates OpenTelemetry trace context automatically
2. **RUM Transaction** → Creates APM trace with correlation ID and custom labels
3. **API Request** → Receives trace context via distributed tracing headers (no manual headers needed)
4. **API Span** → Extracts correlation from OpenTelemetry trace/span IDs
5. **Database Query** → Embeds full OpenTelemetry context + correlation in SQL comments
6. **OTEL Collector** → Extracts real APM trace/span IDs and correlation from SQL text
7. **Observe** → Dashboards, monitors & explorers linking frontend → API → database operations

### Correlation Format (RUM Correlation Removed)
- **OpenTelemetry Trace ID**: `498f7f4d8c70f0b3d8ef243ed48eb913` (32 characters)
- **OpenTelemetry Span ID**: `3fc5f9b6c39c2f0e` (16 characters)
- **Visibility**: Available in frontend RUM, API spans, and database execution plans

## Configuration

The demo uses environment variables configured in `.env` file:

### **Core Configuration Variables**
- `OBSERVE_TENANT_ID`: Your Observe tenant ID
- `OBSERVE_RUM_BEARER_TOKEN`: Your Frontend RUM bearer token
- `OBSERVE_BACKEND_BEARER_TOKEN`: Your Backend/database bearer token
- `OBSERVE_RUM_ENVIRONMENT`: Your deployment environment
- `OBSERVE_RUM_SERVICE_NAME`: Your application/service name

### **Multi-Instance Oracle Configuration**
```bash
# Primary Instance
ORACLE_PASSWORD_PRIMARY=YourSecurePassword123
ORACLE_INSTANCE_NAME_PRIMARY=PROD-ORACLE-01
ORACLE_HOST_PRIMARY=oracle-db-primary

# Secondary Instance  
ORACLE_PASSWORD_SECONDARY=YourSecurePassword456
ORACLE_INSTANCE_NAME_SECONDARY=DEV-ORACLE-02
ORACLE_HOST_SECONDARY=oracle-db-secondary

# Legacy Instance
ORACLE_PASSWORD=YourSecurePassword789
ORACLE_INSTANCE_NAME=LEGACY-ORACLE-03
ORACLE_HOST=oracle-db
```

## What Gets Monitored

### Enterprise Oracle Database Monitoring (40+ Oracle XE Compatible Metrics)
- **Session Management**: Active/total user sessions with connection pool health
- **Memory Utilization**: SGA size and shared pool efficiency monitoring
- **Storage Management**: Tablespace usage with critical alerting levels for all Oracle XE tablespaces
- **Performance Monitoring**: Cache hit ratios, wait events, and performance bottlenecks
- **I/O Operations**: Physical read/write operations and transaction log volume
- **Lock Management**: Deadlock detection, blocking sessions, and contention analysis
- **Transaction Monitoring**: Long-running transactions and redo log frequency
- **Connection Health**: Session limit monitoring and pool exhaustion detection

### Advanced DBA Observability
- **SQL Execution Metrics**: Real-time execution times, CPU usage, I/O metrics with APM correlation
- **Execution Plans**: Query execution plans with full OpenTelemetry trace/span IDs
- **Expensive Query Detection**: Automatic identification of queries >5 seconds with performance classification
- **Blocking Session Analysis**: Real-time blocking session detection with severity levels
- **Alert Log Monitoring**: Critical Oracle error detection with severity classification

### Frontend Observability (Observe RUM)
- **OpenTelemetry Integration**: Elastic APM RUM SDK with automatic trace context generation
- **Distributed Tracing**: Automatic propagation of trace context to API calls
- **User Journey Tracking**: Complete user interaction correlation with APM traces
- **Performance Monitoring**: Real User Monitoring with Core Web Vitals and response times
- **Error Tracking**: JavaScript errors and exceptions with full trace context

### API/Backend Observability (FastAPI + OpenTelemetry)
- **Automatic Instrumentation**: FastAPI automatically instrumented with OpenTelemetry
- **Trace Context Propagation**: Receives and processes RUM trace context from frontend
- **Span Attributes**: Correlation data set as OpenTelemetry span attributes for APM visibility
- **Oracle Integration**: Embeds APM trace/span IDs directly in SQL comments for correlation
- **Database Operation Tracking**: Every SQL operation linked to originating APM trace/span

## Demo Features

The interactive demo at `http://localhost:8081` includes:

### Oracle Database API Calls (with Correlation Tracking)
- **Get All Employees**: Triggers FULL table scan with correlation ID embedding
- **High Salary Filter**: Uses INDEX range scan with correlation tracking
- **Salary Analytics**: GROUP BY aggregation with correlation context
- **Add New Employee**: INSERT operation with correlation ID propagation
- **Complex Join Query**: Self-join operations with end-to-end tracing
- **Slow Query**: Performance testing with correlation tracking

### Enhanced Multi-Instance Load Generator
The demo includes an **automated load generator** that creates realistic production-like load:

#### **Multi-Instance Load Distribution**
- **Primary Database**: 70% of load (production workload simulation)
- **Secondary Database**: 30% of load (development/reporting workload)
- **Realistic Patterns**: Weighted scenario selection based on typical enterprise usage

#### **Load Generation Statistics**
- **Frequency**: 2-8 second intervals between requests
- **Volume**: ~450-900 requests/hour across all instances
- **Correlation**: Every request includes proper OpenTelemetry trace context
- **SQL Variety**: Mix of FULL scans, INDEX scans, JOINs, and aggregations

## What You'll See in Observe

### **Oracle Database Metrics in Observe**
All Oracle metrics appear with comprehensive organization:

#### **Sample Observe Data Structure**
```json
{
  "FIELDS": {
    "name": "oracle.tablespace.usage_percent",
    "value": 99.03,
    "type": "gauge"
  },
  "EXTRA": {
    "description": "Tablespace usage percentage - critical for space monitoring and alerting",
    "attributes": {
      "TABLESPACE_NAME": "SYSTEM",
      "ALERT_LEVEL": "CRITICAL",
      "oracle.alerting.priority": "critical"
    },
    "resource": {
      "oracle.instance.name": "PROD-ORACLE-01",
      "environment": "production",
      "datacenter": "us-east-1a",
      "service.name": "oracle-database-primary"
    }
  }
}
```

#### **Dashboard Organization**
1. **Multi-Instance Overview**: Monitor all 3 Oracle instances simultaneously
2. **Critical Alerts**: Focus on ALERT_LEVEL="CRITICAL" metrics for immediate attention
3. **Performance Analysis**: Use wait events and expensive SQL logs for optimization
4. **Capacity Planning**: Track tablespace usage trends and growth patterns
5. **Troubleshooting**: Correlate blocking sessions with application performance

### **End-to-End Correlation Data**
- **Frontend RUM**: OpenTelemetry trace context and user action metadata
- **API Spans**: Distributed traces with correlation attributes and database operation metadata
- **Database Logs**: Execution plans and performance metrics with full APM correlation
- **Complete Traceability**: End-to-end tracing from frontend → API → database operations

## Production Deployment Ready

This solution provides enterprise-grade Oracle database observability with:
- **✅ Multi-Instance Architecture**: 3 Oracle databases with differentiated monitoring
- **✅ 40+ Production Metrics**: Comprehensive DBA monitoring with critical alerting
- **✅ Advanced Performance Logs**: Expensive SQL, blocking sessions, execution plans
- **✅ Complete Correlation**: OpenTelemetry trace/span correlation throughout
- **✅ Oracle XE to Enterprise Compatibility**: Works across all Oracle editions
- **✅ Zero-Configuration Setup**: Automated TESTUSER and schema creation
- **✅ Production Cost Estimates**: Clear data volume and cost projections
- **✅ Automated Load Generation**: Realistic multi-instance workload simulation
- **✅ Container Persistence**: Database state maintained across restarts

**Deploy this solution in your environment and gain enterprise-grade Oracle database observability with complete correlation tracking, critical alerting, and comprehensive DBA insights that scale from development to production.**

## Data Volume Summary

**Per Oracle Instance (Production Workload):**
- **350 DPM** (Data Points per Minute)
- **21,000 DPH** (Data Points per Hour)  
- **235 KB/hour** of logs and traces
- **Monthly**: ~363M data points + ~170MB logs

**Cost-effective observability** with comprehensive coverage providing everything DBAs need for production Oracle monitoring, performance optimization, and troubleshooting.