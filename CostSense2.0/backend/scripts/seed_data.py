"""Seed database with sample data for demonstration"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from datetime import datetime, timedelta
import random
from app.database import SessionLocal, engine, Base
from app.models import (
    CostRecord,
    CloudProvider,
    Investigation,
    InvestigationStatus,
    Ticket,
    TicketStatus,
    User,
)

def seed_users():
    """Create sample users"""
    db = SessionLocal()

    users = [
        User(
            email="admin@costsense.ai",
            username="admin",
            full_name="Admin User",
            is_active=True,
            is_admin=True,
        ),
        User(
            email="analyst@costsense.ai",
            username="analyst",
            full_name="Cost Analyst",
            is_active=True,
            is_admin=False,
        ),
    ]

    for user in users:
        db.add(user)

    db.commit()
    print(f"✅ Created {len(users)} users")
    db.close()


def seed_cost_records():
    """Create sample cost records"""
    db = SessionLocal()

    services = {
        CloudProvider.AWS: [
            ("EC2", "us-east-1"),
            ("RDS", "us-east-1"),
            ("S3", "us-west-2"),
            ("Lambda", "eu-west-1"),
            ("ECS", "us-east-1"),
        ],
        CloudProvider.AZURE: [
            ("VirtualMachine", "eastus"),
            ("SQLDatabase", "westus"),
            ("StorageAccount", "centralus"),
            ("AppService", "eastus"),
        ],
        CloudProvider.GCP: [
            ("ComputeEngine", "us-central1"),
            ("CloudSQL", "us-east1"),
            ("CloudStorage", "us-west1"),
        ],
    }

    # Generate 90 days of cost data
    cost_records = []
    for days_ago in range(90):
        date = datetime.utcnow() - timedelta(days=days_ago)

        for provider in services:
            for service, region in services[provider]:
                # Generate realistic costs with some variance
                base_cost = random.uniform(100, 1000)
                variance = random.uniform(-0.2, 0.3)  # -20% to +30%
                cost = base_cost * (1 + variance)

                record = CostRecord(
                    provider=provider,
                    account_id=f"{provider.value}-account-001",
                    resource_id=f"{service.lower()}-{random.randint(1000, 9999)}",
                    resource_type=service,
                    resource_name=f"{service}-{region}-prod",
                    region=region,
                    cost=cost,
                    currency="USD",
                    period_start=date.replace(hour=0, minute=0, second=0),
                    period_end=date.replace(hour=23, minute=59, second=59),
                    tags={"environment": "production", "team": "platform"},
                    metadata={"generated": True},
                )
                cost_records.append(record)

    for record in cost_records:
        db.add(record)

    db.commit()
    print(f"✅ Created {len(cost_records)} cost records")
    db.close()


def seed_investigations():
    """Create sample investigations"""
    db = SessionLocal()

    investigations = [
        Investigation(
            title="High EC2 costs in us-east-1",
            description="Investigating unusual spike in EC2 costs",
            status=InvestigationStatus.COMPLETED,
            provider="aws",
            resource_type="EC2",
            ai_summary="Analysis shows significant cost increase due to m5.4xlarge instances running 24/7. Recommend rightsizing or implementing auto-scaling.",
            confidence_score=85,
            total_cost_analyzed=250000,  # $2,500 in cents
            potential_savings=75000,  # $750 in cents
            triggered_by="anomaly",
            completed_at=datetime.utcnow() - timedelta(days=2),
        ),
        Investigation(
            title="Idle RDS instances detected",
            description="Several RDS instances with low CPU utilization",
            status=InvestigationStatus.IN_PROGRESS,
            provider="aws",
            resource_type="RDS",
            triggered_by="scheduled",
        ),
        Investigation(
            title="Azure storage optimization",
            description="Analyzing storage costs and tier optimization opportunities",
            status=InvestigationStatus.PENDING,
            provider="azure",
            resource_type="StorageAccount",
            triggered_by="user",
        ),
    ]

    for inv in investigations:
        db.add(inv)

    db.commit()
    print(f"✅ Created {len(investigations)} investigations")
    db.close()


def seed_tickets():
    """Create sample tickets"""
    db = SessionLocal()

    tickets = [
        Ticket(
            investigation_id=1,
            ticket_number="INC0012345",
            title="Rightsize EC2 instances in us-east-1",
            description="Identified over-provisioned EC2 instances that can be rightsized to save costs.",
            priority="high",
            category="cost_optimization",
            status=TicketStatus.CREATED,
            evidence=[
                "5x m5.4xlarge instances at 15% average CPU",
                "Running 24/7 without auto-scaling",
                "Costing $2,500/month",
            ],
            recommendations=[
                "Rightsize to m5.2xlarge instances",
                "Implement auto-scaling based on CPU",
                "Use Reserved Instances for baseline capacity",
            ],
            estimated_savings=75000,  # $750 in cents
            approved_by="admin@costsense.ai",
            approved_at=datetime.utcnow() - timedelta(days=1),
            servicenow_url="https://mock.service-now.com/incident/INC0012345",
        ),
        Ticket(
            title="Implement S3 lifecycle policies",
            description="Set up lifecycle policies for S3 buckets to reduce storage costs.",
            priority="medium",
            category="cost_optimization",
            status=TicketStatus.DRAFT,
            evidence=[
                "15TB of data in Standard storage",
                "Majority of data not accessed in 90+ days",
            ],
            recommendations=[
                "Move infrequently accessed data to S3-IA",
                "Archive data older than 1 year to Glacier",
            ],
            estimated_savings=45000,  # $450 in cents
        ),
    ]

    for ticket in tickets:
        db.add(ticket)

    db.commit()
    print(f"✅ Created {len(tickets)} tickets")
    db.close()


def main():
    """Run all seed functions"""
    print("🌱 Seeding database with sample data...")
    print()

    # Create tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    print()

    # Seed data
    seed_users()
    seed_cost_records()
    seed_investigations()
    seed_tickets()

    print()
    print("✨ Database seeding complete!")
    print()
    print("Sample data created:")
    print("  • 2 users (admin, analyst)")
    print("  • ~1,350 cost records (90 days x 15 services)")
    print("  • 3 investigations (completed, in-progress, pending)")
    print("  • 2 tickets (created, draft)")


if __name__ == "__main__":
    main()
