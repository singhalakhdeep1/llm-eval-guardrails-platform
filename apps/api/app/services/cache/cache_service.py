"""
Cache Service for LLM Eval Guardrails Platform
Implements distributed caching with Redis for guardrails platform data
"""
import redis
import json
import os

class CacheService:
    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        self.default_ttl = 3600  # 1 hour

    def get(self, key: str) -> str | None:
        """Get value from cache"""
        value = self.redis.get(key)
        return value

    def set(self, key: str, value: str, ttl: int = None) -> None:
        """Set value in cache with TTL"""
        expiration = ttl or self.default_ttl
        self.redis.setex(key, expiration, value)

    def delete(self, key: str) -> None:
        """Delete value from cache"""
        self.redis.delete(key)

    def get_or_set(self, key: str, factory, ttl: int = None) -> str:
        """Get value from cache or set using factory function"""
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value

        value = factory()
        self.set(key, value, ttl)
        return value

    def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate all keys matching pattern"""
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)

    def clear_all(self) -> None:
        """Clear all cache entries"""
        keys = self.redis.keys('*')
        if keys:
            self.redis.delete(*keys)
