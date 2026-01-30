from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from ..database import get_db
from ..models import CostRecord, CloudProvider
from ..middleware import get_current_user
from ..logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/costs", tags=["costs"])


@router.get("/summary")
async def get_cost_summary(
    provider: Optional[CloudProvider] = None,
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get cost summary for the specified period"""
    start_date = datetime.utcnow() - timedelta(days=days)

    query = db.query(
        func.sum(CostRecord.cost).label("total_cost"),
        func.count(CostRecord.id).label("record_count"),
    ).filter(CostRecord.period_start >= start_date)

    if provider:
        query = query.filter(CostRecord.provider == provider)

    result = query.first()

    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": datetime.utcnow().isoformat(),
        "total_cost": float(result.total_cost or 0),
        "record_count": result.record_count or 0,
        "provider": provider.value if provider else "all",
    }


@router.get("/by-provider")
async def get_costs_by_provider(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get cost breakdown by cloud provider"""
    start_date = datetime.utcnow() - timedelta(days=days)

    results = (
        db.query(
            CostRecord.provider,
            func.sum(CostRecord.cost).label("total_cost"),
            func.count(CostRecord.id).label("record_count"),
        )
        .filter(CostRecord.period_start >= start_date)
        .group_by(CostRecord.provider)
        .all()
    )

    return {
        "period_days": days,
        "breakdown": [
            {
                "provider": r.provider.value,
                "total_cost": float(r.total_cost),
                "record_count": r.record_count,
            }
            for r in results
        ],
    }


@router.get("/by-resource-type")
async def get_costs_by_resource_type(
    provider: Optional[CloudProvider] = None,
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get top N most expensive resource types"""
    start_date = datetime.utcnow() - timedelta(days=days)

    query = (
        db.query(
            CostRecord.resource_type,
            CostRecord.provider,
            func.sum(CostRecord.cost).label("total_cost"),
            func.count(CostRecord.id).label("record_count"),
        )
        .filter(CostRecord.period_start >= start_date)
        .group_by(CostRecord.resource_type, CostRecord.provider)
        .order_by(desc("total_cost"))
        .limit(limit)
    )

    if provider:
        query = query.filter(CostRecord.provider == provider)

    results = query.all()

    return {
        "period_days": days,
        "provider": provider.value if provider else "all",
        "top_resource_types": [
            {
                "resource_type": r.resource_type,
                "provider": r.provider.value,
                "total_cost": float(r.total_cost),
                "record_count": r.record_count,
            }
            for r in results
        ],
    }


@router.get("/trend")
async def get_cost_trend(
    provider: Optional[CloudProvider] = None,
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get daily cost trend"""
    start_date = datetime.utcnow() - timedelta(days=days)

    query = (
        db.query(
            func.date(CostRecord.period_start).label("date"),
            func.sum(CostRecord.cost).label("daily_cost"),
        )
        .filter(CostRecord.period_start >= start_date)
        .group_by(func.date(CostRecord.period_start))
        .order_by(func.date(CostRecord.period_start))
    )

    if provider:
        query = query.filter(CostRecord.provider == provider)

    results = query.all()

    return {
        "period_days": days,
        "provider": provider.value if provider else "all",
        "trend": [
            {
                "date": r.date.isoformat(),
                "cost": float(r.daily_cost),
            }
            for r in results
        ],
    }
