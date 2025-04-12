#!/bin/bash
set -e

echo "Starting Docker container..."

# Update MongoDB URI in .env file
echo "Updating MongoDB URI..."
# Use MongoDB container name directly over Docker network
sed -i 's|MONGO_URI="mongodb://[^"]*"|MONGO_URI="mongodb://mongodb:27017"|g' /app/.env
echo "MongoDB URI updated: mongodb://mongodb:27017"

# Check MongoDB connection
echo "Testing MongoDB connection..."
timeout 5 bash -c 'until nc -z mongodb 27017 2>/dev/null; do echo -n "."; sleep 1; done' || echo "Could not connect to MongoDB, but services will start anyway"

echo "Starting log service..."
# Start the FastAPI service in the background
uvicorn log_service:app --host 0.0.0.0 --port 8000 &
LOG_SERVICE_PID=$!

# Wait a short time for service to start
echo "Waiting for log service to start..."
sleep 3

# Check if service is running
if kill -0 $LOG_SERVICE_PID 2>/dev/null; then
    echo "Log service started successfully (PID: $LOG_SERVICE_PID)"
else
    echo "WARNING: There may be an issue starting the log service!"
fi

# Start Streamlit
echo "Starting Streamlit application..."
streamlit run stapp.py --server.port=8501 --server.address=0.0.0.0
