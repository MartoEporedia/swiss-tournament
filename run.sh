#!/bin/bash

# Swiss Tournament Simulator - Launch Script

echo "========================================"
echo "  Swiss Tournament Simulator"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Launch application
echo ""
echo "========================================"
echo "  Starting web server..."
echo "========================================"
echo ""

python app.py
