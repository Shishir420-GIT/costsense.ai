#!/usr/bin/env python3
"""
COMPREHENSIVE Database Seeder for CostSense-AI
Creates realistic Azure infrastructure with detailed resource data
"""

import sys
import os
from pathlib import Path
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

DATABASE_PATH = "costsense.db"
DATABASE_URL = f"sqlite:///./{DATABASE_PATH}"

# Comprehensive Azure VM configurations
VM_CONFIGS = [
    # Production VMs - High spec, running 24/7
    {"name": "prod-web-vm-01", "size": "Standard_D4s_v3", "rg": "production-rg", "location": "eastus", "env": "production", "role": "web-server", "os": "Ubuntu 20.04", "status": "Running"},
    {"name": "prod-web-vm-02", "size": "Standard_D4s_v3", "rg": "production-rg", "location": "westus2", "env": "production", "role": "web-server", "os": "Ubuntu 20.04", "status": "Running"},
    {"name": "prod-api-vm-01", "size": "Standard_E4s_v3", "rg": "production-rg", "location": "eastus", "env": "production", "role": "api-server", "os": "Ubuntu 20.04", "status": "Running"},
    {"name": "prod-api-vm-02", "size": "Standard_E4s_v3", "rg": "production-rg", "location": "westus2", "env": "production", "role": "api-server", "os": "Ubuntu 20.04", "status": "Running"},
    {"name": "prod-db-vm-01", "size": "Standard_E8s_v3", "rg": "production-rg", "location": "eastus", "env": "production", "role": "database", "os": "Ubuntu 20.04", "status": "Running"},
    {"name": "prod-cache-vm-01", "size": "Standard_E2s_v3", "rg": "production-rg", "location": "eastus", "env": "production", "role": "cache", "os": "Ubuntu 20.04", "status": "Running"},
    {"name": "prod-worker-vm-01", "size": "Standard_F4s_v2", "rg": "production-rg", "location": "eastus", "env": "production", "role": "worker", "os": "Ubuntu 20.04", "status": "Running"},
    {"name": "prod-worker-vm-02", "size": "Standard_F4s_v2", "rg": "production-rg", "location": "eastus", "env": "production", "role": "worker", "os": "Ubuntu 20.04", "status": "Running"},

    # Staging VMs - Medium spec
    {"name": "stg-web-vm-01", "size": "Standard_D2s_v3", "rg": "staging-rg", "location": "centralus", "env": "staging", "role": "web-server", "os": "Ubuntu 20.04", "status": "Running"},
    {"name": "stg-api-vm-01", "size": "Standard_D2s_v3", "rg": "staging-rg", "location": "centralus", "env": "staging", "role": "api-server", "os": "Ubuntu 20.04", "status": "Running"},
    {"name": "stg-db-vm-01", "size": "Standard_E4s_v3", "rg": "staging-rg", "location": "centralus", "env": "staging", "role": "database", "os": "Ubuntu 20.04", "status": "Running"},

    # Development VMs - Small spec, can be stopped
    {"name": "dev-vm-01", "size": "Standard_B2s", "rg": "development-rg", "location": "eastus", "env": "development", "role": "dev-machine", "os": "Ubuntu 22.04", "status": "Running"},
    {"name": "dev-vm-02", "size": "Standard_B2s", "rg": "development-rg", "location": "eastus", "env": "development", "role": "dev-machine", "os": "Ubuntu 22.04", "status": "Stopped"},
    {"name": "dev-vm-03", "size": "Standard_B2s", "rg": "development-rg", "location": "eastus", "env": "development", "role": "dev-machine", "os": "Windows Server 2019", "status": "Deallocated"},
    {"name": "dev-vm-04", "size": "Standard_B4ms", "rg": "development-rg", "location": "eastus", "env": "development", "role": "dev-machine", "os": "Ubuntu 22.04", "status": "Running"},
    {"name": "dev-test-vm-01", "size": "Standard_B2ms", "rg": "development-rg", "location": "eastus", "env": "development", "role": "test-server", "os": "Ubuntu 20.04", "status": "Deallocated"},

    # Analytics/Data VMs
    {"name": "analytics-vm-01", "size": "Standard_E8s_v3", "rg": "data-analytics-rg", "location": "eastus", "env": "production", "role": "analytics", "os": "Ubuntu 20.04", "status": "Running"},
    {"name": "etl-vm-01", "size": "Standard_D8s_v3", "rg": "data-analytics-rg", "location": "eastus", "env": "production", "role": "etl", "os": "Ubuntu 20.04", "status": "Running"},
    {"name": "ml-training-vm-01", "size": "Standard_NC6s_v3", "rg": "data-analytics-rg", "location": "eastus", "env": "production", "role": "ml-training", "os": "Ubuntu 20.04", "status": "Stopped"},

    # Shared Services
    {"name": "jump-box-vm-01", "size": "Standard_B2s", "rg": "shared-services-rg", "location": "eastus", "env": "shared", "role": "bastion", "os": "Ubuntu 20.04", "status": "Running"},
    {"name": "monitoring-vm-01", "size": "Standard_D2s_v3", "rg": "shared-services-rg", "location": "eastus", "env": "shared", "role": "monitoring", "os": "Ubuntu 20.04", "status": "Running"},
]

# VM Size to monthly cost mapping (realistic Azure pricing)
VM_SIZE_COSTS = {
    "Standard_B2s": 30.37,
    "Standard_B2ms": 60.74,
    "Standard_B4ms": 121.47,
    "Standard_D2s_v3": 96.36,
    "Standard_D4s_v3": 192.72,
    "Standard_D8s_v3": 385.44,
    "Standard_E2s_v3": 146.00,
    "Standard_E4s_v3": 292.00,
    "Standard_E8s_v3": 584.00,
    "Standard_F4s_v2": 169.34,
    "Standard_NC6s_v3": 3066.00,  # GPU VM
}

# Storage Account configurations
STORAGE_CONFIGS = [
    {"name": "prodwebstorage001", "tier": "Hot", "rg": "production-rg", "location": "eastus", "type": "web-assets", "size_gb": 2048, "replication": "GRS"},
    {"name": "prodbackupstorage001", "tier": "Cool", "rg": "production-rg", "location": "eastus", "type": "backups", "size_gb": 5120, "replication": "LRS"},
    {"name": "prodlogstorage001", "tier": "Hot", "rg": "production-rg", "location": "eastus", "type": "logs", "size_gb": 1024, "replication": "LRS"},
    {"name": "stgappstorage001", "tier": "Hot", "rg": "staging-rg", "location": "centralus", "type": "application", "size_gb": 512, "replication": "LRS"},
    {"name": "devappstorage001", "tier": "Hot", "rg": "development-rg", "location": "eastus", "type": "development", "size_gb": 256, "replication": "LRS"},
    {"name": "archivalstorage001", "tier": "Archive", "rg": "shared-services-rg", "location": "eastus", "type": "long-term-archive", "size_gb": 10240, "replication": "GRS"},
    {"name": "mediasstorage001", "tier": "Cool", "rg": "production-rg", "location": "westus2", "type": "media", "size_gb": 3072, "replication": "RA-GRS"},
    {"name": "analyticsdata001", "tier": "Hot", "rg": "data-analytics-rg", "location": "eastus", "type": "analytics-data", "size_gb": 4096, "replication": "ZRS"},
]


def create_database():
    """Create fresh database"""
    print(f"Creating database at {DATABASE_PATH}...")
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✓ Database created successfully")
    return engine


def seed_comprehensive_vms(session):
    """Seed comprehensive VM data with realistic configurations"""
    print("Seeding comprehensive VM data...")

    vms = []
    for config in VM_CONFIGS:
        # Calculate realistic utilization based on role and status
        if config["status"] == "Running":
            if config["role"] in ["web-server", "api-server"]:
                cpu = round(random.uniform(45, 75), 1)
                memory = round(random.uniform(50, 80), 1)
            elif config["role"] == "database":
                cpu = round(random.uniform(60, 85), 1)
                memory = round(random.uniform(70, 90), 1)
            elif config["role"] == "worker":
                cpu = round(random.uniform(30, 60), 1)
                memory = round(random.uniform(40, 70), 1)
            elif config["role"] == "dev-machine":
                cpu = round(random.uniform(15, 40), 1)
                memory = round(random.uniform(20, 50), 1)
            elif config["role"] == "analytics":
                cpu = round(random.uniform(70, 90), 1)
                memory = round(random.uniform(80, 95), 1)
            elif config["role"] == "ml-training":
                cpu = round(random.uniform(85, 95), 1)
                memory = round(random.uniform(85, 95), 1)
            else:
                cpu = round(random.uniform(30, 70), 1)
                memory = round(random.uniform(35, 75), 1)
        else:
            cpu = 0.0
            memory = 0.0

        # Monthly cost
        base_cost = VM_SIZE_COSTS.get(config["size"], 100.0)
        if config["status"] == "Stopped":
            monthly_cost = base_cost * 0.1  # Storage costs only
        elif config["status"] == "Deallocated":
            monthly_cost = 0.0
        else:
            monthly_cost = base_cost

        # Determine recommendations and savings
        recommendation = None
        recommendation_type = None
        potential_savings = 0.0

        if config["status"] == "Running":
            if cpu < 20 and memory < 30:
                recommendation = f"VM is underutilized. Consider resizing to smaller instance or using auto-shutdown schedule."
                recommendation_type = "Resize"
                potential_savings = round(monthly_cost * 0.4, 2)
            elif cpu < 35 and config["env"] == "development":
                recommendation = f"Development VM running outside business hours. Consider auto-shutdown schedule (7 PM - 7 AM, weekends)."
                recommendation_type = "Shutdown"
                potential_savings = round(monthly_cost * 0.5, 2)
            elif config["role"] in ["web-server", "api-server", "database"] and config["env"] == "production":
                recommendation = f"Production workload with consistent usage. Consider 1-year Reserved Instance for 38% savings."
                recommendation_type = "Reserved Instance"
                potential_savings = round(monthly_cost * 0.38, 2)
        elif config["status"] in ["Stopped", "Deallocated"]:
            recommendation = f"VM has been {config['status'].lower()} for extended period. Consider deleting if no longer needed."
            recommendation_type = "Delete"
            potential_savings = round(monthly_cost, 2)

        vm = AzureVM(
            name=config["name"],
            resource_group=config["rg"],
            location=config["location"],
            size=config["size"],
            status=config["status"],
            cpu_utilization=cpu,
            memory_utilization=memory,
            disk_utilization=round(random.uniform(30, 75), 1) if config["status"] == "Running" else 0.0,
            network_in_mb=round(random.uniform(100, 5000), 2) if config["status"] == "Running" else 0.0,
            network_out_mb=round(random.uniform(50, 3000), 2) if config["status"] == "Running" else 0.0,
            monthly_cost=round(monthly_cost, 2),
            potential_savings=potential_savings,
            recommendation=recommendation,
            recommendation_type=recommendation_type,
            tags=json.dumps({
                "environment": config["env"],
                "role": config["role"],
                "os": config["os"],
                "managed": "true"
            })
        )
        vms.append(vm)

    session.bulk_save_objects(vms)
    session.commit()
    print(f"✓ Seeded {len(vms)} VMs with comprehensive details")


def seed_comprehensive_storage(session):
    """Seed comprehensive storage account data"""
    print("Seeding comprehensive storage data...")

    storage_accounts = []
    for config in STORAGE_CONFIGS:
        # Calculate costs based on tier and size
        if config["tier"] == "Hot":
            cost_per_gb = 0.018
        elif config["tier"] == "Cool":
            cost_per_gb = 0.01
        elif config["tier"] == "Archive":
            cost_per_gb = 0.002
        else:
            cost_per_gb = 0.015

        monthly_cost = config["size_gb"] * cost_per_gb

        # Add replication costs
        if config["replication"] in ["GRS", "RA-GRS"]:
            monthly_cost *= 1.5
        elif config["replication"] == "ZRS":
            monthly_cost *= 1.25

        # Determine last access and recommendations
        if config["type"] in ["web-assets", "logs", "application"]:
            days_since_access = random.randint(1, 7)
            access_frequency = "High"
            recommended_tier = config["tier"]
            potential_savings = 0.0
            recommendations = json.dumps([
                "Current tier is optimal for access patterns",
                f"Consider enabling CDN for {config['type']} content",
                "Review lifecycle policies for old data"
            ])
        elif config["type"] in ["backups", "media"]:
            days_since_access = random.randint(15, 45)
            access_frequency = "Medium"
            if config["tier"] == "Hot":
                recommended_tier = "Cool"
                potential_savings = round(monthly_cost * 0.45, 2)
                recommendations = json.dumps([
                    "Move to Cool tier - accessed infrequently",
                    "Set up lifecycle management policy",
                    "Review data retention requirements"
                ])
            else:
                recommended_tier = config["tier"]
                potential_savings = 0.0
                recommendations = json.dumps([
                    "Current tier is appropriate",
                    "Enable soft delete for data protection"
                ])
        else:  # long-term-archive, analytics-data
            days_since_access = random.randint(60, 180)
            access_frequency = "Rare"
            if config["tier"] != "Archive":
                recommended_tier = "Archive"
                potential_savings = round(monthly_cost * 0.85, 2)
                recommendations = json.dumps([
                    "Move to Archive tier - rarely accessed",
                    "Implement automated archival policy",
                    "Consider Azure Blob Archive for cold data"
                ])
            else:
                recommended_tier = config["tier"]
                potential_savings = 0.0
                recommendations = json.dumps([
                    "Tier is optimal for long-term storage",
                    "Review retention policies annually"
                ])

        last_accessed = date.today() - timedelta(days=days_since_access)

        storage = AzureStorageAccount(
            name=config["name"],
            resource_group=config["rg"],
            location=config["location"],
            tier=config["tier"],
            replication_type=config["replication"],
            size_gb=round(config["size_gb"], 2),
            blob_count=random.randint(5000, 100000),
            container_count=random.randint(5, 50),
            last_accessed=last_accessed,
            access_frequency=access_frequency,
            monthly_cost=round(monthly_cost, 2),
            potential_savings=potential_savings,
            recommended_tier=recommended_tier,
            recommendations=recommendations,
            tags=json.dumps({
                "type": config["type"],
                "managed": "true",
                "backup": "enabled" if "backup" in config["type"] else "disabled"
            })
        )
        storage_accounts.append(storage)

    session.bulk_save_objects(storage_accounts)
    session.commit()
    print(f"✓ Seeded {len(storage_accounts)} Storage Accounts with comprehensive details")


def seed_granular_costs(session):
    """Seed granular cost data - per resource, per day"""
    print("Seeding granular cost data...")

    # Get all VMs and Storage accounts
    vms = session.query(AzureVM).all()
    storage_accounts = session.query(AzureStorageAccount).all()

    # Additional Azure services
    other_services = [
        {"name": "Azure SQL Database", "base_cost": 450, "rg": "production-rg"},
        {"name": "App Service", "base_cost": 200, "rg": "production-rg"},
        {"name": "Azure Functions", "base_cost": 50, "rg": "production-rg"},
        {"name": "Application Insights", "base_cost": 80, "rg": "shared-services-rg"},
        {"name": "Virtual Network", "base_cost": 30, "rg": "shared-services-rg"},
        {"name": "Load Balancer", "base_cost": 100, "rg": "production-rg"},
        {"name": "Azure CDN", "base_cost": 120, "rg": "production-rg"},
        {"name": "Key Vault", "base_cost": 15, "rg": "shared-services-rg"},
        {"name": "Azure Monitor", "base_cost": 90, "rg": "shared-services-rg"},
        {"name": "Azure Cosmos DB", "base_cost": 650, "rg": "data-analytics-rg"},
        {"name": "Azure Kubernetes Service", "base_cost": 300, "rg": "production-rg"},
    ]

    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    cost_records = []
    current_date = start_date

    while current_date <= end_date:
        # Cost records for each VM
        for vm in vms:
            daily_cost = vm.monthly_cost / 30

            # Add variability
            if current_date.weekday() >= 5:  # Weekend
                daily_cost *= 0.7

            # Add random variance
            daily_cost *= random.uniform(0.95, 1.05)

            cost_records.append(AzureCost(
                date=current_date,
                service_name="Virtual Machines",
                resource_group=vm.resource_group,
                cost=round(daily_cost, 2),
                region=vm.location,
                tags=json.dumps({"resource": vm.name, "type": "compute"})
            ))

        # Cost records for each Storage Account
        for storage in storage_accounts:
            daily_cost = storage.monthly_cost / 30
            daily_cost *= random.uniform(0.98, 1.02)

            cost_records.append(AzureCost(
                date=current_date,
                service_name="Storage Accounts",
                resource_group=storage.resource_group,
                cost=round(daily_cost, 2),
                region=storage.location,
                tags=json.dumps({"resource": storage.name, "type": "storage"})
            ))

        # Cost records for other services
        for service in other_services:
            daily_cost = service["base_cost"] / 30

            # Weekday patterns
            if current_date.weekday() >= 5:
                daily_cost *= 0.8

            # Month-end spike
            if current_date.day >= 28:
                daily_cost *= 1.15

            daily_cost *= random.uniform(0.9, 1.1)

            cost_records.append(AzureCost(
                date=current_date,
                service_name=service["name"],
                resource_group=service["rg"],
                cost=round(daily_cost, 2),
                region="eastus",
                tags=json.dumps({"type": "service"})
            ))

        current_date += timedelta(days=1)

    session.bulk_save_objects(cost_records)
    session.commit()
    print(f"✓ Seeded {len(cost_records)} granular cost records")


def seed_comprehensive_recommendations(session):
    """Generate detailed optimization recommendations"""
    print("Seeding comprehensive optimization recommendations...")

    vms = session.query(AzureVM).filter(AzureVM.potential_savings > 0).all()
    storage_accounts = session.query(AzureStorageAccount).filter(AzureStorageAccount.potential_savings > 0).all()

    recommendations = []

    # VM recommendations
    for vm in vms:
        if not vm.recommendation:
            continue

        priority = "Critical" if vm.potential_savings > 500 else "High" if vm.potential_savings > 200 else "Medium"
        impact = "High" if vm.potential_savings > 300 else "Medium"

        if vm.recommendation_type == "Resize":
            effort = "Medium"
            steps = [
                f"Review {vm.name} performance metrics for last 30 days",
                "Identify appropriate target VM size based on utilization",
                "Schedule maintenance window with application team",
                f"Resize {vm.name} to recommended size",
                "Monitor application performance for 1 week post-resize",
                "Update documentation with new configuration"
            ]
            time_est = random.randint(45, 120)
        elif vm.recommendation_type == "Shutdown":
            effort = "Low"
            steps = [
                f"Confirm {vm.name} is non-production workload",
                "Create auto-shutdown schedule via Azure Portal",
                "Configure startup schedule if needed (7 AM weekdays)",
                "Test shutdown/startup automation",
                "Monitor cost savings over 2-week period",
                "Adjust schedule based on actual usage patterns"
            ]
            time_est = random.randint(15, 30)
        elif vm.recommendation_type == "Reserved Instance":
            effort = "Low"
            steps = [
                f"Analyze {vm.name} usage consistency over last 6 months",
                "Calculate 1-year vs 3-year RI savings comparison",
                "Get budget approval for Reserved Instance purchase",
                "Purchase Azure Reserved VM Instance via Portal",
                f"Apply RI discount to {vm.name}",
                "Track savings monthly in Cost Management"
            ]
            time_est = random.randint(20, 45)
        else:  # Delete
            effort = "Low"
            steps = [
                f"Verify {vm.name} is no longer needed",
                "Create final backup snapshot if required",
                "Document deletion reason and date",
                f"Delete {vm.name} and associated resources",
                "Verify all related costs have stopped"
            ]
            time_est = random.randint(10, 20)

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
            estimated_time_minutes=time_est,
            status="pending"
        )
        recommendations.append(rec)

    # Storage recommendations
    for storage in storage_accounts:
        if storage.potential_savings == 0:
            continue

        priority = "High" if storage.potential_savings > 150 else "Medium"
        impact = "High" if storage.potential_savings > 150 else "Medium"
        effort = "Low"

        steps = [
            f"Review access patterns for {storage.name}",
            "Analyze blob age and last accessed dates",
            f"Create lifecycle management policy to move data to {storage.recommended_tier} tier",
            "Test data retrieval from new tier",
            "Enable policy and monitor tier migrations",
            "Track monthly cost reduction"
        ]

        rec = OptimizationRecommendation(
            title=f"Optimize Storage Tier - {storage.name}",
            description=f"Move data from {storage.tier} to {storage.recommended_tier} tier for rarely accessed content",
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
            estimated_time_minutes=random.randint(15, 30),
            status="pending"
        )
        recommendations.append(rec)

    # General best practices
    general_recs = [
        {
            "title": "Enable Azure Advisor Cost Recommendations",
            "description": "Configure Azure Advisor to proactively identify cost optimization opportunities across all subscriptions and resource groups",
            "category": "Governance",
            "priority": "Medium",
            "impact": "Medium",
            "effort": "Low",
            "savings": 0,
            "steps": ["Navigate to Azure Advisor in Portal", "Enable all cost recommendation categories", "Configure email alerts for high-impact recommendations", "Schedule weekly review of recommendations", "Integrate with Azure DevOps for tracking"]
        },
        {
            "title": "Implement Comprehensive Resource Tagging",
            "description": "Standardize resource tagging across all environments for accurate cost allocation, chargeback, and showback reporting",
            "category": "Governance",
            "priority": "High",
            "impact": "Low",
            "effort": "High",
            "savings": 0,
            "steps": ["Define mandatory tag schema (Environment, Owner, CostCenter, Project)", "Create Azure Policy to enforce required tags", "Tag all existing resources using PowerShell/CLI", "Generate monthly cost reports by tags", "Set up automated compliance scanning"]
        },
        {
            "title": "Configure Budget Alerts and Spending Limits",
            "description": "Set up Azure Cost Management budgets with multi-threshold alerts to prevent unexpected cost overruns",
            "category": "Monitoring",
            "priority": "Critical",
            "impact": "High",
            "effort": "Low",
            "savings": 0,
            "steps": ["Navigate to Cost Management + Billing", "Create monthly budget for each subscription", "Configure alerts at 50%, 75%, 90%, 100% thresholds", "Set up action groups for notifications", "Create dashboard for budget tracking"]
        },
        {
            "title": "Review and Right-Size Premium Disks",
            "description": "Analyze disk performance metrics and consider switching over-provisioned Premium SSD to Standard SSD where appropriate",
            "category": "Storage",
            "priority": "Medium",
            "impact": "Medium",
            "effort": "Medium",
            "savings": 800,
            "steps": ["Generate disk performance report for all VMs", "Identify Premium disks with low IOPS usage", "Test application performance with Standard SSD", "Schedule disk tier changes during maintenance windows", "Monitor application performance post-change"]
        }
    ]

    for rec_data in general_recs:
        rec = OptimizationRecommendation(
            title=rec_data["title"],
            description=rec_data["description"],
            category=rec_data["category"],
            priority=rec_data["priority"],
            impact=rec_data["impact"],
            effort=rec_data["effort"],
            savings_monthly=rec_data["savings"],
            savings_annual=rec_data["savings"] * 12,
            resource_type="General",
            resource_name=None,
            resource_group=None,
            implementation_steps=json.dumps(rec_data["steps"]),
            estimated_time_minutes=random.randint(30, 90),
            status="pending"
        )
        recommendations.append(rec)

    session.bulk_save_objects(recommendations)
    session.commit()
    print(f"✓ Seeded {len(recommendations)} comprehensive recommendations")


def seed_dashboard_metrics(session):
    """Pre-calculate dashboard metrics"""
    print("Seeding dashboard metrics...")

    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    metrics = []
    current_date = start_date

    while current_date <= end_date:
        costs_for_date = session.query(AzureCost).filter(AzureCost.date == current_date).all()
        daily_cost = sum(c.cost for c in costs_for_date)

        thirty_days_ago = current_date - timedelta(days=30)
        costs_last_30 = session.query(AzureCost).filter(
            AzureCost.date >= thirty_days_ago,
            AzureCost.date <= current_date
        ).all()
        total_monthly_cost = sum(c.cost for c in costs_last_30)

        sixty_days_ago = current_date - timedelta(days=60)
        costs_prev_30 = session.query(AzureCost).filter(
            AzureCost.date >= sixty_days_ago,
            AzureCost.date < thirty_days_ago
        ).all()
        prev_monthly_cost = sum(c.cost for c in costs_prev_30)

        monthly_change = ((total_monthly_cost - prev_monthly_cost) / prev_monthly_cost * 100) if prev_monthly_cost > 0 else 0.0

        days_elapsed = len(set(c.date for c in costs_last_30))
        avg_daily = total_monthly_cost / days_elapsed if days_elapsed > 0 else 0
        projected_cost = avg_daily * 30

        service_costs = {}
        for cost in costs_for_date:
            service_costs[cost.service_name] = service_costs.get(cost.service_name, 0) + cost.cost

        top_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:5]
        top_services_json = json.dumps([{"service": s, "cost": round(c, 2)} for s, c in top_services])

        rg_costs = {}
        for cost in costs_for_date:
            rg_costs[cost.resource_group] = rg_costs.get(cost.resource_group, 0) + cost.cost

        rg_list = sorted(rg_costs.items(), key=lambda x: x[1], reverse=True)[:5]
        rg_json = json.dumps([{"group": g, "cost": round(c, 2)} for g, c in rg_list])

        compute_util = round(random.uniform(55, 75), 1)
        storage_util = round(random.uniform(65, 85), 1)
        database_util = round(random.uniform(60, 80), 1)
        network_util = round(random.uniform(45, 70), 1)

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
    print(f"✓ Seeded {len(metrics)} dashboard metrics")


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("COMPREHENSIVE CostSense-AI Database Setup")
    print("="*70 + "\n")

    engine = create_database()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        seed_comprehensive_vms(session)
        seed_comprehensive_storage(session)
        seed_granular_costs(session)
        seed_comprehensive_recommendations(session)
        seed_dashboard_metrics(session)

        print("\n" + "="*70)
        print("Database Setup Complete!")
        print("="*70)

        # Summary statistics
        print("\n📊 Database Summary:")
        print(f"  • Virtual Machines: {session.query(AzureVM).count()}")
        print(f"  • Storage Accounts: {session.query(AzureStorageAccount).count()}")
        print(f"  • Cost Records: {session.query(AzureCost).count():,}")
        print(f"  • Recommendations: {session.query(OptimizationRecommendation).count()}")
        print(f"  • Dashboard Metrics: {session.query(DashboardMetric).count()}")

        # Cost summary
        latest_metric = session.query(DashboardMetric).order_by(DashboardMetric.date.desc()).first()
        if latest_metric:
            print(f"\n💰 Latest Metrics ({latest_metric.date}):")
            print(f"  • Total Monthly Cost: ${latest_metric.total_monthly_cost:,.2f}")
            print(f"  • Monthly Change: {latest_metric.monthly_change_percent:+.1f}%")
            print(f"  • Potential Savings: ${latest_metric.total_potential_savings:,.2f}/month")

        # Resource breakdown
        running_vms = session.query(AzureVM).filter(AzureVM.status == "Running").count()
        stopped_vms = session.query(AzureVM).filter(AzureVM.status.in_(["Stopped", "Deallocated"])).count()
        print(f"\n🖥️  VM Status:")
        print(f"  • Running: {running_vms}")
        print(f"  • Stopped/Deallocated: {stopped_vms}")

        print(f"\n✅ Database ready at: {DATABASE_PATH}")
        print("   Backend is ready to serve comprehensive, realistic data!\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
