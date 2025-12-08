"""Storage Repository - Storage Account data access with caching"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
import json

from src.models import AzureStorageAccount
from src.config.database import redis_client


class StorageRepository:
    """Repository for Azure Storage Account data"""

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

    def get_all_storage_accounts(self) -> List[Dict[str, Any]]:
        """Get all storage accounts"""
        cache_key = "storage:all"

        # Try cache
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # Query database
        accounts = self.db.query(AzureStorageAccount).order_by(AzureStorageAccount.name).all()

        result = [account.to_dict() for account in accounts]

        # Cache for 60 seconds
        self._set_cache(cache_key, result)

        return result

    def get_storage_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get single storage account by name"""
        cache_key = f"storage:{name}"

        # Try cache
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # Query database
        account = self.db.query(AzureStorageAccount).filter(
            AzureStorageAccount.name == name
        ).first()

        if not account:
            return None

        result = account.to_dict()

        # Cache for 60 seconds
        self._set_cache(cache_key, result)

        return result

    def get_storage_summary(self) -> Dict[str, Any]:
        """Get storage summary statistics"""
        cache_key = "storage:summary"

        # Try cache
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # Query all storage accounts
        accounts = self.db.query(AzureStorageAccount).all()

        total_count = len(accounts)
        total_size_gb = sum(account.size_gb for account in accounts)
        total_monthly_cost = sum(account.monthly_cost for account in accounts)
        total_potential_savings = sum(account.potential_savings for account in accounts if account.potential_savings)

        # Group by tier
        tier_counts = {}
        for account in accounts:
            tier_counts[account.tier] = tier_counts.get(account.tier, 0) + 1

        # Get accounts with optimization opportunities
        optimization_opportunities = [
            account.to_dict()
            for account in accounts
            if account.potential_savings and account.potential_savings > 0
        ]

        result = {
            "totalCount": total_count,
            "totalSizeGB": round(total_size_gb, 2),
            "totalMonthlyCost": round(total_monthly_cost, 2),
            "potentialSavings": round(total_potential_savings, 2),
            "tierDistribution": tier_counts,
            "optimizationOpportunities": optimization_opportunities
        }

        # Cache for 60 seconds
        self._set_cache(cache_key, result)

        return result

    def get_storage_by_tier(self, tier: str) -> List[Dict[str, Any]]:
        """Get storage accounts by tier"""
        cache_key = f"storage:tier:{tier}"

        # Try cache
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        # Query database
        accounts = self.db.query(AzureStorageAccount).filter(
            AzureStorageAccount.tier == tier
        ).order_by(AzureStorageAccount.name).all()

        result = [account.to_dict() for account in accounts]

        # Cache for 60 seconds
        self._set_cache(cache_key, result)

        return result
