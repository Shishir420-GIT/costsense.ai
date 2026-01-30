"""Dashboard Metric Model - Pre-aggregated metrics for ultra-fast dashboard queries"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Index
from datetime import datetime
from src.config.database import Base


class DashboardMetric(Base):
    """Pre-aggregated dashboard metrics for fast queries"""
    __tablename__ = "dashboard_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)

    # Cost metrics
    total_monthly_cost = Column(Float, nullable=False)
    monthly_change_percent = Column(Float, nullable=False)
    projected_monthly_cost = Column(Float, nullable=False)
    daily_cost = Column(Float, nullable=False)

    # Utilization metrics
    compute_utilization = Column(Float, nullable=True)
    storage_utilization = Column(Float, nullable=True)
    database_utilization = Column(Float, nullable=True)
    network_utilization = Column(Float, nullable=True)

    # Top services (JSON string: [{"service": "...", "cost": 123.45}, ...])
    top_services = Column(String(2000), nullable=True)

    # Resource group costs (JSON string: [{"group": "...", "cost": 123.45}, ...])
    resource_groups = Column(String(2000), nullable=True)

    # Savings opportunities
    total_potential_savings = Column(Float, nullable=True, default=0.0)
    optimization_count = Column(Integer, nullable=True, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Index for date-based queries
    __table_args__ = (
        Index('idx_dashboard_date_desc', 'date'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "totalMonthlyCost": self.total_monthly_cost,
            "monthlyChangePercent": self.monthly_change_percent,
            "projectedMonthlyCost": self.projected_monthly_cost,
            "dailyCost": self.daily_cost,
            "utilizationMetrics": {
                "compute": self.compute_utilization,
                "storage": self.storage_utilization,
                "database": self.database_utilization,
                "network": self.network_utilization,
            },
            "topServices": self.top_services,
            "resourceGroups": self.resource_groups,
            "totalPotentialSavings": self.total_potential_savings,
            "optimizationCount": self.optimization_count,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
