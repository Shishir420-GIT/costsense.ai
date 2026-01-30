"""Azure Cost Model - Daily cost records by service and resource group"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Index
from datetime import datetime
from src.config.database import Base


class AzureCost(Base):
    """Daily Azure cost records"""
    __tablename__ = "azure_costs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    service_name = Column(String(100), nullable=False, index=True)
    resource_group = Column(String(100), nullable=False, index=True)
    cost = Column(Float, nullable=False)
    region = Column(String(50), nullable=True)
    tags = Column(String(500), nullable=True)  # JSON string for flexibility
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Composite index for common queries
    __table_args__ = (
        Index('idx_cost_date_service', 'date', 'service_name'),
        Index('idx_cost_date_resource_group', 'date', 'resource_group'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "service_name": self.service_name,
            "resource_group": self.resource_group,
            "cost": self.cost,
            "region": self.region,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
