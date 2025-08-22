from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from src.agents.registry import agent_registry, AgentType
from src.agents.orchestrator import orchestrator
from src.agents.component_advisor import component_advisor
from src.agents.trusted_advisor_agent import trusted_advisor

router = APIRouter()

class AgentRequest(BaseModel):
    agent_name: str
    query: str
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    agent_name: str
    response: str
    execution_time: float
    timestamp: str

class MultiAgentRequest(BaseModel):
    query: str
    agents: Optional[List[str]] = None
    mode: Optional[str] = "parallel"  # parallel, sequential, or workflow

@router.post("/execute", response_model=AgentResponse)
async def execute_agent(request: AgentRequest):
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Use agent registry to execute query
        result = await agent_registry.execute_agent_query(
            request.agent_name, 
            request.query, 
            request.context
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        execution_time = asyncio.get_event_loop().time() - start_time
        
        return AgentResponse(
            agent_name=request.agent_name,
            response=str(result["result"]),
            execution_time=round(execution_time, 3),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@router.post("/multi-agent")
async def execute_multi_agent(request: MultiAgentRequest):
    try:
        start_time = asyncio.get_event_loop().time()
        
        if request.mode == "parallel":
            # Execute parallel analysis using registry
            result = await agent_registry.execute_parallel_analysis(request.query)
            results = result["results"] if result["success"] else {"error": result["error"]}
        elif request.mode == "comprehensive":
            # Execute comprehensive analysis using registry
            result = await agent_registry.execute_comprehensive_analysis(request.query)
            results = result["results"] if result["success"] else {"error": result["error"]}
        else:
            # Default to orchestrator
            result = await orchestrator.analyze_costs(request.query)
            results = {"orchestrated_analysis": result}
        
        execution_time = asyncio.get_event_loop().time() - start_time
        
        return {
            "results": results,
            "execution_time": round(execution_time, 3),
            "timestamp": datetime.utcnow().isoformat(),
            "mode": request.mode
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-agent execution failed: {str(e)}")

@router.get("/status")
async def get_agents_status():
    try:
        # Use agent registry for comprehensive health check
        health_status = await agent_registry.get_all_agents_health()
        return health_status
        
    except Exception as e:
        return {
            "overall_health": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/capabilities")
async def get_agent_capabilities():
    # Use agent registry for comprehensive capabilities information
    return agent_registry.get_agent_capabilities_summary()

@router.get("/registry")
async def get_registry_info():
    """Get comprehensive agent registry information"""
    return agent_registry.get_registry_info()

@router.get("/agents")
async def list_agents():
    """List all available agents"""
    return {
        "agents": agent_registry.list_agents(),
        "total_agents": len(agent_registry.list_agents()),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/agents/{agent_name}")
async def get_agent_info(agent_name: str):
    """Get detailed information about a specific agent"""
    agent = agent_registry.get_agent(agent_name)
    metadata = agent_registry.get_agent_metadata(agent_name)
    
    if not agent or not metadata:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    return {
        "agent_name": agent_name,
        "metadata": metadata,
        "available": True,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/agents/{agent_name}/health")
async def get_agent_health(agent_name: str):
    """Get health status for a specific agent"""
    health_status = await agent_registry.get_agent_health_status(agent_name)
    
    if "error" in health_status and "not found" in health_status["error"]:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    return health_status

class ComponentAdvisorRequest(BaseModel):
    query: str
    context: Optional[str] = "component_recommendation"

@router.post("/component-advisor")
async def component_advisor_endpoint(request: ComponentAdvisorRequest):
    """Component Advisor endpoint for AWS component recommendations"""
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Execute component advisor analysis
        result = await component_advisor.analyze(request.query, {"context": request.context})
        
        execution_time = asyncio.get_event_loop().time() - start_time
        
        return {
            **result,
            "execution_time": round(execution_time, 3),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Component advisor failed: {str(e)}")

class TrustedAdvisorRequest(BaseModel):
    query: Optional[str] = "full_analysis"
    focus_area: Optional[str] = "cost_optimization"  # cost_optimization, security, all

@router.post("/trusted-advisor")
async def trusted_advisor_endpoint(request: TrustedAdvisorRequest):
    """Trusted Advisor endpoint for AWS cost analysis with tabular data"""
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Execute Trusted Advisor analysis
        result = await trusted_advisor.analyze(
            request.query, 
            {"focus_area": request.focus_area}
        )
        
        execution_time = asyncio.get_event_loop().time() - start_time
        
        return {
            **result,
            "execution_time": round(execution_time, 3),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trusted Advisor analysis failed: {str(e)}")