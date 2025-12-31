#!/bin/bash
# Trade-Scan Start Script

set -e

echo "🚀 Starting Trade-Scan..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Start the backend server
echo "🌐 Starting backend API server..."
echo "   API will be available at http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""

cd backend
python main.py
