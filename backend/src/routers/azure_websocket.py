"""Azure WebSocket Router for Real-time Analysis"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any
import json
import logging
import asyncio
from datetime import datetime

from src.agents_langchain import azure_orchestrator
from src.mock.azure_data_generator import azure_data_generator

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to client: {e}")


# Global connection manager
manager = ConnectionManager()


@router.websocket("/cost-analysis")
async def websocket_cost_analysis(websocket: WebSocket):
    """WebSocket endpoint for real-time cost analysis"""
    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            query = data.get("query", "")

            logger.info(f"Received WebSocket message: {message_type}")

            # Send acknowledgment
            await manager.send_personal_message({
                "type": "ack",
                "message": "Query received, processing..."
            }, websocket)

            # Process based on message type
            if message_type == "cost_analysis":
                await handle_cost_analysis(websocket, query)

            elif message_type == "optimization_request":
                await handle_optimization(websocket, query)

            elif message_type == "parallel_analysis":
                await handle_parallel_analysis(websocket, query)

            elif message_type == "comprehensive_analysis":
                await handle_comprehensive_analysis(websocket, query)

            elif message_type == "dashboard_refresh":
                await handle_dashboard_refresh(websocket)

            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def handle_cost_analysis(websocket: WebSocket, query: str):
    """Handle cost analysis request"""
    try:
        # Send progress update
        await manager.send_personal_message({
            "type": "status",
            "progress": 10,
            "message": "Starting cost analysis..."
        }, websocket)

        # Perform analysis
        result = await azure_orchestrator.analyze(query)

        # Send progress update
        await manager.send_personal_message({
            "type": "status",
            "progress": 90,
            "message": "Analysis complete"
        }, websocket)

        # Send final result
        await manager.send_personal_message({
            "type": "analysis_complete",
            "data": {
                "analysis": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        }, websocket)

    except Exception as e:
        logger.error(f"Cost analysis failed: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Analysis failed: {str(e)}"
        }, websocket)


async def handle_optimization(websocket: WebSocket, query: str):
    """Handle optimization request"""
    try:
        # Send progress updates
        await manager.send_personal_message({
            "type": "status",
            "progress": 20,
            "message": "Analyzing infrastructure..."
        }, websocket)

        await asyncio.sleep(0.5)  # Simulate processing

        await manager.send_personal_message({
            "type": "status",
            "progress": 50,
            "message": "Generating recommendations..."
        }, websocket)

        # Get recommendations
        result = await azure_orchestrator.analyze(query)

        await manager.send_personal_message({
            "type": "status",
            "progress": 90,
            "message": "Finalizing recommendations..."
        }, websocket)

        # Send final result
        await manager.send_personal_message({
            "type": "optimization_complete",
            "data": {
                "recommendations": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        }, websocket)

    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Optimization failed: {str(e)}"
        }, websocket)


async def handle_parallel_analysis(websocket: WebSocket, query: str):
    """Handle parallel analysis with all agents"""
    try:
        # Send initial progress
        await manager.send_personal_message({
            "type": "status",
            "progress": 30,
            "message": "Running parallel analysis with all agents..."
        }, websocket)

        # Run parallel analysis
        results = await azure_orchestrator.parallel_analysis(query)

        # Stream each agent's result
        agents = [
            ("cost_analyst", "Cost Analysis"),
            ("infrastructure_analyst", "Infrastructure Analysis"),
            ("financial_analyst", "Financial Analysis"),
            ("remediation_specialist", "Remediation Plan")
        ]

        progress = 30
        increment = 60 / len(agents)

        for agent_key, agent_name in agents:
            if agent_key in results:
                progress += increment
                await manager.send_personal_message({
                    "type": "agent_result",
                    "agent": agent_name,
                    "progress": int(progress),
                    "data": results[agent_key]
                }, websocket)
                await asyncio.sleep(0.3)  # Brief pause for UX

        # Send completion
        await manager.send_personal_message({
            "type": "parallel_analysis_complete",
            "data": results,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)

    except Exception as e:
        logger.error(f"Parallel analysis failed: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Parallel analysis failed: {str(e)}"
        }, websocket)


async def handle_comprehensive_analysis(websocket: WebSocket, query: str):
    """Handle comprehensive analysis with detailed progress"""
    try:
        # Progress milestones
        milestones = [
            (5, "Initializing analysis..."),
            (15, "Fetching Azure cost data..."),
            (25, "Analyzing virtual machines..."),
            (40, "Analyzing storage accounts..."),
            (55, "Running cost analysis agent..."),
            (70, "Running infrastructure analyst..."),
            (85, "Calculating financial metrics..."),
            (95, "Generating remediation plan..."),
        ]

        for progress, message in milestones:
            await manager.send_personal_message({
                "type": "status",
                "progress": progress,
                "message": message
            }, websocket)
            await asyncio.sleep(0.4)

        # Get comprehensive analysis
        analysis = await azure_orchestrator.comprehensive_analysis(query)

        # Send final result
        await manager.send_personal_message({
            "type": "comprehensive_analysis_complete",
            "data": analysis,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)

    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Comprehensive analysis failed: {str(e)}"
        }, websocket)


async def handle_dashboard_refresh(websocket: WebSocket):
    """Handle dashboard data refresh"""
    try:
        # Get fresh dashboard data
        dashboard_data = azure_data_generator.generate_dashboard_data()

        # Send data
        await manager.send_personal_message({
            "type": "dashboard_data",
            "data": dashboard_data
        }, websocket)

    except Exception as e:
        logger.error(f"Dashboard refresh failed: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Dashboard refresh failed: {str(e)}"
        }, websocket)
