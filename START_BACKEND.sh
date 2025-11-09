#!/bin/bash
# Quick script to start the backend API

echo "🚀 Starting AIATL Memory System Backend..."
echo ""

cd "$(dirname "$0")/apps/api"

# Check if uvicorn is installed
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo "Starting API server on http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

PYTHONPATH=../.. uvicorn main:app --reload --port 8000

