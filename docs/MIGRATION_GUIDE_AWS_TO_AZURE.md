# Migration Guide: AWS → Azure Version
# CostSense-AI Platform Transition

**Quick Reference for Developers**

---

## 🔄 Core Changes Overview

| Aspect | AWS Version | Azure Version |
|--------|------------|---------------|
| **Cloud Provider** | Amazon Web Services | Microsoft Azure |
| **AI Framework** | Strands Agents SDK | LangChain |
| **LLM Model** | llama2 | llama3.2:latest |
| **Ollama Port** | 11434 | 11434 (same) |
| **Data Phase 1** | Mock AWS data | Mock Azure data |
| **Data Phase 2** | AWS Boto3 APIs | Azure SDK APIs |
| **Primary Services** | EC2, S3, RDS, Lambda | VMs, Storage, SQL, Functions |

---

## 📋 Code Comparison

### 1. Agent Framework Migration

#### Before (Strands SDK)
```python
# backend/src/agents/orchestrator_agent.py
from strands_agents import Agent, Orchestrator

class CostOptimizationOrchestrator(Orchestrator):
    def __init__(self):
        super().__init__()
        self.agents = [
            CostAnalystAgent(),
            InfrastructureAgent(),
            FinancialAgent()
        ]

    async def analyze(self, query: str):
        results = await self.coordinate_agents(query)
        return self.synthesize(results)
```

#### After (LangChain)
```python
# backend/src/agents_langchain/orchestrator.py
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_community.llms import Ollama

class AzureCostOrchestrator:
    def __init__(self):
        self.llm = Ollama(
            model="llama3.2:latest",
            base_url="http://localhost:11434"
        )
        self.tools = self._create_tools()
        self.agent = create_react_agent(self.llm, self.tools, prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools)

    async def analyze(self, query: str):
        result = await self.executor.ainvoke({"input": query})
        return result["output"]

    def _create_tools(self):
        return [
            Tool(
                name="cost_analyst",
                func=self._analyze_costs,
                description="Analyzes Azure cost trends..."
            ),
            # ... more tools
        ]
```

### 2. Service Names & Terminology

#### AWS → Azure Service Mapping
```python
# AWS Version
AWS_SERVICES = {
    "EC2": "Elastic Compute Cloud",
    "S3": "Simple Storage Service",
    "RDS": "Relational Database Service",
    "Lambda": "Lambda Functions",
    "CloudFront": "Content Delivery Network"
}

# Azure Version
AZURE_SERVICES = {
    "VirtualMachines": "Virtual Machines",
    "StorageAccounts": "Storage Accounts",
    "SQLDatabase": "Azure SQL Database",
    "Functions": "Azure Functions",
    "CDN": "Azure CDN"
}
```

### 3. Mock Data Changes

#### Before (AWS)
```python
# backend/src/tools/aws_tools_simple.py
def generate_ec2_data():
    instance_types = ["t3.micro", "t3.small", "m5.large", "c5.xlarge"]
    return {
        "instances": [
            {
                "instance_id": "i-abc123",
                "instance_type": "t3.medium",
                "region": "us-east-1"
            }
        ]
    }
```

#### After (Azure)
```python
# backend/src/mock/azure_data_generator.py
def generate_vm_data():
    vm_sizes = ["Standard_B2s", "Standard_D2s_v3", "Standard_E4s_v3"]
    return {
        "instances": [
            {
                "id": "/subscriptions/.../vm-001",
                "name": "vm-web-01",
                "size": "Standard_D2s_v3",
                "location": "eastus",
                "resourceGroup": "rg-production"
            }
        ]
    }
```

### 4. Cost Data Structure

#### AWS Cost Explorer Format
```python
{
    "total_cost": 2450.50,
    "daily_costs": [...],
    "top_services": [
        ["EC2-Instance", 800.00],
        ["S3", 200.00],
        ["RDS", 450.00]
    ]
}
```

#### Azure Cost Management Format
```python
{
    "total_monthly_cost": 12450.50,
    "monthly_change_percent": 8.5,
    "daily_costs": [...],
    "top_services": [
        ["Virtual Machines", 4500.00],
        ["Azure SQL Database", 2800.00],
        ["Storage Accounts", 1900.00]
    ],
    "resource_groups": [
        {"name": "rg-production", "cost": 8000.00}
    ]
}
```

---

## 🛠️ LangChain Implementation Patterns

### Agent Types & Their Roles

#### 1. Orchestrator Agent (ReAct Pattern)
```python
from langchain.agents import create_react_agent
from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    template="""You are an Azure Cost Optimization Orchestrator.

Available tools: {tools}

Question: {input}
Thought: [reasoning]
Action: [tool name]
Action Input: [tool input]
Observation: [tool output]
... (repeat as needed)
Final Answer: [synthesized response]

{agent_scratchpad}""",
    input_variables=["input", "agent_scratchpad", "tools"]
)

agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
```

#### 2. Specialist Agents (LLMChain Pattern)
```python
from langchain.chains import LLMChain

class CostAnalystAgent:
    def __init__(self):
        self.chain = LLMChain(llm=llm, prompt=cost_analyst_prompt)

    async def analyze(self, query: str, cost_data: dict):
        return await self.chain.arun(
            query=query,
            cost_data=str(cost_data)
        )
```

### Tool Creation

#### Custom Azure Tools
```python
from langchain.tools import BaseTool
from typing import Optional

class AzureCostTool(BaseTool):
    name = "azure_cost_explorer"
    description = "Retrieves Azure cost data for a given time period"

    def _run(self, time_period: str = "30d") -> str:
        """Synchronous implementation"""
        data = generate_mock_cost_data(time_period)
        return json.dumps(data)

    async def _arun(self, time_period: str = "30d") -> str:
        """Async implementation"""
        return self._run(time_period)

class VMUtilizationTool(BaseTool):
    name = "vm_utilization_analyzer"
    description = "Analyzes Azure VM utilization metrics"

    def _run(self) -> str:
        data = generate_vm_utilization_data()
        return json.dumps(data)

    async def _arun(self) -> str:
        return self._run()
```

### Streaming Responses

#### WebSocket Integration with LangChain
```python
from langchain.callbacks.base import BaseCallbackHandler

class WebSocketStreamingCallback(BaseCallbackHandler):
    def __init__(self, websocket):
        self.websocket = websocket

    async def on_llm_new_token(self, token: str, **kwargs):
        """Called when LLM generates a new token"""
        await self.websocket.send_json({
            "type": "token",
            "content": token
        })

    async def on_tool_start(self, tool, input_str, **kwargs):
        """Called when a tool starts execution"""
        await self.websocket.send_json({
            "type": "agent_status",
            "agent": tool.name,
            "status": "running"
        })

# Usage
async def stream_analysis(query: str, websocket):
    callback = WebSocketStreamingCallback(websocket)
    result = await executor.ainvoke(
        {"input": query},
        callbacks=[callback]
    )
```

---

## 🔧 Configuration Changes

### Environment Variables

#### Before (.env for AWS)
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2
```

#### After (.env for Azure)
```bash
# Azure Configuration (for Phase 2)
AZURE_SUBSCRIPTION_ID=xxx
AZURE_TENANT_ID=xxx
AZURE_CLIENT_ID=xxx
AZURE_CLIENT_SECRET=xxx

# Ollama with LangChain
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
OLLAMA_TEMPERATURE=0.7
OLLAMA_MAX_TOKENS=2000

# LangChain
LANGCHAIN_TRACING_V2=true  # Optional: for debugging
LANGCHAIN_ENDPOINT=http://localhost:8000
```

### Docker Compose Changes

#### Key Differences
```yaml
# docker-compose.azure.yml
services:
  ollama:
    image: ollama/ollama:latest
    # ... same as before
    command: |
      sh -c "ollama serve &
             sleep 5 &&
             ollama pull llama3.2:latest &&
             wait"

  backend:
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - OLLAMA_MODEL=llama3.2:latest
      - LANGCHAIN_TRACING_V2=false
```

---

## 📦 Dependency Changes

### Backend Requirements

#### Remove (Strands SDK)
```txt
strands-agents==1.0.0
strands-core==1.0.0
boto3==1.28.0
botocore==1.31.0
```

#### Add (LangChain + Azure)
```txt
# LangChain
langchain==0.1.0
langchain-community==0.0.13
langchain-core==0.1.10
langchain-experimental==0.0.47

# Ollama
ollama==0.1.6

# Azure SDKs (for Phase 2)
azure-identity==1.15.0
azure-mgmt-costmanagement==4.0.0
azure-mgmt-compute==30.3.0
azure-mgmt-storage==21.1.0
azure-mgmt-monitor==6.0.0

# Keep existing
fastapi==0.104.1
uvicorn==0.24.0
websockets==12.0
pydantic==2.5.0
```

### Frontend (Minimal Changes)
```json
// package.json - mostly unchanged
{
  "dependencies": {
    "react": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@tanstack/react-query": "^5.12.0",
    "zustand": "^4.4.7",
    "d3": "^7.8.5",
    "chart.js": "^4.4.0",
    // Update service names in API calls
  }
}
```

---

## 🎨 UI Changes

### Terminology Updates

#### Text Changes Throughout UI
```typescript
// Before
"AWS Cost Optimization Platform"
"EC2 Instances"
"S3 Buckets"
"RDS Databases"

// After
"Azure Cost Optimization Platform"
"Virtual Machines"
"Storage Accounts"
"SQL Databases"
```

### Dashboard Metrics

#### Before (AWS)
```typescript
interface Metrics {
  ec2Cost: number;
  s3Cost: number;
  rdsCost: number;
  lambdaCost: number;
}
```

#### After (Azure)
```typescript
interface Metrics {
  vmCost: number;
  storageCost: number;
  sqlDatabaseCost: number;
  functionsCost: number;
  resourceGroups: ResourceGroup[];
}
```

---

## 🧪 Testing Changes

### Unit Tests

#### Before (Strands)
```python
# tests/test_agents.py
def test_orchestrator():
    orchestrator = CostOptimizationOrchestrator()
    result = orchestrator.analyze("test query")
    assert result is not None
```

#### After (LangChain)
```python
# tests/test_langchain_agents.py
import pytest
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_orchestrator():
    with patch('langchain_community.llms.Ollama') as mock_llm:
        mock_llm.return_value.predict = Mock(return_value="test response")

        orchestrator = AzureCostOrchestrator()
        result = await orchestrator.analyze("test query")

        assert result is not None
        assert "test response" in result

@pytest.mark.asyncio
async def test_cost_analyst_agent():
    agent = CostAnalystAgent()
    result = await agent.analyze(
        "What are my top costs?",
        {"total": 1000, "services": [...]}
    )
    assert result is not None
```

---

## 📊 Data Model Changes

### Resource Identification

#### AWS
```python
# Resource IDs
instance_id = "i-0abc123def456"
bucket_name = "my-s3-bucket"
db_instance = "mydb-instance-1"

# Regions
regions = ["us-east-1", "us-west-2", "eu-west-1"]
```

#### Azure
```python
# Resource IDs (full ARM paths)
vm_id = "/subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vm-name}"
storage_account = "staccountname123"
sql_database = "sqldb-production"

# Locations
locations = ["eastus", "westus2", "westeurope"]

# Resource Groups (Azure-specific)
resource_group = "rg-production"
```

---

## 🚀 Migration Checklist

### Phase 1: Setup
- [ ] Install LangChain dependencies
- [ ] Pull llama3.2:latest model
- [ ] Update Docker Compose configuration
- [ ] Create Azure-specific directory structure

### Phase 2: Backend Migration
- [ ] Implement LangChain orchestrator
- [ ] Create specialist agents with LangChain
- [ ] Build Azure mock data generators
- [ ] Update FastAPI routers
- [ ] Implement WebSocket with LangChain callbacks

### Phase 3: Frontend Updates
- [ ] Update service terminology (AWS → Azure)
- [ ] Modify API endpoints
- [ ] Update data models
- [ ] Adjust charts for Azure data structure
- [ ] Update documentation strings

### Phase 4: Testing
- [ ] Write LangChain agent tests
- [ ] Test Ollama integration
- [ ] Verify mock data accuracy
- [ ] Test WebSocket streaming
- [ ] End-to-end testing

### Phase 5: Documentation
- [ ] Update README
- [ ] Document LangChain architecture
- [ ] Update API documentation
- [ ] Create setup guides
- [ ] Write troubleshooting guide

---

## 🐛 Common Migration Issues

### Issue 1: Ollama Model Not Found
```bash
# Solution: Manually pull the model
docker exec -it costsense-ollama ollama pull llama3.2:latest

# Verify
docker exec -it costsense-ollama ollama list
```

### Issue 2: LangChain Agent Not Responding
```python
# Check if Ollama is accessible
import requests
response = requests.get("http://localhost:11434/api/tags")
print(response.json())

# Verify LangChain connection
from langchain_community.llms import Ollama
llm = Ollama(model="llama3.2:latest", base_url="http://localhost:11434")
result = llm.predict("Hello")
print(result)
```

### Issue 3: Agent Tool Not Executing
```python
# Add verbose logging
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # Shows agent reasoning
    return_intermediate_steps=True
)
```

### Issue 4: WebSocket Disconnections
```typescript
// Implement reconnection logic
const ws = new WebSocket(url);
ws.onclose = () => {
  setTimeout(() => {
    console.log("Reconnecting...");
    connectWebSocket();
  }, 3000);
};
```

---

## 📚 Additional Resources

### LangChain Documentation
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)
- [Custom Tools](https://python.langchain.com/docs/modules/agents/tools/)
- [Ollama Integration](https://python.langchain.com/docs/integrations/llms/ollama)
- [Callbacks & Streaming](https://python.langchain.com/docs/modules/callbacks/)

### Azure Documentation
- [Azure Cost Management API](https://docs.microsoft.com/azure/cost-management-billing/)
- [Azure Resource Manager](https://docs.microsoft.com/azure/azure-resource-manager/)
- [Azure Monitor](https://docs.microsoft.com/azure/azure-monitor/)

### Ollama
- [Ollama Documentation](https://ollama.ai/docs)
- [llama3.2 Model Card](https://ollama.ai/library/llama3.2)

---

## 🤝 Support

For migration questions:
- Review the [PRD](./PRD_AZURE_VERSION.md)
- Check the [Implementation Roadmap](./IMPLEMENTATION_ROADMAP_AZURE.md)
- Open a GitHub issue
- Contact: dev-team@costsense.ai

---

**Last Updated**: December 4, 2025
**Version**: 1.0.0
