import json
from typing import Any, Optional
import redis.asyncio as aioredis
from .config import settings
from .logging_config import get_logger

logger = get_logger(__name__)

# Global cache instance
_cache: Optional[aioredis.Redis] = None


async def get_cache() -> aioredis.Redis:
    """Get or create Redis cache instance"""
    global _cache
    if _cache is None:
        _cache = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        logger.info("Redis cache initialized")
    return _cache


async def close_cache():
    """Close Redis connection"""
    global _cache
    if _cache is not None:
        await _cache.close()
        _cache = None
        logger.info("Redis cache closed")


class Cache:
    """Cache abstraction layer"""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error("Cache get error", key=key, error=str(e))
            return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL (seconds)"""
        try:
            serialized = json.dumps(value)
            if ttl:
                await self.redis.setex(key, ttl, serialized)
            else:
                await self.redis.set(key, serialized)
            return True
        except Exception as e:
            logger.error("Cache set error", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error("Cache delete error", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.error("Cache exists error", key=key, error=str(e))
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter"""
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error("Cache increment error", key=key, error=str(e))
            return None

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        return await self.get(f"session:{session_id}")

    async def set_session(
        self, session_id: str, data: dict, ttl: int = 3600
    ) -> bool:
        """Set session data with 1 hour default TTL"""
        return await self.set(f"session:{session_id}", data, ttl)

    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        return await self.delete(f"session:{session_id}")

    async def ping(self) -> bool:
        """Check if Redis is alive"""
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error("Redis ping failed", error=str(e))
            return False


async def get_cache_instance() -> Cache:
    """Dependency for getting cache instance"""
    redis_client = await get_cache()
    return Cache(redis_client)
