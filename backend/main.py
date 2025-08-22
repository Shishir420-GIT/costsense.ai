from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from src.routers import cost_optimization, agents, reports, websocket, shadcn_mcp
from src.utils.websocket_manager import ConnectionManager
from src.config.settings import Settings
from src.utils.logging_config import setup_logging

# Setup logging
setup_logging()

# Initialize settings
settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting AWS Cost Optimization Platform...")
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
    
    # Initialize Ollama models
    try:
        import ollama
        client = ollama.Client(host=settings.OLLAMA_HOST)
        # Pull required models if not exists
        try:
            models = client.list()
            if not any(model['name'].startswith(settings.OLLAMA_MODEL) for model in models['models']):
                print(f"📥 Pulling {settings.OLLAMA_MODEL} model...")
                client.pull(settings.OLLAMA_MODEL)
            print("✅ Ollama models ready")
        except Exception as model_error:
            print(f"⚠️  Ollama model check warning: {model_error}")
    except Exception as e:
        print(f"⚠️  Ollama initialization warning: {e}")
        print("💡 Make sure Ollama is running on", settings.OLLAMA_HOST)
    
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
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cost_optimization.router, prefix="/api/v1", tags=["cost-optimization"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
app.include_router(shadcn_mcp.router, prefix="/api/v1/mcp/shadcn", tags=["shadcn-mcp"])

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Test Ollama connection
        ollama_status = "unknown"
        try:
            import ollama
            client = ollama.Client(host=settings.OLLAMA_HOST)
            client.list()
            ollama_status = "connected"
        except:
            ollama_status = "disconnected"
        
        # Test AWS connection (simplified)
        aws_status = "unknown"
        try:
            import boto3
            boto3.client('sts').get_caller_identity()
            aws_status = "connected"
        except:
            aws_status = "disconnected"
        
        return {
            "status": "healthy",
            "service": "aws-cost-optimizer",
            "version": "1.0.0",
            "dependencies": {
                "ollama": ollama_status,
                "aws": aws_status
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AWS Cost Optimization Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "/ws/cost-analysis",
        "health": "/health"
    }

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )