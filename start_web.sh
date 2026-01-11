#!/usr/bin/env bash
# start_web.sh
# KGCompass Web Interface Quick Startup Script

set -euo pipefail

echo "🚀 Starting KGCompass Web Interface..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
echo "📍 Python version: $python_version"

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing/updating dependencies..."
pip install -r requirements_web.txt

# Create necessary directories
echo "📁 Creating output directories..."
mkdir -p web_outputs
mkdir -p static/css static/js templates

# Check required files
echo "🔍 Checking required files..."
required_files=(
    "app.py"
    "templates/index.html"
    "static/css/style.css"
    "static/js/app.js"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -gt 0 ]]; then
    echo "❌ Missing required files:"
    printf "   - %s\n" "${missing_files[@]}"
    echo "Please ensure all files are created"
    exit 1
fi

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

echo ""
echo "======================================================"
echo "🎉 KGCompass Web Interface startup complete!"
echo "======================================================"
echo "📡 Access URL: http://localhost:5000"
echo "🔧 Development mode: Enabled"
echo "📊 Real-time logs: WebSocket supported"
echo "🛠️  Stop service: Ctrl+C"
echo "======================================================"
echo ""

# Start Flask application
python3 app.py 