from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, JSON, Index
from sqlalchemy.sql import func
from ..database import Base


class CloudProvider(str, PyEnum):
    """Supported cloud providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class CostRecord(Base):
    """Cost record from cloud providers"""

    __tablename__ = "cost_records"

    id = Column(Integer, primary_key=True, index=True)

    # Provider information
    provider = Column(Enum(CloudProvider), nullable=False, index=True)
    account_id = Column(String(255), nullable=False, index=True)

    # Resource information
    resource_id = Column(String(512), nullable=False)
    resource_type = Column(String(255), nullable=False, index=True)
    resource_name = Column(String(512))
    region = Column(String(100), index=True)

    # Cost information
    cost = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")

    # Time information
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Additional metadata
    tags = Column(JSON, default=dict)
    metadata = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes for common queries
    __table_args__ = (
        Index('idx_provider_account', 'provider', 'account_id'),
        Index('idx_provider_period', 'provider', 'period_start', 'period_end'),
        Index('idx_resource_type_period', 'resource_type', 'period_start'),
    )

    def __repr__(self):
        return f"<CostRecord(id={self.id}, provider={self.provider}, cost={self.cost})>"
