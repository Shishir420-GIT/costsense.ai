from typing import Dict, Type, Optional
from .base import CloudCostProvider, CloudProvider
from .aws_adapter import AWSCostAdapter
from .azure_adapter import AzureCostAdapter
from .gcp_adapter import GCPCostAdapter
from ..config import settings
from ..logging_config import get_logger

logger = get_logger(__name__)


class AdapterRegistry:
    """Registry for cloud cost adapters"""

    _adapters: Dict[CloudProvider, Type[CloudCostProvider]] = {
        CloudProvider.AWS: AWSCostAdapter,
        CloudProvider.AZURE: AzureCostAdapter,
        CloudProvider.GCP: GCPCostAdapter,
    }

    _instances: Dict[CloudProvider, CloudCostProvider] = {}

    @classmethod
    def register(cls, provider: CloudProvider, adapter_class: Type[CloudCostProvider]):
        """Register a new adapter"""
        cls._adapters[provider] = adapter_class
        logger.info(f"Registered adapter for {provider.value}")

    @classmethod
    def get_adapter(cls, provider: CloudProvider) -> CloudCostProvider:
        """Get or create adapter instance"""
        if provider not in cls._instances:
            adapter_class = cls._adapters.get(provider)
            if not adapter_class:
                raise ValueError(f"No adapter registered for provider: {provider.value}")

            # Build credentials from settings
            credentials = cls._get_credentials(provider)
            cls._instances[provider] = adapter_class(credentials)
            logger.info(f"Created adapter instance for {provider.value}")

        return cls._instances[provider]

    @classmethod
    def _get_credentials(cls, provider: CloudProvider) -> Dict[str, str]:
        """Get credentials for provider from settings"""
        if provider == CloudProvider.AWS:
            return {
                "aws_access_key_id": settings.aws_access_key_id,
                "aws_secret_access_key": settings.aws_secret_access_key,
                "aws_region": settings.aws_region,
            }
        elif provider == CloudProvider.AZURE:
            return {
                "azure_tenant_id": settings.azure_tenant_id,
                "azure_client_id": settings.azure_client_id,
                "azure_client_secret": settings.azure_client_secret,
                "azure_subscription_id": settings.azure_subscription_id,
            }
        elif provider == CloudProvider.GCP:
            return {
                "google_application_credentials": settings.google_application_credentials,
                "gcp_project_id": settings.gcp_project_id,
            }
        else:
            return {}

    @classmethod
    def list_providers(cls) -> list[str]:
        """List all registered providers"""
        return [p.value for p in cls._adapters.keys()]


def get_adapter(provider: CloudProvider) -> CloudCostProvider:
    """Convenience function to get adapter"""
    return AdapterRegistry.get_adapter(provider)
