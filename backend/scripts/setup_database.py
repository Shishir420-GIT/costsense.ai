#!/usr/bin/env python3
"""
Database Setup and Seeding Script for CostSense-AI

Creates SQLite database with realistic Azure cost and resource data for MVP demo.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta, date
import random
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.database import Base
from src.models import (
    AzureCost,
    AzureVM,
    AzureStorageAccount,
    OptimizationRecommendation,
    DashboardMetric,
)

# SQLite database path
DATABASE_PATH = "costsense.db"
DATABASE_URL = f"sqlite:///./{DATABASE_PATH}"


def create_database():
    """Create database and all tables"""
    print(f"Creating database at {DATABASE_PATH}...")

    # Create engine
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )

    # Drop all tables and recreate (fresh start)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("✓ Database created successfully")
    return engine


def seed_azure_costs(session):
    """Seed 90 days of realistic Azure cost data"""
    print("Seeding Azure cost data...")

    services = [
        "Virtual Machines",
        "Storage Accounts",
        "Azure SQL Database",
        "App Service",
        "Azure Functions",
        "Container Instances",
        "Kubernetes Service",
        "Cosmos DB",
        "API Management",
        "Application Insights",
        "Virtual Network",
        "Load Balancer",
        "Azure CDN",
        "Key Vault",
        "Azure Monitor"
    ]

    resource_groups = [
        "production-rg",
        "staging-rg",
        "development-rg",
        "shared-services-rg",
        "data-analytics-rg"
    ]

    regions = ["eastus", "westus2", "centralus", "westeurope"]

    # Generate 90 days of data
    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    cost_records = []
    current_date = start_date

    while current_date <= end_date:
        # Each service gets a cost entry per day
        for service in services:
            # Base cost varies by service
            if service == "Virtual Machines":
                base_cost = random.uniform(800, 1200)
            elif service == "Storage Accounts":
                base_cost = random.uniform(200, 400)
            elif service == "Azure SQL Database":
                base_cost = random.uniform(300, 600)
            else:
                base_cost = random.uniform(50, 300)

            # Add variability
            # Weekend costs 20% lower (fewer dev resources running)
            if current_date.weekday() >= 5:
                base_cost *= 0.8

            # Month-end spike (data processing jobs)
            if current_date.day >= 28:
                base_cost *= 1.2

            # Random daily variance
            daily_cost = base_cost * random.uniform(0.9, 1.1)

            cost_record = AzureCost(
                date=current_date,
                service_name=service,
                resource_group=random.choice(resource_groups),
                cost=round(daily_cost, 2),
                region=random.choice(regions),
                tags=json.dumps({"environment": random.choice(["prod", "staging", "dev"])})
            )
            cost_records.append(cost_record)

        current_date += timedelta(days=1)

    session.bulk_save_objects(cost_records)
    session.commit()
    print(f"✓ Seeded {len(cost_records)} cost records ({len(services)} services × 91 days)")


def seed_azure_vms(session):
    """Seed 10 Azure VMs with realistic utilization and recommendations"""
    print("Seeding Azure VM data...")

    vm_sizes = [
        "Standard_B2s", "Standard_D2s_v3", "Standard_D4s_v3",
        "Standard_E2s_v3", "Standard_F4s_v2", "Standard_B4ms"
    ]

    locations = ["eastus", "westus2", "centralus", "westeurope"]
    resource_groups = ["production-rg", "staging-rg", "development-rg"]

    vms = []
    for i in range(10):
        # Random utilization
        cpu_util = round(random.uniform(15, 85), 1)
        memory_util = round(random.uniform(20, 90), 1)

        # Determine recommendation based on utilization
        if cpu_util < 20 and memory_util < 30:
            recommendation = "Resize to smaller VM size or consider serverless alternatives"
            recommendation_type = "Resize"
            potential_savings = round(random.uniform(100, 300), 2)
        elif cpu_util < 30 and i % 3 == 0:
            recommendation = "Consider auto-shutdown schedule for non-production hours"
            recommendation_type = "Shutdown"
            potential_savings = round(random.uniform(50, 150), 2)
        elif cpu_util > 70 or memory_util > 80:
            recommendation = "Consider upgrading to larger VM size for better performance"
            recommendation_type = "Resize"
            potential_savings = 0.0
        else:
            recommendation = "Consider Azure Reserved VM Instances for 1-year commitment"
            recommendation_type = "Reserved Instance"
            potential_savings = round(random.uniform(200, 500), 2)

        status = "Running" if i < 7 else random.choice(["Stopped", "Deallocated"])

        vm = AzureVM(
            name=f"vm-app-{i+1:02d}",
            resource_group=random.choice(resource_groups),
            location=random.choice(locations),
            size=random.choice(vm_sizes),
            status=status,
            cpu_utilization=cpu_util,
            memory_utilization=memory_util,
            disk_utilization=round(random.uniform(30, 75), 1),
            network_in_mb=round(random.uniform(100, 5000), 2),
            network_out_mb=round(random.uniform(50, 3000), 2),
            monthly_cost=round(random.uniform(200, 800), 2),
            potential_savings=potential_savings,
            recommendation=recommendation,
            recommendation_type=recommendation_type,
            tags=json.dumps({"env": random.choice(["prod", "staging", "dev"]), "team": random.choice(["backend", "frontend", "data"])})
        )
        vms.append(vm)

    session.bulk_save_objects(vms)
    session.commit()
    print(f"✓ Seeded {len(vms)} VMs with utilization metrics")


def seed_azure_storage(session):
    """Seed 6 Azure Storage Accounts with tier optimization opportunities"""
    print("Seeding Azure Storage data...")

    tiers = ["Hot", "Cool", "Archive"]
    replication_types = ["LRS", "GRS", "ZRS", "RA-GRS"]
    locations = ["eastus", "westus2", "centralus", "westeurope"]
    resource_groups = ["production-rg", "staging-rg", "shared-services-rg"]

    storage_accounts = []
    for i in range(6):
        # Last accessed determines optimization opportunity
        days_since_access = random.randint(1, 180)
        last_accessed = date.today() - timedelta(days=days_since_access)

        # Determine access frequency and recommendation
        if days_since_access > 90:
            access_freq = "Rare"
            current_tier = random.choice(["Hot", "Cool"])
            recommended_tier = "Archive"
            potential_savings = round(random.uniform(100, 250), 2)
            recommendations = json.dumps([
                "Move to Archive tier - accessed rarely",
                "Consider lifecycle management policy",
                "Review data retention requirements"
            ])
        elif days_since_access > 30:
            access_freq = "Low"
            current_tier = "Hot" if i % 2 == 0 else "Cool"
            recommended_tier = "Cool" if current_tier == "Hot" else current_tier
            potential_savings = round(random.uniform(50, 150), 2) if current_tier == "Hot" else 0.0
            recommendations = json.dumps([
                "Consider moving to Cool tier",
                "Enable soft delete for data protection",
                "Set up access tier optimization"
            ])
        else:
            access_freq = random.choice(["Medium", "High"])
            current_tier = "Hot"
            recommended_tier = "Hot"
            potential_savings = 0.0
            recommendations = json.dumps([
                "Current tier is optimal",
                "Consider enabling Azure CDN for frequently accessed blobs",
                "Review backup and disaster recovery settings"
            ])

        storage = AzureStorageAccount(
            name=f"storage{i+1:02d}{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))}",
            resource_group=random.choice(resource_groups),
            location=random.choice(locations),
            tier=current_tier,
            replication_type=random.choice(replication_types),
            size_gb=round(random.uniform(500, 5000), 2),
            blob_count=random.randint(1000, 50000),
            container_count=random.randint(5, 30),
            last_accessed=last_accessed,
            access_frequency=access_freq,
            monthly_cost=round(random.uniform(100, 600), 2),
            potential_savings=potential_savings,
            recommended_tier=recommended_tier,
            recommendations=recommendations,
            tags=json.dumps({"type": random.choice(["backups", "logs", "media", "data"])})
        )
        storage_accounts.append(storage)

    session.bulk_save_objects(storage_accounts)
    session.commit()
    print(f"✓ Seeded {len(storage_accounts)} Storage Accounts with tier recommendations")


def seed_optimization_recommendations(session):
    """Generate optimization recommendations from VM and Storage analysis"""
    print("Seeding optimization recommendations...")

    # Get VMs with savings opportunities
    vms = session.query(AzureVM).filter(AzureVM.potential_savings > 0).all()

    # Get Storage accounts with savings
    storage_accounts = session.query(AzureStorageAccount).filter(AzureStorageAccount.potential_savings > 0).all()

    recommendations = []

    # VM-based recommendations
    for vm in vms:
        if vm.recommendation_type == "Resize":
            priority = "High" if vm.cpu_utilization < 15 else "Medium"
            impact = "High" if vm.potential_savings > 200 else "Medium"
            effort = "Medium"
            steps = [
                "Review VM performance metrics for last 30 days",
                "Identify appropriate target VM size",
                "Schedule maintenance window",
                "Resize VM and validate application performance",
                "Monitor for 1 week to confirm stability"
            ]
        elif vm.recommendation_type == "Shutdown":
            priority = "Medium"
            impact = "Medium"
            effort = "Low"
            steps = [
                "Confirm VM is non-production workload",
                "Create auto-shutdown schedule (e.g., 7 PM - 7 AM)",
                "Configure startup schedule if needed",
                "Test shutdown/startup automation",
                "Monitor cost savings"
            ]
        else:  # Reserved Instance
            priority = "Medium"
            impact = "High"
            effort = "Low"
            steps = [
                "Analyze VM usage patterns for consistency",
                "Calculate 1-year vs 3-year RI savings",
                "Purchase Reserved Instance",
                "Apply RI to VM",
                "Track savings monthly"
            ]

        rec = OptimizationRecommendation(
            title=f"Optimize {vm.name} - {vm.recommendation_type}",
            description=vm.recommendation,
            category="Compute",
            priority=priority,
            impact=impact,
            effort=effort,
            savings_monthly=vm.potential_savings,
            savings_annual=vm.potential_savings * 12,
            resource_type="VirtualMachine",
            resource_name=vm.name,
            resource_group=vm.resource_group,
            implementation_steps=json.dumps(steps),
            estimated_time_minutes=random.randint(15, 90),
            status="pending"
        )
        recommendations.append(rec)

    # Storage-based recommendations
    for storage in storage_accounts:
        if storage.potential_savings > 0:
            priority = "High" if storage.potential_savings > 150 else "Medium"
            impact = "High" if storage.potential_savings > 150 else "Medium"
            effort = "Low"
            steps = [
                f"Review access patterns for {storage.name}",
                f"Configure lifecycle management policy to move to {storage.recommended_tier} tier",
                "Set up monitoring for tier changes",
                "Test data retrieval from new tier",
                "Monitor cost reduction"
            ]

            rec = OptimizationRecommendation(
                title=f"Optimize Storage Tier - {storage.name}",
                description=f"Move rarely accessed data from {storage.tier} to {storage.recommended_tier} tier",
                category="Storage",
                priority=priority,
                impact=impact,
                effort=effort,
                savings_monthly=storage.potential_savings,
                savings_annual=storage.potential_savings * 12,
                resource_type="StorageAccount",
                resource_name=storage.name,
                resource_group=storage.resource_group,
                implementation_steps=json.dumps(steps),
                estimated_time_minutes=random.randint(10, 30),
                status="pending"
            )
            recommendations.append(rec)

    # Add some general recommendations
    general_recs = [
        {
            "title": "Enable Azure Advisor Cost Recommendations",
            "description": "Configure Azure Advisor to automatically identify cost optimization opportunities across all resources",
            "category": "General",
            "priority": "Low",
            "impact": "Medium",
            "effort": "Low",
            "savings_monthly": 0.0,
            "steps": ["Navigate to Azure Advisor", "Enable Cost recommendations", "Configure email alerts", "Review recommendations weekly"]
        },
        {
            "title": "Implement Resource Tagging Strategy",
            "description": "Standardize resource tagging for better cost allocation and chargeback",
            "category": "General",
            "priority": "Medium",
            "impact": "Low",
            "effort": "Medium",
            "savings_monthly": 0.0,
            "steps": ["Define tagging standards", "Create Azure Policy for required tags", "Tag existing resources", "Generate cost reports by tags"]
        },
        {
            "title": "Set Up Budget Alerts",
            "description": "Configure Azure Cost Management budgets and alerts to prevent cost overruns",
            "category": "Monitoring",
            "priority": "High",
            "impact": "Low",
            "effort": "Low",
            "savings_monthly": 0.0,
            "steps": ["Navigate to Cost Management + Billing", "Create monthly budget", "Set up 80%, 90%, 100% alerts", "Configure action groups for notifications"]
        }
    ]

    for gen_rec in general_recs:
        rec = OptimizationRecommendation(
            title=gen_rec["title"],
            description=gen_rec["description"],
            category=gen_rec["category"],
            priority=gen_rec["priority"],
            impact=gen_rec["impact"],
            effort=gen_rec["effort"],
            savings_monthly=gen_rec["savings_monthly"],
            savings_annual=gen_rec["savings_monthly"] * 12,
            resource_type="General",
            resource_name=None,
            resource_group=None,
            implementation_steps=json.dumps(gen_rec["steps"]),
            estimated_time_minutes=random.randint(15, 60),
            status="pending"
        )
        recommendations.append(rec)

    session.bulk_save_objects(recommendations)
    session.commit()
    print(f"✓ Seeded {len(recommendations)} optimization recommendations")


def seed_dashboard_metrics(session):
    """Pre-calculate dashboard metrics for last 30 days for ultra-fast queries"""
    print("Seeding dashboard metrics...")

    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    metrics = []
    current_date = start_date

    while current_date <= end_date:
        # Calculate total cost for this date
        costs_for_date = session.query(AzureCost).filter(AzureCost.date == current_date).all()
        daily_cost = sum(c.cost for c in costs_for_date)

        # Calculate 30-day running total
        thirty_days_ago = current_date - timedelta(days=30)
        costs_last_30 = session.query(AzureCost).filter(
            AzureCost.date >= thirty_days_ago,
            AzureCost.date <= current_date
        ).all()
        total_monthly_cost = sum(c.cost for c in costs_last_30)

        # Calculate change from previous period
        sixty_days_ago = current_date - timedelta(days=60)
        costs_prev_30 = session.query(AzureCost).filter(
            AzureCost.date >= sixty_days_ago,
            AzureCost.date < thirty_days_ago
        ).all()
        prev_monthly_cost = sum(c.cost for c in costs_prev_30)

        if prev_monthly_cost > 0:
            monthly_change = ((total_monthly_cost - prev_monthly_cost) / prev_monthly_cost) * 100
        else:
            monthly_change = 0.0

        # Project month-end cost
        days_in_period = 30
        days_elapsed = len(set(c.date for c in costs_last_30))
        if days_elapsed > 0:
            avg_daily = total_monthly_cost / days_elapsed
            projected_cost = avg_daily * days_in_period
        else:
            projected_cost = total_monthly_cost

        # Top services for this date
        service_costs = {}
        for cost in costs_for_date:
            service_costs[cost.service_name] = service_costs.get(cost.service_name, 0) + cost.cost

        top_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:5]
        top_services_json = json.dumps([{"service": s, "cost": round(c, 2)} for s, c in top_services])

        # Resource group costs
        rg_costs = {}
        for cost in costs_for_date:
            rg_costs[cost.resource_group] = rg_costs.get(cost.resource_group, 0) + cost.cost

        rg_list = sorted(rg_costs.items(), key=lambda x: x[1], reverse=True)[:5]
        rg_json = json.dumps([{"group": g, "cost": round(c, 2)} for g, c in rg_list])

        # Utilization metrics (random but realistic)
        compute_util = round(random.uniform(45, 85), 1)
        storage_util = round(random.uniform(60, 90), 1)
        database_util = round(random.uniform(55, 80), 1)
        network_util = round(random.uniform(40, 70), 1)

        # Savings opportunities
        all_recommendations = session.query(OptimizationRecommendation).filter(
            OptimizationRecommendation.status == "pending"
        ).all()
        total_savings = sum(r.savings_monthly for r in all_recommendations)

        metric = DashboardMetric(
            date=current_date,
            total_monthly_cost=round(total_monthly_cost, 2),
            monthly_change_percent=round(monthly_change, 1),
            projected_monthly_cost=round(projected_cost, 2),
            daily_cost=round(daily_cost, 2),
            compute_utilization=compute_util,
            storage_utilization=storage_util,
            database_utilization=database_util,
            network_utilization=network_util,
            top_services=top_services_json,
            resource_groups=rg_json,
            total_potential_savings=round(total_savings, 2),
            optimization_count=len(all_recommendations)
        )
        metrics.append(metric)

        current_date += timedelta(days=1)

    session.bulk_save_objects(metrics)
    session.commit()
    print(f"✓ Seeded {len(metrics)} dashboard metric records (31 days)")


def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("CostSense-AI Database Setup")
    print("="*60 + "\n")

    # Create database and tables
    engine = create_database()

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Seed all data in order (dependencies matter!)
        seed_azure_costs(session)
        seed_azure_vms(session)
        seed_azure_storage(session)
        seed_optimization_recommendations(session)
        seed_dashboard_metrics(session)

        print("\n" + "="*60)
        print("Database Setup Complete!")
        print("="*60)

        # Print summary statistics
        print("\nDatabase Summary:")
        print(f"  • Cost Records: {session.query(AzureCost).count():,}")
        print(f"  • Virtual Machines: {session.query(AzureVM).count()}")
        print(f"  • Storage Accounts: {session.query(AzureStorageAccount).count()}")
        print(f"  • Optimization Recommendations: {session.query(OptimizationRecommendation).count()}")
        print(f"  • Dashboard Metrics: {session.query(DashboardMetric).count()}")

        # Show total potential savings
        total_savings_recs = session.query(OptimizationRecommendation).filter(
            OptimizationRecommendation.status == "pending"
        ).all()
        monthly_savings = sum(r.savings_monthly for r in total_savings_recs)
        annual_savings = sum(r.savings_annual for r in total_savings_recs)

        print(f"\n  💰 Total Potential Savings:")
        print(f"     - Monthly: ${monthly_savings:,.2f}")
        print(f"     - Annual: ${annual_savings:,.2f}")

        # Show latest metrics
        latest_metric = session.query(DashboardMetric).order_by(DashboardMetric.date.desc()).first()
        if latest_metric:
            print(f"\n  📊 Latest Dashboard Metrics ({latest_metric.date}):")
            print(f"     - Total Monthly Cost: ${latest_metric.total_monthly_cost:,.2f}")
            print(f"     - Monthly Change: {latest_metric.monthly_change_percent:+.1f}%")
            print(f"     - Projected Cost: ${latest_metric.projected_monthly_cost:,.2f}")

        print(f"\n✅ Database ready at: {DATABASE_PATH}")
        print("   You can now start the FastAPI server with USE_DATABASE=true\n")

    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
