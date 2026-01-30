from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from ..database import get_db
from ..models import Ticket, TicketStatus, Investigation
from ..integrations import get_servicenow_client, TicketPayload
from ..middleware import get_current_user
from ..logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


class TicketCreateRequest(BaseModel):
    investigation_id: Optional[int] = None
    title: str
    description: str
    priority: str = "medium"
    category: str = "cost_optimization"
    evidence: list[str] = []
    recommendations: list[str] = []
    estimated_savings: float = 0.0


class TicketApprovalRequest(BaseModel):
    approved: bool
    rejection_reason: Optional[str] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_ticket_draft(
    ticket_data: TicketCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a ticket draft (requires approval before sending to ServiceNow)"""
    # Validate investigation if provided
    if ticket_data.investigation_id:
        investigation = (
            db.query(Investigation)
            .filter(Investigation.id == ticket_data.investigation_id)
            .first()
        )
        if not investigation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investigation {ticket_data.investigation_id} not found",
            )

    # Create ticket in database
    ticket = Ticket(
        investigation_id=ticket_data.investigation_id,
        title=ticket_data.title,
        description=ticket_data.description,
        priority=ticket_data.priority,
        category=ticket_data.category,
        status=TicketStatus.DRAFT,
        evidence=ticket_data.evidence,
        recommendations=ticket_data.recommendations,
        estimated_savings=int(ticket_data.estimated_savings * 100),  # Store as cents
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    logger.info(
        "Ticket draft created",
        ticket_id=ticket.id,
        title=ticket.title,
        user=current_user["email"],
    )

    return {
        "id": ticket.id,
        "status": ticket.status,
        "title": ticket.title,
        "requires_approval": True,
        "message": "Ticket draft created. Use /approve endpoint to submit to ServiceNow.",
    }


@router.post("/{ticket_id}/approve")
async def approve_ticket(
    ticket_id: int,
    approval: TicketApprovalRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Approve or reject a ticket"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} not found",
        )

    if ticket.status != TicketStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticket is not in draft status (current: {ticket.status})",
        )

    if not approval.approved:
        # Reject the ticket
        ticket.status = TicketStatus.REJECTED
        ticket.rejection_reason = approval.rejection_reason
        db.commit()

        logger.info(
            "Ticket rejected",
            ticket_id=ticket_id,
            user=current_user["email"],
            reason=approval.rejection_reason,
        )

        return {
            "id": ticket.id,
            "status": ticket.status,
            "message": "Ticket rejected",
        }

    # Approve and create in ServiceNow
    ticket.status = TicketStatus.APPROVED
    ticket.approved_by = current_user["email"]
    ticket.approved_at = datetime.utcnow()

    # Create ServiceNow ticket
    sn_client = get_servicenow_client()
    payload = TicketPayload(
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        category=ticket.category,
        evidence=ticket.evidence or [],
        recommendations=ticket.recommendations or [],
        estimated_savings=ticket.estimated_savings / 100 if ticket.estimated_savings else 0,
    )

    sn_response = await sn_client.create_incident(payload)

    if sn_response.success:
        ticket.status = TicketStatus.CREATED
        ticket.ticket_number = sn_response.ticket_number
        ticket.servicenow_sys_id = sn_response.sys_id
        ticket.servicenow_url = sn_response.ticket_url
        ticket.servicenow_response = {
            "ticket_number": sn_response.ticket_number,
            "sys_id": sn_response.sys_id,
            "ticket_url": sn_response.ticket_url,
        }

        logger.info(
            "Ticket created in ServiceNow",
            ticket_id=ticket.id,
            ticket_number=sn_response.ticket_number,
            user=current_user["email"],
        )
    else:
        logger.error(
            "Failed to create ServiceNow ticket",
            ticket_id=ticket.id,
            error=sn_response.error,
        )

    db.commit()
    db.refresh(ticket)

    return {
        "id": ticket.id,
        "status": ticket.status,
        "ticket_number": ticket.ticket_number,
        "ticket_url": ticket.servicenow_url,
        "success": sn_response.success,
        "error": sn_response.error,
    }


@router.get("/")
async def list_tickets(
    status: Optional[TicketStatus] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all tickets"""
    query = db.query(Ticket).order_by(desc(Ticket.created_at))

    if status:
        query = query.filter(Ticket.status == status)

    tickets = query.offset(offset).limit(limit).all()

    return [
        {
            "id": t.id,
            "ticket_number": t.ticket_number,
            "title": t.title,
            "status": t.status,
            "priority": t.priority,
            "estimated_savings": t.estimated_savings / 100 if t.estimated_savings else 0,
            "created_at": t.created_at,
            "ticket_url": t.servicenow_url,
        }
        for t in tickets
    ]


@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get ticket details"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} not found",
        )

    return {
        "id": ticket.id,
        "investigation_id": ticket.investigation_id,
        "ticket_number": ticket.ticket_number,
        "title": ticket.title,
        "description": ticket.description,
        "status": ticket.status,
        "priority": ticket.priority,
        "category": ticket.category,
        "evidence": ticket.evidence,
        "recommendations": ticket.recommendations,
        "estimated_savings": ticket.estimated_savings / 100 if ticket.estimated_savings else 0,
        "approved_by": ticket.approved_by,
        "approved_at": ticket.approved_at,
        "created_at": ticket.created_at,
        "servicenow_url": ticket.servicenow_url,
    }
