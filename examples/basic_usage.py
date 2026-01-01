"""
Example: Basic Usage of SLAYER Enterprise
"""

import asyncio
from slayer_enterprise import SlayerClient


async def basic_get_request():
    """Simple GET request."""
    async with SlayerClient() as client:
        response = await client.get('https://httpbin.org/get')
        data = await response.json()
        print(f"Response: {data}")


async def post_with_json():
    """POST request with JSON body."""
    async with SlayerClient() as client:
        response = await client.post(
            'https://httpbin.org/post',
            json={'name': 'John', 'email': 'john@example.com'}
        )
        data = await response.json()
        print(f"Created: {data}")


async def batch_requests():
    """Multiple concurrent requests."""
    urls = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/1'
    ]
    
    async with SlayerClient() as client:
        responses = await client.batch_get(urls)
        print(f"Completed {len(responses)} requests")
        
        # Show stats
        stats = client.get_stats()
        print(f"Total requests: {stats['metrics']['total_requests']}")


async def main():
    """Run all examples."""
    print("=== Basic GET Request ===")
    await basic_get_request()
    
    print("\n=== POST with JSON ===")
    await post_with_json()
    
    print("\n=== Batch Requests ===")
    await batch_requests()


if __name__ == '__main__':
    asyncio.run(main())
