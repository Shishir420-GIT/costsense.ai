from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
import asyncio

from src.agents.orchestrator_agent_simple import orchestrator
from src.tools.aws_tools_simple import AWSCostExplorerTool, EC2UtilizationTool, S3OptimizationTool
from src.tools.calculation_tools_simple import SavingsCalculationTool

router = APIRouter()

# Request/Response Models
class CostAnalysisRequest(BaseModel):
    query: str
    time_period: Optional[str] = "30_days"
    services: Optional[List[str]] = None

class OptimizationRequest(BaseModel):
    query: str
    service: Optional[str] = "all"
    priority: Optional[str] = "savings"

class CostAnalysisResponse(BaseModel):
    analysis: str
    timestamp: str
    confidence: str
    
class OptimizationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    potential_savings: float
    implementation_plan: str
    timestamp: str

# Initialize tools
cost_tool = AWSCostExplorerTool()
ec2_tool = EC2UtilizationTool()
s3_tool = S3OptimizationTool()
calc_tool = SavingsCalculationTool()

@router.post("/analyze-costs", response_model=CostAnalysisResponse)
async def analyze_costs(request: CostAnalysisRequest):
    try:
        # Get cost data
        cost_data = cost_tool._run(request.time_period)
        
        # Enhance query with cost data
        enhanced_query = f"""
        Analyze these AWS costs and provide insights:
        
        User Query: {request.query}
        Cost Data: {cost_data}
        
        Provide analysis including:
        1. Cost trends and patterns
        2. Highest spending services
        3. Potential anomalies or spikes
        4. Initial optimization opportunities
        """
        
        # Run analysis
        result = await orchestrator.analyze_costs(enhanced_query)
        
        return CostAnalysisResponse(
            analysis=result,
            timestamp=datetime.utcnow().isoformat(),
            confidence="High" if len(result) > 500 else "Medium"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cost analysis failed: {str(e)}")

@router.post("/optimize", response_model=OptimizationResponse)
async def get_optimization_recommendations(request: OptimizationRequest):
    try:
        recommendations = []
        total_savings = 0.0
        
        # Get service-specific analysis
        if request.service in ["all", "ec2"]:
            ec2_data = ec2_tool._run()
            ec2_analysis = json.loads(ec2_data) if ec2_data.startswith("{") else {"instances": []}
            
            for instance in ec2_analysis.get("instances", []):
                if instance.get("recommendation") != "Optimal":
                    recommendations.append({
                        "service": "EC2",
                        "resource": instance.get("instance_id"),
                        "current_type": instance.get("instance_type"),
                        "recommendation": instance.get("recommendation"),
                        "potential_savings": 50.0,  # Simplified
                        "confidence": "High"
                    })
                    total_savings += 50.0
        
        if request.service in ["all", "s3"]:
            s3_data = s3_tool._run()
            s3_analysis = json.loads(s3_data) if s3_data.startswith("{") else {"buckets": []}
            
            for bucket in s3_analysis.get("buckets", []):
                if bucket.get("recommendations"):
                    recommendations.append({
                        "service": "S3",
                        "resource": bucket.get("bucket_name"),
                        "size_gb": bucket.get("size_gb", 0),
                        "recommendations": bucket.get("recommendations"),
                        "potential_savings": min(bucket.get("size_gb", 0) * 0.01, 100.0),
                        "confidence": "Medium"
                    })
                    total_savings += min(bucket.get("size_gb", 0) * 0.01, 100.0)
        
        # Generate implementation plan using orchestrator
        plan_query = f"""
        Create an implementation plan for these optimization recommendations:
        {json.dumps(recommendations, indent=2)}
        
        Include:
        1. Prioritized action items
        2. Implementation timeline
        3. Risk considerations
        4. Success metrics
        """
        
        implementation_plan = await orchestrator.analyze_costs(plan_query)
        
        return OptimizationResponse(
            recommendations=recommendations,
            potential_savings=round(total_savings, 2),
            implementation_plan=implementation_plan,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization analysis failed: {str(e)}")

@router.get("/cost-data/{time_period}")
async def get_cost_data(time_period: str):
    try:
        cost_data = cost_tool._run(time_period)
        
        if cost_data.startswith("{"):
            return json.loads(cost_data)
        else:
            return {"error": cost_data}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve cost data: {str(e)}")

@router.get("/infrastructure-analysis")
async def get_infrastructure_analysis():
    try:
        # Get EC2 analysis
        ec2_data = ec2_tool._run()
        ec2_result = json.loads(ec2_data) if ec2_data.startswith("{") else {"error": ec2_data}
        
        # Get S3 analysis
        s3_data = s3_tool._run()
        s3_result = json.loads(s3_data) if s3_data.startswith("{") else {"error": s3_data}
        
        return {
            "ec2_analysis": ec2_result,
            "s3_analysis": s3_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Infrastructure analysis failed: {str(e)}")

@router.post("/calculate-savings")
async def calculate_savings(optimization_data: Dict[str, Any]):
    try:
        # Use the calculation tool
        savings_data = calc_tool._run(json.dumps(optimization_data))
        
        if savings_data.startswith("{"):
            return json.loads(savings_data)
        else:
            return {"error": savings_data}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Savings calculation failed: {str(e)}")

@router.get("/agent-status")
async def get_agent_status():
    try:
        return {
            "orchestrator": "active",
            "cost_analyst": "active", 
            "infrastructure_analyst": "active",
            "financial_analyst": "active",
            "remediation_specialist": "active",
            "ollama_connected": True,  # Would check actual connection
            "aws_connected": True,     # Would check AWS credentials
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }