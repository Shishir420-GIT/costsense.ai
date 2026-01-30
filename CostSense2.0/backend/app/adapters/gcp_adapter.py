from datetime import datetime
from typing import List, Optional, Dict
from .base import CloudCostProvider, CostData, ResourceData, UtilizationData, CloudProvider
from ..logging_config import get_logger

logger = get_logger(__name__)


class GCPCostAdapter(CloudCostProvider):
    """GCP Cloud Billing adapter (stub implementation)"""

    def get_provider_name(self) -> CloudProvider:
        return CloudProvider.GCP

    async def fetch_costs(
        self,
        start_date: datetime,
        end_date: datetime,
        account_id: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> List[CostData]:
        """Fetch cost data from GCP Cloud Billing (stub)"""
        logger.warning("GCP cost fetching not yet implemented - returning mock data")

        # Return mock data for demonstration
        return [
            CostData(
                provider=CloudProvider.GCP,
                account_id=account_id or "gcp-project-id",
                resource_id="mock-instance-1",
                resource_type="ComputeEngine",
                resource_name="mock-instance-us-central1",
                region="us-central1",
                cost=89.75,
                currency="USD",
                period_start=start_date,
                period_end=end_date,
                tags={"env": "staging", "app": "api"},
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
        """Fetch utilization metrics from GCP Monitoring (stub)"""
        logger.warning("GCP utilization fetching not yet implemented")
        return []

    async def list_resources(
        self,
        resource_type: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[ResourceData]:
        """List GCP resources (stub)"""
        logger.warning("GCP resource listing not yet implemented - returning mock data")

        return [
            ResourceData(
                provider=CloudProvider.GCP,
                account_id="gcp-project-id",
                resource_id="mock-instance-1",
                resource_type="ComputeEngine",
                resource_name="mock-instance-us-central1",
                region="us-central1",
                status="RUNNING",
                tags={"env": "staging"},
                metadata={"stub": True, "machine_type": "n1-standard-2"},
            )
        ]
