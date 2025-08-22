from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from src.routers import cost_optimization, agents
from src.agents.orchestrator_agent_simple import orchestrator

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting AWS Cost Optimization Platform...")
    Path("logs").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
    yield
    print("🛑 Shutting down AWS Cost Optimization Platform...")

# Create FastAPI app
app = FastAPI(
    title="AWS Cost Optimization Platform",
    description="AI-powered AWS cost optimization with multi-agent analysis",
    version="1.0.0",
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
app.include_router(cost_optimization.router, prefix="/api/v1", tags=["cost-optimization"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "aws-cost-optimizer",
        "version": "1.0.0",
        "dependencies": {
            "orchestrator": "connected",
            "agents": "active"
        }
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AWS Cost Optimization Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )