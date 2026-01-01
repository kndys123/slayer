"""
Comprehensive test suite for SLAYER Enterprise.
"""

import pytest
import asyncio
from aioresponses import aioresponses

from slayer_enterprise import SlayerClient
from slayer_enterprise.core.config import SlayerConfig
from slayer_enterprise.core.exceptions import *
from slayer_enterprise.security.rate_limiter import RateLimiter, RateLimitConfig
from slayer_enterprise.security.ssrf_protection import SSRFProtection
from slayer_enterprise.performance.cache import MemoryCache, CacheManager
from slayer_enterprise.performance.circuit_breaker import CircuitBreaker, CircuitBreakerConfig


@pytest.fixture
def config():
    """Create test configuration."""
    return SlayerConfig(
        debug=True,
        environment='test'
    )


@pytest.fixture
async def client(config):
    """Create test client."""
    async with SlayerClient(config) as c:
        yield c


class TestSlayerClient:
    """Test main client functionality."""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, config):
        """Test client initialization."""
        async with SlayerClient(config) as client:
            assert client._initialized
            assert client.config.environment == 'test'
    
    @pytest.mark.asyncio
    async def test_get_request(self, client):
        """Test GET request."""
        with aioresponses() as m:
            m.get('https://api.example.com/test', status=200, payload={'result': 'ok'})
            
            response = await client.get('https://api.example.com/test')
            assert response.status == 200
    
    @pytest.mark.asyncio
    async def test_post_request(self, client):
        """Test POST request."""
        with aioresponses() as m:
            m.post('https://api.example.com/test', status=201, payload={'created': True})
            
            response = await client.post(
                'https://api.example.com/test',
                json={'data': 'test'}
            )
            assert response.status == 201
    
    @pytest.mark.asyncio
    async def test_batch_requests(self, client):
        """Test batch requests."""
        urls = [
            'https://api.example.com/1',
            'https://api.example.com/2',
            'https://api.example.com/3'
        ]
        
        with aioresponses() as m:
            for url in urls:
                m.get(url, status=200, payload={'ok': True})
            
            responses = await client.batch_get(urls)
            assert len(responses) == 3
            assert all(r.status == 200 for r in responses if not isinstance(r, Exception))
    
    @pytest.mark.asyncio
    async def test_get_stats(self, client):
        """Test statistics retrieval."""
        stats = client.get_stats()
        
        assert 'version' in stats
        assert 'environment' in stats
        assert stats['environment'] == 'test'
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check."""
        health = client.health_check()
        
        assert 'status' in health
        assert health['status'] == 'healthy'


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    @pytest.mark.asyncio
    async def test_token_bucket_allow(self):
        """Test token bucket allows requests."""
        config = RateLimitConfig(max_requests=10, window_seconds=60)
        limiter = RateLimiter(config)
        
        # Should allow first request
        assert await limiter.acquire('test')
    
    @pytest.mark.asyncio
    async def test_token_bucket_exceed(self):
        """Test token bucket blocks when exceeded."""
        config = RateLimitConfig(max_requests=2, window_seconds=60)
        limiter = RateLimiter(config)
        
        # First two should pass
        await limiter.acquire('test')
        await limiter.acquire('test')
        
        # Third should fail
        with pytest.raises(RateLimitExceeded):
            await limiter.acquire('test')
    
    @pytest.mark.asyncio
    async def test_rate_limit_stats(self):
        """Test rate limiter statistics."""
        config = RateLimitConfig(max_requests=10, window_seconds=60)
        limiter = RateLimiter(config)
        
        await limiter.acquire('test')
        stats = limiter.get_stats('test')
        
        assert 'available_tokens' in stats or 'requests_in_window' in stats


class TestSSRFProtection:
    """Test SSRF protection."""
    
    def test_valid_url(self):
        """Test valid URL passes."""
        ssrf = SSRFProtection()
        assert ssrf.validate_url('https://example.com')
    
    def test_private_ip_blocked(self):
        """Test private IP is blocked."""
        ssrf = SSRFProtection()
        
        with pytest.raises(SSRFDetected):
            ssrf.validate_url('http://192.168.1.1')
    
    def test_localhost_blocked(self):
        """Test localhost is blocked."""
        ssrf = SSRFProtection()
        
        with pytest.raises(SSRFDetected):
            ssrf.validate_url('http://localhost')
    
    def test_metadata_endpoint_blocked(self):
        """Test cloud metadata endpoint is blocked."""
        ssrf = SSRFProtection()
        
        with pytest.raises(SSRFDetected):
            ssrf.validate_url('http://169.254.169.254')
    
    def test_invalid_scheme(self):
        """Test invalid scheme is blocked."""
        ssrf = SSRFProtection(allowed_schemes=['http', 'https'])
        
        with pytest.raises(SSRFDetected):
            ssrf.validate_url('file:///etc/passwd')


class TestCache:
    """Test caching functionality."""
    
    @pytest.mark.asyncio
    async def test_memory_cache_set_get(self):
        """Test memory cache set and get."""
        cache = MemoryCache()
        
        await cache.set('key1', 'value1')
        value = await cache.get('key1')
        
        assert value == 'value1'
    
    @pytest.mark.asyncio
    async def test_memory_cache_ttl(self):
        """Test memory cache TTL."""
        cache = MemoryCache()
        
        await cache.set('key1', 'value1', ttl=1)
        await asyncio.sleep(1.1)
        
        value = await cache.get('key1')
        assert value is None
    
    @pytest.mark.asyncio
    async def test_memory_cache_eviction(self):
        """Test memory cache LRU eviction."""
        cache = MemoryCache(max_size=2)
        
        await cache.set('key1', 'value1')
        await cache.set('key2', 'value2')
        await cache.set('key3', 'value3')  # Should evict key1
        
        assert await cache.get('key1') is None
        assert await cache.get('key2') == 'value2'
        assert await cache.get('key3') == 'value3'
    
    @pytest.mark.asyncio
    async def test_cache_manager_get_or_compute(self):
        """Test cache manager get_or_compute."""
        cache = MemoryCache()
        manager = CacheManager(cache, default_ttl=60)
        
        call_count = 0
        
        async def compute():
            nonlocal call_count
            call_count += 1
            return 'computed_value'
        
        # First call should compute
        value1 = await manager.get_or_compute('test_key', compute)
        assert value1 == 'computed_value'
        assert call_count == 1
        
        # Second call should use cache
        value2 = await manager.get_or_compute('test_key', compute)
        assert value2 == 'computed_value'
        assert call_count == 1  # Should not have called compute again


class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    @pytest.mark.asyncio
    async def test_circuit_closed_allows_requests(self):
        """Test circuit in closed state allows requests."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker(config)
        
        async def successful_func():
            return "success"
        
        result = await breaker.call(successful_func)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_circuit_opens_after_failures(self):
        """Test circuit opens after threshold failures."""
        config = CircuitBreakerConfig(failure_threshold=2, timeout=1)
        breaker = CircuitBreaker(config)
        
        async def failing_func():
            raise Exception("Failed")
        
        # Fail twice to open circuit
        with pytest.raises(Exception):
            await breaker.call(failing_func)
        
        with pytest.raises(Exception):
            await breaker.call(failing_func)
        
        # Next call should fail fast with CircuitBreakerOpen
        with pytest.raises(CircuitBreakerOpen):
            await breaker.call(failing_func)
    
    @pytest.mark.asyncio
    async def test_circuit_half_open_recovery(self):
        """Test circuit recovery through half-open state."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            timeout=0.1,  # Short timeout for testing
            success_threshold=1
        )
        breaker = CircuitBreaker(config)
        
        async def failing_func():
            raise Exception("Failed")
        
        async def successful_func():
            return "success"
        
        # Open the circuit
        with pytest.raises(Exception):
            await breaker.call(failing_func)
        
        # Wait for timeout
        await asyncio.sleep(0.2)
        
        # Should be in half-open now, success should close it
        result = await breaker.call(successful_func)
        assert result == "success"
        assert breaker.get_state().value == "closed"


class TestValidation:
    """Test input validation."""
    
    def test_valid_url_validation(self):
        """Test valid URL passes validation."""
        from slayer_enterprise.security.validator import RequestValidator
        
        validator = RequestValidator()
        assert validator.validate_url('https://example.com/api')
    
    def test_invalid_url_validation(self):
        """Test invalid URL fails validation."""
        from slayer_enterprise.security.validator import RequestValidator
        
        validator = RequestValidator()
        
        with pytest.raises(ValidationError):
            validator.validate_url('not a url')
    
    def test_header_validation(self):
        """Test header validation."""
        from slayer_enterprise.security.validator import RequestValidator
        
        validator = RequestValidator()
        
        # Valid headers
        assert validator.validate_headers({'Content-Type': 'application/json'})
        
        # Invalid headers with CRLF
        with pytest.raises(ValidationError):
            validator.validate_headers({'Bad-Header': 'value\r\nInjection: here'})


# Performance and stress tests
class TestPerformance:
    """Performance and load testing."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        with aioresponses() as m:
            url = 'https://api.example.com/test'
            for _ in range(100):
                m.get(url, status=200, payload={'ok': True})
            
            tasks = [client.get(url) for _ in range(100)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = [r for r in responses if not isinstance(r, Exception)]
            assert len(successful) >= 90  # At least 90% success rate


# Configuration tests
class TestConfiguration:
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = SlayerConfig()
        
        assert config.version == "3.0.0"
        assert config.security.enable_ssrf_protection
        assert config.performance.enable_caching
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = SlayerConfig()
        assert config.validate()
        
        # Test invalid configuration
        config.performance.request_timeout = -1
        with pytest.raises(ValueError):
            config.validate()
    
    def test_config_to_dict(self):
        """Test configuration serialization."""
        config = SlayerConfig()
        data = config.to_dict()
        
        assert isinstance(data, dict)
        assert 'version' in data
        assert 'security' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=slayer_enterprise'])
