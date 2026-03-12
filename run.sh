#!/bin/bash

echo "================================================="
echo "  Air Quality Monitoring Dashboard - Starting   "
echo "================================================="
echo ""

# Check if data exists
if [ ! -f "data/sensor_data.csv" ]; then
    echo "⚠ Data not found. Please run ./setup.sh first"
    exit 1
fi

# Check if models exist
if [ ! -f "models/aqi_predictor.pkl" ]; then
    echo "⚠ Models not found. Please run ./setup.sh first"
    exit 1
fi

echo "Starting backend API server..."
echo "Backend will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo ""

cd backend
python3 api.py &
BACKEND_PID=$!

echo "Backend started (PID: $BACKEND_PID)"
echo ""
echo "Waiting for backend to initialize..."
sleep 3

echo ""
echo "================================================="
echo "  ✓ Dashboard is Ready!                         "
echo "================================================="
echo ""
echo "📊 Frontend Dashboard:"
echo "   Open: frontend/index.html"
echo "   Or run: cd frontend && python3 -m http.server 8080"
echo "   Then navigate to: http://localhost:8080"
echo ""
echo "🔌 API Endpoints:"
echo "   http://localhost:8000/api/dashboard_summary"
echo "   http://localhost:8000/docs (Swagger UI)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Stopping backend...'; kill $BACKEND_PID; exit 0" INT
wait
