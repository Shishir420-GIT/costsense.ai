#!/bin/bash

echo "🚀 Starting AWS Cost Optimization Platform in development mode..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if environment file exists
if [ ! -f "backend/.env" ]; then
    print_error "Environment file not found!"
    print_warning "Please run ./setup.sh first or create backend/.env from backend/.env.example"
    exit 1
fi

# Function to cleanup processes
cleanup() {
    echo ""
    print_status "🛑 Stopping all services..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        print_status "Backend stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        print_status "Frontend stopped"
    fi
    
    docker-compose down
    print_success "Infrastructure services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start infrastructure services
print_status "🐳 Starting infrastructure services..."
docker-compose up -d postgres redis ollama

# Wait for services
print_status "⏳ Waiting for services..."
sleep 15

# Check service health
print_status "🏥 Checking service health..."

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U postgres &> /dev/null; then
    print_success "PostgreSQL is healthy"
else
    print_warning "PostgreSQL may not be ready yet"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping | grep -q PONG 2>/dev/null; then
    print_success "Redis is healthy"
else
    print_warning "Redis may not be ready yet"
fi

# Check Ollama
if curl -s http://localhost:11434/api/tags &> /dev/null; then
    print_success "Ollama is healthy"
else
    print_warning "Ollama may not be ready yet"
fi

# Start backend in background
print_status "🐍 Starting backend..."
cd backend

if [ ! -d "venv" ]; then
    print_error "Virtual environment not found! Please run ./setup.sh first"
    cd ..
    exit 1
fi

source venv/bin/activate
nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
print_status "Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health &> /dev/null; then
        print_success "Backend is running on http://localhost:8000"
        break
    fi
    echo -n "."
    sleep 2
done

# Start frontend in background
print_status "⚛️ Starting frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    print_error "Node modules not found! Please run ./setup.sh first"
    cd ..
    exit 1
fi

nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
print_status "Waiting for frontend to start..."
for i in {1..30}; do
    if curl -s http://localhost:3000 &> /dev/null; then
        print_success "Frontend is running on http://localhost:3000"
        break
    fi
    echo -n "."
    sleep 2
done

print_success "🎉 Application started successfully!"
echo ""
echo "🌐 Access URLs:"
echo "• Frontend: http://localhost:3000"
echo "• Backend API: http://localhost:8000"
echo "• API Documentation: http://localhost:8000/docs"
echo "• System Health: http://localhost:8000/health"
echo ""
echo "📊 Service Status:"
echo "• PostgreSQL: localhost:5432"
echo "• Redis: localhost:6379"  
echo "• Ollama: http://localhost:11434"
echo ""
echo "📝 Logs:"
echo "• Backend: logs/backend.log"
echo "• Frontend: logs/frontend.log"
echo "• Docker: docker-compose logs"
echo ""
print_warning "Press Ctrl+C to stop all services"
echo ""

# Keep script running and show real-time logs
print_status "📋 Real-time status monitoring (press Ctrl+C to exit)..."

while true; do
    sleep 30
    
    # Check if processes are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_error "Backend process died!"
        break
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_error "Frontend process died!"
        break
    fi
    
    # Show a heartbeat
    echo -n "💓"
done

# If we get here, something went wrong
cleanup