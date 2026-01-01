"""
SLAYER Enterprise Client - Main HTTP client with all enterprise features.
"""

import asyncio
import time
import uuid
from typing import Optional, Dict, Any, List, Callable
from urllib.parse import urlparse
import random

import aiohttp

from .config import SlayerConfig
from .session_manager import SessionManager
from .request_builder import RequestBuilder, HTTPMethod
from .exceptions import *

from ..security.validator import RequestValidator, ResponseValidator
from ..security.ssrf_protection import SSRFProtection
from ..security.rate_limiter import RateLimiter, RateLimitConfig
from ..security.auth import AuthenticationManager

from ..performance.cache import CacheManager, MemoryCache, RedisCache
from ..performance.circuit_breaker import CircuitBreakerManager, CircuitBreakerConfig
from ..performance.connection_pool import ConnectionPoolManager

from ..monitoring.metrics import MetricsCollector
from ..monitoring.logger import StructuredLogger, AuditLogger
from ..monitoring.tracer import RequestTracer


class SlayerClient:
    """
    Enterprise-grade HTTP client with advanced features:
    
    - Async/await with aiohttp for high performance
    - Connection pooling and session management
    - Multi-level caching (memory, Redis)
    - Circuit breakers for resilience
    - Rate limiting
    - SSRF protection and input validation
    - Comprehensive metrics and monitoring
    - Audit logging for compliance
    - Distributed tracing
    - Retry logic with exponential backoff
    - Plugin/middleware system
    """
    
    def __init__(self, config: Optional[SlayerConfig] = None):
        """
        Initialize SLAYER client.
        
        Args:
            config: Configuration object. If None, loads from environment.
        """
        self.config = config or SlayerConfig.from_env()
        self.config.validate()
        
        # Core components
        self.session_manager = SessionManager(self.config)
        self._initialized = False
        
        # Security components
        self.request_validator = RequestValidator(strict_mode=True)
        self.response_validator = ResponseValidator()
        
        if self.config.security.enable_ssrf_protection:
            self.ssrf_protection = SSRFProtection(
                allowed_schemes=self.config.security.allowed_schemes,
                enable_dns_resolution=True
            )
        else:
            self.ssrf_protection = None
        
        if self.config.security.enable_rate_limiting:
            rate_config = RateLimitConfig(
                max_requests=self.config.security.rate_limit_requests,
                window_seconds=self.config.security.rate_limit_period
            )
            self.rate_limiter = RateLimiter(rate_config)
        else:
            self.rate_limiter = None
        
        self.auth_manager = AuthenticationManager()
        
        # Performance components
        if self.config.performance.enable_caching:
            if self.config.performance.cache_backend == "redis" and self.config.performance.redis_url:
                backend = RedisCache(
                    self.config.performance.redis_url,
                    self.config.performance.redis_db
                )
            else:
                backend = MemoryCache(max_size=1000)
            
            self.cache_manager = CacheManager(
                backend=backend,
                default_ttl=self.config.performance.cache_ttl
            )
        else:
            self.cache_manager = None
        
        if self.config.resilience.enable_circuit_breaker:
            cb_config = CircuitBreakerConfig(
                failure_threshold=self.config.resilience.circuit_breaker_threshold,
                timeout=self.config.resilience.circuit_breaker_timeout,
                half_open_max_calls=self.config.resilience.circuit_breaker_half_open_max_calls
            )
            self.circuit_breaker_manager = CircuitBreakerManager(cb_config)
        else:
            self.circuit_breaker_manager = None
        
        self.connection_pool = ConnectionPoolManager(
            max_connections=self.config.performance.pool_maxsize,
            max_per_host=self.config.performance.pool_connections
        )
        
        # Monitoring components
        if self.config.monitoring.enable_metrics:
            self.metrics = MetricsCollector()
        else:
            self.metrics = None
        
        self.logger = StructuredLogger(
            name="slayer",
            level=self.config.monitoring.log_level
        )
        
        if self.config.monitoring.enable_audit_logging:
            self.audit_logger = AuditLogger(
                log_file=self.config.monitoring.audit_log_path
            )
        else:
            self.audit_logger = None
        
        self.tracer = RequestTracer(service_name=self.config.app_name)
        
        # Middleware/plugins
        self._request_middlewares: List[Callable] = []
        self._response_middlewares: List[Callable] = []
    
    async def initialize(self):
        """Initialize async components."""
        if not self._initialized:
            await self.session_manager.get_session()
            self._initialized = True
            self.logger.info("SLAYER client initialized", 
                           version=self.config.version,
                           environment=self.config.environment)
    
    async def request(self,
                     method: str,
                     url: str,
                     **kwargs) -> aiohttp.ClientResponse:
        """
        Make HTTP request with all enterprise features.
        
        Args:
            method: HTTP method
            url: Target URL
            **kwargs: Additional request parameters
            
        Returns:
            ClientResponse object
        """
        if not self._initialized:
            await self.initialize()
        
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())
        trace_headers = self.tracer.create_trace_headers()
        
        # Merge headers
        headers = kwargs.get('headers', {})
        headers.update(trace_headers)
        kwargs['headers'] = headers
        
        # Add user agent if not present
        if 'User-Agent' not in headers:
            headers['User-Agent'] = random.choice(self.config.user_agents)
        
        # Build request
        builder = (RequestBuilder()
                  .url(url)
                  .method(HTTPMethod(method.upper()))
                  .headers(headers))
        
        request_data = builder.build()
        
        # Security validation
        await self._validate_request(request_data)
        
        # Check rate limit
        if self.rate_limiter:
            await self.rate_limiter.acquire(self._get_rate_limit_key(url))
        
        # Start timing
        start_time = time.time()
        
        if self.metrics:
            await self.metrics.increment_active_requests()
        
        # Audit log request
        if self.audit_logger:
            self.audit_logger.log_request(
                request_id=request_id,
                method=method,
                url=url
            )
        
        try:
            # Execute with circuit breaker if enabled
            if self.circuit_breaker_manager:
                endpoint_key = urlparse(url).netloc
                response = await self.circuit_breaker_manager.call(
                    endpoint_key,
                    self._execute_request,
                    method,
                    url,
                    **kwargs
                )
            else:
                response = await self._execute_request(method, url, **kwargs)
            
            # Record metrics
            duration = time.time() - start_time
            
            if self.metrics:
                await self.metrics.record_request(
                    method=method,
                    endpoint=urlparse(url).path,
                    status_code=response.status,
                    duration_seconds=duration
                )
                await self.metrics.decrement_active_requests()
            
            # Audit log response
            if self.audit_logger:
                self.audit_logger.log_response(
                    request_id=request_id,
                    status_code=response.status,
                    duration_ms=duration * 1000,
                    response_size=len(await response.read())
                )
            
            self.logger.debug(
                f"Request completed: {method} {url}",
                request_id=request_id,
                status=response.status,
                duration_ms=duration * 1000
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            if self.metrics:
                await self.metrics.record_error(type(e).__name__)
                await self.metrics.decrement_active_requests()
            
            if self.audit_logger:
                self.audit_logger.log_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    request_id=request_id
                )
            
            self.logger.error(
                f"Request failed: {method} {url}",
                request_id=request_id,
                error=str(e),
                duration_ms=duration * 1000
            )
            
            raise
    
    async def _execute_request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Execute the actual HTTP request with retry logic."""
        session = await self.session_manager.get_session()
        self.session_manager.increment_request_count()
        
        # Retry logic
        max_retries = self.config.performance.max_retries if self.config.performance.enable_retry else 1
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                response = await session.request(method, url, **kwargs)
                
                # Check if we should retry based on status code
                if attempt < max_retries - 1 and response.status in self.config.performance.retry_statuses:
                    retry_after = self._calculate_retry_delay(attempt)
                    self.logger.warning(
                        f"Retrying request after {retry_after}s",
                        attempt=attempt + 1,
                        status=response.status
                    )
                    await asyncio.sleep(retry_after)
                    continue
                
                return response
                
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                if attempt < max_retries - 1:
                    retry_after = self._calculate_retry_delay(attempt)
                    self.logger.warning(
                        f"Retrying request after {retry_after}s",
                        attempt=attempt + 1,
                        error=str(e)
                    )
                    await asyncio.sleep(retry_after)
                else:
                    raise
        
        if last_exception:
            raise last_exception
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff."""
        base_delay = self.config.performance.retry_backoff_factor
        max_delay = 60
        delay = min(base_delay * (2 ** attempt), max_delay)
        # Add jitter
        jitter = random.uniform(0, 0.1 * delay)
        return delay + jitter
    
    async def _validate_request(self, request: Dict[str, Any]):
        """Validate request before execution."""
        url = request['url']
        
        # SSRF protection
        if self.ssrf_protection:
            self.ssrf_protection.validate_url(url)
        
        # Input validation
        self.request_validator.validate_request(request)
    
    def _get_rate_limit_key(self, url: str) -> str:
        """Generate rate limit key from URL."""
        parsed = urlparse(url)
        return f"{parsed.netloc}{parsed.path}"
    
    # Convenience methods
    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Perform GET request."""
        return await self.request('GET', url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Perform POST request."""
        return await self.request('POST', url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Perform PUT request."""
        return await self.request('PUT', url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Perform DELETE request."""
        return await self.request('DELETE', url, **kwargs)
    
    async def patch(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Perform PATCH request."""
        return await self.request('PATCH', url, **kwargs)
    
    async def head(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Perform HEAD request."""
        return await self.request('HEAD', url, **kwargs)
    
    # Batch operations
    async def batch_get(self, urls: List[str], **kwargs) -> List[aiohttp.ClientResponse]:
        """Perform multiple GET requests concurrently."""
        tasks = [self.get(url, **kwargs) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    # Middleware
    def add_request_middleware(self, middleware: Callable):
        """Add request middleware."""
        self._request_middlewares.append(middleware)
    
    def add_response_middleware(self, middleware: Callable):
        """Add response middleware."""
        self._response_middlewares.append(middleware)
    
    # Statistics and health
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive client statistics."""
        stats = {
            'version': self.config.version,
            'environment': self.config.environment,
            'session': self.session_manager.get_stats() if self._initialized else {},
            'connection_pool': self.connection_pool.get_stats(),
        }
        
        if self.metrics:
            stats['metrics'] = self.metrics.get_metrics()
        
        if self.cache_manager:
            stats['cache'] = self.cache_manager.get_stats()
        
        if self.rate_limiter:
            stats['rate_limiter'] = self.rate_limiter.get_stats()
        
        if self.circuit_breaker_manager:
            stats['circuit_breakers'] = self.circuit_breaker_manager.get_all_stats()
        
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return {
            'status': 'healthy' if self._initialized else 'not_initialized',
            'timestamp': time.time(),
            'version': self.config.version
        }
    
    async def close(self):
        """Close client and cleanup resources."""
        await self.session_manager.close()
        
        if self.cache_manager and hasattr(self.cache_manager.backend, 'close'):
            await self.cache_manager.backend.close()
        
        self.logger.info("SLAYER client closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
