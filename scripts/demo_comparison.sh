#!/bin/bash
# Demo script: Compare Plain API vs Enhanced System

echo "🚀 MAPI System Comparison Demo"
echo "================================"
echo ""
echo "This demo compares:"
echo "1. Plain API (baseline - limited knowledge)"
echo "2. Enhanced System (our algorithm + trained knowledge)"
echo ""

# Check if API is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is running"
    echo ""
    echo "Running comparison..."
    echo ""
    python3 scripts/compare_systems.py
else
    echo "⚠️  API is not running"
    echo ""
    echo "Starting API in background..."
    cd apps/api && PYTHONPATH=../.. uvicorn main:app --port 8000 > /tmp/mapi_api.log 2>&1 &
    API_PID=$!
    echo "API started (PID: $API_PID)"
    echo "Waiting for API to be ready..."
    sleep 5
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is ready"
        echo ""
        echo "Running comparison..."
        echo ""
        python3 scripts/compare_systems.py
        
        echo ""
        echo "Stopping API..."
        kill $API_PID
    else
        echo "❌ API failed to start"
        echo "Start manually with: make api"
    fi
fi

