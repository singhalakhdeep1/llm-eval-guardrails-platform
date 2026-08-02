# Redis integration for llm-eval-guardrails-platform

import redis
import json
import pickle
import os

class RedisService:
    def __init__(self):
        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=False
        )

    def set(self, key: str, value: str, expire: int = None):
        """Set a key-value pair"""
        return self.client.set(key, value, ex=expire)

    def get(self, key: str):
        """Get a value by key"""
        return self.client.get(key)

    def delete(self, key: str):
        """Delete a key"""
        return self.client.delete(key)

    def exists(self, key: str):
        """Check if a key exists"""
        return self.client.exists(key)

    def expire(self, key: str, seconds: int):
        """Set expiration for a key"""
        return self.client.expire(key, seconds)

    def set_json(self, key: str, value: dict, expire: int = None):
        """Set a JSON value"""
        return self.client.set(key, json.dumps(value), ex=expire)

    def get_json(self, key: str):
        """Get a JSON value"""
        value = self.client.get(key)
        return json.loads(value) if value else None

    def set_pickle(self, key: str, value: any, expire: int = None):
        """Set a pickled value"""
        return self.client.set(key, pickle.dumps(value), ex=expire)

    def get_pickle(self, key: str):
        """Get a pickled value"""
        value = self.client.get(key)
        return pickle.loads(value) if value else None

    def lpush(self, key: str, *values):
        """Push values to the left of a list"""
        return self.client.lpush(key, *values)

    def rpush(self, key: str, *values):
        """Push values to the right of a list"""
        return self.client.rpush(key, *values)

    def lpop(self, key: str):
        """Pop from the left of a list"""
        return self.client.lpop(key)

    def rpop(self, key: str):
        """Pop from the right of a list"""
        return self.client.rpop(key)

    def lrange(self, key: str, start: int, end: int):
        """Get a range of list elements"""
        return self.client.lrange(key, start, end)

    def sadd(self, key: str, *members):
        """Add members to a set"""
        return self.client.sadd(key, *members)

    def srem(self, key: str, *members):
        """Remove members from a set"""
        return self.client.srem(key, *members)

    def smembers(self, key: str):
        """Get all members of a set"""
        return self.client.smembers(key)

    def hset(self, name: str, key: str, value: str):
        """Set a hash field"""
        return self.client.hset(name, key, value)

    def hget(self, name: str, key: str):
        """Get a hash field"""
        return self.client.hget(name, key)

    def hgetall(self, name: str):
        """Get all hash fields"""
        return self.client.hgetall(name)

    def hdel(self, name: str, *keys):
        """Delete hash fields"""
        return self.client.hdel(name, *keys)

    def incr(self, key: str):
        """Increment a key"""
        return self.client.incr(key)

    def decr(self, key: str):
        """Decrement a key"""
        return self.client.decr(key)

    def flushdb(self):
        """Flush the current database"""
        return self.client.flushdb()

    def ping(self):
        """Ping the Redis server"""
        return self.client.ping()
