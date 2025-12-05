# CostSense-AI Azure Migration - Step-by-Step Implementation Plan

**Based on Current Codebase Analysis**
**Version**: 1.0.0
**Created**: December 4, 2025

---

## 🎯 Executive Summary

This implementation plan provides a detailed, actionable roadmap for migrating CostSense-AI from AWS to Azure, replacing Strands Agents SDK with LangChain, and upgrading to llama3.2:latest.

**Current State Analysis:**
- ✅ Production-ready AWS implementation with Strands SDK
- ✅ 4 specialized agents (Cost, Infrastructure, Financial, Remediation)
- ✅ WebSocket real-time streaming
- ✅ React 18 frontend with Zustand state management
- ✅ Mock data generators in place
- ✅ Agent registry pattern for orchestration
- ⚠️ **No LangChain** - currently using Strands SDK
- ⚠️ **AWS-specific** - EC2, S3, RDS focus

**Target State:**
- 🎯 Azure-focused platform (VMs, Storage Accounts, SQL Database)
- 🎯 LangChain framework replacing Strands SDK
- 🎯 llama3.2:latest model via Ollama
- 🎯 Mock data (Phase 1) → Real Azure APIs (Phase 2)
- 🎯 Maintain all existing features and UX quality

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: Foundation Setup (Week 1)](#phase-1-foundation-setup-week-1)
3. [Phase 2: Backend Migration (Week 2)](#phase-2-backend-migration-week-2)
4. [Phase 3: Frontend Updates (Week 3)](#phase-3-frontend-updates-week-3)
5. [Phase 4: Integration & Testing (Week 4)](#phase-4-integration--testing-week-4)
6. [Migration Checklist](#migration-checklist)
7. [Rollback Plan](#rollback-plan)

---

## Prerequisites

### System Requirements
```bash
# Verify installations
python --version      # 3.11+
node --version        # 18+
docker --version      # 20.10+
docker-compose --version  # 2.0+

# Check available resources
free -h              # 16GB RAM minimum
df -h               # 20GB free disk space
```

### Current Codebase Backup
```bash
# Create backup branch
git checkout -b backup/aws-version-$(date +%Y%m%d)
git push origin backup/aws-version-$(date +%Y%m%d)

# Tag current state
git tag -a aws-v1.0.0 -m "AWS version before Azure migration"
git push origin aws-v1.0.0
```

### Environment Setup
```bash
# Create feature branch
git checkout -b feature/azure-migration

# Verify current setup works
cd backend
source venv/bin/activate
python -c "from src.agents.registry import agent_registry; print('✓ Strands SDK working')"

cd ../frontend
npm install
npm run build
echo "✓ Frontend builds successfully"
```

---

## Phase 1: Foundation Setup (Week 1)

### Day 1: Ollama & LangChain Setup

#### Step 1.1: Install Ollama with llama3.2:latest

```bash
# Stop existing containers
docker-compose down

# Update docker-compose.yml for Azure
cp docker-compose.yml docker-compose.azure.yml

# Edit docker-compose.azure.yml
```

**File: `docker-compose.azure.yml`**
```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: costsense-azure-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_azure_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_KEEP_ALIVE=24h
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
    # Optional: GPU support
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]

  postgres:
    image: postgres:15-alpine
    container_name: costsense-azure-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
      POSTGRES_DB: costsense_azure
    ports:
      - "5432:5432"
    volumes:
      - postgres_azure_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: costsense-azure-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_azure_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  ollama_azure_data:
  postgres_azure_data:
  redis_azure_data:

networks:
  default:
    name: costsense-azure-network
```

```bash
# Start services
docker-compose -f docker-compose.azure.yml up -d

# Wait for Ollama to be ready
sleep 10

# Pull llama3.2:latest
docker exec costsense-azure-ollama ollama pull llama3.2:latest

# Verify model
docker exec costsense-azure-ollama ollama list
# Expected output: llama3.2:latest  ...  7.4 GB  ...

# Test model
docker exec costsense-azure-ollama ollama run llama3.2:latest "Hello, test Azure analysis"
```

**Verification Checklist:**
- [ ] Ollama container running
- [ ] llama3.2:latest model downloaded (verify size ~7.4GB)
- [ ] Model responds to test queries
- [ ] PostgreSQL accessible on port 5432
- [ ] Redis accessible on port 6379

---

#### Step 1.2: Install LangChain Dependencies

**File: `backend/requirements-azure.txt`**
```txt
# Existing dependencies (keep most)
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0

# Database (keep)
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
redis==5.0.1

# REMOVE Strands SDK (to be replaced)
# strands-agents==1.4.0
# strands-agents-tools==1.0.0

# ADD LangChain
langchain==0.1.0
langchain-community==0.0.13
langchain-core==0.1.10
langchain-experimental==0.0.47
ollama==0.1.6

# Azure SDKs (for Phase 2)
azure-identity==1.15.0
azure-mgmt-costmanagement==4.0.0
azure-mgmt-compute==30.3.0
azure-mgmt-storage==21.1.0
azure-mgmt-monitor==6.0.0
azure-mgmt-resource==23.0.0

# REMOVE AWS (to be replaced)
# boto3==1.34.0
# botocore==1.34.0

# Keep utilities
pandas==2.1.4
numpy==1.24.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
cryptography==41.0.8

# Keep for RAG (if used later)
chromadb==0.4.18
sentence-transformers==2.2.2

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
```

```bash
# Create new virtual environment for Azure version
cd backend
python -m venv venv-azure
source venv-azure/bin/activate  # or venv-azure\Scripts\activate on Windows

# Install dependencies
pip install -r requirements-azure.txt

# Verify LangChain installation
python -c "from langchain import __version__; print(f'LangChain {__version__} installed')"
python -c "from langchain_community.llms import Ollama; print('✓ Ollama integration available')"
python -c "import ollama; print('✓ Ollama Python client ready')"
```

**Verification Checklist:**
- [ ] New venv-azure created
- [ ] LangChain installed (check version)
- [ ] Ollama Python client working
- [ ] No import errors
- [ ] Azure SDKs available (for future use)

---

#### Step 1.3: Update Configuration

**File: `backend/.env.azure`**
```bash
# Application
APP_NAME=CostSense-AI-Azure
ENV=development
DEBUG=true
LOG_LEVEL=INFO

# API
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
OLLAMA_TEMPERATURE=0.7
OLLAMA_MAX_TOKENS=2000
OLLAMA_TIMEOUT=120

# LangChain
LANGCHAIN_TRACING_V2=false
LANGCHAIN_ENDPOINT=http://localhost:8000
LANGCHAIN_API_KEY=optional
LANGCHAIN_PROJECT=costsense-azure

# Database
POSTGRES_URL=postgresql://postgres:postgres123@localhost:5432/costsense_azure
REDIS_URL=redis://localhost:6379
CACHE_EXPIRY_HOURS=24

# Azure Configuration (for Phase 2)
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_REGION=eastus

# Security
SECRET_KEY=your-secret-key-change-in-production
ENCRYPTION_KEY=your-encryption-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-change-in-production
JWT_ALGORITHM=HS256

# Agent Configuration
MAX_CONCURRENT_AGENTS=5
AGENT_TIMEOUT=300
AGENT_MAX_RETRIES=3

# WebSocket
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS=100
```

**File: `backend/src/config/langchain_config.py`** (NEW)
```python
"""LangChain configuration for Azure Cost Optimization"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class LangChainSettings(BaseSettings):
    """LangChain-specific settings"""

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:latest"
    OLLAMA_TEMPERATURE: float = 0.7
    OLLAMA_MAX_TOKENS: int = 2000
    OLLAMA_TIMEOUT: int = 120

    # LangChain
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_ENDPOINT: Optional[str] = None
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "costsense-azure"

    # Agent Configuration
    MAX_CONCURRENT_AGENTS: int = 5
    AGENT_TIMEOUT: int = 300
    AGENT_MAX_RETRIES: int = 3

    class Config:
        env_file = ".env.azure"
        case_sensitive = True


@lru_cache()
def get_langchain_settings() -> LangChainSettings:
    """Get cached LangChain settings"""
    return LangChainSettings()


def get_ollama_llm():
    """
    Get configured Ollama LLM instance

    Returns:
        Ollama: Configured LLM instance
    """
    from langchain_community.llms import Ollama

    settings = get_langchain_settings()

    return Ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=settings.OLLAMA_TEMPERATURE,
        num_predict=settings.OLLAMA_MAX_TOKENS,
        timeout=settings.OLLAMA_TIMEOUT
    )


# Test connection on import (optional, for debugging)
if __name__ == "__main__":
    settings = get_langchain_settings()
    print(f"✓ LangChain configured:")
    print(f"  - Model: {settings.OLLAMA_MODEL}")
    print(f"  - Base URL: {settings.OLLAMA_BASE_URL}")
    print(f"  - Temperature: {settings.OLLAMA_TEMPERATURE}")

    try:
        llm = get_ollama_llm()
        response = llm.invoke("Hello")
        print(f"✓ Ollama connection successful")
        print(f"  Response: {response[:100]}...")
    except Exception as e:
        print(f"✗ Ollama connection failed: {e}")
```

```bash
# Test configuration
cd backend
source venv-azure/bin/activate
python src/config/langchain_config.py
# Expected: ✓ LangChain configured, ✓ Ollama connection successful
```

**Verification Checklist:**
- [ ] .env.azure created with all required variables
- [ ] langchain_config.py created and tested
- [ ] Ollama connection working from Python
- [ ] Configuration loads without errors

---

### Day 2: Azure Mock Data Generators

#### Step 2.1: Create Azure Data Generator Module

**File Structure:**
```
backend/src/mock/
├── __init__.py
├── azure_data_generator.py       # Main generator
├── azure_vm_data.py               # VM-specific mock data
├── azure_storage_data.py          # Storage-specific mock data
├── azure_sql_data.py              # SQL Database mock data
└── azure_cost_data.py             # Cost Management mock data
```

**File: `backend/src/mock/__init__.py`**
```python
"""Mock data generators for Azure resources"""

from .azure_data_generator import AzureMockDataGenerator
from .azure_vm_data import VMDataGenerator
from .azure_storage_data import StorageDataGenerator
from .azure_sql_data import SQLDatabaseDataGenerator
from .azure_cost_data import CostDataGenerator

__all__ = [
    'AzureMockDataGenerator',
    'VMDataGenerator',
    'StorageDataGenerator',
    'SQLDatabaseDataGenerator',
    'CostDataGenerator'
]
```

**File: `backend/src/mock/azure_data_generator.py`**
```python
"""Main Azure mock data generator orchestrator"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import random
from .azure_vm_data import VMDataGenerator
from .azure_storage_data import StorageDataGenerator
from .azure_sql_data import SQLDatabaseDataGenerator
from .azure_cost_data import CostDataGenerator


class AzureMockDataGenerator:
    """
    Master generator for all Azure mock data

    Generates realistic Azure cost and resource data for development and testing.
    All data follows Azure naming conventions and pricing patterns.
    """

    def __init__(self, seed: int = None):
        """
        Initialize data generators

        Args:
            seed: Random seed for reproducible data
        """
        if seed:
            random.seed(seed)

        self.vm_generator = VMDataGenerator()
        self.storage_generator = StorageDataGenerator()
        self.sql_generator = SQLDatabaseDataGenerator()
        self.cost_generator = CostDataGenerator()

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """
        Generate complete dashboard summary data

        Returns:
            Dictionary with dashboard metrics:
            - total_monthly_cost: Current month spending
            - monthly_change_percent: % change from last month
            - projected_monthly_cost: Forecasted month-end cost
            - daily_costs: 30-day cost history
            - top_services: Top 5 services by cost
            - resource_groups: Cost by resource group
            - utilization_metrics: Resource utilization percentages
        """
        # Generate cost data
        daily_costs = self.cost_generator.generate_daily_costs(days=30)
        top_services = self.cost_generator.generate_service_costs()
        resource_groups = self._generate_resource_groups()

        # Calculate metrics
        total_monthly_cost = sum(day["cost"] for day in daily_costs[-30:])
        last_month_cost = total_monthly_cost * random.uniform(0.85, 1.15)
        monthly_change = ((total_monthly_cost - last_month_cost) / last_month_cost) * 100

        # Project month-end cost
        days_in_month = 30
        days_elapsed = len(daily_costs)
        avg_daily_cost = total_monthly_cost / days_elapsed
        projected_monthly_cost = avg_daily_cost * days_in_month

        return {
            "total_monthly_cost": round(total_monthly_cost, 2),
            "monthly_change_percent": round(monthly_change, 1),
            "projected_monthly_cost": round(projected_monthly_cost, 2),
            "daily_costs": daily_costs,
            "top_services": top_services,
            "resource_groups": resource_groups,
            "utilization_metrics": {
                "compute": round(random.uniform(45, 85), 1),
                "storage": round(random.uniform(60, 90), 1),
                "database": round(random.uniform(55, 80), 1),
                "network": round(random.uniform(40, 70), 1)
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    def generate_vm_data(self) -> Dict[str, Any]:
        """
        Generate virtual machine data

        Returns:
            Dictionary with VM instances and metrics
        """
        return self.vm_generator.generate()

    def generate_storage_data(self) -> Dict[str, Any]:
        """
        Generate storage account data

        Returns:
            Dictionary with storage accounts and metrics
        """
        return self.storage_generator.generate()

    def generate_sql_database_data(self) -> Dict[str, Any]:
        """
        Generate SQL database data

        Returns:
            Dictionary with SQL databases and metrics
        """
        return self.sql_generator.generate()

    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Generate comprehensive cost analysis data

        Similar to orchestrator_agent_simple.comprehensive_analysis()
        but with Azure-specific structure

        Returns:
            Complete analysis with all resource types
        """
        vm_data = self.generate_vm_data()
        storage_data = self.generate_storage_data()
        sql_data = self.generate_sql_database_data()
        cost_data = self.cost_generator.generate_daily_costs(days=30)

        total_potential_savings = (
            vm_data.get("potential_savings", 0) +
            storage_data.get("potential_savings", 0) +
            sql_data.get("potential_savings", 0)
        )

        return {
            "cost_analysis": {
                "total_cost": sum(day["cost"] for day in cost_data),
                "daily_costs": cost_data,
                "top_services": self.cost_generator.generate_service_costs(),
                "cost_trend": "increasing" if random.random() > 0.5 else "decreasing",
                "variance_percentage": round(random.uniform(5, 20), 1)
            },
            "infrastructure_analysis": {
                "vm_analysis": vm_data,
                "storage_analysis": storage_data,
                "sql_database_analysis": sql_data
            },
            "financial_analysis": {
                "total_potential_savings": round(total_potential_savings, 2),
                "roi_percentage": round(random.uniform(150, 250), 0),
                "payback_period_months": round(random.uniform(1.5, 3.5), 1),
                "confidence_level": round(random.uniform(80, 95), 0)
            },
            "remediation_plan": [
                "Implement Azure VM auto-shutdown for non-production resources",
                "Enable Azure Storage lifecycle management policies",
                "Right-size SQL Database tiers based on actual DTU usage",
                "Consider Azure Reserved VM Instances for consistent workloads",
                "Enable Azure Advisor recommendations monitoring"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

    def _generate_resource_groups(self) -> List[Dict[str, Any]]:
        """Generate resource group cost data"""
        rg_names = ["production", "staging", "development", "shared-services", "networking"]
        resource_groups = []

        for name in rg_names:
            cost = round(random.uniform(1000, 8000), 2)
            resource_count = random.randint(8, 45)

            resource_groups.append({
                "name": f"rg-{name}",
                "cost": cost,
                "resourceCount": resource_count,
                "location": random.choice(["eastus", "westus2", "westeurope"]),
                "tags": {
                    "environment": name if name in ["production", "staging", "development"] else "shared",
                    "managed-by": "terraform",
                    "cost-center": f"cc-{random.randint(1000, 9999)}"
                }
            })

        return resource_groups


# Singleton instance
azure_data_generator = AzureMockDataGenerator()
```

*(Continue in next message due to length...)*

**Verification Checklist:**
- [ ] azure_data_generator.py created
- [ ] Generates dashboard data successfully
- [ ] Data structure matches Azure format
- [ ] Resource groups include Azure-specific fields

---

### Day 3-4: Implement Detailed Mock Data Generators

I'll continue with the detailed implementation files for VM, Storage, SQL, and Cost data generators in the next steps. This gives you:

1. ✅ Ollama setup with llama3.2:latest
2. ✅ LangChain dependencies installed
3. ✅ Configuration files ready
4. ✅ Foundation for mock data generators

**Next Steps Preview:**
- Complete mock data generators (VM, Storage, SQL, Cost)
- Create LangChain tools for Azure
- Build LangChain agents (Orchestrator, Cost, Infrastructure, Financial, Remediation)
- Update FastAPI routers
- Migrate frontend components

Would you like me to continue with the detailed implementation of the mock data generators and LangChain agents?
