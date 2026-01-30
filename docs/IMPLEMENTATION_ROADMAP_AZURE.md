# Implementation Roadmap: CostSense-AI Azure Edition
# Technical Migration & Development Plan

**Version:** 1.0.0
**Created:** December 4, 2025
**Status:** Planning

---

## 🎯 Quick Reference

### Key Changes Summary
| Component | Current (AWS) | New (Azure) |
|-----------|---------------|-------------|
| Cloud Platform | AWS | Microsoft Azure |
| AI Framework | Strands Agents SDK | LangChain |
| LLM Model | llama2 | llama3.2:latest |
| Data Source | AWS APIs | Mock → Azure APIs |
| Services Focus | EC2, S3, RDS | VMs, Storage, SQL |

---

## 📋 Phase 1: MVP Development (Weeks 1-4)

### Week 1: Project Foundation & Setup

#### Day 1-2: Environment Setup
```bash
# Task Checklist
- [ ] Create new branch: feature/azure-migration
- [ ] Update Docker configuration for Azure
- [ ] Install Ollama with llama3.2:latest
- [ ] Set up LangChain development environment
- [ ] Configure project structure
```

**Files to Create/Modify:**
```
backend/
  ├── requirements.txt          # Add LangChain dependencies
  ├── src/
  │   ├── agents_langchain/     # New LangChain agents directory
  │   │   ├── __init__.py
  │   │   ├── orchestrator.py
  │   │   ├── cost_analyst.py
  │   │   ├── infrastructure_analyst.py
  │   │   ├── financial_analyst.py
  │   │   └── remediation_specialist.py
  │   ├── tools_azure/          # Azure-specific tools
  │   │   ├── __init__.py
  │   │   ├── cost_tools.py
  │   │   ├── vm_tools.py
  │   │   └── storage_tools.py
  │   └── config/
  │       └── langchain_config.py
  docker-compose.azure.yml      # Azure-specific compose file
  .env.azure.example            # Azure environment template
```

**Dependencies to Add:**
```txt
# requirements.txt additions
langchain==0.1.0
langchain-community==0.0.13
langchain-core==0.1.10
ollama==0.1.6
azure-identity==1.15.0
azure-mgmt-costmanagement==4.0.0  # For Phase 2
azure-mgmt-compute==30.3.0        # For Phase 2
azure-mgmt-storage==21.1.0        # For Phase 2
```

#### Day 3-4: Ollama & LangChain Setup

**Task: Configure Ollama Service**
```yaml
# docker-compose.azure.yml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: costsense-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    build: ./backend
    depends_on:
      - ollama
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - OLLAMA_MODEL=llama3.2:latest

volumes:
  ollama_data:
```

**Task: Pull llama3.2:latest Model**
```bash
# After starting Ollama container
docker exec -it costsense-ollama ollama pull llama3.2:latest

# Verify model
docker exec -it costsense-ollama ollama list
```

**Task: Create LangChain Configuration**
```python
# backend/src/config/langchain_config.py
from langchain_community.llms import Ollama
from pydantic_settings import BaseSettings

class LangChainSettings(BaseSettings):
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:latest"
    OLLAMA_TEMPERATURE: float = 0.7
    OLLAMA_MAX_TOKENS: int = 2000

    class Config:
        env_file = ".env"

settings = LangChainSettings()

def get_llm():
    return Ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=settings.OLLAMA_TEMPERATURE
    )
```

#### Day 5: Mock Data Generators

**Task: Create Azure Mock Data**
```python
# backend/src/mock/azure_data_generator.py
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random

class AzureMockDataGenerator:
    """Generates realistic Azure cost and resource data"""

    @staticmethod
    def generate_dashboard_data() -> Dict[str, Any]:
        """Generate dashboard summary data"""
        return {
            "total_monthly_cost": round(random.uniform(10000, 20000), 2),
            "monthly_change_percent": round(random.uniform(-5, 15), 1),
            "projected_monthly_cost": round(random.uniform(11000, 21000), 2),
            "daily_costs": AzureMockDataGenerator._generate_daily_costs(30),
            "top_services": [
                ["Virtual Machines", round(random.uniform(3000, 6000), 2)],
                ["Azure SQL Database", round(random.uniform(2000, 4000), 2)],
                ["Storage Accounts", round(random.uniform(1500, 3000), 2)],
                ["App Services", round(random.uniform(1000, 2500), 2)],
                ["Azure Kubernetes Service", round(random.uniform(800, 2000), 2)]
            ],
            "resource_groups": AzureMockDataGenerator._generate_resource_groups()
        }

    @staticmethod
    def _generate_daily_costs(days: int) -> List[Dict[str, Any]]:
        """Generate daily cost data with realistic patterns"""
        costs = []
        base_cost = 350

        for i in range(days):
            date = (datetime.now() - timedelta(days=days-1-i)).strftime('%Y-%m-%d')
            day_of_week = (datetime.now() - timedelta(days=days-1-i)).weekday()

            # Weekend dip pattern
            if day_of_week >= 5:
                cost = base_cost * random.uniform(0.7, 0.8)
            else:
                cost = base_cost * random.uniform(0.95, 1.15)

            costs.append({
                "date": date,
                "cost": round(cost, 2)
            })

        return costs

    @staticmethod
    def _generate_resource_groups() -> List[Dict[str, Any]]:
        """Generate resource group data"""
        rg_names = ["production", "staging", "development", "shared-services"]
        return [
            {
                "name": f"rg-{name}",
                "cost": round(random.uniform(1000, 5000), 2),
                "resourceCount": random.randint(10, 50)
            }
            for name in rg_names
        ]

    @staticmethod
    def generate_vm_data() -> Dict[str, Any]:
        """Generate VM utilization data"""
        vm_sizes = [
            "Standard_B2s", "Standard_D2s_v3", "Standard_D4s_v3",
            "Standard_E4s_v3", "Standard_F4s_v2"
        ]

        instances = []
        for i in range(random.randint(5, 12)):
            cpu_util = round(random.uniform(15, 95), 1)
            recommendation = "Optimal" if 40 <= cpu_util <= 80 else (
                "Downsize" if cpu_util < 40 else "Consider scaling"
            )

            instances.append({
                "id": f"/subscriptions/.../vm-{i:03d}",
                "name": f"vm-{['web', 'api', 'worker', 'db'][i % 4]}-{i:02d}",
                "size": random.choice(vm_sizes),
                "location": random.choice(["eastus", "westus2", "westeurope"]),
                "resourceGroup": f"rg-{random.choice(['production', 'staging'])}",
                "status": random.choice(["running", "running", "running", "stopped"]),
                "cpuUtilization": cpu_util,
                "memoryUtilization": round(random.uniform(30, 85), 1),
                "monthlyCost": round(random.uniform(50, 500), 2),
                "recommendation": recommendation,
                "potentialSavings": round(random.uniform(20, 150), 2) if recommendation != "Optimal" else 0
            })

        return {
            "totalInstances": len(instances),
            "instances": instances,
            "totalMonthlyCost": sum(vm["monthlyCost"] for vm in instances),
            "potentialSavings": sum(vm["potentialSavings"] for vm in instances)
        }

    @staticmethod
    def generate_storage_data() -> Dict[str, Any]:
        """Generate storage account data"""
        tiers = ["Standard", "Premium"]
        replications = ["LRS", "GRS", "RA-GRS"]

        accounts = []
        for i in range(random.randint(3, 8)):
            size_gb = random.randint(100, 5000)
            tier = random.choice(tiers)

            cost_per_gb = 0.0208 if tier == "Standard" else 0.15
            monthly_cost = size_gb * cost_per_gb

            recommendations = []
            if tier == "Premium" and size_gb < 500:
                recommendations.append("Consider Standard tier")
            if size_gb > 1000:
                recommendations.append("Implement lifecycle policies")

            accounts.append({
                "name": f"staccount{i:03d}",
                "location": random.choice(["eastus", "westus2"]),
                "tier": tier,
                "replication": random.choice(replications),
                "sizeGB": size_gb,
                "monthlyCost": round(monthly_cost, 2),
                "recommendations": recommendations,
                "potentialSavings": round(monthly_cost * 0.2, 2) if recommendations else 0
            })

        return {
            "totalAccounts": len(accounts),
            "accounts": accounts,
            "totalSizeGB": sum(acc["sizeGB"] for acc in accounts),
            "totalMonthlyCost": sum(acc["monthlyCost"] for acc in accounts)
        }
```

---

### Week 2: Backend Development - LangChain Agents

#### Day 1-2: Orchestrator Agent

**File: `backend/src/agents_langchain/orchestrator.py`**
```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from typing import Dict, Any
from src.config.langchain_config import get_llm

class AzureCostOrchestrator:
    def __init__(self):
        self.llm = get_llm()
        self.tools = self._create_tools()
        self.agent = self._create_agent()

    def _create_tools(self) -> list:
        """Create specialist agent tools"""
        return [
            Tool(
                name="cost_analyst",
                func=self._analyze_costs,
                description="""Analyzes Azure cost trends, identifies spending
                patterns, and highlights anomalies. Use for cost-related queries."""
            ),
            Tool(
                name="infrastructure_analyst",
                func=self._analyze_infrastructure,
                description="""Evaluates Azure resource utilization and identifies
                optimization opportunities. Use for VM, storage, database queries."""
            ),
            Tool(
                name="financial_analyst",
                func=self._calculate_savings,
                description="""Performs financial calculations, ROI analysis, and
                savings projections. Use for financial impact questions."""
            ),
            Tool(
                name="remediation_specialist",
                func=self._create_action_plan,
                description="""Creates prioritized action plans for implementing
                recommendations. Use for implementation planning queries."""
            )
        ]

    def _create_agent(self) -> AgentExecutor:
        """Create the orchestrator agent"""
        prompt = PromptTemplate(
            template="""You are an Azure Cost Optimization Orchestrator AI.

Your role:
1. Understand user queries about Azure costs and resources
2. Delegate tasks to specialist agents
3. Synthesize results into clear, actionable insights
4. Provide specific recommendations with cost savings

Available tools:
{tools}

Tool names: {tool_names}

Format:
Question: the input question
Thought: consider which specialist agents to use
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Observation as needed)
Thought: I now have enough information
Final Answer: comprehensive answer with recommendations

Question: {input}
{agent_scratchpad}""",
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
        )

        agent = create_react_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    async def analyze(self, query: str) -> str:
        """Main analysis entry point"""
        result = await self.agent.ainvoke({"input": query})
        return result["output"]

    def _analyze_costs(self, query: str) -> str:
        """Cost analysis specialist (placeholder)"""
        # Will be implemented with actual agent logic
        return "Cost analysis results..."

    def _analyze_infrastructure(self, query: str) -> str:
        """Infrastructure analysis specialist (placeholder)"""
        return "Infrastructure analysis results..."

    def _calculate_savings(self, query: str) -> str:
        """Financial analysis specialist (placeholder)"""
        return "Financial analysis results..."

    def _create_action_plan(self, query: str) -> str:
        """Remediation planning specialist (placeholder)"""
        return "Action plan..."
```

#### Day 3-4: Specialist Agents

**File: `backend/src/agents_langchain/cost_analyst.py`**
```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from src.config.langchain_config import get_llm
from src.mock.azure_data_generator import AzureMockDataGenerator

class CostAnalystAgent:
    def __init__(self):
        self.llm = get_llm()
        self.data_generator = AzureMockDataGenerator()
        self.chain = self._create_chain()

    def _create_chain(self) -> LLMChain:
        prompt = PromptTemplate(
            template="""You are an Azure Cost Analysis Specialist.

Analyze the following Azure cost data and provide insights:

Cost Data:
{cost_data}

User Query: {query}

Provide:
1. Key cost trends and patterns
2. Top spending services and their percentages
3. Cost anomalies or unusual spikes
4. Month-over-month comparison
5. Specific recommendations for cost reduction

Analysis:""",
            input_variables=["cost_data", "query"]
        )
        return LLMChain(llm=self.llm, prompt=prompt)

    async def analyze(self, query: str) -> str:
        cost_data = self.data_generator.generate_dashboard_data()
        result = await self.chain.arun(
            cost_data=str(cost_data),
            query=query
        )
        return result
```

**Similar pattern for:**
- `infrastructure_analyst.py` - VM and resource analysis
- `financial_analyst.py` - Savings calculations and projections
- `remediation_specialist.py` - Action plan generation

#### Day 5: FastAPI Integration

**File: `backend/src/routers/azure_cost_optimization.py`**
```python
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from src.agents_langchain.orchestrator import AzureCostOrchestrator
from src.mock.azure_data_generator import AzureMockDataGenerator

router = APIRouter(prefix="/api/v1", tags=["azure-optimization"])
orchestrator = AzureCostOrchestrator()
data_generator = AzureMockDataGenerator()

class AnalysisRequest(BaseModel):
    query: str
    timePeriod: Optional[str] = "30d"

class AnalysisResponse(BaseModel):
    analysis: str
    timestamp: str
    confidence: str

@router.get("/dashboard/summary")
async def get_dashboard_summary():
    """Get dashboard mock data"""
    return data_generator.generate_dashboard_data()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_costs(request: AnalysisRequest):
    """Analyze costs using AI agents"""
    try:
        result = await orchestrator.analyze(request.query)
        return AnalysisResponse(
            analysis=result,
            timestamp=datetime.utcnow().isoformat(),
            confidence="High"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket for streaming AI responses"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            # Stream AI response back
            # Implementation with streaming callbacks
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
```

---

### Week 3: Frontend Development

#### Day 1-2: Dashboard with Mock Data

**File: `frontend/src/pages/AzureDashboard.tsx`**
```typescript
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CostTrendChart } from '@/components/Charts/CostTrendChart';
import { ServiceBreakdownChart } from '@/components/Charts/ServiceBreakdownChart';

interface DashboardData {
  totalMonthlyCost: number;
  monthlyChangePercent: number;
  projectedMonthlyCost: number;
  dailyCosts: Array<{ date: string; cost: number }>;
  topServices: Array<[string, number]>;
  resourceGroups: Array<{
    name: string;
    cost: number;
    resourceCount: number;
  }>;
}

export default function AzureDashboard() {
  const { data, isLoading, error } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/api/v1/dashboard/summary');
      return response.json();
    },
    refetchInterval: 60000, // Refresh every minute
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div className="space-y-6 p-6">
      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Total Monthly Cost</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              ${data?.totalMonthlyCost.toFixed(2)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Monthly Change</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold ${
              data?.monthlyChangePercent > 0 ? 'text-red-500' : 'text-green-500'
            }`}>
              {data?.monthlyChangePercent > 0 ? '+' : ''}
              {data?.monthlyChangePercent.toFixed(1)}%
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Projected Cost</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              ${data?.projectedMonthlyCost.toFixed(2)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Cost Trend (30 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            <CostTrendChart data={data?.dailyCosts || []} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Azure Services</CardTitle>
          </CardHeader>
          <CardContent>
            <ServiceBreakdownChart data={data?.topServices || []} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

#### Day 3-4: AI Chat Interface

**File: `frontend/src/pages/AIAnalysis.tsx`**
```typescript
import { useState } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { ChatPanel } from '@/components/ui/chat-panel';
import { AgentStatusPanel } from '@/components/AgentStatusPanel';

export default function AIAnalysis() {
  const [messages, setMessages] = useState([]);
  const { sendMessage, isConnected } = useWebSocket();

  const handleSendQuery = async (query: string) => {
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: query }]);

    // Send to backend
    sendMessage({
      type: 'analyze',
      payload: { query }
    });
  };

  return (
    <div className="flex h-screen">
      <div className="flex-1">
        <ChatPanel
          messages={messages}
          onSendMessage={handleSendQuery}
          isConnected={isConnected}
        />
      </div>
      <div className="w-80 border-l">
        <AgentStatusPanel />
      </div>
    </div>
  );
}
```

#### Day 5: Optimization View

**File: `frontend/src/pages/Optimization.tsx`**
```typescript
// Recommendations list with filtering, sorting
// Display savings calculations
// Implementation guidance
```

---

### Week 4: Integration & Testing

#### Testing Checklist
```
Backend Tests:
- [ ] Ollama connection tests
- [ ] LangChain agent tests
- [ ] Mock data generation tests
- [ ] API endpoint tests
- [ ] WebSocket tests

Frontend Tests:
- [ ] Dashboard rendering
- [ ] Chart components
- [ ] AI chat interface
- [ ] WebSocket integration
- [ ] State management

Integration Tests:
- [ ] End-to-end user flows
- [ ] Agent orchestration
- [ ] Real-time updates
- [ ] Error handling
```

---

## 📦 Deliverables

### Documentation
- [ ] Architecture diagram (LangChain version)
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Setup guide (Ollama + LangChain)
- [ ] User guide
- [ ] Agent configuration guide

### Code
- [ ] Backend (FastAPI + LangChain)
- [ ] Frontend (React + TypeScript)
- [ ] Docker configuration
- [ ] CI/CD pipelines
- [ ] Tests (>80% coverage)

### Deployment
- [ ] Docker Compose configuration
- [ ] Environment setup scripts
- [ ] Ollama model download scripts
- [ ] Health check endpoints

---

## 🚀 Quick Start Commands

```bash
# 1. Clone and setup
git clone <repo>
cd CostSense-AI
git checkout feature/azure-migration

# 2. Start Ollama and pull model
docker-compose -f docker-compose.azure.yml up -d ollama
docker exec -it costsense-ollama ollama pull llama3.2:latest

# 3. Install backend dependencies
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Start backend
uvicorn main_azure:app --reload --port 8000

# 5. Install frontend dependencies
cd ../frontend
npm install

# 6. Start frontend
npm run dev

# 7. Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Ollama: http://localhost:11434
```

---

## 📊 Progress Tracking

Use this checklist to track implementation progress:

### Foundation ✅
- [ ] Docker environment configured
- [ ] Ollama running with llama3.2:latest
- [ ] LangChain installed and tested
- [ ] Project structure created

### Backend 🔄
- [ ] Orchestrator agent implemented
- [ ] Cost analyst agent implemented
- [ ] Infrastructure analyst agent implemented
- [ ] Financial analyst agent implemented
- [ ] Remediation specialist agent implemented
- [ ] Mock data generators created
- [ ] FastAPI endpoints created
- [ ] WebSocket handler implemented

### Frontend 🔄
- [ ] Dashboard with mock data
- [ ] AI chat interface
- [ ] Optimization view
- [ ] Real-time updates
- [ ] Chart components

### Testing & QA 🔄
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] E2E tests written
- [ ] Performance testing
- [ ] Security review

### Documentation 📝
- [ ] Technical documentation
- [ ] API documentation
- [ ] User guide
- [ ] Setup instructions

---

## 🔗 Related Documents

- [PRD: Azure Edition](./PRD_AZURE_VERSION.md)
- [Architecture Diagrams](./architecture/)
- [API Documentation](./API_AZURE.md)
- Original AWS README: [../README.md](../README.md)

---

**Status**: Planning Phase
**Next Update**: Week 1 completion
**Contact**: dev-team@costsense.ai
