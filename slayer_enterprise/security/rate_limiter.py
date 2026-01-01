"""
Enterprise-grade rate limiter with multiple strategies.
Supports token bucket, leaky bucket, and sliding window algorithms.
"""

import time
import asyncio
from typing import Dict, Optional
from collections import deque
from dataclasses import dataclass, field
from enum import Enum

from ..core.exceptions import RateLimitExceeded


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiter."""
    max_requests: int = 100
    window_seconds: int = 60
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    burst_size: Optional[int] = None  # For token bucket


class RateLimiter:
    """
    Thread-safe rate limiter with multiple strategies.
    
    Supports:
    - Token bucket (allows bursts)
    - Sliding window (precise)
    - Fixed window (simple)
    """
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self._locks: Dict[str, asyncio.Lock] = {}
        self._token_buckets: Dict[str, 'TokenBucket'] = {}
        self._sliding_windows: Dict[str, deque] = {}
        self._fixed_windows: Dict[str, Dict] = {}
        
    async def acquire(self, key: str = "default") -> bool:
        """
        Acquire permission to make a request.
        
        Args:
            key: Identifier for rate limit bucket (e.g., user_id, ip_address)
            
        Returns:
            True if request is allowed
            
        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        # Get or create lock for this key
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        
        async with self._locks[key]:
            if self.config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                return await self._token_bucket_acquire(key)
            elif self.config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                return await self._sliding_window_acquire(key)
            else:  # FIXED_WINDOW
                return await self._fixed_window_acquire(key)
    
    async def _token_bucket_acquire(self, key: str) -> bool:
        """Token bucket algorithm."""
        if key not in self._token_buckets:
            burst_size = self.config.burst_size or self.config.max_requests
            refill_rate = self.config.max_requests / self.config.window_seconds
            self._token_buckets[key] = TokenBucket(burst_size, refill_rate)
        
        bucket = self._token_buckets[key]
        if bucket.consume():
            return True
        else:
            retry_after = bucket.time_until_token()
            raise RateLimitExceeded(
                f"Rate limit exceeded for key '{key}'",
                retry_after=int(retry_after),
                details={'strategy': 'token_bucket', 'key': key}
            )
    
    async def _sliding_window_acquire(self, key: str) -> bool:
        """Sliding window algorithm."""
        if key not in self._sliding_windows:
            self._sliding_windows[key] = deque()
        
        window = self._sliding_windows[key]
        now = time.time()
        cutoff = now - self.config.window_seconds
        
        # Remove old requests
        while window and window[0] < cutoff:
            window.popleft()
        
        # Check if we can add new request
        if len(window) < self.config.max_requests:
            window.append(now)
            return True
        else:
            retry_after = window[0] + self.config.window_seconds - now
            raise RateLimitExceeded(
                f"Rate limit exceeded for key '{key}'",
                retry_after=int(retry_after),
                details={'strategy': 'sliding_window', 'key': key}
            )
    
    async def _fixed_window_acquire(self, key: str) -> bool:
        """Fixed window algorithm."""
        if key not in self._fixed_windows:
            self._fixed_windows[key] = {'count': 0, 'reset_at': time.time() + self.config.window_seconds}
        
        window = self._fixed_windows[key]
        now = time.time()
        
        # Reset window if expired
        if now >= window['reset_at']:
            window['count'] = 0
            window['reset_at'] = now + self.config.window_seconds
        
        # Check if we can add new request
        if window['count'] < self.config.max_requests:
            window['count'] += 1
            return True
        else:
            retry_after = window['reset_at'] - now
            raise RateLimitExceeded(
                f"Rate limit exceeded for key '{key}'",
                retry_after=int(retry_after),
                details={'strategy': 'fixed_window', 'key': key}
            )
    
    def get_stats(self, key: str = "default") -> Dict:
        """Get rate limit statistics for a key."""
        if self.config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            if key in self._token_buckets:
                bucket = self._token_buckets[key]
                return {
                    'available_tokens': bucket.tokens,
                    'capacity': bucket.capacity,
                    'refill_rate': bucket.refill_rate
                }
        elif self.config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            if key in self._sliding_windows:
                window = self._sliding_windows[key]
                return {
                    'requests_in_window': len(window),
                    'max_requests': self.config.max_requests,
                    'window_seconds': self.config.window_seconds
                }
        else:  # FIXED_WINDOW
            if key in self._fixed_windows:
                window = self._fixed_windows[key]
                return {
                    'requests_in_window': window['count'],
                    'max_requests': self.config.max_requests,
                    'reset_at': window['reset_at']
                }
        
        return {'status': 'No data for key'}
    
    async def reset(self, key: str = "default"):
        """Reset rate limit for a key."""
        self._token_buckets.pop(key, None)
        self._sliding_windows.pop(key, None)
        self._fixed_windows.pop(key, None)


class TokenBucket:
    """Token bucket implementation for burst handling."""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = float(capacity)
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens."""
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def time_until_token(self) -> float:
        """Time until next token is available."""
        self._refill()
        if self.tokens >= 1:
            return 0.0
        tokens_needed = 1.0 - self.tokens
        return tokens_needed / self.refill_rate
