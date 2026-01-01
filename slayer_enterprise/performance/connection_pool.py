"""Connection pool management."""

from typing import Dict, Any


class ConnectionPoolManager:
    """
    Manages connection pools for optimal resource usage.
    Wraps aiohttp connector configuration.
    """
    
    def __init__(self, max_connections: int = 100, max_per_host: int = 30):
        self.max_connections = max_connections
        self.max_per_host = max_per_host
        self._active_connections = 0
        self._total_connections_created = 0
    
    def get_config(self) -> Dict[str, Any]:
        """Get connection pool configuration."""
        return {
            'limit': self.max_connections,
            'limit_per_host': self.max_per_host,
        }
    
    def track_connection(self):
        """Track new connection."""
        self._active_connections += 1
        self._total_connections_created += 1
    
    def release_connection(self):
        """Release connection."""
        self._active_connections = max(0, self._active_connections - 1)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        return {
            'active_connections': self._active_connections,
            'max_connections': self.max_connections,
            'total_created': self._total_connections_created,
            'utilization': self._active_connections / self.max_connections if self.max_connections > 0 else 0
        }
