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

# Copy the main application file
COPY . . 
RUN mkdir -p results uploads

EXPOSE 8000

# サーバ起動コマンド（app.py内にFastAPIのappオブジェクトが「app」として存在する前提）
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]


