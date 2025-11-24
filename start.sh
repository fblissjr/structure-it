#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Shutting down services..."
    kill $(jobs -p)
    exit
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

echo "Starting Backend Server..."
# Start backend in background
uv run uvicorn server.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting Frontend..."
# Start frontend in background
cd ui && npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
