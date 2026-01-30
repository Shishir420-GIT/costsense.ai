"""Azure Virtual Machine Model - VM inventory with utilization metrics"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from datetime import datetime
from src.config.database import Base


class AzureVM(Base):
    """Azure Virtual Machine inventory and metrics"""
    __tablename__ = "azure_vms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    resource_group = Column(String(100), nullable=False, index=True)
    location = Column(String(50), nullable=False, index=True)
    size = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, index=True)  # Running, Stopped, Deallocated

    # Utilization metrics
    cpu_utilization = Column(Float, nullable=False)  # Percentage
    memory_utilization = Column(Float, nullable=False)  # Percentage
    disk_utilization = Column(Float, nullable=True)  # Percentage
    network_in_mb = Column(Float, nullable=True)  # MB
    network_out_mb = Column(Float, nullable=True)  # MB

    # Cost data
    monthly_cost = Column(Float, nullable=False)
    potential_savings = Column(Float, nullable=False, default=0.0)

    # Recommendations
    recommendation = Column(String(500), nullable=True)
    recommendation_type = Column(String(50), nullable=True)  # Resize, Shutdown, Reserved Instance

    # Metadata
    tags = Column(String(500), nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_vm_status_location', 'status', 'location'),
        Index('idx_vm_resource_group', 'resource_group'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "resourceGroup": self.resource_group,
            "location": self.location,
            "size": self.size,
            "status": self.status,
            "cpuUtilization": self.cpu_utilization,
            "memoryUtilization": self.memory_utilization,
            "diskUtilization": self.disk_utilization,
            "networkInMB": self.network_in_mb,
            "networkOutMB": self.network_out_mb,
            "monthlyCost": self.monthly_cost,
            "potentialSavings": self.potential_savings,
            "recommendation": self.recommendation,
            "recommendationType": self.recommendation_type,
            "tags": self.tags,
            "lastUpdated": self.last_updated.isoformat() if self.last_updated else None,
        }
