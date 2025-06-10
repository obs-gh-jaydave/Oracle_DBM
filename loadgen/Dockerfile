FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y libaio1 wget unzip && \
    rm -rf /var/lib/apt/lists/*

# Install required Python packages
RUN pip install requests

WORKDIR /app
COPY loadgen.py .

CMD ["python", "loadgen.py"]