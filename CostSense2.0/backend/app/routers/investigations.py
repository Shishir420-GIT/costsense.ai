from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from ..database import get_db
from ..models import Investigation, InvestigationStatus
from ..middleware import get_current_user
from ..logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/investigations", tags=["investigations"])


class InvestigationCreate(BaseModel):
    title: str
    description: Optional[str] = None
    provider: Optional[str] = None
    resource_type: Optional[str] = None


class InvestigationResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: InvestigationStatus
    provider: Optional[str]
    resource_type: Optional[str]
    ai_summary: Optional[str]
    confidence_score: Optional[int]
    total_cost_analyzed: Optional[int]
    potential_savings: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    investigation_data: InvestigationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new cost investigation"""
    investigation = Investigation(
        title=investigation_data.title,
        description=investigation_data.description,
        provider=investigation_data.provider,
        resource_type=investigation_data.resource_type,
        status=InvestigationStatus.PENDING,
        triggered_by="user",
    )

    db.add(investigation)
    db.commit()
    db.refresh(investigation)

    logger.info(
        "Investigation created",
        investigation_id=investigation.id,
        title=investigation.title,
        user=current_user["email"],
    )

    return investigation


@router.get("/", response_model=List[InvestigationResponse])
async def list_investigations(
    status: Optional[InvestigationStatus] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List investigations with optional filtering"""
    query = db.query(Investigation).order_by(desc(Investigation.created_at))

    if status:
        query = query.filter(Investigation.status == status)

    investigations = query.offset(offset).limit(limit).all()

    return investigations


@router.get("/{investigation_id}", response_model=InvestigationResponse)
async def get_investigation(
    investigation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get investigation by ID"""
    investigation = db.query(Investigation).filter(Investigation.id == investigation_id).first()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation {investigation_id} not found",
        )

    return investigation


@router.patch("/{investigation_id}/status")
async def update_investigation_status(
    investigation_id: int,
    new_status: InvestigationStatus,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update investigation status"""
    investigation = db.query(Investigation).filter(Investigation.id == investigation_id).first()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation {investigation_id} not found",
        )

    investigation.status = new_status
    if new_status == InvestigationStatus.COMPLETED:
        investigation.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(investigation)

    logger.info(
        "Investigation status updated",
        investigation_id=investigation_id,
        old_status=investigation.status,
        new_status=new_status,
    )

    return investigation
