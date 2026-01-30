from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum


class CloudProvider(str, Enum):
    """Supported cloud providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class CostData(BaseModel):
    """Normalized cost data structure"""
    provider: CloudProvider
    account_id: str
    resource_id: str
    resource_type: str
    resource_name: Optional[str] = None
    region: str
    cost: float
    currency: str = "USD"
    period_start: datetime
    period_end: datetime
    tags: Dict[str, str] = {}
    metadata: Dict[str, Any] = {}


class ResourceData(BaseModel):
    """Normalized resource data structure"""
    provider: CloudProvider
    account_id: str
    resource_id: str
    resource_type: str
    resource_name: Optional[str] = None
    region: str
    status: str
    tags: Dict[str, str] = {}
    metadata: Dict[str, Any] = {}
    created_at: Optional[datetime] = None


class UtilizationData(BaseModel):
    """Normalized utilization data structure"""
    provider: CloudProvider
    resource_id: str
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}


class CloudCostProvider(ABC):
    """Abstract base class for cloud cost providers"""

    def __init__(self, credentials: Dict[str, str]):
        """Initialize provider with credentials"""
        self.credentials = credentials
        self.provider = self.get_provider_name()

    @abstractmethod
    def get_provider_name(self) -> CloudProvider:
        """Return the provider name"""
        pass

    @abstractmethod
    async def fetch_costs(
        self,
        start_date: datetime,
        end_date: datetime,
        account_id: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> List[CostData]:
        """Fetch cost data for the specified period"""
        pass

    @abstractmethod
    async def fetch_utilization(
        self,
        resource_id: str,
        metric_name: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[UtilizationData]:
        """Fetch utilization metrics for a resource"""
        pass

    @abstractmethod
    async def list_resources(
        self,
        resource_type: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[ResourceData]:
        """List cloud resources"""
        pass

    async def test_connection(self) -> bool:
        """Test if credentials are valid and connection works"""
        try:
            # Try to fetch a small amount of data
            resources = await self.list_resources()
            return True
        except Exception as e:
            return False
