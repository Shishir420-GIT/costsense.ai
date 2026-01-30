from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON, Text, Index
from sqlalchemy.sql import func
from ..database import Base


class AuditEventType(str, PyEnum):
    """Types of auditable events"""
    # AI events
    AI_PROMPT = "ai_prompt"
    AI_RESPONSE = "ai_response"
    AI_FUNCTION_CALL = "ai_function_call"
    AI_ERROR = "ai_error"

    # Cost events
    COST_QUERY = "cost_query"
    COST_ANALYSIS = "cost_analysis"
    ANOMALY_DETECTED = "anomaly_detected"

    # Ticket events
    TICKET_CREATED = "ticket_created"
    TICKET_APPROVED = "ticket_approved"
    TICKET_REJECTED = "ticket_rejected"

    # User events
    USER_ACTION = "user_action"
    USER_CONFIRMATION = "user_confirmation"
    USER_REJECTION = "user_rejection"

    # System events
    SYSTEM_ERROR = "system_error"
    SYSTEM_WARNING = "system_warning"


class AuditLog(Base):
    """Comprehensive audit log for compliance and debugging"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Event information
    event_type = Column(Enum(AuditEventType), nullable=False, index=True)
    event_name = Column(String(255), nullable=False)
    event_description = Column(Text)

    # Actor information
    actor_type = Column(String(50))  # 'user', 'system', 'ai'
    actor_id = Column(String(255))

    # Target information
    target_type = Column(String(100))  # 'investigation', 'ticket', 'cost_record'
    target_id = Column(String(255))

    # Event details
    request_data = Column(JSON)
    response_data = Column(JSON)
    error_data = Column(JSON)

    # Context
    session_id = Column(String(100), index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(512))

    # AI-specific fields
    ai_model = Column(String(100))
    ai_prompt = Column(Text)
    ai_response = Column(Text)
    ai_tokens_used = Column(Integer)
    ai_latency_ms = Column(Integer)

    # Metadata
    metadata = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_event_type_created', 'event_type', 'created_at'),
        Index('idx_actor_created', 'actor_type', 'actor_id', 'created_at'),
        Index('idx_session_created', 'session_id', 'created_at'),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, event_type={self.event_type}, event_name='{self.event_name}')>"
