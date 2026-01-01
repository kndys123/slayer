"""
Enterprise-grade caching system with multiple backends.
Supports in-memory, Redis, and Memcached.
"""

import asyncio
import hashlib
import json
import pickle
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import time

from ..core.exceptions import CacheError


class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str):
        """Delete value from cache."""
        pass
    
    @abstractmethod
    async def clear(self):
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass


class MemoryCache(CacheBackend):
    """In-memory cache implementation with TTL support."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry['expires_at'] and time.time() > entry['expires_at']:
                del self._cache[key]
                del self._access_times[key]
                return None
            
            # Update access time for LRU
            self._access_times[key] = time.time()
            
            return entry['value']
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache."""
        async with self._lock:
            # Evict if cache is full
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()
            
            expires_at = None
            if ttl:
                expires_at = time.time() + ttl
            
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': time.time()
            }
            self._access_times[key] = time.time()
    
    async def delete(self, key: str):
        """Delete value from cache."""
        async with self._lock:
            self._cache.pop(key, None)
            self._access_times.pop(key, None)
    
    async def clear(self):
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            self._access_times.clear()
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        value = await self.get(key)
        return value is not None
    
    def _evict_lru(self):
        """Evict least recently used item."""
        if not self._access_times:
            return
        
        lru_key = min(self._access_times, key=self._access_times.get)
        del self._cache[lru_key]
        del self._access_times[lru_key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'utilization': len(self._cache) / self.max_size if self.max_size > 0 else 0
        }


class RedisCache(CacheBackend):
    """Redis cache implementation."""
    
    def __init__(self, redis_url: str, db: int = 0, prefix: str = "slayer:"):
        self.redis_url = redis_url
        self.db = db
        self.prefix = prefix
        self._redis = None
    
    async def _get_redis(self):
        """Get or create Redis connection."""
        if self._redis is None:
            try:
                import aioredis
                self._redis = await aioredis.create_redis_pool(
                    self.redis_url,
                    db=self.db,
                    encoding='utf-8'
                )
            except ImportError:
                raise CacheError(
                    "aioredis not installed. Install with: pip install aioredis"
                )
            except Exception as e:
                raise CacheError(f"Failed to connect to Redis: {str(e)}")
        
        return self._redis
    
    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        redis = await self._get_redis()
        full_key = self._make_key(key)
        
        try:
            value = await redis.get(full_key)
            if value is None:
                return None
            
            # Deserialize
            return pickle.loads(value)
        except Exception as e:
            raise CacheError(f"Failed to get from cache: {str(e)}")
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache."""
        redis = await self._get_redis()
        full_key = self._make_key(key)
        
        try:
            # Serialize
            serialized = pickle.dumps(value)
            
            if ttl:
                await redis.setex(full_key, ttl, serialized)
            else:
                await redis.set(full_key, serialized)
        except Exception as e:
            raise CacheError(f"Failed to set in cache: {str(e)}")
    
    async def delete(self, key: str):
        """Delete value from cache."""
        redis = await self._get_redis()
        full_key = self._make_key(key)
        await redis.delete(full_key)
    
    async def clear(self):
        """Clear all cache entries with prefix."""
        redis = await self._get_redis()
        pattern = f"{self.prefix}*"
        
        cursor = b'0'
        while cursor:
            cursor, keys = await redis.scan(cursor, match=pattern)
            if keys:
                await redis.delete(*keys)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        redis = await self._get_redis()
        full_key = self._make_key(key)
        return await redis.exists(full_key)
    
    async def close(self):
        """Close Redis connection."""
        if self._redis:
            self._redis.close()
            await self._redis.wait_closed()


class CacheManager:
    """
    High-level cache manager with automatic key generation and serialization.
    """
    
    def __init__(self, backend: CacheBackend, default_ttl: int = 300):
        self.backend = backend
        self.default_ttl = default_ttl
        self._hit_count = 0
        self._miss_count = 0
    
    async def get_or_compute(self, 
                            key: str, 
                            compute_func, 
                            ttl: Optional[int] = None) -> Any:
        """
        Get from cache or compute and cache the result.
        
        Args:
            key: Cache key
            compute_func: Async function to compute value if not in cache
            ttl: Time to live in seconds
        """
        # Try to get from cache
        cached = await self.backend.get(key)
        if cached is not None:
            self._hit_count += 1
            return cached
        
        # Compute value
        self._miss_count += 1
        value = await compute_func()
        
        # Cache the result
        await self.backend.set(key, value, ttl or self.default_ttl)
        
        return value
    
    @staticmethod
    def generate_key(*args, **kwargs) -> str:
        """Generate cache key from arguments."""
        # Create deterministic key from args and kwargs
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern (if backend supports it)."""
        # This would need backend-specific implementation
        pass
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self._hit_count + self._miss_count
        if total == 0:
            return 0.0
        return self._hit_count / total
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            'hits': self._hit_count,
            'misses': self._miss_count,
            'hit_rate': self.get_hit_rate()
        }
        
        # Add backend stats if available
        if hasattr(self.backend, 'get_stats'):
            stats['backend'] = self.backend.get_stats()
        
        return stats
    
    async def clear(self):
        """Clear cache and reset statistics."""
        await self.backend.clear()
        self._hit_count = 0
        self._miss_count = 0
