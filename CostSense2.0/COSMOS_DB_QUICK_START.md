# 🚀 Azure Cosmos DB for PostgreSQL - Quick Start

This guide gets you running with Azure Cosmos DB for PostgreSQL in **under 10 minutes**.

---

## ⚡ 1-Minute Setup

```bash
# Set your variables
RESOURCE_GROUP="costsense-rg"
CLUSTER_NAME="costsense-db"
PASSWORD="YourStr0ngP@ssw0rd!"

# Create everything
az group create --name $RESOURCE_GROUP --location eastus

az cosmosdb postgres cluster create \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --location eastus \
  --administrator-login citus \
  --administrator-login-password "$PASSWORD" \
  --node-count 1 \
  --coordinator-v-cores 2 \
  --coordinator-storage-quota-in-mb 131072

# Get connection string
HOST=$(az cosmosdb postgres cluster show \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --query "serverNames[0].fullyQualifiedDomainName" -o tsv)

echo "Connection String:"
echo "DATABASE_URL=postgresql://citus:$PASSWORD@$HOST:5432/citus?sslmode=require"
```

---

## 🔧 Update CostSense

### Option 1: Using .env file

```bash
# Create .env file in backend/
cat > backend/.env << EOF
DATABASE_URL=postgresql://citus:PASSWORD@HOST:5432/citus?sslmode=require
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
REDIS_URL=redis://redis:6379/0
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1:8b-instruct
EOF

# Start CostSense (postgres service will be skipped)
docker-compose up -d
```

### Option 2: Environment variable

```bash
# Set in terminal
export DATABASE_URL="postgresql://citus:PASSWORD@HOST:5432/citus?sslmode=require"

# Start services
docker-compose up -d
```

---

## 📊 Initialize Database

```bash
# Run migrations
docker exec -it costsense-backend alembic upgrade head

# Seed sample data (90 days of costs)
docker exec -it costsense-backend python scripts/seed_data.py
```

---

## ✅ Verify

```bash
# Test connection
docker exec -it costsense-backend python -c "
from app.database import engine
with engine.connect() as conn:
    result = conn.execute('SELECT version()')
    print('Connected:', result.fetchone()[0][:50])
"

# Check API
curl http://localhost:8000/health

# Access UI
open http://localhost
```

---

## 🎯 What You Get

- ✅ **Scalable Database** - Azure Cosmos DB for PostgreSQL
- ✅ **No Code Changes** - Drop-in replacement
- ✅ **High Availability** - Built-in replication
- ✅ **Managed Backups** - Automated daily backups
- ✅ **Global Ready** - Multi-region support

---

## 💰 Cost Estimate

**Development Tier** (what we just created):
- 1 node, 2 vCores, 128GB storage
- ~$200-300/month
- Perfect for testing and small deployments

**Production Tier** (recommended):
- 2+ nodes, 4+ vCores each
- High availability enabled
- ~$500-1000/month

---

## 🔒 Secure It

```bash
# Get your IP
MY_IP=$(curl -s https://api.ipify.org)

# Allow only your IP
az cosmosdb postgres cluster firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --cluster-name $CLUSTER_NAME \
  --rule-name AllowMyIP \
  --start-ip-address $MY_IP \
  --end-ip-address $MY_IP

# For production, use Private Endpoints instead
```

---

## 📈 Scale Up When Ready

```bash
# Add more compute
az cosmosdb postgres cluster update \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --coordinator-v-cores 4

# Add worker nodes (for sharding)
az cosmosdb postgres cluster update \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --node-count 2

# Enable high availability
az cosmosdb postgres cluster update \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --enable-ha true
```

---

## 🆘 Troubleshooting

### Cannot connect?

```bash
# Check firewall rules
az cosmosdb postgres cluster firewall-rule list \
  --resource-group $RESOURCE_GROUP \
  --cluster-name $CLUSTER_NAME

# Add Azure services
az cosmosdb postgres cluster firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --cluster-name $CLUSTER_NAME \
  --rule-name AllowAzure \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### Slow queries?

```bash
# Increase connection pool
export DATABASE_POOL_SIZE=30
export DATABASE_MAX_OVERFLOW=60
```

---

## 🎉 You're Done!

Your CostSense AI is now running on enterprise-grade Azure Cosmos DB for PostgreSQL!

**Next Steps:**
- Connect your cloud providers (AWS/Azure/GCP)
- Explore the chatbot assistant
- Create cost optimization investigations
- Generate ServiceNow tickets

For detailed features, see [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md)
