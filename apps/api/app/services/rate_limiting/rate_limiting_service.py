"""
Rate Limiting Service for LLM Eval Guardrails Platform
Implements token bucket algorithm for API rate limiting
"""
import redis
import json
import os
import time

class RateLimitingService:
    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        self.bucket_capacity = 100
        self.refill_rate = 1  # tokens per second

    def is_allowed(self, key: str, tokens_requested: int = 1) -> bool:
        """Check if request is allowed based on rate limit"""
        bucket = self._get_or_create_bucket(key)

        now = time.time()
        time_since_last_refill = now - bucket['lastRefill']

        tokens_to_add = int(time_since_last_refill * self.refill_rate)
        bucket['tokens'] = min(bucket['tokens'] + tokens_to_add, self.bucket_capacity)
        bucket['lastRefill'] = now

        if bucket['tokens'] >= tokens_requested:
            bucket['tokens'] -= tokens_requested
            self._save_bucket(key, bucket)
            return True

        return False

    def get_remaining_tokens(self, key: str) -> int:
        """Get remaining tokens for a key"""
        bucket = self._get_or_create_bucket(key)

        now = time.time()
        time_since_last_refill = now - bucket['lastRefill']
        tokens_to_add = int(time_since_last_refill * self.refill_rate)
        bucket['tokens'] = min(bucket['tokens'] + tokens_to_add, self.bucket_capacity)
        bucket['lastRefill'] = now

        self._save_bucket(key, bucket)
        return bucket['tokens']

    def reset_bucket(self, key: str) -> None:
        """Reset rate limit bucket for a key"""
        self.redis.delete(f'rate_limit:{key}')

    def _get_or_create_bucket(self, key: str) -> dict:
        """Get or create token bucket for a key"""
        data = self.redis.get(f'rate_limit:{key}')

        if data:
            return json.loads(data)

        bucket = {
            'tokens': self.bucket_capacity,
            'lastRefill': time.time()
        }

        self._save_bucket(key, bucket)
        return bucket

    def _save_bucket(self, key: str, bucket: dict) -> None:
        """Save token bucket to Redis"""
        self.redis.setex(f'rate_limit:{key}', 3600, json.dumps(bucket))
