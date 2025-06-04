FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y libaio1 wget unzip && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install fastapi uvicorn oracledb opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-requests opentelemetry-exporter-otlp opentelemetry-instrumentation-sqlalchemy

WORKDIR /app
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]