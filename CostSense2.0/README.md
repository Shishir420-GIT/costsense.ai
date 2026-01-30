# CostSense AI

**Multi-Cloud Cost Intelligence Platform with AI-Assisted Optimization**

CostSense AI is a production-grade, AI-assisted platform for tracking, analyzing, and optimizing cloud infrastructure costs across AWS, Azure, and GCP. Built with a focus on safety, explainability, and human oversight.

---

## 🏗️ Architecture

```
CostSense AI
├── Backend (FastAPI + Python 3.11)
│   ├── Cloud cost adapters (AWS, Azure, GCP)
│   ├── AI orchestration (local LLaMA 3.1 via Ollama)
│   ├── ITSM integration (ServiceNow)
│   └── WebSocket for real-time updates
├── Frontend (React 18 + TypeScript + Vite)
│   ├── Cost dashboards
│   ├── AI-powered chatbot
│   └── Real-time streaming updates
└── Infrastructure
    ├── PostgreSQL (data persistence)
    ├── Redis (caching & sessions)
    └── Ollama (local AI inference)
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- 8GB+ RAM (for Ollama LLM)
- 20GB+ disk space

### 1. Clone and Setup

```bash
cd CostSense2.0
cp backend/.env.example backend/.env
```

### 2. Start All Services

```bash
docker-compose up -d
```

This will:
- Start PostgreSQL database
- Start Redis cache
- Start Ollama AI runtime
- Pull LLaMA 3.1 8B model (first run only - ~5GB download)
- Start FastAPI backend
- Build and start React frontend

### 3. Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📦 Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 80 | React application (Nginx) |
| Backend | 8000 | FastAPI REST & WebSocket API |
| PostgreSQL | 5432 | Primary database |
| Redis | 6379 | Cache & session store |
| Ollama | 11434 | Local AI inference |

---

## 🔧 Development Setup

### Backend Development

```bash
cd backend

# Install Poetry
pip install poetry

# Install dependencies
poetry install

# Run migrations (when available)
poetry run alembic upgrade head

# Start development server
poetry run uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Access at http://localhost:5173

### Pull Ollama Model Manually

```bash
# If model wasn't pulled automatically
docker exec -it costsense-ollama ollama pull llama3.1:8b-instruct

# Verify model is available
docker exec -it costsense-ollama ollama list
```

---

## 🎨 Design System

CostSense AI uses a professional color scheme inspired by Ernst & Young:

- **Primary**: Yellow (#FFE600) - Actions, highlights, success
- **Background**: Black (#000000) - Main background
- **Surface**: Dark Grey (#1a1a1a) - Cards and panels
- **Border**: Medium Grey (#3a3a3a) - Separators
- **Text**: White - Primary text

---

## 🔐 Security Model

**Key Principles:**

1. ✅ **AI is decision-support only** - No autonomous actions
2. ✅ **Local AI inference** - No external LLM APIs
3. ✅ **Read-only cloud access** - No write permissions
4. ✅ **Human confirmation required** - For all actions
5. ✅ **Full audit trail** - Every decision logged

---

## 🧠 AI Capabilities

CostSense AI uses **LLaMA 3.1 8B Instruct** via Ollama for:

- Cost trend analysis
- Natural language explanations
- Anomaly detection reasoning
- Optimization recommendation summaries
- Intent classification for chatbot

**What AI Does NOT Do:**
- Make autonomous changes
- Access external APIs
- Execute cloud operations
- Bypass human approval

---

## 📊 Features (Roadmap)

### Phase 1: Foundation ✅
- [x] Monorepo structure
- [x] Backend FastAPI service
- [x] Frontend React application
- [x] Docker containerization
- [x] PostgreSQL & Redis setup
- [x] Ollama integration

### Phase 2: Core Backend (Next)
- [ ] Database models & migrations
- [ ] WebSocket streaming
- [ ] Auth middleware
- [ ] Structured logging

### Phase 3: Cloud Adapters
- [ ] AWS cost adapter
- [ ] Azure cost adapter (stub)
- [ ] GCP cost adapter (stub)
- [ ] Normalized cost schema

### Phase 4: AI Runtime
- [ ] Ollama client wrapper
- [ ] Function calling framework
- [ ] System prompts
- [ ] JSON schema enforcement

### Phase 5: Agent Orchestration
- [ ] Cost Analysis Agent
- [ ] Optimization Agent
- [ ] Explanation Agent
- [ ] Task routing

### Phase 6: ITSM Integration
- [ ] ServiceNow client
- [ ] Ticket creation workflow
- [ ] Confirmation system

### Phase 7: Chatbot
- [ ] Intent classification
- [ ] Context injection
- [ ] Tool routing
- [ ] Session memory

### Phase 8: Frontend UI
- [ ] Cost dashboards
- [ ] Real-time charts
- [ ] Chatbot widget
- [ ] Investigation history

### Phase 9: Observability
- [ ] Comprehensive logging
- [ ] Audit tables
- [ ] Error handling
- [ ] Metrics

### Phase 10: Production Ready
- [ ] Guardrail validation
- [ ] Seed data
- [ ] Final documentation

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.109+
- **Language**: Python 3.11
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **AI Runtime**: Ollama (LLaMA 3.1)

### Frontend
- **Framework**: React 18
- **Language**: TypeScript 5.3
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3.4
- **State**: Zustand
- **Data Fetching**: TanStack Query
- **Charts**: Recharts
- **Icons**: Lucide React

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Target Deployment**: Azure Container Apps
- **Web Server**: Nginx (production)

---

## 📝 Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://costsense:costsense@postgres:5432/costsense

# Redis
REDIS_URL=redis://redis:6379/0

# Ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1:8b-instruct

# Application
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Cloud Providers (optional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1

AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
AZURE_SUBSCRIPTION_ID=

GOOGLE_APPLICATION_CREDENTIALS=
GCP_PROJECT_ID=

# ServiceNow (optional)
SERVICENOW_INSTANCE=
SERVICENOW_USERNAME=
SERVICENOW_PASSWORD=
```

---

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f ollama

# Restart a service
docker-compose restart backend

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Rebuild services
docker-compose build
docker-compose up -d --force-recreate
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
poetry run pytest

# Frontend tests
cd frontend
npm run test
```

---

## 📖 API Documentation

Once the backend is running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🤝 Contributing

This is a production-grade reference implementation. Key principles:

1. **Safety First**: Never compromise on guardrails
2. **Explainability**: All AI decisions must be traceable
3. **Human-in-the-Loop**: No autonomous actions
4. **Code Quality**: Type hints, tests, documentation

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🆘 Troubleshooting

### Ollama model not downloading
```bash
# Check ollama logs
docker-compose logs ollama-init

# Manually pull model
docker exec -it costsense-ollama ollama pull llama3.1:8b-instruct
```

### Backend can't connect to database
```bash
# Check postgres is running
docker-compose ps postgres

# View postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres
```

### Frontend showing 502 errors
```bash
# Check backend is healthy
curl http://localhost:8000/health

# Check backend logs
docker-compose logs backend
```

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process (replace PID)
kill -9 <PID>

# Or change port in docker-compose.yml
```

---

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ for responsible AI-assisted cloud cost optimization**

---

## 🌐 Azure Cosmos DB for PostgreSQL Support

CostSense AI supports **Azure Cosmos DB for PostgreSQL** for enterprise-grade scalability:

### Quick Setup

```bash
# 1. Create Cosmos DB for PostgreSQL cluster
az cosmosdb postgres cluster create \
  --resource-group costsense-rg \
  --name costsense-cosmos-pg \
  --location eastus \
  --administrator-login citus \
  --administrator-login-password '<STRONG_PASSWORD>'

# 2. Update .env with connection string
DATABASE_URL=postgresql://citus:PASSWORD@c-costsense.12345.postgres.cosmos.azure.com:5432/citus?sslmode=require

# 3. Run migrations
docker exec -it costsense-backend alembic upgrade head

# 4. Seed data
docker exec -it costsense-backend python scripts/seed_data.py
```

### Benefits

✅ **Horizontal Scaling** - Distribute data across nodes  
✅ **High Availability** - Built-in replication and failover  
✅ **Global Distribution** - Deploy to multiple regions  
✅ **Managed Service** - Automated backups and patching  
✅ **PostgreSQL Compatible** - No code changes required  

For detailed setup instructions, see **[AZURE_COSMOS_DB_SETUP.md](AZURE_COSMOS_DB_SETUP.md)**.

