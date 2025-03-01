#!/bin/bash

# Start backend
cd backend
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Function to kill processes on exit
function cleanup {
    echo "Stopping services..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

# Trap Ctrl+C
trap cleanup SIGINT

# Keep script running
wait