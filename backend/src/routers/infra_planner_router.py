"""Infrastructure Planner API Router"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from src.agents_langchain.infra_planner import infra_planner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/infra-planner", tags=["Infrastructure Planner"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class InfraPlanRequest(BaseModel):
    """Request model for infrastructure planning"""
    requirements: str
    existing_resources: Optional[Dict[str, Any]] = None


class InfraPlanResponse(BaseModel):
    """Response model for infrastructure plan"""
    description: str
    dsl_code: str
    svg_diagram: str
    services: list
    estimated_monthly_cost: float
    recommendations: list
    timestamp: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/plan", response_model=InfraPlanResponse)
async def create_infrastructure_plan(request: InfraPlanRequest):
    """
    Generate Azure infrastructure plan from requirements

    This endpoint creates a complete infrastructure architecture plan including:
    - Architecture description
    - DSL code for visualization
    - SVG diagram
    - List of Azure services
    - Cost estimate
    - Best practice recommendations

    Example request:
    ```json
    {
        "requirements": "I need a web application with database and storage"
    }
    ```
    """
    try:
        logger.info(f"Generating infrastructure plan for: {request.requirements[:100]}...")

        # Generate plan using the infrastructure planner agent
        plan = await infra_planner.plan(request.requirements)

        return InfraPlanResponse(
            description=plan["description"],
            dsl_code=plan["dsl_code"],
            svg_diagram=plan.get("svg_diagram", ""),
            services=plan["services"],
            estimated_monthly_cost=plan["estimated_monthly_cost"],
            recommendations=plan["recommendations"],
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Infrastructure planning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/azure-services")
async def get_azure_services():
    """
    Get list of supported Azure services

    Returns categorized list of Azure services that can be used in infrastructure planning.
    """
    return {
        "categories": {
            "Compute": [
                "Virtual Machines",
                "App Service",
                "Azure Kubernetes Service (AKS)",
                "Container Instances",
                "Functions"
            ],
            "Networking": [
                "Virtual Network",
                "Load Balancer",
                "Application Gateway",
                "VPN Gateway",
                "Azure Firewall"
            ],
            "Database": [
                "SQL Database",
                "Cosmos DB",
                "PostgreSQL",
                "MySQL",
                "Redis Cache"
            ],
            "Storage": [
                "Storage Account",
                "Blob Storage",
                "File Storage",
                "Data Lake Storage",
                "Managed Disks"
            ],
            "Security": [
                "Key Vault",
                "Security Center",
                "Azure AD",
                "DDoS Protection"
            ],
            "Monitoring": [
                "Application Insights",
                "Log Analytics",
                "Monitor",
                "Service Health"
            ],
            "Integration": [
                "Logic Apps",
                "Service Bus",
                "Event Grid",
                "API Management"
            ]
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/status")
async def get_status():
    """Get infrastructure planner agent status"""
    return {
        "status": "operational",
        "agent": "InfraPlannerAgent",
        "llm_available": infra_planner.llm_available,
        "model": "llama3.2:latest" if infra_planner.llm_available else "fallback",
        "capabilities": [
            "Architecture design",
            "DSL generation",
            "Cost estimation",
            "Service recommendations",
            "Best practices validation"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }
