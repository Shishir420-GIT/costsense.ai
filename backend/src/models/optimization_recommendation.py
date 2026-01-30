"""Optimization Recommendation Model - Actionable optimization recommendations"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from datetime import datetime
from src.config.database import Base


class OptimizationRecommendation(Base):
    """Optimization recommendations with savings and implementation details"""
    __tablename__ = "optimization_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=False)
    category = Column(String(50), nullable=False, index=True)  # Compute, Storage, Database, Network, Security
    priority = Column(String(20), nullable=False, index=True)  # Critical, High, Medium, Low

    # Impact and effort
    impact = Column(String(20), nullable=False, index=True)  # High, Medium, Low
    effort = Column(String(20), nullable=False)  # Low, Medium, High
    savings_monthly = Column(Float, nullable=False)
    savings_annual = Column(Float, nullable=False)

    # Resource details
    resource_type = Column(String(50), nullable=False)  # VirtualMachine, StorageAccount, Database, etc.
    resource_name = Column(String(100), nullable=True, index=True)
    resource_group = Column(String(100), nullable=True, index=True)

    # Implementation
    implementation_steps = Column(String(2000), nullable=True)  # JSON array string
    estimated_time_minutes = Column(Integer, nullable=True)

    # Status tracking
    status = Column(String(20), nullable=False, default="pending", index=True)  # pending, in_progress, completed, dismissed
    implemented_at = Column(DateTime, nullable=True)

    # Metadata
    tags = Column(String(500), nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_opt_priority_category', 'priority', 'category'),
        Index('idx_opt_status_priority', 'status', 'priority'),
        Index('idx_opt_resource_type_name', 'resource_type', 'resource_name'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "impact": self.impact,
            "effort": self.effort,
            "savingsMonthly": self.savings_monthly,
            "savingsAnnual": self.savings_annual,
            "resourceType": self.resource_type,
            "resourceName": self.resource_name,
            "resourceGroup": self.resource_group,
            "implementationSteps": self.implementation_steps,
            "estimatedTimeMinutes": self.estimated_time_minutes,
            "status": self.status,
            "implementedAt": self.implemented_at.isoformat() if self.implemented_at else None,
            "tags": self.tags,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
