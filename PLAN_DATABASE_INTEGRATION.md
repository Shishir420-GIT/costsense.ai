# Database Integration Plan: Replace Mock Data with Real-Time Data

## Executive Summary

Currently, **ALL data in the CostSense-AI application is mocked**. This plan outlines the comprehensive strategy to replace all mock data generators with a real-time database-backed system that supports:
- Lightning-fast updates (sub-second refresh)
- Realistic demo capabilities with persistent data
- Real-time streaming updates
- Production-ready scalability

---

## 1. Current State: What Data is Being Mocked

### 1.1 **Dashboard Data** (`azure_data_generator.generate_dashboard_data()`)
**Used by:** Dashboard page, Cost Analysis, AI Chat context

**Mocked Data:**
- `total_monthly_cost` - Total Azure spending ($11,147.72)
- `monthly_change_percent` - Month-over-month change (-1.3%)
- `projected_monthly_cost` - Projected end-of-month cost
- `daily_costs[]` - 30 days of historical costs with patterns (weekday/weekend/month-end variations)
- `top_services[]` - Top 10 Azure services by cost (Virtual Machines, SQL Database, Storage, etc.)
- `resource_groups[]` - Cost breakdown by resource group
- `utilization_metrics` - Compute, storage, database, network utilization percentages

**Current Source:** `backend/src/mock/azure_cost_data.py`
**Endpoints Using:**
- `/api/v1/dashboard/summary`
- `/api/v1/costs`
- `/api/v1/costs/daily`
- WebSocket: `/ws/cost-analysis`

---

### 1.2 **Virtual Machine Data** (`vm_data_generator.generate()`)
**Used by:** Infrastructure page, VM Analysis, Optimization recommendations

**Mocked Data:**
- `totalInstances` - Total number of VMs (6-12 random)
- `runningInstances` - Number of currently running VMs
- `instances[]` - Individual VM details:
  - `name` - VM name (vm-web-01, vm-database-03, etc.)
  - `size` - VM SKU (Standard_D8s_v3, Standard_B4ms, etc.)
  - `location` - Azure region (eastus, westus2, etc.)
  - `status` - running/stopped/deallocated
  - `cpuUtilization` - CPU usage percentage (5-95%)
  - `memoryUtilization` - Memory usage percentage
  - `monthlyCost` - Monthly cost per VM
  - `potentialSavings` - Savings from right-sizing
  - `recommendation` - AI recommendation (right-size, Reserved Instance, etc.)

**Current Source:** `backend/src/mock/azure_vm_data.py`
**Endpoints Using:**
- `/api/v1/infrastructure/vms`
- `/api/v1/infrastructure/resources`

---

### 1.3 **Storage Account Data** (`storage_data_generator.generate()`)
**Used by:** Infrastructure page, Storage Analysis, Optimization recommendations

**Mocked Data:**
- `totalAccounts` - Total number of storage accounts (3-8 random)
- `accounts[]` - Individual storage account details:
  - `name` - Storage account name (starchives01897, etc.)
  - `tier` - Storage tier (Hot, Cool, Archive)
  - `sizeGB` - Storage size in GB (500-8000 GB)
  - `monthlyCost` - Monthly cost per account
  - `potentialSavings` - Savings from tier optimization
  - `recommendations[]` - Tier migration suggestions
  - `lastAccessed` - Last access date patterns

**Current Source:** `backend/src/mock/azure_storage_data.py`
**Endpoints Using:**
- `/api/v1/infrastructure/storage`
- `/api/v1/infrastructure/resources`

---

### 1.4 **Optimization Recommendations** (`remediation_specialist._generate_recommendations()`)
**Used by:** Optimization page, AI recommendations

**Mocked Data:**
- `recommendations[]` - List of actionable recommendations:
  - `priority` - High/Medium/Low
  - `category` - Compute/Storage/Cost
  - `resource` - Resource name
  - `current_state` - Current configuration
  - `recommendation` - Action to take
  - `savings` - Monthly savings amount
  - `complexity` - Implementation complexity
  - `estimated_time` - Time to implement
  - `implementation_steps[]` - Step-by-step guide (NOT in current schema)

**Current Source:** `backend/src/agents_langchain/remediation_specialist.py`
**Endpoints Using:**
- `/api/v1/recommendations`

---

### 1.5 **Cost Trends & Analytics** (`cost_data_generator.generate_cost_trend()`)
**Used by:** Charts, trend analysis, forecasting

**Mocked Data:**
- `daily_costs[]` - Historical daily costs with realistic patterns
- `cost_trend` - Trend direction and statistics
- Service-level cost breakdowns
- Resource group cost allocations

**Current Source:** `backend/src/mock/azure_cost_data.py`
**Endpoints Using:**
- `/api/v1/costs/trend`
- Various analytics endpoints

---

## 2. Target Architecture: Database-Backed Real-Time System

### 2.1 **Technology Stack**

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  Dashboard │ AI Chat │ Optimization │ Infrastructure         │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST + WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Cost   │  │   VM     │  │ Storage  │  │ Recommend│   │
│  │ Analyst  │  │ Analyst  │  │ Analyst  │  │  Agent   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌─────▼─────┐ ┌─────▼──────┐
│  PostgreSQL  │ │   Redis   │ │ Background │
│   (Primary)  │ │  (Cache)  │ │  Workers   │
│              │ │           │ │ (Celery)   │
└──────────────┘ └───────────┘ └────────────┘
```

**Components:**
- **PostgreSQL** - Primary relational database for persistent data
- **Redis** - Caching layer for lightning-fast reads + real-time pub/sub
- **SQLAlchemy ORM** - Database models and queries
- **Alembic** - Database migrations
- **Celery** (optional) - Background tasks for data updates
- **WebSocket** - Real-time push updates to frontend

---

### 2.2 **Database Schema Design**

#### **Table 1: `azure_costs`**
```sql
CREATE TABLE azure_costs (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    total_cost DECIMAL(12, 2) NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    resource_group VARCHAR(255),
    cost DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    tags JSONB,  -- Flexible metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(date, service_name, resource_group)
);

CREATE INDEX idx_costs_date ON azure_costs(date DESC);
CREATE INDEX idx_costs_service ON azure_costs(service_name);
CREATE INDEX idx_costs_resource_group ON azure_costs(resource_group);
```

**Purpose:** Historical cost data for trends, analytics, and AI context

---

#### **Table 2: `azure_vms`**
```sql
CREATE TABLE azure_vms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    resource_id VARCHAR(500) UNIQUE NOT NULL,  -- Azure resource ID
    size VARCHAR(100) NOT NULL,  -- Standard_D8s_v3
    location VARCHAR(100) NOT NULL,
    resource_group VARCHAR(255),
    status VARCHAR(50) NOT NULL,  -- running, stopped, deallocated
    cpu_utilization DECIMAL(5, 2),  -- percentage
    memory_utilization DECIMAL(5, 2),
    monthly_cost DECIMAL(10, 2),
    potential_savings DECIMAL(10, 2),
    recommendation TEXT,
    tags JSONB,
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),

    CHECK (cpu_utilization >= 0 AND cpu_utilization <= 100),
    CHECK (memory_utilization >= 0 AND memory_utilization <= 100)
);

CREATE INDEX idx_vms_status ON azure_vms(status);
CREATE INDEX idx_vms_location ON azure_vms(location);
CREATE INDEX idx_vms_resource_group ON azure_vms(resource_group);
CREATE INDEX idx_vms_last_updated ON azure_vms(last_updated DESC);
```

**Purpose:** Current VM inventory with utilization metrics

---

#### **Table 3: `azure_storage_accounts`**
```sql
CREATE TABLE azure_storage_accounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    resource_id VARCHAR(500) UNIQUE NOT NULL,
    tier VARCHAR(50) NOT NULL,  -- Hot, Cool, Archive
    location VARCHAR(100) NOT NULL,
    resource_group VARCHAR(255),
    size_gb DECIMAL(12, 2) NOT NULL,
    monthly_cost DECIMAL(10, 2),
    potential_savings DECIMAL(10, 2),
    last_accessed DATE,
    recommendations JSONB,  -- Array of recommendation strings
    tags JSONB,
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_storage_tier ON azure_storage_accounts(tier);
CREATE INDEX idx_storage_location ON azure_storage_accounts(location);
CREATE INDEX idx_storage_last_accessed ON azure_storage_accounts(last_accessed);
```

**Purpose:** Storage account inventory with tier optimization data

---

#### **Table 4: `optimization_recommendations`**
```sql
CREATE TABLE optimization_recommendations (
    id SERIAL PRIMARY KEY,
    priority VARCHAR(20) NOT NULL,  -- High, Medium, Low, Critical
    category VARCHAR(50) NOT NULL,  -- Compute, Storage, Cost, Network
    resource_type VARCHAR(50) NOT NULL,  -- VM, Storage, etc.
    resource_id VARCHAR(500),  -- Foreign key to resource
    resource_name VARCHAR(255),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    current_state VARCHAR(500),
    recommendation TEXT NOT NULL,
    savings_monthly DECIMAL(10, 2),
    impact VARCHAR(20),  -- High, Medium, Low
    effort VARCHAR(20),  -- High, Medium, Low
    complexity VARCHAR(20),
    estimated_time VARCHAR(100),
    implementation_steps JSONB,  -- Array of step strings
    status VARCHAR(50) DEFAULT 'pending',  -- pending, in_progress, completed, dismissed
    tags JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,

    CHECK (priority IN ('Critical', 'High', 'Medium', 'Low'))
);

CREATE INDEX idx_recommendations_priority ON optimization_recommendations(priority);
CREATE INDEX idx_recommendations_category ON optimization_recommendations(category);
CREATE INDEX idx_recommendations_status ON optimization_recommendations(status);
CREATE INDEX idx_recommendations_created ON optimization_recommendations(created_at DESC);
```

**Purpose:** Actionable optimization recommendations with tracking

---

#### **Table 5: `dashboard_metrics`**
```sql
CREATE TABLE dashboard_metrics (
    id SERIAL PRIMARY KEY,
    metric_date DATE NOT NULL,
    total_monthly_cost DECIMAL(12, 2) NOT NULL,
    monthly_change_percent DECIMAL(5, 2),
    projected_monthly_cost DECIMAL(12, 2),
    compute_utilization DECIMAL(5, 2),
    storage_utilization DECIMAL(5, 2),
    database_utilization DECIMAL(5, 2),
    network_utilization DECIMAL(5, 2),
    total_vms INTEGER,
    total_storage_accounts INTEGER,
    total_potential_savings DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(metric_date)
);

CREATE INDEX idx_metrics_date ON dashboard_metrics(metric_date DESC);
```

**Purpose:** Pre-aggregated dashboard metrics for ultra-fast queries

---

### 2.3 **Redis Caching Strategy**

**Cache Keys:**
```
costsense:dashboard:summary          # TTL: 30 seconds
costsense:vms:list                   # TTL: 60 seconds
costsense:storage:list               # TTL: 60 seconds
costsense:recommendations:active     # TTL: 120 seconds
costsense:costs:daily:{date}         # TTL: 300 seconds (historical data)
costsense:costs:trend:30d            # TTL: 300 seconds
```

**Cache Invalidation:**
- On data update: Clear specific cache keys
- WebSocket broadcast triggers frontend refresh
- Background job updates cache every 30s

---

## 3. Implementation Plan

### **Phase 1: Database Setup & Models** (Day 1-2)

**Tasks:**
1. Create database models using SQLAlchemy
   - `models/azure_cost.py`
   - `models/azure_vm.py`
   - `models/azure_storage.py`
   - `models/optimization_recommendation.py`
   - `models/dashboard_metric.py`

2. Create Alembic migrations
   - Initial schema creation
   - Indexes for performance
   - Constraints and validations

3. Create database seeder script
   - Convert mock data generators to seeders
   - Generate realistic demo data
   - Support for re-seeding (for demos)

4. Test database setup
   - Verify schema creation
   - Test seed data generation
   - Validate indexes and constraints

**Deliverables:**
- `src/models/` directory with all models
- `alembic/versions/` migration files
- `scripts/seed_database.py` seeder script
- Database running with demo data

---

### **Phase 2: Data Access Layer** (Day 2-3)

**Tasks:**
1. Create repository pattern for data access
   - `repositories/cost_repository.py`
   - `repositories/vm_repository.py`
   - `repositories/storage_repository.py`
   - `repositories/recommendation_repository.py`

2. Implement CRUD operations
   - Get, create, update, delete methods
   - Batch operations for efficiency
   - Query builders for complex filters

3. Add Redis caching layer
   - Cache decorators
   - Cache invalidation logic
   - TTL configurations

4. Create data update services
   - Background workers (optional Celery)
   - Scheduled data refreshes
   - Real-time update handlers

**Deliverables:**
- `src/repositories/` directory with all repositories
- `src/services/data_service.py` for updates
- Redis caching integrated
- Unit tests for repositories

---

### **Phase 3: API Endpoint Migration** (Day 3-4)

**Tasks:**
1. Replace mock calls in endpoints
   - Update `/api/v1/dashboard/summary`
   - Update `/api/v1/infrastructure/vms`
   - Update `/api/v1/infrastructure/storage`
   - Update `/api/v1/recommendations`
   - Update `/api/v1/costs/*` endpoints

2. Optimize query performance
   - Use database indexes
   - Implement pagination
   - Add query result caching
   - Optimize N+1 queries

3. Add WebSocket real-time updates
   - Broadcast data changes
   - Subscribe to specific data streams
   - Handle connection lifecycle

4. Update agent integrations
   - Cost Analyst uses real data
   - Infrastructure Analyst uses real data
   - Remediation Specialist uses real data
   - Financial Analyst uses real data

**Deliverables:**
- All API endpoints using database
- WebSocket real-time updates working
- Agents using real data context
- API response times <100ms

---

### **Phase 4: Data Simulation & Demo Mode** (Day 4-5)

**Tasks:**
1. Create realistic data simulator
   - Simulate daily cost variations
   - Simulate VM utilization changes
   - Simulate storage growth patterns
   - Simulate new recommendations

2. Build admin panel for demo control
   - Reset database to demo state
   - Trigger cost spikes/drops
   - Add/remove resources
   - Generate new recommendations

3. Implement data refresh mechanisms
   - Background job to update metrics
   - Scheduled cost calculations
   - Utilization metric updates
   - Recommendation generation

4. Create demo scenarios
   - "High cost alert" scenario
   - "Optimization opportunity" scenario
   - "Cost reduction success" scenario
   - Real-time update showcase

**Deliverables:**
- `scripts/simulate_data.py` simulator
- Admin endpoints for demo control
- Background job scheduler setup
- Demo scenario presets

---

### **Phase 5: Performance Optimization** (Day 5-6)

**Tasks:**
1. Database query optimization
   - Analyze slow queries
   - Add missing indexes
   - Optimize joins
   - Use database views for complex aggregations

2. Caching optimization
   - Tune TTL values
   - Implement cache warming
   - Add cache hit/miss monitoring
   - Optimize cache key design

3. WebSocket optimization
   - Batch updates
   - Throttle update frequency
   - Client-side caching

4. Load testing
   - Test with 1000+ resources
   - Test concurrent users
   - Test WebSocket scalability
   - Identify bottlenecks

**Deliverables:**
- All queries under 50ms
- Cache hit rate >80%
- WebSocket updates <500ms latency
- Load test results documented

---

### **Phase 6: Testing & Validation** (Day 6-7)

**Tasks:**
1. Unit tests
   - Repository tests
   - Model validation tests
   - Cache layer tests

2. Integration tests
   - End-to-end API tests
   - WebSocket connection tests
   - Agent integration tests

3. Demo validation
   - Test all demo scenarios
   - Verify data consistency
   - Test refresh mechanisms
   - Validate real-time updates

4. Documentation
   - Database schema docs
   - API endpoint updates
   - Admin panel guide
   - Demo setup guide

**Deliverables:**
- 80%+ test coverage
- All tests passing
- Demo mode fully functional
- Complete documentation

---

## 4. Migration Strategy

### **4.1 Backwards Compatibility**

During migration, support both mock and database modes:

```python
# settings.py
USE_DATABASE = os.getenv("USE_DATABASE", "true").lower() == "true"

# data_service.py
def get_dashboard_data():
    if settings.USE_DATABASE:
        return database_repository.get_dashboard_summary()
    else:
        return azure_data_generator.generate_dashboard_data()
```

### **4.2 Gradual Rollout**

1. Week 1: Dashboard endpoints
2. Week 2: Infrastructure endpoints
3. Week 3: Optimization endpoints
4. Week 4: Real-time updates

---

## 5. Success Metrics

**Performance:**
- Dashboard load time: <2 seconds
- API response time: <100ms (p95)
- WebSocket update latency: <500ms
- Database query time: <50ms (p95)

**Reliability:**
- Cache hit rate: >80%
- Database uptime: 99.9%
- Zero data loss
- Consistent data across all views

**Demo Capability:**
- Can reset to clean state in <30 seconds
- Can simulate 1 month of data in <5 minutes
- Real-time updates visible to viewers
- Support 50+ concurrent demo viewers

---

## 6. Risk Mitigation

**Risk 1: Performance degradation**
- **Mitigation:** Aggressive caching, database indexes, query optimization
- **Fallback:** Keep mock mode as emergency fallback

**Risk 2: Data inconsistency**
- **Mitigation:** Database transactions, cache invalidation, WebSocket sync
- **Fallback:** Database rollback, cache clear

**Risk 3: Migration complexity**
- **Mitigation:** Gradual rollout, feature flags, comprehensive testing
- **Fallback:** Rollback to mock mode per endpoint

---

## 7. Future Enhancements

**After Initial Implementation:**

1. **Azure API Integration**
   - Connect to real Azure Cost Management API
   - Pull live data from Azure Monitor
   - Real-time resource discovery

2. **Historical Data Analytics**
   - Time-series analysis
   - Cost forecasting ML models
   - Anomaly detection

3. **Multi-Tenant Support**
   - Per-customer databases
   - Role-based access control
   - Custom dashboards

4. **Advanced Caching**
   - Distributed Redis cluster
   - Cache pre-warming strategies
   - Intelligent cache invalidation

---

## 8. Summary: What Gets Replaced

| Current Mock Generator | Replacement | Database Table(s) |
|------------------------|-------------|-------------------|
| `azure_data_generator.generate_dashboard_data()` | `DashboardRepository.get_summary()` | `dashboard_metrics`, `azure_costs` |
| `vm_data_generator.generate()` | `VMRepository.get_all()` | `azure_vms` |
| `storage_data_generator.generate()` | `StorageRepository.get_all()` | `azure_storage_accounts` |
| `cost_data_generator.generate_daily_costs()` | `CostRepository.get_daily_costs()` | `azure_costs` |
| `cost_data_generator.generate_service_costs()` | `CostRepository.get_by_service()` | `azure_costs` |
| `remediation_specialist._generate_recommendations()` | `RecommendationRepository.get_active()` | `optimization_recommendations` |

**ALL endpoints will use database queries instead of mock generators.**

---

## 9. Estimated Timeline

- **Phase 1:** 2 days (Database setup)
- **Phase 2:** 1.5 days (Data access layer)
- **Phase 3:** 1.5 days (API migration)
- **Phase 4:** 1 day (Demo mode)
- **Phase 5:** 1 day (Performance)
- **Phase 6:** 1 day (Testing)

**Total: 7-8 days for full implementation**

---

## 10. Next Steps (Immediate)

1. **User Approval** - Get approval for this plan
2. **Database Setup** - Set up PostgreSQL and Redis
3. **Create Models** - Define SQLAlchemy models
4. **Seed Data** - Create initial realistic dataset
5. **Migrate First Endpoint** - Start with `/api/v1/dashboard/summary`

---

**Ready to proceed with implementation?**
