"""Audit logging utilities for comprehensive traceability"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import AuditLog, AuditEventType
from ..logging_config import get_logger

logger = get_logger(__name__)


class AuditLogger:
    """Utility for creating audit logs"""

    @staticmethod
    def log_event(
        db: Session,
        event_type: AuditEventType,
        event_name: str,
        event_description: Optional[str] = None,
        actor_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        error_data: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Create an audit log entry"""
        audit_log = AuditLog(
            event_type=event_type,
            event_name=event_name,
            event_description=event_description,
            actor_type=actor_type,
            actor_id=actor_id,
            target_type=target_type,
            target_id=target_id,
            request_data=request_data,
            response_data=response_data,
            error_data=error_data,
            session_id=session_id,
            metadata=metadata or {},
        )

        db.add(audit_log)
        db.commit()

        logger.info(
            "Audit log created",
            event_type=event_type.value,
            event_name=event_name,
            actor=actor_id,
        )

        return audit_log

    @staticmethod
    def log_ai_interaction(
        db: Session,
        prompt: str,
        response: str,
        model: str,
        tokens_used: Optional[int] = None,
        latency_ms: Optional[int] = None,
        session_id: Optional[str] = None,
        actor_id: Optional[str] = None,
    ) -> AuditLog:
        """Log AI/LLM interaction for compliance"""
        return AuditLogger.log_event(
            db=db,
            event_type=AuditEventType.AI_RESPONSE,
            event_name="LLM Generation",
            event_description="AI model generated response",
            actor_type="ai",
            actor_id=model,
            ai_model=model,
            ai_prompt=prompt[:1000],  # Truncate long prompts
            ai_response=response[:1000],  # Truncate long responses
            ai_tokens_used=tokens_used,
            ai_latency_ms=latency_ms,
            session_id=session_id,
            metadata={"user_id": actor_id} if actor_id else {},
        )

    @staticmethod
    def log_user_action(
        db: Session,
        action_name: str,
        user_id: str,
        description: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> AuditLog:
        """Log user action"""
        return AuditLogger.log_event(
            db=db,
            event_type=AuditEventType.USER_ACTION,
            event_name=action_name,
            event_description=description,
            actor_type="user",
            actor_id=user_id,
            request_data=request_data,
            session_id=session_id,
        )

    @staticmethod
    def log_ticket_event(
        db: Session,
        event_type: AuditEventType,
        ticket_id: int,
        user_id: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Log ticket-related event"""
        return AuditLogger.log_event(
            db=db,
            event_type=event_type,
            event_name=f"Ticket {event_type.value}",
            event_description=description,
            actor_type="user",
            actor_id=user_id,
            target_type="ticket",
            target_id=str(ticket_id),
            metadata=metadata,
        )
