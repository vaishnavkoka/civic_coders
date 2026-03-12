#!/bin/bash

echo "================================================="
echo "  Air Quality Monitoring Dashboard - Setup      "
echo "================================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3 not found. Please install Python 3.8+"; exit 1; }

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q fastapi uvicorn pydantic pandas numpy scikit-learn joblib || {
    echo "Error installing dependencies. Trying with --user flag..."
    pip install --user -q fastapi uvicorn pydantic pandas numpy scikit-learn joblib
}

echo "✓ Dependencies installed"

# Generate data
echo ""
echo "Generating synthetic sensor data..."
cd data
python3 generate_data.py || { echo "Error generating data"; exit 1; }
cd ..

# Train models
echo ""
echo "Training ML models..."
cd models
python3 train_models.py || { echo "Error training models"; exit 1; }
cd ..

echo ""
echo "================================================="
echo "  ✓ Setup Complete!                             "
echo "================================================="
echo ""
echo "To start the dashboard:"
echo "  1. Run: ./run.sh"
echo "  2. Or manually:"
echo "     - Backend: cd backend && python3 api.py"
echo "     - Frontend: Open frontend/index.html in browser"
echo ""
