"""Azure Cost Optimization API Router"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from src.agents_langchain import azure_orchestrator
from src.agents_langchain.agentic_orchestrator import agentic_orchestrator
from src.mock.azure_data_generator import azure_data_generator
from src.config.settings import Settings
from src.config.database import get_db
from src.repositories import (
    DashboardRepository,
    VMRepository,
    StorageRepository,
    OptimizationRepository
)

# Initialize settings
settings = Settings()

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class CostAnalysisRequest(BaseModel):
    query: str = Field(..., description="Cost analysis question")
    time_period: Optional[str] = Field("30d", description="Time period for analysis")

    class Config:
        schema_extra = {
            "example": {
                "query": "Analyze my Azure costs for the last month",
                "time_period": "30d"
            }
        }


class OptimizationRequest(BaseModel):
    query: str = Field(..., description="Optimization question or request")
    priority: Optional[str] = Field("savings", description="Priority: savings, performance, or balanced")

    class Config:
        schema_extra = {
            "example": {
                "query": "How can I reduce my VM costs?",
                "priority": "savings"
            }
        }


class AnalysisResponse(BaseModel):
    analysis: str
    timestamp: str
    confidence: str
    agent_used: Optional[str] = None


# Dashboard Endpoints
@router.get("/dashboard/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get comprehensive dashboard data (Database-backed with caching)"""
    try:
        if settings.USE_DATABASE:
            # Use database with Redis caching
            dashboard_repo = DashboardRepository(db)
            data = dashboard_repo.get_dashboard_summary()
            logger.info("Dashboard summary served from database")
        else:
            # Fallback to mock data generator
            data = azure_data_generator.generate_dashboard_data()
            logger.info("Dashboard summary served from mock generator")

        return data
    except Exception as e:
        logger.error(f"Dashboard summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/costs")
async def get_cost_data(period: str = "30d"):
    """Get cost data for specific time period"""
    try:
        days_map = {"7d": 7, "30d": 30, "90d": 90}
        days = days_map.get(period, 30)

        daily_costs = azure_data_generator.cost_gen.generate_daily_costs(days=days)
        total_cost = sum(day["cost"] for day in daily_costs)

        return {
            "period": period,
            "daily_costs": daily_costs,
            "total_cost": round(total_cost, 2),
            "average_daily_cost": round(total_cost / days, 2),
            "trend": azure_data_generator.cost_gen.generate_cost_trend(days)
        }
    except Exception as e:
        logger.error(f"Cost data retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Analysis Endpoints
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_costs(request: CostAnalysisRequest):
    """Perform AI-powered cost analysis (Fully Agentic with Tool Calling)"""
    try:
        # Use fully agentic orchestrator with database tool calling
        result = await agentic_orchestrator.analyze(request.query)

        return AnalysisResponse(
            analysis=result,
            timestamp=datetime.utcnow().isoformat(),
            confidence="High",
            agent_used="agentic_orchestrator"
        )
    except Exception as e:
        logger.error(f"Cost analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/optimize", response_model=AnalysisResponse)
async def get_optimization_recommendations(request: OptimizationRequest):
    """Get AI-powered optimization recommendations (Fully Agentic with Tool Calling)"""
    try:
        # Use fully agentic orchestrator with database tool calling
        result = await agentic_orchestrator.analyze(request.query)

        return AnalysisResponse(
            analysis=result,
            timestamp=datetime.utcnow().isoformat(),
            confidence="High",
            agent_used="agentic_orchestrator"
        )
    except Exception as e:
        logger.error(f"Optimization analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.post("/parallel-analysis")
async def parallel_analysis(request: CostAnalysisRequest):
    """Run all agents in parallel for comprehensive analysis"""
    try:
        results = await azure_orchestrator.parallel_analysis(request.query)

        return {
            "query": request.query,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Parallel analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Infrastructure Endpoints
@router.get("/infrastructure/vms")
async def get_vm_analysis(db: Session = Depends(get_db)):
    """Get VM utilization analysis (Database-backed)"""
    try:
        if settings.USE_DATABASE:
            # Use database with Redis caching
            vm_repo = VMRepository(db)
            vms = vm_repo.get_all_vms()
            summary = vm_repo.get_vms_summary()

            return {
                "vms": vms,
                "summary": summary,
                "totalMonthlyCost": summary["totalMonthlyCost"],
                "potentialSavings": summary["potentialSavings"]
            }
        else:
            # Fallback to mock data generator
            vm_data = azure_data_generator.vm_gen.generate()
            return vm_data
    except Exception as e:
        logger.error(f"VM analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/infrastructure/storage")
async def get_storage_analysis(db: Session = Depends(get_db)):
    """Get storage account analysis (Database-backed)"""
    try:
        if settings.USE_DATABASE:
            # Use database with Redis caching
            storage_repo = StorageRepository(db)
            accounts = storage_repo.get_all_storage_accounts()
            summary = storage_repo.get_storage_summary()

            return {
                "storage_accounts": accounts,
                "summary": summary,
                "totalMonthlyCost": summary["totalMonthlyCost"],
                "potentialSavings": summary["potentialSavings"]
            }
        else:
            # Fallback to mock data generator
            storage_data = azure_data_generator.storage_gen.generate()
            return storage_data
    except Exception as e:
        logger.error(f"Storage analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/infrastructure/comprehensive")
async def get_comprehensive_infrastructure():
    """Get comprehensive infrastructure analysis"""
    try:
        vm_data = azure_data_generator.vm_gen.generate()
        storage_data = azure_data_generator.storage_gen.generate()

        return {
            "virtual_machines": vm_data,
            "storage_accounts": storage_data,
            "total_monthly_cost": vm_data["totalMonthlyCost"] + storage_data["totalMonthlyCost"],
            "total_potential_savings": vm_data["potentialSavings"] + storage_data["potentialSavings"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Comprehensive infrastructure analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Recommendations Endpoint
@router.get("/recommendations")
async def get_all_recommendations(db: Session = Depends(get_db)):
    """Get all optimization recommendations (Database-backed)"""
    try:
        if settings.USE_DATABASE:
            # Use database with Redis caching
            opt_repo = OptimizationRepository(db)
            recommendations = opt_repo.get_all_recommendations(status="pending")
            summary = opt_repo.get_optimization_summary()

            return {
                "recommendations": recommendations,
                "total_potential_savings": summary["totalMonthlySavings"],
                "count": summary["totalCount"],
                "summary": summary,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            # Fallback to mock data generator
            from src.agents_langchain.remediation_specialist import remediation_specialist
            recommendations = remediation_specialist._generate_recommendations()

            return {
                "recommendations": recommendations,
                "total_potential_savings": sum(r["savings"] for r in recommendations),
                "count": len(recommendations),
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Recommendations retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Comprehensive Analysis Endpoint
@router.post("/comprehensive-analysis")
async def comprehensive_analysis(request: CostAnalysisRequest):
    """Get comprehensive analysis with all data"""
    try:
        analysis = await azure_orchestrator.comprehensive_analysis(request.query)
        return analysis
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Resource Groups Endpoint
@router.get("/resource-groups")
async def get_resource_groups():
    """Get resource group cost breakdown"""
    try:
        resource_groups = azure_data_generator.cost_gen.generate_resource_group_costs()

        return {
            "resource_groups": resource_groups,
            "total_cost": sum(rg["cost"] for rg in resource_groups),
            "count": len(resource_groups),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Resource group retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Demo/Test Endpoint - Shows all mock data
@router.get("/demo-data")
async def get_demo_data():
    """Get all demo/mock data for testing - shows comprehensive Azure cost data"""
    try:
        # Get all mock data
        dashboard = azure_data_generator.generate_dashboard_data()
        comprehensive = azure_data_generator.generate_comprehensive_analysis()
        vms = azure_data_generator.vm_gen.generate()
        storage = azure_data_generator.storage_gen.generate()
        from src.agents_langchain.remediation_specialist import remediation_specialist
        recommendations = remediation_specialist._generate_recommendations()

        return {
            "message": "🎉 All Azure Cost Optimization mock data is working!",
            "summary": {
                "total_monthly_cost": dashboard["total_monthly_cost"],
                "monthly_change": f"{dashboard['monthly_change_percent']:+.1f}%",
                "potential_savings": comprehensive["financial_analysis"]["total_potential_savings"],
                "total_vms": vms["totalInstances"],
                "total_storage_accounts": storage["totalAccounts"],
                "recommendations_count": len(recommendations)
            },
            "data": {
                "dashboard": dashboard,
                "comprehensive_analysis": comprehensive,
                "virtual_machines": vms,
                "storage": storage,
                "recommendations": recommendations
            },
            "api_endpoints": {
                "dashboard": "/api/v1/dashboard/summary",
                "analyze": "POST /api/v1/analyze",
                "optimize": "POST /api/v1/optimize",
                "parallel_analysis": "POST /api/v1/parallel-analysis",
                "vms": "/api/v1/infrastructure/vms",
                "storage": "/api/v1/infrastructure/storage",
                "recommendations": "/api/v1/recommendations"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Demo data retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
