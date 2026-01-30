from datetime import datetime
from typing import List, Optional, Dict
from .base import CloudCostProvider, CostData, ResourceData, UtilizationData, CloudProvider
from ..logging_config import get_logger

logger = get_logger(__name__)


class AzureCostAdapter(CloudCostProvider):
    """Azure Cost Management adapter (stub implementation)"""

    def get_provider_name(self) -> CloudProvider:
        return CloudProvider.AZURE

    async def fetch_costs(
        self,
        start_date: datetime,
        end_date: datetime,
        account_id: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> List[CostData]:
        """Fetch cost data from Azure Cost Management (stub)"""
        logger.warning("Azure cost fetching not yet implemented - returning mock data")

        # Return mock data for demonstration
        return [
            CostData(
                provider=CloudProvider.AZURE,
                account_id=account_id or "azure-subscription-id",
                resource_id="mock-vm-1",
                resource_type="VirtualMachine",
                resource_name="mock-vm-eastus",
                region="eastus",
                cost=125.50,
                currency="USD",
                period_start=start_date,
                period_end=end_date,
                tags={"environment": "production", "team": "platform"},
                metadata={"stub": True},
            )
        ]

    async def fetch_utilization(
        self,
        resource_id: str,
        metric_name: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[UtilizationData]:
        """Fetch utilization metrics from Azure Monitor (stub)"""
        logger.warning("Azure utilization fetching not yet implemented")
        return []

    async def list_resources(
        self,
        resource_type: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[ResourceData]:
        """List Azure resources (stub)"""
        logger.warning("Azure resource listing not yet implemented - returning mock data")

        return [
            ResourceData(
                provider=CloudProvider.AZURE,
                account_id="azure-subscription-id",
                resource_id="mock-vm-1",
                resource_type="VirtualMachine",
                resource_name="mock-vm-eastus",
                region="eastus",
                status="running",
                tags={"environment": "production"},
                metadata={"stub": True, "size": "Standard_D2s_v3"},
            )
        ]
