"""Azure Storage Account Model - Storage inventory with tier optimization"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Index
from datetime import datetime
from src.config.database import Base


class AzureStorageAccount(Base):
    """Azure Storage Account inventory and optimization data"""
    __tablename__ = "azure_storage_accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    resource_group = Column(String(100), nullable=False, index=True)
    location = Column(String(50), nullable=False, index=True)
    tier = Column(String(20), nullable=False, index=True)  # Hot, Cool, Archive
    replication_type = Column(String(20), nullable=False)  # LRS, GRS, ZRS, RA-GRS

    # Storage metrics
    size_gb = Column(Float, nullable=False)
    blob_count = Column(Integer, nullable=True)
    container_count = Column(Integer, nullable=True)

    # Usage patterns
    last_accessed = Column(Date, nullable=True)
    access_frequency = Column(String(20), nullable=True)  # High, Medium, Low, Rare

    # Cost data
    monthly_cost = Column(Float, nullable=False)
    potential_savings = Column(Float, nullable=False, default=0.0)

    # Recommendations
    recommended_tier = Column(String(20), nullable=True)
    recommendations = Column(String(1000), nullable=True)  # JSON array string

    # Metadata
    tags = Column(String(500), nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_storage_tier_location', 'tier', 'location'),
        Index('idx_storage_resource_group', 'resource_group'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "resourceGroup": self.resource_group,
            "location": self.location,
            "tier": self.tier,
            "replicationType": self.replication_type,
            "sizeGB": self.size_gb,
            "blobCount": self.blob_count,
            "containerCount": self.container_count,
            "lastAccessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "accessFrequency": self.access_frequency,
            "monthlyCost": self.monthly_cost,
            "potentialSavings": self.potential_savings,
            "recommendedTier": self.recommended_tier,
            "recommendations": self.recommendations,
            "tags": self.tags,
            "lastUpdated": self.last_updated.isoformat() if self.last_updated else None,
        }
