# CostSense AI - Deployment Guide

## 🚀 Quick Deploy

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM
- 20GB+ disk space

### Local Development

```bash
# 1. Clone repository
cd CostSense2.0

# 2. Set up environment
cp backend/.env.example backend/.env

# 3. Start all services
docker-compose up -d

# 4. Wait for Ollama model download (~5GB, first run only)
docker-compose logs -f ollama-init

# 5. Seed database with sample data
docker exec -it costsense-backend python scripts/seed_data.py

# 6. Access application
open http://localhost              # Frontend
open http://localhost:8000/docs    # API Documentation
```

## 📦 Production Deployment

### Azure Container Apps (Recommended)

#### 1. Prepare Infrastructure

```bash
# Create resource group
az group create --name costsense-rg --location eastus

# Create Container Apps environment
az containerapp env create \
  --name costsense-env \
  --resource-group costsense-rg \
  --location eastus

# Create PostgreSQL Flexible Server
az postgres flexible-server create \
  --name costsense-db \
  --resource-group costsense-rg \
  --location eastus \
  --admin-user costsense \
  --admin-password <SECURE_PASSWORD> \
  --sku-name Standard_B2s \
  --tier Burstable \
  --storage-size 32

# Create Azure Cache for Redis
az redis create \
  --name costsense-cache \
  --resource-group costsense-rg \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

#### 2. Build and Push Images

```bash
# Login to Azure Container Registry
az acr login --name <YOUR_ACR_NAME>

# Build and push backend
docker build -t <YOUR_ACR_NAME>.azurecr.io/costsense-backend:latest ./backend
docker push <YOUR_ACR_NAME>.azurecr.io/costsense-backend:latest

# Build and push frontend
docker build -t <YOUR_ACR_NAME>.azurecr.io/costsense-frontend:latest ./frontend
docker push <YOUR_ACR_NAME>.azurecr.io/costsense-frontend:latest
```

#### 3. Deploy Container Apps

```bash
# Deploy backend
az containerapp create \
  --name costsense-backend \
  --resource-group costsense-rg \
  --environment costsense-env \
  --image <YOUR_ACR_NAME>.azurecr.io/costsense-backend:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --env-vars \
    DATABASE_URL="<POSTGRES_CONNECTION_STRING>" \
    REDIS_URL="<REDIS_CONNECTION_STRING>" \
    OLLAMA_BASE_URL="http://ollama:11434"

# Deploy frontend
az containerapp create \
  --name costsense-frontend \
  --resource-group costsense-rg \
  --environment costsense-env \
  --image <YOUR_ACR_NAME>.azurecr.io/costsense-frontend:latest \
  --target-port 80 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3
```

### Environment Variables

#### Backend (.env)

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:5432/costsense
REDIS_URL=redis://host:6379/0
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1:8b-instruct

# Optional - Cloud Providers
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_REGION=us-east-1

AZURE_TENANT_ID=<your-tenant>
AZURE_CLIENT_ID=<your-client>
AZURE_CLIENT_SECRET=<your-secret>
AZURE_SUBSCRIPTION_ID=<your-subscription>

GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GCP_PROJECT_ID=<your-project>

# Optional - ServiceNow
SERVICENOW_INSTANCE=<your-instance>
SERVICENOW_USERNAME=<your-username>
SERVICENOW_PASSWORD=<your-password>
```

## 🔒 Security Hardening

### 1. Enable Authentication

Replace placeholder auth in `app/middleware/auth.py`:

```python
# TODO: Implement real JWT authentication
# - Use python-jose for JWT
# - Store hashed passwords with bcrypt
# - Implement token refresh
# - Add RBAC
```

### 2. Secure Database

```bash
# Use SSL connections
DATABASE_URL=postgresql://user:pass@host:5432/costsense?sslmode=require

# Enable connection pooling
# Already configured in app/database.py
```

### 3. API Rate Limiting

Install and configure:

```bash
pip install slowapi

# Add to main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### 4. Secrets Management

Use Azure Key Vault:

```bash
az keyvault create \
  --name costsense-kv \
  --resource-group costsense-rg \
  --location eastus

# Store secrets
az keyvault secret set --vault-name costsense-kv \
  --name database-url --value "<CONNECTION_STRING>"
```

## 📊 Monitoring

### Application Insights

```python
# Add to backend
from opencensus.ext.azure import metrics_exporter
from opencensus.ext.azure.log_exporter import AzureLogHandler

# Configure
exporter = metrics_exporter.new_metrics_exporter(
    connection_string='<CONNECTION_STRING>'
)
```

### Health Checks

Already implemented:
- `/health` - Basic health check
- Database connection test
- Redis connection test
- Ollama availability check

### Logging

Structured logging already configured:
- JSON output in production
- Log levels configurable via `LOG_LEVEL`
- All AI interactions logged for audit

## 🧪 Testing

```bash
# Backend tests
cd backend
poetry run pytest

# Frontend tests
cd frontend
npm run test

# Integration tests
docker-compose -f docker-compose.test.yml up
```

## 📈 Scaling

### Horizontal Scaling

Container Apps auto-scaling rules:

```bash
az containerapp update \
  --name costsense-backend \
  --resource-group costsense-rg \
  --min-replicas 2 \
  --max-replicas 10 \
  --scale-rule-name cpu-rule \
  --scale-rule-type cpu \
  --scale-rule-metadata "type=Utilization" "value=70"
```

### Database Scaling

```bash
# Scale PostgreSQL
az postgres flexible-server update \
  --name costsense-db \
  --resource-group costsense-rg \
  --sku-name Standard_D4s_v3

# Enable read replicas
az postgres flexible-server replica create \
  --replica-name costsense-db-replica \
  --source-server costsense-db \
  --resource-group costsense-rg
```

## 🔄 CI/CD

### GitHub Actions

```yaml
name: Deploy to Azure
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build and push
        run: |
          docker build -t ${{ secrets.ACR_NAME }}.azurecr.io/costsense-backend:${{ github.sha }} ./backend
          docker push ${{ secrets.ACR_NAME }}.azurecr.io/costsense-backend:${{ github.sha }}

      - name: Deploy to Container Apps
        run: |
          az containerapp update \
            --name costsense-backend \
            --resource-group costsense-rg \
            --image ${{ secrets.ACR_NAME }}.azurecr.io/costsense-backend:${{ github.sha }}
```

## 🆘 Troubleshooting

### Ollama Issues

```bash
# Check Ollama logs
docker logs costsense-ollama

# Manually pull model
docker exec -it costsense-ollama ollama pull llama3.1:8b-instruct

# Verify model
docker exec -it costsense-ollama ollama list
```

### Database Connection

```bash
# Test connection
docker exec -it costsense-backend python -c "from app.database import engine; print(engine.connect())"

# Run migrations
docker exec -it costsense-backend alembic upgrade head
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Scale services
docker-compose up -d --scale backend=3
```

## 📞 Support

- Documentation: [README.md](README.md)
- Issues: GitHub Issues
- Email: support@costsense.ai

---

**Security Note**: Never commit secrets or credentials. Always use environment variables or secret management systems.
