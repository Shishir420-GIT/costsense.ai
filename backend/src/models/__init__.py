"""Database models for CostSense-AI

All models use SQLAlchemy ORM and support both SQLite (MVP) and PostgreSQL (production)
"""

from .azure_cost import AzureCost
from .azure_vm import AzureVM
from .azure_storage import AzureStorageAccount
from .optimization_recommendation import OptimizationRecommendation
from .dashboard_metric import DashboardMetric

__all__ = [
    "AzureCost",
    "AzureVM",
    "AzureStorageAccount",
    "OptimizationRecommendation",
    "DashboardMetric",
]
