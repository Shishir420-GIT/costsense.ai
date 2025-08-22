#!/bin/bash

echo "🚀 Setting up AWS Cost Optimization Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    echo "Visit: https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3.11+ is not installed. Please install Python first."
    echo "Visit: https://python.org/"
    exit 1
fi

print_status "📋 System requirements check passed!"

# Create environment file
print_status "📝 Creating environment file..."
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    print_success "Environment file created"
    print_warning "Please update backend/.env with your AWS credentials and settings"
else
    print_warning "Environment file already exists, skipping creation"
fi

# Create necessary directories
print_status "📁 Creating project directories..."
mkdir -p backend/logs
mkdir -p backend/reports
mkdir -p docs
print_success "Project directories created"

# Start infrastructure services
print_status "🐳 Starting infrastructure services..."
docker-compose up -d postgres redis ollama

# Wait for services to be ready
print_status "⏳ Waiting for services to start..."
echo "Postgres, Redis, and Ollama are starting up..."

# Wait for PostgreSQL
print_status "Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U postgres &> /dev/null; then
        print_success "PostgreSQL is ready"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Redis
print_status "Waiting for Redis..."
for i in {1..30}; do
    if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
        print_success "Redis is ready"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for Ollama
print_status "Waiting for Ollama..."
for i in {1..60}; do
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        print_success "Ollama is ready"
        break
    fi
    echo -n "."
    sleep 3
done

# Pull Ollama model
print_status "📥 Pulling Ollama model..."
if docker exec cost-optimizer-ollama ollama pull llama2; then
    print_success "Llama2 model downloaded"
else
    print_warning "Failed to download Llama2 model. You can do this later with: docker exec cost-optimizer-ollama ollama pull llama2"
fi

# Install backend dependencies
print_status "🐍 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Python virtual environment created"
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install --upgrade pip
if pip install -r requirements.txt; then
    print_success "Backend dependencies installed"
else
    print_error "Failed to install backend dependencies"
    cd ..
    exit 1
fi

cd ..

# Install frontend dependencies
print_status "⚛️ Setting up frontend..."
cd frontend

if npm install; then
    print_success "Frontend dependencies installed"
else
    print_error "Failed to install frontend dependencies"
    cd ..
    exit 1
fi

cd ..

print_success "Setup complete!"
echo ""
echo "🎉 AWS Cost Optimization Platform is ready!"
echo ""
echo "📖 Next steps:"
echo "1. Update backend/.env with your AWS credentials"
echo "2. Start the development servers:"
echo "   • Backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "   • Frontend: cd frontend && npm run dev"
echo ""
echo "🌐 URLs:"
echo "• Frontend: http://localhost:3000"
echo "• Backend API: http://localhost:8000"
echo "• API Documentation: http://localhost:8000/docs"
echo "• PostgreSQL: localhost:5432 (postgres/password)"
echo "• Redis: localhost:6379"
echo "• Ollama: http://localhost:11434"
echo ""
echo "🔧 Alternative: Use the development script:"
echo "   ./start-dev.sh"
echo ""
print_warning "Note: Make sure to configure your AWS credentials in backend/.env before starting!"
print_warning "The Strands Agents require proper Ollama setup to function correctly."