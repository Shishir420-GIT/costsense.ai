"""Main FastAPI application for Azure Cost Optimization Platform"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import logging
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routers
from src.routers import azure_cost_optimization, azure_websocket

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    logger.info("🚀 Starting Azure Cost Optimization Platform...")

    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)

    # Test Ollama connection
    try:
        from src.config.langchain_config import test_ollama_connection
        if test_ollama_connection():
            logger.info("✓ Ollama connection successful")
        else:
            logger.warning("⚠️  Ollama not available - using fallback mode")
    except Exception as e:
        logger.warning(f"⚠️  Could not connect to Ollama: {e}")

    # Initialize agents
    try:
        from src.agents_langchain import azure_orchestrator
        logger.info("✓ Azure Cost Orchestrator initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize orchestrator: {e}")

    yield

    logger.info("🛑 Shutting down Azure Cost Optimization Platform...")


# Create FastAPI app
app = FastAPI(
    title="Azure Cost Optimization Platform",
    description="AI-powered Azure cost optimization with LangChain multi-agent analysis",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    azure_cost_optimization.router,
    prefix="/api/v1",
    tags=["azure-cost-optimization"]
)

app.include_router(
    azure_websocket.router,
    prefix="/ws",
    tags=["websocket"]
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from src.config.langchain_config import test_ollama_connection

    ollama_status = test_ollama_connection()

    return {
        "status": "healthy",
        "service": "azure-cost-optimizer",
        "version": "2.0.0",
        "cloud_provider": "Azure",
        "ai_framework": "LangChain",
        "llm_model": "llama3.2:latest",
        "dependencies": {
            "orchestrator": "active",
            "ollama": "connected" if ollama_status else "unavailable",
            "agents": "active"
        }
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Azure Cost Optimization Platform API",
        "version": "2.0.0",
        "cloud_provider": "Azure",
        "ai_framework": "LangChain",
        "docs": "/docs",
        "health": "/health",
        "features": {
            "cost_analysis": True,
            "infrastructure_optimization": True,
            "financial_analysis": True,
            "remediation_planning": True,
            "real_time_websocket": True,
            "mock_data": True,
            "azure_integration": False  # Phase 2
        }
    }

# Agent status endpoint
@app.get("/api/v1/agent-status")
async def get_agent_status():
    """Get status of all agents"""
    from datetime import datetime

    return {
        "orchestrator": "active",
        "cost_analyst": "active",
        "infrastructure_analyst": "active",
        "financial_analyst": "active",
        "remediation_specialist": "active",
        "ollama_connected": True,
        "langchain_enabled": True,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_azure:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
