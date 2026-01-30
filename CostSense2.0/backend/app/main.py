from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .config import settings
from .logging_config import configure_logging, get_logger
from .database import get_db, engine, Base
from .cache import get_cache, close_cache

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    logger.info("Starting CostSense AI backend", version="0.1.0")

    # Create database tables (in production, use Alembic migrations)
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)

    # Test database connection
    try:
        with next(get_db()) as db:
            logger.info("Database connection successful")
    except Exception as e:
        logger.error("Database connection failed", error=str(e))

    # Test cache connection
    try:
        cache = await get_cache()
        logger.info("Cache connection successful")
    except Exception as e:
        logger.error("Cache connection failed", error=str(e))

    yield

    # Cleanup
    logger.info("Shutting down CostSense AI backend")
    await close_cache()


app = FastAPI(
    title="CostSense AI",
    description="Multi-cloud cost intelligence platform with AI-assisted optimization",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from .routers import costs, investigations, tickets, chat

app.include_router(costs.router)
app.include_router(investigations.router)
app.include_router(tickets.router)
app.include_router(chat.router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "costsense-ai",
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CostSense AI - Multi-cloud Cost Intelligence Platform",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    logger.info("WebSocket connection established", client=websocket.client)

    try:
        while True:
            data = await websocket.receive_text()
            logger.debug("WebSocket message received", data=data)
            await websocket.send_json({
                "type": "echo",
                "data": data,
                "message": "WebSocket connection active"
            })
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed", client=websocket.client)
