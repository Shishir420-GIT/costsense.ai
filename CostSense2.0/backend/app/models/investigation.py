from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON, Text
from sqlalchemy.sql import func
from ..database import Base


class InvestigationStatus(str, PyEnum):
    """Status of cost investigation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Investigation(Base):
    """AI-powered cost investigation record"""

    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)

    # Investigation details
    title = Column(String(512), nullable=False)
    description = Column(Text)
    status = Column(Enum(InvestigationStatus), default=InvestigationStatus.PENDING, index=True)

    # Target information
    provider = Column(String(50))
    resource_type = Column(String(255))
    time_range_start = Column(DateTime(timezone=True))
    time_range_end = Column(DateTime(timezone=True))

    # AI analysis
    ai_summary = Column(Text)
    ai_recommendations = Column(JSON, default=list)
    confidence_score = Column(Integer)  # 0-100

    # Results
    total_cost_analyzed = Column(Integer)  # in cents
    potential_savings = Column(Integer)  # in cents
    findings = Column(JSON, default=list)

    # Metadata
    triggered_by = Column(String(100))  # 'user', 'scheduled', 'anomaly'
    metadata = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<Investigation(id={self.id}, status={self.status}, title='{self.title}')>"
