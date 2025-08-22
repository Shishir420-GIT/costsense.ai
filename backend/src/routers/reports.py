from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

from src.agents.orchestrator_agent import orchestrator
from src.tools.aws_tools import AWSCostExplorerTool

router = APIRouter()

class ReportRequest(BaseModel):
    report_type: str  # "cost_analysis", "optimization", "comprehensive"
    time_period: Optional[str] = "30_days"
    format: Optional[str] = "json"  # "json", "csv", "pdf"
    include_recommendations: Optional[bool] = True
    email_recipients: Optional[List[str]] = None

class ScheduledReportRequest(BaseModel):
    name: str
    report_type: str
    schedule: str  # "daily", "weekly", "monthly"
    recipients: List[str]
    format: str = "json"

# Initialize tools
cost_tool = AWSCostExplorerTool()

@router.post("/generate")
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    try:
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate report based on type
        if request.report_type == "cost_analysis":
            report_data = await generate_cost_analysis_report(request.time_period)
        elif request.report_type == "optimization":
            report_data = await generate_optimization_report(request.time_period)
        elif request.report_type == "comprehensive":
            report_data = await generate_comprehensive_report(request.time_period)
        else:
            raise HTTPException(status_code=400, detail="Invalid report type")
        
        # Save report
        report_path = await save_report(report_data, report_id, request.format)
        
        # Schedule email if recipients provided
        if request.email_recipients:
            background_tasks.add_task(
                send_report_email, 
                request.email_recipients, 
                report_path, 
                request.report_type
            )
        
        return {
            "report_id": report_id,
            "report_path": str(report_path),
            "format": request.format,
            "generated_at": datetime.utcnow().isoformat(),
            "download_url": f"/api/v1/reports/download/{report_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.get("/download/{report_id}")
async def download_report(report_id: str):
    try:
        # Find report file
        reports_dir = Path("reports")
        report_files = list(reports_dir.glob(f"{report_id}.*"))
        
        if not report_files:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report_file = report_files[0]
        
        return FileResponse(
            path=report_file,
            filename=report_file.name,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report download failed: {str(e)}")

@router.get("/list")
async def list_reports():
    try:
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        reports = []
        for report_file in reports_dir.iterdir():
            if report_file.is_file():
                stat = report_file.stat()
                reports.append({
                    "filename": report_file.name,
                    "size_bytes": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sort by creation time, newest first
        reports.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "reports": reports,
            "total_reports": len(reports)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")

@router.post("/schedule")
async def schedule_report(request: ScheduledReportRequest):
    # This would integrate with a job scheduler like Celery in production
    try:
        scheduled_report = {
            "id": f"scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "name": request.name,
            "report_type": request.report_type,
            "schedule": request.schedule,
            "recipients": request.recipients,
            "format": request.format,
            "created_at": datetime.utcnow().isoformat(),
            "next_run": calculate_next_run(request.schedule),
            "status": "active"
        }
        
        # In production, this would be stored in database and picked up by scheduler
        return {
            "message": "Report scheduled successfully",
            "scheduled_report": scheduled_report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule report: {str(e)}")

async def generate_cost_analysis_report(time_period: str) -> Dict[str, Any]:
    # Get cost data
    cost_data_raw = cost_tool._run(time_period)
    cost_data = json.loads(cost_data_raw) if cost_data_raw.startswith("{") else {}
    
    # Generate AI analysis
    analysis_query = f"""
    Generate a comprehensive cost analysis report for the past {time_period}:
    
    Cost Data: {json.dumps(cost_data, indent=2)}
    
    Include:
    1. Executive Summary
    2. Cost Trends Analysis
    3. Service Breakdown
    4. Key Findings
    5. Budget Impact Assessment
    """
    
    ai_analysis = await orchestrator.analyze_costs(analysis_query)
    
    return {
        "report_type": "Cost Analysis",
        "time_period": time_period,
        "generated_at": datetime.utcnow().isoformat(),
        "executive_summary": "Cost analysis for AWS infrastructure",
        "cost_data": cost_data,
        "ai_analysis": ai_analysis,
        "total_cost": cost_data.get("total_cost", 0),
        "top_services": cost_data.get("top_services", [])
    }

async def generate_optimization_report(time_period: str) -> Dict[str, Any]:
    # Run comprehensive analysis
    optimization_query = f"""
    Generate detailed optimization recommendations for AWS infrastructure over the past {time_period}.
    
    Focus on:
    1. Cost reduction opportunities
    2. Performance improvements
    3. Resource rightsizing
    4. Reserved instance opportunities
    5. Implementation priorities
    """
    
    optimization_analysis = await orchestrator.comprehensive_analysis(optimization_query)
    
    return {
        "report_type": "Optimization Analysis",
        "time_period": time_period,
        "generated_at": datetime.utcnow().isoformat(),
        "executive_summary": "Optimization opportunities and recommendations",
        "analysis_results": optimization_analysis,
        "potential_savings": 0,  # Would be calculated from analysis
        "implementation_timeline": "4-12 weeks"
    }

async def generate_comprehensive_report(time_period: str) -> Dict[str, Any]:
    # Combine cost analysis and optimization
    cost_report = await generate_cost_analysis_report(time_period)
    optimization_report = await generate_optimization_report(time_period)
    
    # Generate executive summary
    executive_query = """
    Create an executive summary combining cost analysis and optimization findings.
    
    Include:
    1. Key financial metrics
    2. Top recommendations
    3. Expected ROI
    4. Implementation priorities
    """
    
    executive_summary = await orchestrator.analyze_costs(executive_query)
    
    return {
        "report_type": "Comprehensive Cost Optimization",
        "time_period": time_period,
        "generated_at": datetime.utcnow().isoformat(),
        "executive_summary": executive_summary,
        "cost_analysis": cost_report,
        "optimization_analysis": optimization_report,
        "recommendations_count": 10,  # Would be calculated
        "total_potential_savings": 0   # Would be calculated
    }

async def save_report(report_data: Dict[str, Any], report_id: str, format: str) -> Path:
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    if format == "json":
        report_path = reports_dir / f"{report_id}.json"
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
    
    elif format == "csv":
        report_path = reports_dir / f"{report_id}.csv"
        
        # Convert to DataFrame for CSV export
        if "cost_data" in report_data and "daily_costs" in report_data["cost_data"]:
            df = pd.DataFrame(report_data["cost_data"]["daily_costs"])
            df.to_csv(report_path, index=False)
        else:
            # Fallback: create a summary CSV
            summary_data = {
                "Metric": ["Total Cost", "Report Type", "Generated At"],
                "Value": [
                    report_data.get("total_cost", "N/A"),
                    report_data.get("report_type", "N/A"),
                    report_data.get("generated_at", "N/A")
                ]
            }
            pd.DataFrame(summary_data).to_csv(report_path, index=False)
    
    else:  # Default to JSON
        report_path = reports_dir / f"{report_id}.json"
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
    
    return report_path

async def send_report_email(recipients: List[str], report_path: Path, report_type: str):
    # This would integrate with an email service in production
    print(f"Sending {report_type} report to {recipients}: {report_path}")
    # Implementation would use services like SendGrid, SES, etc.
    pass

def calculate_next_run(schedule: str) -> str:
    now = datetime.utcnow()
    
    if schedule == "daily":
        next_run = now + timedelta(days=1)
    elif schedule == "weekly":
        next_run = now + timedelta(weeks=1)
    elif schedule == "monthly":
        next_run = now + timedelta(days=30)
    else:
        next_run = now + timedelta(days=1)
    
    return next_run.isoformat()