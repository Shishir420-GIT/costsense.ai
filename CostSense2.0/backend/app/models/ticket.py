from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class TicketStatus(str, PyEnum):
    """ITSM ticket status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CREATED = "created"
    CLOSED = "closed"


class Ticket(Base):
    """ServiceNow ticket record"""

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    # Investigation reference
    investigation_id = Column(Integer, ForeignKey("investigations.id"), index=True)

    # Ticket details
    ticket_number = Column(String(100), unique=True, index=True)
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(50))  # 'low', 'medium', 'high', 'critical'
    category = Column(String(100))  # 'cost_optimization', 'anomaly', etc.

    # Status
    status = Column(Enum(TicketStatus), default=TicketStatus.DRAFT, index=True)

    # ServiceNow integration
    servicenow_sys_id = Column(String(100), unique=True, index=True)
    servicenow_url = Column(String(512))
    servicenow_response = Column(JSON)

    # Approval workflow
    approved_by = Column(String(255))
    approved_at = Column(DateTime(timezone=True))
    rejection_reason = Column(Text)

    # Evidence and recommendations
    evidence = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    estimated_savings = Column(Integer)  # in cents

    # Metadata
    metadata = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<Ticket(id={self.id}, ticket_number='{self.ticket_number}', status={self.status})>"
