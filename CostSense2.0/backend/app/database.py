from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
from .logging_config import get_logger

logger = get_logger(__name__)

# Create engine with configurable connection pool
# Works with both standard PostgreSQL and Azure Cosmos DB for PostgreSQL
engine = create_engine(
    settings.database_url,
    pool_pre_ping=settings.database_pool_pre_ping,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    # Azure Cosmos DB for PostgreSQL specific optimizations
    connect_args={
        "connect_timeout": 10,
        # SSL is required for Azure Cosmos DB - automatically handled by sslmode=require in URL
    } if "cosmos.azure.com" in settings.database_url else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Log database configuration (without credentials)
db_type = "Azure Cosmos DB for PostgreSQL" if "cosmos.azure.com" in settings.database_url else "PostgreSQL"
logger.info(f"Database configured: {db_type}")


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
