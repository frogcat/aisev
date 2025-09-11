FROM python:3.12-slim

# Set environment variables for proxy
ENV no_proxy 0.0.0.0, localhost

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# Install Python dependencies
COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5010"]
