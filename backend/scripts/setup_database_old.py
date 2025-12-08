#!/usr/bin/env python3
"""
Complete Database Setup Script for CostSense-AI
- Creates all SQLite tables
- Seeds with realistic demo data
- Fast and ready for MVP
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, JSON, Boolean, Text, Index
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import random
from src.config.database import Base, engine, SessionLocal

print("🚀 CostSense-AI Database Setup")
print("=" * 60)

# ============================================================================
# STEP 1: Define All Models
# ============================================================================

class AzureCost(Base):
    """Daily cost records by service and resource group"""
    __tablename__ = "azure_costs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    service_name = Column(String(255), nullable=False, index=True)
    resource_group = Column(String(255), index=True)
    cost = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    tags = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_date_service', 'date', 'service_name'),
    )


class AzureVM(Base):
    """Virtual Machine inventory with utilization metrics"""
    __tablename__ = "azure_vms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    resource_id = Column(String(500), unique=True, nullable=False)
    size = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False, index=True)
    resource_group = Column(String(255), index=True)
    status = Column(String(50), nullable=False, index=True)
    cpu_utilization = Column(Float)
    memory_utilization = Column(Float)
    monthly_cost = Column(Float)
    potential_savings = Column(Float)
    recommendation = Column(Text)
    tags = Column(JSON)
    last_updated = Column(DateTime, default=func.now(), index=True)
    created_at = Column(DateTime, default=func.now())


class AzureStorageAccount(Base):
    """Storage account inventory with tier optimization"""
    __tablename__ = "azure_storage_accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    resource_id = Column(String(500), unique=True, nullable=False)
    tier = Column(String(50), nullable=False, index=True)
    location = Column(String(100), nullable=False)
    resource_group = Column(String(255), index=True)
    size_gb = Column(Float, nullable=False)
    monthly_cost = Column(Float)
    potential_savings = Column(Float)
    last_accessed = Column(Date)
    recommendations = Column(JSON)
    tags = Column(JSON)
    last_updated = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())


class OptimizationRecommendation(Base):
    """Actionable optimization recommendations"""
    __tablename__ = "optimization_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    priority = Column(String(20), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(500))
    resource_name = Column(String(255))
    title = Column(String(500), nullable=False)
    description = Column(Text)
    current_state = Column(String(500))
    recommendation = Column(Text, nullable=False)
    savings_monthly = Column(Float)
    impact = Column(String(20))
    effort = Column(String(20))
    complexity = Column(String(20))
    estimated_time = Column(String(100))
    implementation_steps = Column(JSON)
    status = Column(String(50), default="pending", index=True)
    tags = Column(JSON)
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime)


class DashboardMetric(Base):
    """Pre-aggregated dashboard metrics for ultra-fast queries"""
    __tablename__ = "dashboard_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_date = Column(Date, unique=True, nullable=False, index=True)
    total_monthly_cost = Column(Float, nullable=False)
    monthly_change_percent = Column(Float)
    projected_monthly_cost = Column(Float)
    compute_utilization = Column(Float)
    storage_utilization = Column(Float)
    database_utilization = Column(Float)
    network_utilization = Column(Float)
    total_vms = Column(Integer)
    total_storage_accounts = Column(Integer)
    total_potential_savings = Column(Float)
    top_services = Column(JSON)  # Stores top services array
    created_at = Column(DateTime, default=func.now())


# ============================================================================
# STEP 2: Create All Tables
# ============================================================================

print("\n📊 Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully")

# ============================================================================
# STEP 3: Seed Realistic Data
# ============================================================================

print("\n🌱 Seeding database with realistic Azure data...")

db = SessionLocal()

try:
    # Clear existing data
    print("  Clearing existing data...")
    db.query(DashboardMetric).delete()
    db.query(OptimizationRecommendation).delete()
    db.query(AzureVM).delete()
    db.query(AzureStorageAccount).delete()
    db.query(AzureCost).delete()
    db.commit()

    # Azure Services and typical cost ranges
    AZURE_SERVICES = {
        "Virtual Machines": (3000, 6000),
        "Azure SQL Database": (2000, 4000),
        "Storage Accounts": (1500, 3000),
        "App Services": (1000, 2500),
        "Azure Kubernetes Service": (800, 2000),
        "Azure Functions": (200, 600),
        "Azure CDN": (300, 800),
        "Application Gateway": (400, 900),
        "Virtual Network": (200, 500),
        "Azure Monitor": (150, 400)
    }

    RESOURCE_GROUPS = ["production", "development", "staging", "qa", "shared"]

    # Generate 90 days of cost history
    print("  Generating 90 days of cost history...")
    base_daily_cost = 400
    costs_created = 0

    for days_ago in range(90):
        date = (datetime.now() - timedelta(days=days_ago)).date()
        day_of_week = date.weekday()

        # Weekend pattern (reduced costs)
        if day_of_week >= 5:
            multiplier = random.uniform(0.7, 0.8)
        # Month-end spike
        elif date.day >= 28:
            multiplier = random.uniform(1.05, 1.15)
        # Normal weekday
        else:
            multiplier = random.uniform(0.90, 1.10)

        daily_total = base_daily_cost * multiplier

        # Distribute across services
        for service_name, (min_cost, max_cost) in AZURE_SERVICES.items():
            service_daily = (random.uniform(min_cost, max_cost) / 30) * multiplier

            for rg in random.sample(RESOURCE_GROUPS, k=random.randint(1, 3)):
                cost_record = AzureCost(
                    date=date,
                    service_name=service_name,
                    resource_group=rg,
                    cost=round(service_daily / 2, 2),
                    currency="USD"
                )
                db.add(cost_record)
                costs_created += 1

    print(f"  ✅ Created {costs_created} cost records")

    # Generate VMs
    print("  Generating Virtual Machines...")
    VM_SIZES = {
        "Standard_B1s": 7.59,
        "Standard_B2s": 30.37,
        "Standard_B4ms": 121.47,
        "Standard_D2s_v3": 96.36,
        "Standard_D4s_v3": 192.72,
        "Standard_D8s_v3": 385.44,
        "Standard_E2s_v3": 109.50,
        "Standard_E4s_v3": 219.00,
        "Standard_F2s_v2": 76.65,
        "Standard_F4s_v2": 153.30,
    }

    VM_WORKLOADS = ["web", "api", "worker", "database", "cache", "jumpbox"]
    LOCATIONS = ["eastus", "westus2", "westeurope", "southeastasia"]
    STATUSES = ["running", "stopped", "deallocated"]

    vms_created = 0
    for i in range(10):
        workload = random.choice(VM_WORKLOADS)
        size = random.choice(list(VM_SIZES.keys()))
        status = random.choices(STATUSES, weights=[0.7, 0.2, 0.1])[0]

        cpu = random.uniform(15, 85) if status == "running" else 0
        memory = random.uniform(25, 90) if status == "running" else 0

        monthly_cost = VM_SIZES[size]

        # Determine recommendation based on utilization
        if cpu < 20 and status == "running":
            recommendation = "Consider right-sizing to lower tier"
            potential_savings = monthly_cost * 0.3
        elif cpu < 40:
            recommendation = "Consider Reserved Instance for long-term savings"
            potential_savings = monthly_cost * 0.2
        else:
            recommendation = "Optimal sizing"
            potential_savings = 0

        vm = AzureVM(
            name=f"vm-{workload}-{i:02d}",
            resource_id=f"/subscriptions/sub-{random.randint(1000, 9999)}/resourceGroups/{random.choice(RESOURCE_GROUPS)}/providers/Microsoft.Compute/virtualMachines/vm-{workload}-{i:02d}",
            size=size,
            location=random.choice(LOCATIONS),
            resource_group=random.choice(RESOURCE_GROUPS),
            status=status,
            cpu_utilization=round(cpu, 1),
            memory_utilization=round(memory, 1),
            monthly_cost=round(monthly_cost, 2),
            potential_savings=round(potential_savings, 2),
            recommendation=recommendation,
            tags={"environment": random.choice(["prod", "dev", "staging"]), "managed_by": "terraform"}
        )
        db.add(vm)
        vms_created += 1

    print(f"  ✅ Created {vms_created} VMs")

    # Generate Storage Accounts
    print("  Generating Storage Accounts...")
    TIERS = ["Hot", "Cool", "Archive"]
    storage_created = 0

    for i in range(6):
        tier = random.choice(TIERS)
        size_gb = random.uniform(500, 8000)

        # Cost calculation based on tier
        cost_per_gb = {"Hot": 0.020, "Cool": 0.010, "Archive": 0.002}
        monthly_cost = size_gb * cost_per_gb[tier]

        # Last accessed for tier recommendation
        last_accessed = datetime.now().date() - timedelta(days=random.randint(1, 365))

        # Generate recommendations
        recs = []
        potential_savings = 0
        if tier == "Hot" and (datetime.now().date() - last_accessed).days > 90:
            recs.append("Move to Cool tier for infrequent access")
            potential_savings = monthly_cost * 0.5
        elif tier == "Cool" and (datetime.now().date() - last_accessed).days > 180:
            recs.append("Move to Archive tier for long-term storage")
            potential_savings = monthly_cost * 0.8
        else:
            recs.append("Already optimized")

        storage = AzureStorageAccount(
            name=f"starchives{random.randint(10000, 99999):05d}",
            resource_id=f"/subscriptions/sub-{random.randint(1000, 9999)}/resourceGroups/{random.choice(RESOURCE_GROUPS)}/providers/Microsoft.Storage/storageAccounts/st{random.randint(10000, 99999)}",
            tier=tier,
            location=random.choice(LOCATIONS),
            resource_group=random.choice(RESOURCE_GROUPS),
            size_gb=round(size_gb, 2),
            monthly_cost=round(monthly_cost, 2),
            potential_savings=round(potential_savings, 2),
            last_accessed=last_accessed,
            recommendations=recs
        )
        db.add(storage)
        storage_created += 1

    print(f"  ✅ Created {storage_created} Storage Accounts")

    # Generate Optimization Recommendations
    print("  Generating Optimization Recommendations...")
    recommendations_created = 0

    # Get VMs and Storage for recommendations
    vms = db.query(AzureVM).all()
    storages = db.query(AzureStorageAccount).all()

    for vm in vms:
        if vm.potential_savings > 0:
            rec = OptimizationRecommendation(
                priority="High" if vm.potential_savings > 50 else "Medium",
                category="Compute",
                resource_type="VM",
                resource_id=vm.resource_id,
                resource_name=vm.name,
                title=f"Optimize {vm.name}",
                description=f"VM is underutilized with {vm.cpu_utilization}% CPU usage",
                current_state=f"{vm.size} ({vm.status})",
                recommendation=vm.recommendation,
                savings_monthly=vm.potential_savings,
                impact="High" if vm.potential_savings > 50 else "Medium",
                effort="Low",
                complexity="Low",
                estimated_time="15-30 minutes",
                implementation_steps=[
                    "Stop the VM during maintenance window",
                    f"Resize VM to appropriate tier",
                    "Start and verify application functionality",
                    "Monitor performance for 24 hours"
                ],
                status="pending"
            )
            db.add(rec)
            recommendations_created += 1

    for storage in storages:
        if storage.potential_savings > 0 and storage.recommendations[0] != "Already optimized":
            rec = OptimizationRecommendation(
                priority="Medium",
                category="Storage",
                resource_type="Storage",
                resource_id=storage.resource_id,
                resource_name=storage.name,
                title=f"Optimize {storage.name} tier",
                description=f"Storage not accessed in {(datetime.now().date() - storage.last_accessed).days} days",
                current_state=f"{storage.tier} tier, {storage.size_gb} GB",
                recommendation=storage.recommendations[0],
                savings_monthly=storage.potential_savings,
                impact="Medium",
                effort="Low",
                complexity="Low",
                estimated_time="10-20 minutes",
                implementation_steps=[
                    "Review access patterns",
                    "Set lifecycle management policy",
                    "Test tier migration with sample data",
                    "Apply to entire storage account"
                ],
                status="pending"
            )
            db.add(rec)
            recommendations_created += 1

    print(f"  ✅ Created {recommendations_created} Recommendations")

    # Generate Dashboard Metrics
    print("  Generating Dashboard Metrics...")

    # Calculate from actual cost data
    for days_ago in range(30):
        metric_date = (datetime.now() - timedelta(days=days_ago)).date()

        # Get costs for this date
        day_costs = db.query(AzureCost).filter(AzureCost.date == metric_date).all()
        total_cost = sum(c.cost for c in day_costs)

        # Get previous month for comparison
        prev_month_date = metric_date - timedelta(days=30)
        prev_costs = db.query(AzureCost).filter(AzureCost.date == prev_month_date).all()
        prev_total = sum(c.cost for c in prev_costs)

        monthly_change = ((total_cost - prev_total) / prev_total * 100) if prev_total > 0 else 0

        # Aggregate by service
        service_totals = {}
        for cost in day_costs:
            service_totals[cost.service_name] = service_totals.get(cost.service_name, 0) + cost.cost

        top_services = sorted(service_totals.items(), key=lambda x: x[1], reverse=True)[:5]

        # Get VM and storage counts
        total_vms = db.query(AzureVM).count()
        total_storage = db.query(AzureStorageAccount).count()
        total_savings = sum(vm.potential_savings or 0 for vm in db.query(AzureVM).all())
        total_savings += sum(st.potential_savings or 0 for st in db.query(AzureStorageAccount).all())

        metric = DashboardMetric(
            metric_date=metric_date,
            total_monthly_cost=round(total_cost * 30, 2),  # Project to monthly
            monthly_change_percent=round(monthly_change, 1),
            projected_monthly_cost=round(total_cost * 30 * 1.05, 2),
            compute_utilization=round(random.uniform(55, 75), 1),
            storage_utilization=round(random.uniform(65, 85), 1),
            database_utilization=round(random.uniform(60, 80), 1),
            network_utilization=round(random.uniform(45, 65), 1),
            total_vms=total_vms,
            total_storage_accounts=total_storage,
            total_potential_savings=round(total_savings, 2),
            top_services=top_services
        )
        db.add(metric)

    print(f"  ✅ Created 30 days of dashboard metrics")

    # Commit all data
    print("\n💾 Committing data to database...")
    db.commit()
    print("✅ Database seeded successfully!")

    # Print summary
    print("\n📈 Database Summary:")
    print(f"  Cost Records: {db.query(AzureCost).count()}")
    print(f"  Virtual Machines: {db.query(AzureVM).count()}")
    print(f"  Storage Accounts: {db.query(AzureStorageAccount).count()}")
    print(f"  Recommendations: {db.query(OptimizationRecommendation).count()}")
    print(f"  Dashboard Metrics: {db.query(DashboardMetric).count()}")

    # Get today's metrics
    today = datetime.now().date()
    today_metric = db.query(DashboardMetric).filter(DashboardMetric.metric_date == today).first()
    if today_metric:
        print(f"\n💰 Today's Summary:")
        print(f"  Total Monthly Cost: ${today_metric.total_monthly_cost:,.2f}")
        print(f"  Monthly Change: {today_metric.monthly_change_percent:+.1f}%")
        print(f"  Potential Savings: ${today_metric.total_potential_savings:,.2f}/month")

except Exception as e:
    print(f"\n❌ Error: {e}")
    db.rollback()
    raise
finally:
    db.close()

print("\n" + "=" * 60)
print("✨ Database setup complete! Ready to use.")
print("=" * 60)
