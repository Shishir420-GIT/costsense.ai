"""VM Repository - Virtual Machine data access with caching"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
import json

from src.models import AzureVM
from src.config.database import redis_client


class VMRepository:
    """Repository for Azure VM data"""

    CACHE_TTL = 60  # 60 seconds cache

    def __init__(self, db: Session):
        self.db = db

    def _get_cache(self, key: str) -> Optional[Any]:
        """Get data from Redis cache"""
        if not redis_client:
            return None

        try:
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass

        return None

    def _set_cache(self, key: str, data: Any, ttl: int = CACHE_TTL):
        """Set data in Redis cache"""
        if not redis_client:
            return

        try:
            redis_client.setex(key, ttl, json.dumps(data))
        except Exception:
            pass

    def get_all_vms(self) -> List[Dict[str, Any]]:
        """Get all VMs with utilization metrics"""
        cache_key = "vms:all"

        # Try cache
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # Query database
        vms = self.db.query(AzureVM).order_by(AzureVM.name).all()

        result = [vm.to_dict() for vm in vms]

        # Cache for 60 seconds
        self._set_cache(cache_key, result)

        return result

    def get_vm_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get single VM by name"""
        cache_key = f"vm:{name}"

        # Try cache
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # Query database
        vm = self.db.query(AzureVM).filter(AzureVM.name == name).first()

        if not vm:
            return None

        result = vm.to_dict()

        # Cache for 60 seconds
        self._set_cache(cache_key, result)

        return result

    def get_vms_summary(self) -> Dict[str, Any]:
        """Get VM summary statistics"""
        cache_key = "vms:summary"

        # Try cache
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # Query all VMs
        vms = self.db.query(AzureVM).all()

        total_count = len(vms)
        running_count = sum(1 for vm in vms if vm.status == "Running")
        stopped_count = sum(1 for vm in vms if vm.status in ["Stopped", "Deallocated"])

        total_monthly_cost = sum(vm.monthly_cost for vm in vms)
        total_potential_savings = sum(vm.potential_savings for vm in vms if vm.potential_savings)

        avg_cpu = sum(vm.cpu_utilization for vm in vms) / total_count if total_count > 0 else 0
        avg_memory = sum(vm.memory_utilization for vm in vms) / total_count if total_count > 0 else 0

        # Get underutilized VMs (< 30% CPU)
        underutilized = [
            vm.to_dict()
            for vm in vms
            if vm.cpu_utilization < 30 and vm.status == "Running"
        ]

        result = {
            "totalCount": total_count,
            "runningCount": running_count,
            "stoppedCount": stopped_count,
            "totalMonthlyCost": round(total_monthly_cost, 2),
            "potentialSavings": round(total_potential_savings, 2),
            "avgCpuUtilization": round(avg_cpu, 1),
            "avgMemoryUtilization": round(avg_memory, 1),
            "underutilizedVMs": underutilized[:5]  # Top 5 underutilized
        }

        # Cache for 60 seconds
        self._set_cache(cache_key, result)

        return result

    def get_vms_with_recommendations(self) -> List[Dict[str, Any]]:
        """Get VMs that have optimization recommendations"""
        cache_key = "vms:with_recommendations"

        # Try cache
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # Query VMs with savings > 0
        vms = self.db.query(AzureVM).filter(
            AzureVM.potential_savings > 0
        ).order_by(desc(AzureVM.potential_savings)).all()

        result = [vm.to_dict() for vm in vms]

        # Cache for 60 seconds
        self._set_cache(cache_key, result)

        return result
