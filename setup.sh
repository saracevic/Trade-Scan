#!/bin/bash
# Trade-Scan Setup Script

set -e

echo "🚀 Trade-Scan Setup Script"
echo "=========================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version found"

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo "✅ Virtual environment activated"

# Install dependencies
echo ""
echo "📦 Installing backend dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r backend/requirements.txt
echo "✅ Dependencies installed"

# Create .env file
echo ""
echo "⚙️  Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
else
    echo "ℹ️  .env file already exists"
fi

# Run tests
echo ""
echo "🧪 Running tests..."
cd backend
python -m pytest tests/ -v --tb=short
test_status=$?
cd ..

if [ $test_status -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "⚠️  Some tests failed"
fi

echo ""
echo "=========================="
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "  python backend/main.py"
echo ""
echo "API will be available at:"
echo "  http://localhost:5000"
echo ""
echo "Frontend is available at:"
echo "  Open index.html in your browser"
echo ""
