"""
Example: Advanced Configuration
"""

import asyncio
from slayer_enterprise import SlayerClient
from slayer_enterprise.core.config import (
    SlayerConfig,
    SecurityConfig,
    PerformanceConfig,
    MonitoringConfig
)


async def advanced_client():
    """Client with custom configuration."""
    
    # Create custom configuration
    config = SlayerConfig(
        environment='production',
        debug=False,
        
        security=SecurityConfig(
            enable_ssrf_protection=True,
            enable_rate_limiting=True,
            rate_limit_requests=100,
            rate_limit_period=60,
            verify_ssl=True
        ),
        
        performance=PerformanceConfig(
            enable_caching=True,
            cache_backend='memory',
            cache_ttl=300,
            max_concurrent_requests=50,
            request_timeout=30,
            enable_retry=True,
            max_retries=3
        ),
        
        monitoring=MonitoringConfig(
            enable_metrics=True,
            enable_audit_logging=True,
            log_level='INFO'
        )
    )
    
    # Use configured client
    async with SlayerClient(config) as client:
        # Make requests
        for i in range(10):
            response = await client.get(f'https://httpbin.org/uuid')
            print(f"Request {i+1}: {response.status}")
        
        # Show statistics
        stats = client.get_stats()
        print(f"\nStatistics:")
        print(f"- Total requests: {stats['metrics']['total_requests']}")
        print(f"- Cache hit rate: {stats['cache']['hit_rate']:.2%}")
        print(f"- Avg response time: {stats['metrics']['response_time_percentiles']['mean']*1000:.2f}ms")


async def with_redis_cache():
    """Client with Redis cache."""
    
    config = SlayerConfig()
    config.performance.enable_caching = True
    config.performance.cache_backend = 'redis'
    config.performance.redis_url = 'redis://localhost:6379'
    config.performance.cache_ttl = 600  # 10 minutes
    
    async with SlayerClient(config) as client:
        # First request - miss
        response1 = await client.get('https://httpbin.org/uuid')
        print(f"First request: {response1.status}")
        
        # Second request - hit
        response2 = await client.get('https://httpbin.org/uuid')
        print(f"Second request (cached): {response2.status}")
        
        stats = client.get_stats()
        print(f"Cache hit rate: {stats['cache']['hit_rate']:.2%}")


if __name__ == '__main__':
    print("=== Advanced Configuration ===")
    asyncio.run(advanced_client())
    
    print("\n=== Redis Cache Example ===")
    print("(Requires Redis running on localhost:6379)")
    # asyncio.run(with_redis_cache())
