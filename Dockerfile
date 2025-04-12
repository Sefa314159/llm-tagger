FROM python:3.11-slim

# Install required packages
RUN apt-get update && apt-get install -y procps netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose ports for the FastAPI service and Streamlit
EXPOSE 8000
EXPOSE 8501

# Use a startup script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
