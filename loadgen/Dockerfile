FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y libaio1 wget unzip && \
    rm -rf /var/lib/apt/lists/*

# Instead of cx_Oracle, install python-oracledb
RUN pip install oracledb

WORKDIR /app
COPY loadgen.py .

CMD ["python", "loadgen.py"]