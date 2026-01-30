# Azure Cosmos DB for PostgreSQL Setup Guide

CostSense AI now supports **Azure Cosmos DB for PostgreSQL** (formerly known as Hyperscale/Citus) as an alternative to standard PostgreSQL. This provides enterprise-grade scalability and global distribution.

---

## 🎯 Why Azure Cosmos DB for PostgreSQL?

- **Scalability**: Horizontal scaling with sharding
- **Performance**: Distributed query processing
- **High Availability**: Built-in replication and failover
- **Global Distribution**: Multi-region deployment
- **Managed Service**: Automated backups, patching, monitoring
- **PostgreSQL Compatible**: Works with existing SQLAlchemy models

---

## 🚀 Quick Setup

### 1. Create Azure Cosmos DB for PostgreSQL

```bash
# Set variables
RESOURCE_GROUP="costsense-rg"
LOCATION="eastus"
CLUSTER_NAME="costsense-cosmos-pg"

# Create resource group (if not exists)
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Cosmos DB for PostgreSQL cluster
az cosmosdb postgres cluster create \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --location $LOCATION \
  --administrator-login citus \
  --administrator-login-password '<STRONG_PASSWORD>' \
  --node-count 1 \
  --node-storage-quota-in-mb 131072 \
  --coordinator-v-cores 2 \
  --coordinator-storage-quota-in-mb 131072 \
  --enable-ha false

# Wait for cluster to be ready (5-10 minutes)
az cosmosdb postgres cluster wait \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --created
```

### 2. Configure Firewall Rules

```bash
# Allow Azure services
az cosmosdb postgres cluster firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --cluster-name $CLUSTER_NAME \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Allow your IP (for development)
MY_IP=$(curl -s https://api.ipify.org)
az cosmosdb postgres cluster firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --cluster-name $CLUSTER_NAME \
  --rule-name AllowMyIP \
  --start-ip-address $MY_IP \
  --end-ip-address $MY_IP
```

### 3. Get Connection String

```bash
# Get the connection details
az cosmosdb postgres cluster show \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --query "{host:serverNames[0].fullyQualifiedDomainName, port:port}" \
  -o json
```

Output example:
```json
{
  "host": "c-costsense.12345.postgres.cosmos.azure.com",
  "port": 5432
}
```

### 4. Update CostSense Configuration

Edit your `.env` file:

```bash
# Replace with your Cosmos DB connection string
DATABASE_URL=postgresql://citus:YOUR_PASSWORD@c-costsense.12345.postgres.cosmos.azure.com:5432/citus?sslmode=require

# Optional: Adjust pool settings for production
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
DATABASE_POOL_PRE_PING=true
```

**Important Notes:**
- **SSL is required** - Always include `?sslmode=require` in the connection string
- Default database name is `citus`
- Default admin user is `citus`
- Port is always `5432`

---

## 🔧 Database Migration

### Run Alembic Migrations

```bash
# From backend directory
cd backend

# Install dependencies (if not already)
poetry install

# Set environment variable
export DATABASE_URL="postgresql://citus:PASSWORD@c-costsense.12345.postgres.cosmos.azure.com:5432/citus?sslmode=require"

# Run migrations
poetry run alembic upgrade head
```

Or using Docker:

```bash
# Update docker-compose.yml with Cosmos DB URL
docker-compose up -d backend

# Run migrations
docker exec -it costsense-backend alembic upgrade head
```

### Seed Sample Data

```bash
# Using Docker
docker exec -it costsense-backend python scripts/seed_data.py

# Or locally
poetry run python scripts/seed_data.py
```

---

## 📊 Performance Optimization

### 1. Connection Pooling

Cosmos DB for PostgreSQL benefits from larger connection pools:

```bash
DATABASE_POOL_SIZE=30
DATABASE_MAX_OVERFLOW=60
```

### 2. Enable Distributed Tables (Optional)

For very large datasets, enable sharding:

```sql
-- Connect to your Cosmos DB
psql "postgresql://citus:PASSWORD@c-costsense.12345.postgres.cosmos.azure.com:5432/citus?sslmode=require"

-- Distribute cost_records table by provider
SELECT create_distributed_table('cost_records', 'provider');

-- Distribute investigations by provider
SELECT create_distributed_table('investigations', 'provider');
```

This distributes data across nodes for better performance.

### 3. Indexes

The application already creates indexes, but you can verify:

```sql
-- List indexes
SELECT tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public';
```

---

## 🔒 Security Best Practices

### 1. Use Azure Key Vault for Secrets

```bash
# Create Key Vault
az keyvault create \
  --name costsense-kv \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Store database password
az keyvault secret set \
  --vault-name costsense-kv \
  --name cosmos-db-password \
  --value '<YOUR_PASSWORD>'

# Grant Container App access
az keyvault set-policy \
  --name costsense-kv \
  --object-id <CONTAINER_APP_IDENTITY> \
  --secret-permissions get
```

### 2. Restrict Network Access

```bash
# Remove public access
az cosmosdb postgres cluster firewall-rule delete \
  --resource-group $RESOURCE_GROUP \
  --cluster-name $CLUSTER_NAME \
  --rule-name AllowMyIP

# Use Private Endpoint instead
az cosmosdb postgres cluster private-endpoint create \
  --resource-group $RESOURCE_GROUP \
  --cluster-name $CLUSTER_NAME \
  --vnet-name costsense-vnet \
  --subnet-name costsense-subnet
```

### 3. Enable Audit Logging

```bash
# Enable server logs
az cosmosdb postgres cluster update \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --enable-pgaudit true
```

---

## 📈 Monitoring

### 1. Azure Monitor Integration

Cosmos DB for PostgreSQL automatically integrates with Azure Monitor:

```bash
# View metrics
az monitor metrics list \
  --resource "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.DBforPostgreSQL/serverGroupsv2/$CLUSTER_NAME" \
  --metric "cpu_percent" \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z
```

### 2. Query Store

Enable query performance insights:

```sql
-- Connect and enable
ALTER SYSTEM SET pg_stat_statements.track = 'all';
SELECT pg_reload_conf();

-- View slow queries
SELECT
  query,
  calls,
  total_time,
  mean_time,
  max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

## 💰 Cost Optimization

### 1. Right-Size Your Cluster

Start small and scale up:

```bash
# Scale up coordinator
az cosmosdb postgres cluster update \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --coordinator-v-cores 4 \
  --coordinator-storage-quota-in-mb 262144
```

### 2. Use Burstable Compute

For development/staging:

```bash
az cosmosdb postgres cluster create \
  --name costsense-dev \
  --node-count 0 \
  --coordinator-v-cores 1 \
  --coordinator-storage-quota-in-mb 32768
```

### 3. Schedule Backups

Automated backups are included, but you can customize retention:

```bash
az cosmosdb postgres cluster update \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --backup-retention-days 14
```

---

## 🔄 Migration from Standard PostgreSQL

### Option 1: Using pg_dump/pg_restore

```bash
# Export from standard PostgreSQL
pg_dump -h localhost -U costsense -d costsense -F c -f costsense_backup.dump

# Restore to Cosmos DB
pg_restore -h c-costsense.12345.postgres.cosmos.azure.com \
  -U citus -d citus \
  --no-owner --no-acl \
  costsense_backup.dump
```

### Option 2: Using Azure Database Migration Service

```bash
# Create migration service
az dms create \
  --resource-group $RESOURCE_GROUP \
  --name costsense-dms \
  --location $LOCATION \
  --sku-name Premium_4vCores

# Create migration project via Azure Portal
```

---

## ✅ Verification

### Test Connection

```python
# test_cosmos_connection.py
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://citus:PASSWORD@c-costsense.12345.postgres.cosmos.azure.com:5432/citus?sslmode=require"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(result.fetchone())
    print("✅ Connection successful!")
```

### Check CostSense Health

```bash
# Start application
docker-compose up -d

# Check health endpoint
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","service":"costsense-ai","version":"0.1.0"}
```

---

## 📚 Additional Resources

- [Azure Cosmos DB for PostgreSQL Documentation](https://learn.microsoft.com/en-us/azure/cosmos-db/postgresql/)
- [Citus Documentation](https://docs.citusdata.com/)
- [Connection Pooling Best Practices](https://docs.citusdata.com/en/stable/admin_guide/connection_pooling.html)
- [Performance Tuning](https://docs.citusdata.com/en/stable/performance/performance_tuning.html)

---

## 🆘 Troubleshooting

### Connection Timeout

```bash
# Increase timeout in .env
DATABASE_URL=postgresql://citus:PASSWORD@host:5432/citus?sslmode=require&connect_timeout=30
```

### SSL Certificate Issues

```bash
# Download root certificate
curl -o root.crt https://cacerts.digicert.com/DigiCertGlobalRootCA.crt.pem

# Update connection string
DATABASE_URL=postgresql://citus:PASSWORD@host:5432/citus?sslmode=verify-full&sslrootcert=root.crt
```

### High Connection Count

```bash
# Check active connections
SELECT count(*) FROM pg_stat_activity;

# Reduce pool size if needed
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=10
```

---

## 🎉 Success!

Your CostSense AI application now runs on **Azure Cosmos DB for PostgreSQL** with enterprise-grade scalability and reliability!

For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md) for complete Azure Container Apps setup.
