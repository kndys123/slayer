"""
Circuit Breaker pattern implementation for resilience.
Prevents cascading failures by failing fast when a service is unhealthy.
"""

import asyncio
import time
from enum import Enum
from typing import Optional, Callable, Any
from dataclasses import dataclass

from ..core.exceptions import CircuitBreakerOpen


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes to close from half-open
    timeout: int = 60  # Seconds before trying half-open
    half_open_max_calls: int = 3  # Max concurrent calls in half-open


class CircuitBreaker:
    """
    Circuit breaker implementation.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests fail immediately
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Async function to execute
            *args, **kwargs: Arguments for the function
            
        Returns:
            Result from function
            
        Raises:
            CircuitBreakerOpen: If circuit is open
        """
        async with self._lock:
            # Check if we should transition to half-open
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                else:
                    raise CircuitBreakerOpen(
                        "Circuit breaker is open",
                        failure_count=self.failure_count
                    )
            
            # Check if we're at capacity in half-open
            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.config.half_open_max_calls:
                    raise CircuitBreakerOpen(
                        "Circuit breaker is half-open and at capacity",
                        failure_count=self.failure_count
                    )
                self.half_open_calls += 1
        
        # Execute the function
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise e
    
    async def _on_success(self):
        """Handle successful call."""
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self._reset()
            else:
                # Reset failure count on success
                self.failure_count = 0
    
    async def _on_failure(self):
        """Handle failed call."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                # Go back to open on any failure in half-open
                self.state = CircuitState.OPEN
                self.success_count = 0
            elif self.failure_count >= self.config.failure_threshold:
                # Open the circuit
                self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try half-open state."""
        if self.last_failure_time is None:
            return True
        
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.config.timeout
    
    def _reset(self):
        """Reset circuit breaker to closed state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
    
    async def reset_manually(self):
        """Manually reset the circuit breaker."""
        async with self._lock:
            self._reset()
    
    def get_state(self) -> CircuitState:
        """Get current state."""
        return self.state
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time
        }


class CircuitBreakerManager:
    """Manages multiple circuit breakers by endpoint."""
    
    def __init__(self, default_config: CircuitBreakerConfig):
        self.default_config = default_config
        self._breakers: dict[str, CircuitBreaker] = {}
    
    def get_breaker(self, key: str) -> CircuitBreaker:
        """Get or create circuit breaker for a key."""
        if key not in self._breakers:
            self._breakers[key] = CircuitBreaker(self.default_config)
        return self._breakers[key]
    
    async def call(self, key: str, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker for specific key."""
        breaker = self.get_breaker(key)
        return await breaker.call(func, *args, **kwargs)
    
    def get_all_stats(self) -> dict:
        """Get statistics for all circuit breakers."""
        return {
            key: breaker.get_stats()
            for key, breaker in self._breakers.items()
        }
