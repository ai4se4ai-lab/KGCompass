#!/usr/bin/env bash
# start_web_docker.sh
# KGCompass Web Interface Startup Script (Docker Support Version)

set -euo pipefail

echo "🚀 Starting KGCompass Web Interface (Docker mode)..."

# Check Docker environment
echo "🐳 Checking Docker environment..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed, please install Docker first"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed, please install Docker Compose first"
    exit 1
fi

# Check .env file
if [[ ! -f ".env" ]]; then
    echo "⚠️  .env file does not exist"
    if [[ -f ".env.example" ]]; then
        echo "📄 Creating .env file from .env.example..."
        cp .env.example .env
        echo "✅ Please edit .env file and fill in necessary API keys"
    else
        echo "❌ .env.example file not found"
        echo "💡 Please manually create .env file and set necessary environment variables"
    fi
fi

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
    "templates/patch_view.html"
    "static/css/style.css"
    "static/js/app.js"
    "docker-compose.yml"
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

# Check and start Docker services
echo "🐳 Checking Docker service status..."

# Check if docker-compose.yml contains required services
if ! grep -q "app:" docker-compose.yml; then
    echo "❌ app service not found in docker-compose.yml"
    exit 1
fi

if ! grep -q "neo4j:" docker-compose.yml; then
    echo "❌ neo4j service not found in docker-compose.yml"
    exit 1
fi

# Check existing container status
app_status=$(docker-compose ps -q app 2>/dev/null || echo "")
neo4j_status=$(docker-compose ps -q neo4j 2>/dev/null || echo "")

if [[ -z "$app_status" ]] || [[ -z "$neo4j_status" ]]; then
    echo "🚀 Starting Docker services..."
    docker-compose up -d --build
    echo "⏳ Waiting for services to start..."
    sleep 15
    echo "✅ Docker services started"
else
    echo "✅ Docker services already running"
fi

# Verify Docker services
echo "🔍 Verifying Docker service status..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ Docker services running normally"
else
    echo "❌ Docker service startup failed"
    echo "📋 Service status:"
    docker-compose ps
    exit 1
fi

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export DOCKER_MODE=1

echo ""
echo "======================================================"
echo "🎉 KGCompass Web Interface startup complete! (Docker mode)"
echo "======================================================"
echo "📡 Access URL: http://localhost:5000"
echo "🔧 Development mode: Enabled"
echo "🐳 Docker containers: Started"
echo "📊 Real-time logs: WebSocket supported"
echo "🛠️  Stop service: Ctrl+C"
echo ""
echo "🔧 Docker service management:"
echo "   Check status: docker-compose ps"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Rebuild services: docker-compose up -d --build"
echo ""
echo "💡 Note: Repair process will execute in Docker container"
echo "======================================================"
echo ""

# Start Flask application
echo "🌐 Starting Web service..."
python3 app.py 