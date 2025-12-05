#!/bin/bash

# CostSense-AI Azure Edition - Startup Script
# This script starts all services and verifies they're working

set -e

echo "🚀 Starting CostSense-AI Azure Edition..."
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Start Docker services
echo -e "\n${YELLOW}Step 1: Starting Docker services...${NC}"
docker compose -f docker-compose.azure.yml up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker services started${NC}"
else
    echo -e "${RED}✗ Failed to start Docker services${NC}"
    exit 1
fi

# Step 2: Wait for Ollama to be ready
echo -e "\n${YELLOW}Step 2: Waiting for Ollama to be ready...${NC}"
for i in {1..30}; do
    if docker exec costsense-azure-ollama curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama is ready${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Step 3: Check if llama3.2:latest model exists
echo -e "\n${YELLOW}Step 3: Checking for llama3.2:latest model...${NC}"
if docker exec costsense-azure-ollama ollama list | grep -q "llama3.2:latest"; then
    echo -e "${GREEN}✓ Model llama3.2:latest found${NC}"
else
    echo -e "${YELLOW}⚠ Model not found. Pulling llama3.2:latest (this may take 10-15 minutes)...${NC}"
    docker exec costsense-azure-ollama ollama pull llama3.2:latest
    echo -e "${GREEN}✓ Model downloaded${NC}"
fi

# Step 4: Check Python environment
echo -e "\n${YELLOW}Step 4: Checking Python environment...${NC}"
cd backend

if [ ! -d "venv-azure" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv-azure
fi

source venv-azure/bin/activate

# Install dependencies if needed
if ! python -c "import langchain" 2>/dev/null; then
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip install -q --upgrade pip
    pip install -q -r requirements-azure.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Python environment ready${NC}"
fi

# Step 5: Start backend server
echo -e "\n${YELLOW}Step 5: Starting backend server...${NC}"
echo -e "${GREEN}✓ Starting FastAPI server on http://localhost:8000${NC}"
echo ""
echo -e "${GREEN}=========================================="
echo -e "🎉 CostSense-AI Azure Edition is ready!"
echo -e "=========================================="
echo ""
echo "Backend API:        http://localhost:8000"
echo "API Documentation:  http://localhost:8000/docs"
echo "Health Check:       http://localhost:8000/health"
echo "Agent Status:       http://localhost:8000/api/v1/agent-status"
echo ""
echo "WebSocket:          ws://localhost:8000/ws/cost-analysis"
echo ""
echo -e "Press Ctrl+C to stop the server"
echo -e "==========================================${NC}"
echo ""

# Start the server
python main_azure.py
