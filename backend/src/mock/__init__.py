"""Azure mock data generators"""

from .azure_data_generator import (
    AzureMockDataGenerator,
    azure_data_generator
)
from .azure_cost_data import (
    CostDataGenerator,
    cost_data_generator
)
from .azure_vm_data import (
    VMDataGenerator,
    vm_data_generator
)
from .azure_storage_data import (
    StorageDataGenerator,
    storage_data_generator
)

__all__ = [
    'AzureMockDataGenerator',
    'azure_data_generator',
    'CostDataGenerator',
    'cost_data_generator',
    'VMDataGenerator',
    'vm_data_generator',
    'StorageDataGenerator',
    'storage_data_generator',
]
