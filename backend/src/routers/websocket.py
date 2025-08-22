from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Any
import json
import asyncio
import logging
from datetime import datetime

from src.utils.websocket_manager import manager
from src.agents.orchestrator_agent import orchestrator

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/cost-analysis")
async def websocket_cost_analysis(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Send acknowledgment
            await manager.send_personal_message({
                "type": "ack",
                "message": "Request received, starting analysis..."
            }, websocket)
            
            # Route message based on type
            if message.get("type") == "cost_analysis":
                await handle_cost_analysis(message, websocket)
            elif message.get("type") == "optimization_request":
                await handle_optimization_request(message, websocket)
            elif message.get("type") == "parallel_analysis":
                await handle_parallel_analysis(message, websocket)
            elif message.get("type") == "comprehensive_analysis":
                await handle_comprehensive_analysis(message, websocket)
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Unknown request type"
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from cost analysis WebSocket")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Server error: {str(e)}"
        }, websocket)

async def handle_cost_analysis(message: Dict[str, Any], websocket: WebSocket):
    try:
        user_query = message.get("query", "")
        
        # Send status update
        await manager.send_personal_message({
            "type": "status",
            "message": "🔍 Analyzing AWS costs...",
            "progress": 10
        }, websocket)
        
        # Execute analysis
        result = await orchestrator.analyze_costs(user_query)
        
        # Stream response
        await manager.stream_agent_response(websocket, result, "cost_optimizer")
        
        # Send completion
        await manager.send_personal_message({
            "type": "analysis_complete",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Analysis failed: {str(e)}"
        }, websocket)

async def handle_optimization_request(message: Dict[str, Any], websocket: WebSocket):
    try:
        user_query = message.get("query", "")
        service = message.get("service", "all")
        
        await manager.send_personal_message({
            "type": "status",
            "message": f"🔧 Generating optimization recommendations for {service}...",
            "progress": 20
        }, websocket)
        
        # Execute optimization analysis
        result = await orchestrator.analyze_costs(
            f"Provide optimization recommendations for {service}: {user_query}"
        )
        
        await manager.stream_agent_response(websocket, result, "optimization_specialist")
        
        await manager.send_personal_message({
            "type": "optimization_complete",
            "result": result,
            "service": service,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Optimization analysis failed: {str(e)}"
        }, websocket)

async def handle_parallel_analysis(message: Dict[str, Any], websocket: WebSocket):
    try:
        user_query = message.get("query", "")
        
        await manager.send_personal_message({
            "type": "status",
            "message": "🚀 Running parallel analysis with multiple agents...",
            "progress": 30
        }, websocket)
        
        # Execute parallel analysis
        results = await orchestrator.parallel_analysis(user_query)
        
        # Send results from each agent
        for agent_name, result in results.items():
            await manager.send_personal_message({
                "type": "agent_result",
                "agent": agent_name,
                "result": result
            }, websocket)
        
        await manager.send_personal_message({
            "type": "parallel_analysis_complete",
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Parallel analysis failed: {str(e)}"
        }, websocket)

async def handle_comprehensive_analysis(message: Dict[str, Any], websocket: WebSocket):
    try:
        user_query = message.get("query", "")
        
        await manager.send_personal_message({
            "type": "status", 
            "message": "🔍 Starting comprehensive cost optimization analysis...",
            "progress": 5
        }, websocket)
        
        # Step-by-step comprehensive analysis with progress updates
        await manager.send_personal_message({
            "type": "status",
            "message": "📊 Analyzing historical costs and trends...",
            "progress": 25
        }, websocket)
        
        await manager.send_personal_message({
            "type": "status", 
            "message": "🏗️ Evaluating infrastructure utilization...",
            "progress": 50
        }, websocket)
        
        await manager.send_personal_message({
            "type": "status",
            "message": "💰 Calculating potential savings and ROI...", 
            "progress": 75
        }, websocket)
        
        await manager.send_personal_message({
            "type": "status",
            "message": "📋 Generating implementation roadmap...",
            "progress": 90
        }, websocket)
        
        # Execute comprehensive analysis
        results = await orchestrator.comprehensive_analysis(user_query)
        
        # Send final results
        await manager.send_personal_message({
            "type": "comprehensive_analysis_complete",
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
            "progress": 100
        }, websocket)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Comprehensive analysis failed: {str(e)}"
        }, websocket)