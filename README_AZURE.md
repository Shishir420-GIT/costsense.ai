# 🚀 CostSense-AI: Azure Edition

**Production-Ready Azure Cost Optimization Platform powered by LangChain & Ollama**

Version: 2.0.0 | Cloud Provider: Microsoft Azure | AI Framework: LangChain | Model: llama3.2:latest

---

## 🎯 Overview

CostSense-AI Azure Edition is an intelligent cost optimization platform that uses local AI processing (Ollama + LangChain) to analyze Azure spending, identify optimization opportunities, and provide actionable recommendations.

### Key Features

✅ **Multi-Agent AI System** - 4 specialized LangChain agents working together
✅ **Real-time Analysis** - WebSocket-based streaming responses
✅ **Azure-Focused** - VMs, Storage Accounts, SQL Databases, Resource Groups
✅ **Privacy-First** - All AI processing happens locally (no external API calls)
✅ **Production-Grade** - Comprehensive error handling and fallback mechanisms
✅ **Mock Data Ready** - Realistic Azure data for development and testing

---

## 📋 Requirements

- **Python**: 3.11+
- **Node.js**: 18+
- **Docker**: 20.10+ (for Ollama)
- **RAM**: 16GB minimum (for llama3.2 model)
- **Disk**: 20GB free space

---

## ⚡ Quick Start

### 1. Start Ollama & Pull Model

```bash
# Start Docker services
docker compose -f docker-compose.azure.yml up -d

# Wait for Ollama to be ready (30 seconds)
sleep 30

# Pull llama3.2:latest model (~7.4GB download)
docker exec costsense-azure-ollama ollama pull llama3.2:latest

# Verify model is ready
docker exec costsense-azure-ollama ollama list
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv-azure
source venv-azure/bin/activate  # Windows: venv-azure\Scripts\activate

# Install dependencies
pip install -r requirements-azure.txt

# Copy environment file
cp .env.azure .env

# Start backend server
python main_azure.py
```

Backend will be available at: **http://localhost:8000**

### 3. Verify Installation

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "azure-cost-optimizer",
#   "version": "2.0.0",
#   "llm_model": "llama3.2:latest",
#   "dependencies": {
#     "orchestrator": "active",
#     "ollama": "connected"
#   }
# }
```

---

## 🏗️ Architecture

### Multi-Agent System

```
User Query
    ↓
Orchestrator Agent (LangChain ReAct)
    ↓
┌────────────┴────────────┐
│                         │
Cost Analyst        Infrastructure Analyst
│                         │
Financial Analyst    Remediation Specialist
│                         │
└────────────┬────────────┘
             ↓
    Ollama LLM (llama3.2:latest)
             ↓
    Synthesized Response
```

### Technology Stack

**Backend:**
- FastAPI 0.104.1
- LangChain 0.1.0
- Ollama (llama3.2:latest)
- PostgreSQL 15
- Redis 7

**AI/ML:**
- LangChain for agent orchestration
- Ollama for local LLM processing
- ReAct agent pattern for reasoning

**Infrastructure:**
- Docker Compose for services
- WebSocket for real-time communication

---

## 📊 API Endpoints

### Health & Status

```bash
GET /health
GET /api/v1/agent-status
```

### Dashboard

```bash
GET /api/v1/dashboard/summary
GET /api/v1/dashboard/costs?period=30d
```

### Analysis

```bash
POST /api/v1/analyze
{
  "query": "Analyze my Azure VM costs",
  "time_period": "30d"
}

POST /api/v1/optimize
{
  "query": "How can I reduce storage costs?",
  "priority": "savings"
}

POST /api/v1/parallel-analysis
{
  "query": "Comprehensive cost analysis"
}
```

### Infrastructure

```bash
GET /api/v1/infrastructure/vms
GET /api/v1/infrastructure/storage
GET /api/v1/infrastructure/comprehensive
```

### Recommendations

```bash
GET /api/v1/recommendations
```

### WebSocket

```bash
WS /ws/cost-analysis

# Message format:
{
  "type": "cost_analysis",  // or "optimization_request", "parallel_analysis", "comprehensive_analysis"
  "query": "Your question here"
}
```

---

## 🤖 Agent Capabilities

### 1. Cost Analyst Agent

**Specialization:** Azure cost trends and spending analysis

**Use Cases:**
- "What are my top spending services?"
- "Show me cost trends for the last 30 days"
- "Identify any cost anomalies"

**Capabilities:**
- Cost trend analysis
- Service-level cost breakdown
- Anomaly detection
- Month-over-month comparisons

### 2. Infrastructure Analyst Agent

**Specialization:** Resource utilization and right-sizing

**Use Cases:**
- "Which VMs are underutilized?"
- "How can I optimize storage accounts?"
- "Show me right-sizing opportunities"

**Capabilities:**
- VM utilization analysis
- Storage tier optimization
- Right-sizing recommendations
- Reserved Instance opportunities

### 3. Financial Analyst Agent

**Specialization:** ROI calculations and projections

**Use Cases:**
- "Calculate ROI for these optimizations"
- "What's the payback period?"
- "Project costs for next 6 months"

**Capabilities:**
- ROI calculations
- Payback period analysis
- Cost-benefit analysis
- Future cost projections

### 4. Remediation Specialist Agent

**Specialization:** Actionable implementation plans

**Use Cases:**
- "Create an implementation plan"
- "How do I implement these recommendations?"
- "Prioritize optimizations by impact"

**Capabilities:**
- Step-by-step implementation plans
- Priority-based ordering
- Risk assessment
- Rollback procedures

---

## 💡 Usage Examples

### Example 1: Cost Analysis

```python
import requests

response = requests.post("http://localhost:8000/api/v1/analyze", json={
    "query": "Analyze my Azure costs and identify top 3 optimization opportunities",
    "time_period": "30d"
})

print(response.json()["analysis"])
```

### Example 2: Parallel Agent Analysis

```python
response = requests.post("http://localhost:8000/api/v1/parallel-analysis", json={
    "query": "Comprehensive Azure cost optimization analysis"
})

results = response.json()["results"]
print(f"Cost Analysis: {results['cost_analysis']}")
print(f"Infrastructure: {results['infrastructure_analysis']}")
print(f"Financial: {results['financial_analysis']}")
print(f"Remediation: {results['remediation_plan']}")
```

### Example 3: WebSocket Real-time Analysis

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/cost-analysis');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'comprehensive_analysis',
    query: 'Analyze everything and give me a detailed report'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'status') {
    console.log(`Progress: ${data.progress}% - ${data.message}`);
  } else if (data.type === 'comprehensive_analysis_complete') {
    console.log('Analysis complete!', data.data);
  }
};
```

---

## 🧪 Testing

### Test Mock Data Generators

```bash
cd backend
source venv-azure/bin/activate

# Test data generators
python -c "from src.mock import azure_data_generator; print(azure_data_generator.generate_dashboard_data())"
```

### Test LangChain Agents

```bash
# Test cost analyst
python -c "from src.agents_langchain import cost_analyst; import asyncio; print(asyncio.run(cost_analyst.analyze('What are my costs?')))"

# Test orchestrator
python -c "from src.agents_langchain import azure_orchestrator; import asyncio; print(asyncio.run(azure_orchestrator.analyze('Analyze my Azure spending')))"
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Dashboard data
curl http://localhost:8000/api/v1/dashboard/summary | jq .

# Cost analysis
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "What are my top costs?"}' | jq .
```

---

## 🐛 Troubleshooting

### Ollama Not Connecting

```bash
# Check if Ollama container is running
docker ps | grep ollama

# Check Ollama logs
docker logs costsense-azure-ollama

# Test Ollama directly
curl http://localhost:11434/api/tags

# Restart Ollama
docker restart costsense-azure-ollama
```

### Model Not Found

```bash
# Pull model again
docker exec costsense-azure-ollama ollama pull llama3.2:latest

# List available models
docker exec costsense-azure-ollama ollama list
```

### Backend Startup Issues

```bash
# Check Python version
python --version  # Must be 3.11+

# Verify virtual environment
which python  # Should point to venv-azure

# Check installed packages
pip list | grep langchain

# View backend logs
tail -f logs/app_*.log
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Or use different port
uvicorn main_azure:app --port 8001
```

---

## 📁 Project Structure

```
CostSense-AI/
├── backend/
│   ├── main_azure.py                 # FastAPI application entry point
│   ├── requirements-azure.txt        # Python dependencies
│   ├── .env.azure                    # Configuration
│   │
│   └── src/
│       ├── config/
│       │   └── langchain_config.py   # LangChain configuration
│       │
│       ├── mock/                     # Azure mock data generators
│       │   ├── azure_data_generator.py
│       │   ├── azure_cost_data.py
│       │   ├── azure_vm_data.py
│       │   └── azure_storage_data.py
│       │
│       ├── agents_langchain/         # LangChain agents
│       │   ├── orchestrator.py
│       │   ├── cost_analyst.py
│       │   ├── infrastructure_analyst.py
│       │   ├── financial_analyst.py
│       │   └── remediation_specialist.py
│       │
│       └── routers/                  # API routers
│           ├── azure_cost_optimization.py
│           └── azure_websocket.py
│
├── docker-compose.azure.yml          # Docker services
└── README_AZURE.md                   # This file
```

---

## 🔒 Security

### Local AI Processing
- All LLM processing happens locally via Ollama
- No data sent to external APIs
- Complete data sovereignty

### API Security (Production)
- Enable HTTPS/WSS
- Implement JWT authentication
- Add rate limiting
- Enable CORS restrictions
- Use secrets manager for sensitive data

### Azure Permissions (Phase 2)
When integrating with real Azure APIs, use read-only permissions:
- `Microsoft.CostManagement/*/read`
- `Microsoft.Compute/*/read`
- `Microsoft.Storage/*/read`
- `Microsoft.Monitor/*/read`

---

## 🚀 Production Deployment

### Environment Variables

Update `.env.azure` for production:

```bash
ENV=production
DEBUG=false
SECRET_KEY=<strong-secret-key>
ENCRYPTION_KEY=<strong-encryption-key>

# Azure credentials (Phase 2)
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<your-client-id>
AZURE_CLIENT_SECRET=<your-client-secret>
```

### Scaling

```bash
# Scale with Docker Compose
docker compose -f docker-compose.azure.yml up -d --scale backend=3

# Or deploy to cloud
# - Azure App Service
# - Azure Kubernetes Service (AKS)
# - Azure Container Instances
```

---

## 📈 Performance

### Metrics

- **Dashboard Load**: <2 seconds
- **AI Response Time**: 5-10 seconds (depends on query complexity)
- **WebSocket Latency**: <100ms
- **Concurrent Users**: 50+ (with proper scaling)
- **Memory Usage**: ~8GB (Ollama + llama3.2)

### Optimization Tips

1. **Cache frequently accessed data** (Redis)
2. **Use connection pooling** (PostgreSQL)
3. **Enable response compression**
4. **Implement request queuing** for AI queries
5. **Monitor Ollama performance** and adjust model settings

---

## 🎓 Learning Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Azure Cost Management](https://docs.microsoft.com/azure/cost-management-billing/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📞 Support

- **Documentation**: See `/docs` folder
- **API Reference**: http://localhost:8000/docs (when running)
- **Issues**: GitHub Issues
- **Email**: support@costsense.ai

---

**Built with ❤️ using LangChain, Ollama, and FastAPI**

🌟 Star this repo if you find it useful!
