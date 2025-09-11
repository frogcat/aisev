FROM python:3.12-slim

ENV no_proxy 0.0.0.0, localhost


# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Copy and install the Zscaler certificate

# Set certificate environment variables for Python

# Install Python dependencies
COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

# Copy the proxy insertion script into the container
COPY insert_proxy_to_openai.sh /app/insert_proxy_to_openai.sh
RUN chmod +x /app/insert_proxy_to_openai.sh

# Run the script to patch the OpenAI client with proxy support
RUN sed -i 's/\r$//' /app/insert_proxy_to_openai.sh
RUN /app/insert_proxy_to_openai.sh


