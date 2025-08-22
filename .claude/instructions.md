# AWS Cost Optimization Platform - Complete Build Instructions for Claude Code

## 🎯 **Project Overview**

Build a production-ready AWS Cost Optimization platform using:
- **Frontend**: React 18 + TypeScript + Tailwind CSS + Vite
- **Backend**: FastAPI + Python 3.11
- **Agents**: Strands Agents SDK with multi-agent orchestration
- **LLM**: Ollama (local) with Llama 2/Code Llama
- **Database**: PostgreSQL + Redis
- **Charts**: D3.js + Chart.js + Recharts
- **Real-time**: WebSockets
- **AWS**: Boto3 read-only tools

---

## 📁 **Complete Project Structure**

```
aws-cost-optimizer/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── frontend/                          # React TypeScript Application
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   ├── public/
│   │   └── favicon.ico
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── components/
│       │   ├── Dashboard/
│       │   │   ├── CostAnalyticsDashboard.tsx
│       │   │   ├── OptimizationDashboard.tsx
│       │   │   └── AgentStatusPanel.tsx
│       │   ├── Charts/
│       │   │   ├── CostTrendChart.tsx
│       │   │   ├── ServiceBreakdownChart.tsx
│       │   │   ├── SavingsProjectionChart.tsx
│       │   │   └── UtilizationHeatmap.tsx
│       │   ├── Chat/
│       │   │   ├── ChatInterface.tsx
│       │   │   ├── MessageBubble.tsx
│       │   │   └── AgentTypingIndicator.tsx
│       │   ├── Reports/
│       │   │   ├── ReportViewer.tsx
│       │   │   ├── ReportExporter.tsx
│       │   │   └── EmailReportSender.tsx
│       │   └── Layout/
│       │       ├── Header.tsx
│       │       ├── Sidebar.tsx
│       │       └── Footer.tsx
│       ├── hooks/
│       │   ├── useWebSocket.ts
│       │   ├── useAgentStatus.ts
│       │   ├── useCostData.ts
│       │   └── useChartData.ts
│       ├── store/
│       │   ├── costStore.ts
│       │   ├── agentStore.ts
│       │   ├── userStore.ts
│       │   └── appStore.ts
│       ├── services/
│       │   ├── api.ts
│       │   ├── websocket.ts
│       │   └── chartHelpers.ts
│       ├── types/
│       │   ├── cost.types.ts
│       │   ├── agent.types.ts
│       │   └── api.types.ts
│       └── utils/
│           ├── formatters.ts
│           ├── constants.ts
│           └── helpers.ts
├── backend/                           # FastAPI Python Application
│   ├── requirements.txt
│   ├── main.py
│   ├── .env
│   └── src/
│       ├── __init__.py
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings.py
│       │   └── database.py
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base_agent.py
│       │   ├── cost_analysis_agent.py
│       │   ├── remediation_agent.py
│       │   ├── calculation_agent.py
│       │   ├── documentation_agent.py
│       │   ├── reporting_agent.py
│       │   └── orchestrator_agent.py
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── aws_tools.py
│       │   ├── cost_explorer_tool.py
│       │   ├── ec2_tools.py
│       │   ├── s3_tools.py
│       │   ├── rds_tools.py
│       │   ├── lambda_tools.py
│       │   └── calculation_tools.py
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── cost_optimization.py
│       │   ├── agents.py
│       │   ├── reports.py
│       │   └── websocket.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── cost_models.py
│       │   ├── agent_models.py
│       │   └── user_models.py
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── websocket_manager.py
│       │   ├── rag_system.py
│       │   ├── data_manager.py
│       │   ├── security.py
│       │   ├── monitoring.py
│       │   └── logging_config.py
│       └── tests/
│           ├── __init__.py
│           ├── test_agents.py
│           ├── test_aws_tools.py
│           └── test_api.py
└── docs/
    ├── SETUP.md
    ├── API.md
    ├── AGENTS.md
    └── DEPLOYMENT.md
```

---

## 🔧 **Environment Configuration**

### `.env` file (create in backend/ directory):
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Database Configuration
POSTGRES_URL=postgresql://postgres:password@localhost:5432/costoptimization
REDIS_URL=redis://localhost:6379

# API Configuration
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=["http://localhost:3000"]

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ENCRYPTION_KEY=your-encryption-key-for-sensitive-data

# Strands Agents Configuration
STRANDS_MODEL_PROVIDER=ollama
STRANDS_DEFAULT_MODEL=llama2
STRANDS_SESSION_STORAGE=postgresql

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
MAX_CONCURRENT_AGENTS=5
AGENT_TIMEOUT=300
CACHE_EXPIRY_HOURS=24
```

---

## 📦 **Dependencies and Package Files**

### Backend Requirements (`backend/requirements.txt`):
```txt
# FastAPI and Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
python-multipart==0.0.6
python-dotenv==1.0.0

# Strands Agents Framework
strands-agents==1.4.0
strands-agents-tools==1.0.0

# AWS SDK and Tools
boto3==1.34.0
botocore==1.34.0

# Ollama Integration
ollama==0.1.7

# Database and Storage
psycopg2-binary==2.9.9
redis==5.0.1
sqlalchemy==2.0.23
alembic==1.13.1

# Vector Database for RAG
chromadb==0.4.18
sentence-transformers==2.2.2

# Data Processing
pandas==2.1.4
numpy==1.24.3

# HTTP and Web
aiohttp==3.9.1
requests==2.31.0
beautifulsoup4==4.12.2

# Security and Encryption
cryptography==41.0.8
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0

# Utilities
pydantic==2.5.0
asyncio-throttle==1.0.2
python-slugify==8.0.1

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

### Frontend Package (`frontend/package.json`):
```json
{
  "name": "aws-cost-optimizer-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.2.0",
    "zustand": "^4.4.7",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    "d3": "^7.8.5",
    "@types/d3": "^7.4.3",
    "recharts": "^2.8.0",
    "axios": "^1.6.0",
    "@tanstack/react-query": "^5.8.0",
    "framer-motion": "^10.16.0",
    "lucide-react": "^0.294.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "date-fns": "^2.30.0",
    "react-hot-toast": "^2.4.1",
    "react-loading-skeleton": "^3.3.1"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.1.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.45.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5"
  }
}
```

---

## 🐳 **Docker Configuration**

### `docker-compose.yml`:
```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: cost-optimizer-postgres
    environment:
      POSTGRES_DB: costoptimization
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_HOST_AUTH_METHOD: trust
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: cost-optimizer-redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Ollama for Local LLM
  ollama:
    image: ollama/ollama:latest
    container_name: cost-optimizer-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_KEEP_ALIVE=24h
      - OLLAMA_HOST=0.0.0.0
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Backend API
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    container_name: cost-optimizer-backend
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_URL=postgresql://postgres:password@postgres:5432/costoptimization
      - REDIS_URL=redis://redis:6379
      - OLLAMA_HOST=http://ollama:11434
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      ollama:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - /app/.venv
    restart: unless-stopped

  # Frontend React App
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: cost-optimizer-frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
      - VITE_WS_URL=ws://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  ollama_data:
    driver: local
```

---

## 🚀 **Core Implementation Files**

### Backend Main Application (`backend/main.py`):
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
from contextlib import asynccontextmanager

from src.routers import cost_optimization, agents, reports, websocket
from src.utils.websocket_manager import ConnectionManager
from src.config.settings import Settings
from src.utils.logging_config import setup_logging

# Setup logging
setup_logging()

# Initialize settings
settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting AWS Cost Optimization Platform...")
    
    # Initialize Ollama models
    try:
        import ollama
        client = ollama.Client(host=settings.OLLAMA_HOST)
        # Pull required models if not exists
        models = client.list()
        if not any(model['name'].startswith(settings.OLLAMA_MODEL) for model in models['models']):
            print(f"📥 Pulling {settings.OLLAMA_MODEL} model...")
            client.pull(settings.OLLAMA_MODEL)
        print("✅ Ollama models ready")
    except Exception as e:
        print(f"⚠️  Ollama initialization warning: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AWS Cost Optimization Platform...")

# Create FastAPI app
app = FastAPI(
    title="AWS Cost Optimization Platform",
    description="AI-powered AWS cost optimization with multi-agent analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cost_optimization.router, prefix="/api/v1", tags=["cost-optimization"])
app.include_router(agents.router, prefix="/api/v1", tags=["agents"])
app.include_router(reports.router, prefix="/api/v1", tags=["reports"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "aws-cost-optimizer"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AWS Cost Optimization Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

### Frontend Main Application (`frontend/src/App.tsx`):
```tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import CostAnalysis from './pages/CostAnalysis';
import Optimization from './pages/Optimization';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/cost-analysis" element={<CostAnalysis />} />
              <Route path="/optimization" element={<Optimization />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
```

---

## 🤖 **Strands Agents Integration**

### Main Orchestrator (`backend/src/agents/orchestrator_agent.py`):
```python
from strands import Agent, tool
from strands.models.ollama import OllamaModel
from strands.multiagent import GraphBuilder, Swarm
from strands_tools import calculator, memory
import asyncio
from typing import Dict, Any, List

from src.config.settings import Settings
from src.tools.aws_tools import AWSCostExplorerTool, EC2UtilizationTool, S3OptimizationTool
from src.tools.calculation_tools import SavingsCalculationTool

class CostOptimizationOrchestrator:
    def __init__(self):
        self.settings = Settings()
        
        # Configure Ollama model
        self.ollama_model = OllamaModel(
            host=self.settings.OLLAMA_HOST,
            model_id=self.settings.OLLAMA_MODEL,
            temperature=0.1
        )
        
        # Initialize tools
        self.aws_cost_tool = AWSCostExplorerTool()
        self.ec2_tool = EC2UtilizationTool()
        self.s3_tool = S3OptimizationTool()
        self.calc_tool = SavingsCalculationTool()
        
        # Create specialized agents
        self._create_agents()
        self._create_orchestrator()
    
    def _create_agents(self):
        """Create specialized agents for different aspects of cost optimization"""
        
        # Cost Analysis Agent
        self.cost_analyst = Agent(
            model=self.ollama_model,
            system_prompt="""You are an AWS Cost Analysis Expert. Analyze spending patterns, 
            identify trends, and provide insights about cost optimization opportunities.""",
            tools=[self.aws_cost_tool, memory],
            name="cost_analyst"
        )
        
        # Infrastructure Analysis Agent
        self.infrastructure_analyst = Agent(
            model=self.ollama_model,
            system_prompt="""You are an AWS Infrastructure Optimization Specialist. 
            Focus on EC2 rightsizing, S3 optimization, and resource utilization.""",
            tools=[self.ec2_tool, self.s3_tool, memory],
            name="infrastructure_analyst"
        )
        
        # Financial Calculator Agent
        self.financial_analyst = Agent(
            model=self.ollama_model,
            system_prompt="""You are a Financial Analysis Expert. Perform precise 
            calculations, ROI analysis, and financial projections.""",
            tools=[self.calc_tool, calculator, memory],
            name="financial_analyst"
        )
        
        # Remediation Agent
        self.remediation_specialist = Agent(
            model=self.ollama_model,
            system_prompt="""You are a Cost Optimization Remediation Specialist. 
            Generate actionable recommendations with implementation plans.""",
            tools=[memory],
            name="remediation_specialist"
        )
    
    def _create_orchestrator(self):
        """Create main orchestrator agent"""
        
        @tool
        def cost_analysis_tool(query: str) -> str:
            """Analyze AWS costs and spending patterns"""
            return str(self.cost_analyst(query))
        
        @tool
        def infrastructure_analysis_tool(query: str) -> str:
            """Analyze infrastructure for optimization opportunities"""
            return str(self.infrastructure_analyst(query))
        
        @tool
        def financial_analysis_tool(query: str) -> str:
            """Perform financial calculations and projections"""
            return str(self.financial_analyst(query))
        
        @tool
        def remediation_tool(query: str) -> str:
            """Generate optimization recommendations"""
            return str(self.remediation_specialist(query))
        
        self.orchestrator = Agent(
            model=self.ollama_model,
            system_prompt="""You are the AWS Cost Optimization Orchestrator. 
            Coordinate specialists to provide comprehensive cost optimization analysis.
            
            Available specialists:
            - cost_analysis_tool: For spending analysis and trends
            - infrastructure_analysis_tool: For resource optimization
            - financial_analysis_tool: For calculations and ROI
            - remediation_tool: For actionable recommendations
            
            Always provide complete, actionable insights.""",
            tools=[
                cost_analysis_tool,
                infrastructure_analysis_tool,
                financial_analysis_tool,
                remediation_tool,
                memory
            ],
            name="orchestrator"
        )
    
    async def analyze_costs(self, user_query: str) -> str:
        """Main method to analyze costs using orchestrator"""
        try:
            result = self.orchestrator(user_query)
            return str(result)
        except Exception as e:
            return f"Error during analysis: {str(e)}"
    
    async def parallel_analysis(self, user_query: str) -> Dict[str, str]:
        """Perform parallel analysis using swarm"""
        swarm = Swarm([
            self.cost_analyst,
            self.infrastructure_analyst,
            self.financial_analyst,
            self.remediation_specialist
        ])
        
        results = await swarm.execute(user_query)
        
        return {
            "cost_analysis": str(results[0]),
            "infrastructure_analysis": str(results[1]),
            "financial_analysis": str(results[2]),
            "remediation": str(results[3])
        }
    
    def create_workflow_graph(self):
        """Create a workflow graph for complex analysis"""
        graph_builder = GraphBuilder()
        
        graph_builder.add_agent("cost_analyst", self.cost_analyst)
        graph_builder.add_agent("infrastructure_analyst", self.infrastructure_analyst)
        graph_builder.add_agent("financial_analyst", self.financial_analyst)
        graph_builder.add_agent("remediation_specialist", self.remediation_specialist)
        
        # Define workflow
        graph_builder.add_edge("cost_analyst", "infrastructure_analyst")
        graph_builder.add_edge("infrastructure_analyst", "financial_analyst")
        graph_builder.add_edge("financial_analyst", "remediation_specialist")
        
        return graph_builder.build()

# Global instance
orchestrator = CostOptimizationOrchestrator()
```

---

## 🌐 **WebSocket Implementation**

### WebSocket Manager (`backend/src/utils/websocket_manager.py`):
```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_connections[user_id] = websocket
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: str = None):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def send_to_user(self, message: Dict[str, Any], user_id: str):
        """Send message to specific user"""
        if user_id in self.user_connections:
            await self.send_personal_message(message, self.user_connections[user_id])
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connections"""
        if self.active_connections:
            tasks = []
            for connection in self.active_connections.copy():
                try:
                    tasks.append(self.send_personal_message(message, connection))
                except Exception as e:
                    logger.error(f"Error broadcasting to connection: {e}")
                    self.active_connections.remove(connection)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stream_agent_response(self, websocket: WebSocket, agent_response: str, agent_name: str):
        """Stream agent response word by word for real-time effect"""
        words = agent_response.split()
        
        for i, word in enumerate(words):
            message = {
                "type": "agent_stream",
                "agent": agent_name,
                "content": word + " ",
                "is_complete": i == len(words) - 1,
                "progress": (i + 1) / len(words)
            }
            
            await self.send_personal_message(message, websocket)
            await asyncio.sleep(0.05)  # Small delay for streaming effect

# Global manager instance
manager = ConnectionManager()
```

### WebSocket Router (`backend/src/routers/websocket.py`):
```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Any
import json
import asyncio
import logging

from src.utils.websocket_manager import manager
from src.agents.orchestrator_agent import orchestrator

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/cost-analysis")
async def websocket_cost_analysis(websocket: WebSocket):
    """WebSocket endpoint for real-time cost analysis"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Send acknowledgment
            await manager.send_personal_message({
                "type": "ack",
                "message": "Request received, starting analysis..."
            }, websocket)
            
            # Route message based on type
            if message.get("type") == "cost_analysis":
                await handle_cost_analysis(message, websocket)
            elif message.get("type") == "optimization_request":
                await handle_optimization_request(message, websocket)
            elif message.get("type") == "parallel_analysis":
                await handle_parallel_analysis(message, websocket)
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Unknown request type"
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from cost analysis WebSocket")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Server error: {str(e)}"
        }, websocket)

async def handle_cost_analysis(message: Dict[str, Any], websocket: WebSocket):
    """Handle cost analysis requests"""
    try:
        user_query = message.get("query", "")
        
        # Send status update
        await manager.send_personal_message({
            "type": "status",
            "message": "🔍 Analyzing AWS costs...",
            "progress": 10
        }, websocket)
        
        # Execute analysis
        result = await orchestrator.analyze_costs(user_query)
        
        # Stream response
        await manager.stream_agent_response(websocket, result, "cost_optimizer")
        
        # Send completion
        await manager.send_personal_message({
            "type": "analysis_complete",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Analysis failed: {str(e)}"
        }, websocket)

async def handle_optimization_request(message: Dict[str, Any], websocket: WebSocket):
    """Handle optimization recommendation requests"""
    try:
        user_query = message.get("query", "")
        service = message.get("service", "all")
        
        await manager.send_personal_message({
            "type": "status",
            "message": f"🔧 Generating optimization recommendations for {service}...",
            "progress": 20
        }, websocket)
        
        # Execute optimization analysis
        result = await orchestrator.analyze_costs(
            f"Provide optimization recommendations for {service}: {user_query}"
        )
        
        await manager.stream_agent_response(websocket, result, "optimization_specialist")
        
        await manager.send_personal_message({
            "type": "optimization_complete",
            "result": result,
            "service": service,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Optimization analysis failed: {str(e)}"
        }, websocket)

async def handle_parallel_analysis(message: Dict[str, Any], websocket: WebSocket):
    """Handle parallel multi-agent analysis"""
    try:
        user_query = message.get("query", "")
        
        await manager.send_personal_message({
            "type": "status",
            "message": "🚀 Running parallel analysis with multiple agents...",
            "progress": 30
        }, websocket)
        
        # Execute parallel analysis
        results = await orchestrator.parallel_analysis(user_query)
        
        # Send results from each agent
        for agent_name, result in results.items():
            await manager.send_personal_message({
                "type": "agent_result",
                "agent": agent_name,
                "result": result
            }, websocket)
        
        await manager.send_personal_message({
            "type": "parallel_analysis_complete",
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Parallel analysis failed: {str(e)}"
        }, websocket)
```

---

## 📊 **Chart Components**

### Cost Trend Chart (`frontend/src/components/Charts/CostTrendChart.tsx`):
```tsx
import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { CostDataPoint } from '../../types/cost.types';

interface CostTrendChartProps {
  data: CostDataPoint[];
  width?: number;
  height?: number;
  className?: string;
}

export const CostTrendChart: React.FC<CostTrendChartProps> = ({
  data,
  width = 800,
  height = 400,
  className = ''
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data || data.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Parse dates and prepare data
    const parseDate = d3.timeParse("%Y-%m-%d");
    const processedData = data.map(d => ({
      ...d,
      date: parseDate(d.date) || new Date(),
      cost: +d.cost
    }));

    // Scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(processedData, d => d.date) as [Date, Date])
      .range([0, innerWidth]);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(processedData, d => d.cost) as number])
      .nice()
      .range([innerHeight, 0]);

    // Create main group
    const g = svg
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Add gradient definition
    const gradient = svg.append("defs")
      .append("linearGradient")
      .attr("id", "cost-gradient")
      .attr("gradientUnits", "userSpaceOnUse")
      .attr("x1", 0).attr("y1", innerHeight)
      .attr("x2", 0).attr("y2", 0);

    gradient.append("stop")
      .attr("offset", "0%")
      .attr("stop-color", "#3B82F6")
      .attr("stop-opacity", 0.1);

    gradient.append("stop")
      .attr("offset", "100%")
      .attr("stop-color", "#3B82F6")
      .attr("stop-opacity", 0.8);

    // Line generator
    const line = d3.line<any>()
      .x(d => xScale(d.date))
      .y(d => yScale(d.cost))
      .curve(d3.curveMonotoneX);

    // Area generator
    const area = d3.area<any>()
      .x(d => xScale(d.date))
      .y0(innerHeight)
      .y1(d => yScale(d.cost))
      .curve(d3.curveMonotoneX);

    // Add area
    g.append("path")
      .datum(processedData)
      .attr("fill", "url(#cost-gradient)")
      .attr("d", area);

    // Add line
    g.append("path")
      .datum(processedData)
      .attr("fill", "none")
      .attr("stroke", "#3B82F6")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Add dots
    g.selectAll(".dot")
      .data(processedData)
      .enter().append("circle")
      .attr("class", "dot")
      .attr("cx", d => xScale(d.date))
      .attr("cy", d => yScale(d.cost))
      .attr("r", 4)
      .attr("fill", "#3B82F6")
      .style("cursor", "pointer")
      .on("mouseover", function(event, d) {
        // Tooltip
        const tooltip = d3.select("body").append("div")
          .attr("class", "tooltip")
          .style("position", "absolute")
          .style("background", "rgba(0, 0, 0, 0.8)")
          .style("color", "white")
          .style("padding", "8px")
          .style("border-radius", "4px")
          .style("font-size", "12px")
          .style("pointer-events", "none")
          .style("opacity", 0);

        tooltip.transition()
          .duration(200)
          .style("opacity", 0.9);

        tooltip.html(`
          <div>Date: ${d3.timeFormat("%Y-%m-%d")(d.date)}</div>
          <div>Cost: ${d.cost.toLocaleString()}</div>
        `)
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 28) + "px");
      })
      .on("mouseout", function() {
        d3.selectAll(".tooltip").remove();
      });

    // Add X axis
    g.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale).tickFormat(d3.timeFormat("%b %Y")));

    // Add Y axis
    g.append("g")
      .call(d3.axisLeft(yScale).tickFormat(d => `${d3.format(".2s")(d)}`));

    // Add axis labels
    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - (innerHeight / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .style("fill", "#666")
      .text("Cost ($)");

    g.append("text")
      .attr("transform", `translate(${innerWidth / 2}, ${innerHeight + margin.bottom})`)
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .style("fill", "#666")
      .text("Date");

  }, [data, width, height]);

  return (
    <div className={`cost-trend-chart ${className}`}>
      <svg ref={svgRef}></svg>
    </div>
  );
};

export default CostTrendChart;
```

### Service Breakdown Chart (`frontend/src/components/Charts/ServiceBreakdownChart.tsx`):
```tsx
import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  TooltipItem,
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

interface ServiceCost {
  service: string;
  cost: number;
  percentage: number;
}

interface ServiceBreakdownChartProps {
  data: ServiceCost[];
  className?: string;
}

export const ServiceBreakdownChart: React.FC<ServiceBreakdownChartProps> = ({
  data,
  className = ''
}) => {
  const colors = [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
    '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6B7280'
  ];

  const chartData = {
    labels: data.map(item => item.service),
    datasets: [
      {
        data: data.map(item => item.cost),
        backgroundColor: colors.slice(0, data.length),
        borderColor: colors.slice(0, data.length).map(color => color + '80'),
        borderWidth: 2,
        hoverOffset: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 20,
          usePointStyle: true,
          font: {
            size: 12,
          },
        },
      },
      tooltip: {
        callbacks: {
          label: function(context: TooltipItem<'doughnut'>) {
            const label = context.label || '';
            const value = context.parsed;
            const percentage = data[context.dataIndex]?.percentage || 0;
            return `${label}: ${value.toLocaleString()} (${percentage.toFixed(1)}%)`;
          },
        },
      },
    },
    maintainAspectRatio: false,
  };

  return (
    <div className={`service-breakdown-chart ${className}`}>
      <div className="h-80">
        <Doughnut data={chartData} options={options} />
      </div>
    </div>
  );
};

export default ServiceBreakdownChart;
```

---

## 🔧 **Development Setup Commands**

### Setup Script (`setup.sh`):
```bash
#!/bin/bash

echo "🚀 Setting up AWS Cost Optimization Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file
echo "📝 Creating environment file..."
cp backend/.env.example backend/.env
echo "✅ Environment file created. Please update with your AWS credentials."

# Start infrastructure services
echo "🐳 Starting infrastructure services..."
docker-compose up -d postgres redis ollama

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Pull Ollama model
echo "📥 Pulling Ollama model..."
docker exec cost-optimizer-ollama ollama pull llama2

# Install backend dependencies
echo "🐍 Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Setting up database..."
alembic upgrade head

# Install frontend dependencies
echo "⚛️ Setting up frontend..."
cd ../frontend
npm install

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "2. Frontend: cd frontend && npm run dev"
echo ""
echo "Access the application at: http://localhost:3000"
echo "API documentation at: http://localhost:8000/docs"
```

### Development Start Script (`start-dev.sh`):
```bash
#!/bin/bash

echo "🚀 Starting AWS Cost Optimization Platform in development mode..."

# Start infrastructure services
echo "🐳 Starting infrastructure services..."
docker-compose up -d postgres redis ollama

# Wait for services
echo "⏳ Waiting for services..."
sleep 10

# Start backend in background
echo "🐍 Starting backend..."
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend in background
echo "⚛️ Starting frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Application started!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; docker-compose down; exit" INT
wait
```

---

## 🧪 **Testing Configuration**

### Backend Tests (`backend/src/tests/test_agents.py`):
```python
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.agents.orchestrator_agent import CostOptimizationOrchestrator

class TestCostOptimizationOrchestrator:
    @pytest.fixture
    def orchestrator(self):
        return CostOptimizationOrchestrator()
    
    @pytest.mark.asyncio
    async def test_analyze_costs(self, orchestrator):
        """Test basic cost analysis functionality"""
        query = "Analyze my AWS costs for the last 30 days"
        result = await orchestrator.analyze_costs(query)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_parallel_analysis(self, orchestrator):
        """Test parallel analysis with multiple agents"""
        query = "Provide comprehensive cost optimization recommendations"
        results = await orchestrator.parallel_analysis(query)
        
        assert isinstance(results, dict)
        assert "cost_analysis" in results
        assert "infrastructure_analysis" in results
        assert "financial_analysis" in results
        assert "remediation" in results
    
    def test_agent_initialization(self, orchestrator):
        """Test that all agents are properly initialized"""
        assert orchestrator.cost_analyst is not None
        assert orchestrator.infrastructure_analyst is not None
        assert orchestrator.financial_analyst is not None
        assert orchestrator.remediation_specialist is not None
        assert orchestrator.orchestrator is not None

@pytest.mark.asyncio
async def test_aws_tool_integration():
    """Test AWS tools integration"""
    with patch('boto3.client') as mock_client:
        mock_ce = Mock()
        mock_client.return_value = mock_ce
        mock_ce.get_cost_and_usage.return_value = {
            'ResultsByTime': [
                {
                    'TimePeriod': {'Start': '2024-01-01', 'End': '2024-01-02'},
                    'Total': {'BlendedCost': {'Amount': '100.00'}}
                }
            ]
        }
        
        from src.tools.aws_tools import AWSCostExplorerTool
        tool = AWSCostExplorerTool()
        result = tool._run("30_days")
        
        assert "total_cost" in result
        mock_ce.get_cost_and_usage.assert_called_once()
```

### Frontend Tests (`frontend/src/components/__tests__/CostTrendChart.test.tsx`):
```tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { CostTrendChart } from '../Charts/CostTrendChart';

const mockData = [
  { date: '2024-01-01', cost: 1000 },
  { date: '2024-01-02', cost: 1200 },
  { date: '2024-01-03', cost: 950 },
];

describe('CostTrendChart', () => {
  it('renders without crashing', () => {
    render(<CostTrendChart data={mockData} />);
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('handles empty data gracefully', () => {
    render(<CostTrendChart data={[]} />);
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <CostTrendChart data={mockData} className="custom-chart" />
    );
    expect(container.firstChild).toHaveClass('custom-chart');
  });
});
```

---

## 📝 **Documentation Files**

### README.md:
```markdown
# AWS Cost Optimization Platform

A production-ready AWS cost optimization platform powered by AI agents using Strands Agents SDK, React, and FastAPI.

## 🚀 Features

- **Multi-Agent AI System**: Specialized agents for cost analysis, optimization, and recommendations
- **Real-time Analysis**: WebSocket-based real-time cost analysis and monitoring
- **Interactive Dashboards**: Advanced D3.js and Chart.js visualizations
- **AWS Integration**: Comprehensive AWS service cost analysis
- **Local LLM Processing**: Privacy-focused local processing with Ollama
- **Production Ready**: Full observability, monitoring, and deployment support

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, D3.js, Chart.js
- **Backend**: FastAPI, Python 3.11, Strands Agents SDK
- **LLM**: Ollama with Llama 2/Code Llama
- **Database**: PostgreSQL, Redis
- **Infrastructure**: Docker, Docker Compose

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- AWS CLI configured with appropriate permissions

## 🚀 Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd aws-cost-optimizer
   ```

2. **Run setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure environment**:
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your AWS credentials
   ```

4. **Start development servers**:
   ```bash
   chmod +x start-dev.sh
   ./start-dev.sh
   ```

5. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🏗️ Architecture

### Multi-Agent System
- **Cost Analysis Agent**: AWS spending pattern analysis
- **Infrastructure Agent**: Resource optimization recommendations
- **Financial Agent**: Precise calculations and ROI analysis
- **Remediation Agent**: Actionable implementation plans
- **Orchestrator Agent**: Intelligent task routing and coordination

### Real-time Communication
- WebSocket-based real-time updates
- Streaming agent responses
- Live progress monitoring
- Multi-user support

## 🔧 Development

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Running Tests
```bash
# Backend tests
cd backend && python -m pytest tests/ -v

# Frontend tests
cd frontend && npm test
```

## 🚢 Deployment

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### AWS Deployment
- Configure AWS credentials
- Set up RDS for PostgreSQL
- Deploy using AWS ECS or EC2
- Configure load balancer and SSL

## 📊 Monitoring

- Built-in performance monitoring
- Agent execution tracking
- Cost analysis metrics
- Real-time dashboards

## 🔒 Security

- Read-only AWS permissions
- Local LLM processing (no data sent to external APIs)
- Encrypted sensitive data storage
- Rate limiting and authentication

## 📖 Documentation

- [Setup Guide](docs/SETUP.md)
- [API Documentation](docs/API.md)
- [Agent Architecture](docs/AGENTS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
```

---

## 🎯 **Final Instructions for Claude Code**

### **Primary Command:**
```
Create a production-ready AWS Cost Optimization platform using the complete specifications provided. Implement all components including:

1. React TypeScript frontend with advanced D3.js charts
2. FastAPI backend with Strands Agents multi-agent system
3. WebSocket real-time communication
4. Ollama local LLM integration
5. Complete AWS Boto3 tools integration
6. PostgreSQL and Redis setup
7. Docker containerization
8. Comprehensive testing framework

Follow the exact project structure, dependencies, and implementation patterns specified in the documentation package.
```

### **Development Phases:**
1. **Phase 1**: Setup project structure and dependencies
2. **Phase 2**: Implement Strands Agents multi-agent system
3. **Phase 3**: Create FastAPI backend with WebSocket support
4. **Phase 4**: Build React frontend with advanced charts
5. **Phase 5**: Integrate AWS tools and real-time features
6. **Phase 6**: Add testing and documentation
7. **Phase 7**: Docker containerization and deployment setup

### **Success Criteria:**
✅ Multi-agent cost analysis with Strands Agents
✅ Real-time WebSocket communication
✅ Interactive D3.js cost visualization charts
✅ AWS service integration with read-only tools
✅ Local Ollama LLM processing
✅ Production-ready deployment configuration
✅ Comprehensive testing coverage
✅ Professional UI/UX with Tailwind CSS

This package provides everything needed to build the complete AWS Cost Optimization platform as specified!