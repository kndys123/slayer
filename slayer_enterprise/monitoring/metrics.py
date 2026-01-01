"""
Metrics collection and Prometheus export.
Tracks performance, errors, and system health.
"""

import time
from typing import Dict, Any, List, Optional
from collections import defaultdict
from dataclasses import dataclass, field
import asyncio


@dataclass
class MetricValue:
    """Represents a metric value."""
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class MetricsCollector:
    """
    Collects application metrics.
    
    Metrics tracked:
    - Request count by status, method, endpoint
    - Response time (histogram)
    - Error count by type
    - Cache hit/miss rate
    - Circuit breaker state changes
    - Active connections
    """
    
    def __init__(self):
        # Counters
        self._request_count: Dict[tuple, int] = defaultdict(int)
        self._error_count: Dict[str, int] = defaultdict(int)
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Gauges
        self._active_requests = 0
        self._active_connections = 0
        
        # Histograms (for percentiles)
        self._response_times: List[float] = []
        self._max_histogram_size = 10000
        
        # Summary stats
        self._start_time = time.time()
        self._lock = asyncio.Lock()
    
    async def record_request(self, 
                            method: str, 
                            endpoint: str, 
                            status_code: int,
                            duration_seconds: float):
        """Record a completed request."""
        async with self._lock:
            # Increment counter
            key = (method, endpoint, status_code)
            self._request_count[key] += 1
            
            # Record response time
            self._response_times.append(duration_seconds)
            if len(self._response_times) > self._max_histogram_size:
                # Keep only recent measurements
                self._response_times = self._response_times[-self._max_histogram_size:]
    
    async def record_error(self, error_type: str):
        """Record an error."""
        async with self._lock:
            self._error_count[error_type] += 1
    
    async def increment_active_requests(self):
        """Increment active requests counter."""
        async with self._lock:
            self._active_requests += 1
    
    async def decrement_active_requests(self):
        """Decrement active requests counter."""
        async with self._lock:
            self._active_requests = max(0, self._active_requests - 1)
    
    async def record_cache_hit(self):
        """Record cache hit."""
        async with self._lock:
            self._cache_hits += 1
    
    async def record_cache_miss(self):
        """Record cache miss."""
        async with self._lock:
            self._cache_misses += 1
    
    def set_active_connections(self, count: int):
        """Set active connections gauge."""
        self._active_connections = count
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        uptime = time.time() - self._start_time
        
        # Calculate percentiles
        percentiles = self._calculate_percentiles()
        
        # Total requests
        total_requests = sum(self._request_count.values())
        
        # Calculate rates
        requests_per_second = total_requests / uptime if uptime > 0 else 0
        
        # Cache stats
        total_cache_ops = self._cache_hits + self._cache_misses
        cache_hit_rate = self._cache_hits / total_cache_ops if total_cache_ops > 0 else 0
        
        return {
            'uptime_seconds': uptime,
            'total_requests': total_requests,
            'requests_per_second': requests_per_second,
            'active_requests': self._active_requests,
            'active_connections': self._active_connections,
            'requests_by_status': self._group_by_status(),
            'errors': dict(self._error_count),
            'response_time_percentiles': percentiles,
            'cache': {
                'hits': self._cache_hits,
                'misses': self._cache_misses,
                'hit_rate': cache_hit_rate
            }
        }
    
    def _calculate_percentiles(self) -> Dict[str, float]:
        """Calculate response time percentiles."""
        if not self._response_times:
            return {'p50': 0, 'p95': 0, 'p99': 0, 'mean': 0, 'max': 0}
        
        sorted_times = sorted(self._response_times)
        n = len(sorted_times)
        
        return {
            'mean': sum(sorted_times) / n,
            'p50': sorted_times[int(n * 0.50)],
            'p95': sorted_times[int(n * 0.95)],
            'p99': sorted_times[int(n * 0.99)],
            'max': sorted_times[-1]
        }
    
    def _group_by_status(self) -> Dict[str, int]:
        """Group request counts by status code."""
        by_status = defaultdict(int)
        for (method, endpoint, status), count in self._request_count.items():
            by_status[str(status)] += count
        return dict(by_status)
    
    async def reset(self):
        """Reset all metrics."""
        async with self._lock:
            self._request_count.clear()
            self._error_count.clear()
            self._response_times.clear()
            self._cache_hits = 0
            self._cache_misses = 0
            self._active_requests = 0
            self._start_time = time.time()


class PrometheusExporter:
    """
    Exports metrics in Prometheus format.
    """
    
    def __init__(self, collector: MetricsCollector, namespace: str = "slayer"):
        self.collector = collector
        self.namespace = namespace
    
    def export(self) -> str:
        """Export metrics in Prometheus text format."""
        metrics = self.collector.get_metrics()
        lines = []
        
        # Total requests counter
        lines.append(f"# HELP {self.namespace}_requests_total Total number of HTTP requests")
        lines.append(f"# TYPE {self.namespace}_requests_total counter")
        lines.append(f"{self.namespace}_requests_total {metrics['total_requests']}")
        lines.append("")
        
        # Active requests gauge
        lines.append(f"# HELP {self.namespace}_active_requests Number of active requests")
        lines.append(f"# TYPE {self.namespace}_active_requests gauge")
        lines.append(f"{self.namespace}_active_requests {metrics['active_requests']}")
        lines.append("")
        
        # Response time percentiles
        lines.append(f"# HELP {self.namespace}_response_time_seconds Response time in seconds")
        lines.append(f"# TYPE {self.namespace}_response_time_seconds summary")
        for percentile, value in metrics['response_time_percentiles'].items():
            quantile = percentile.replace('p', '0.')
            if percentile == 'mean':
                continue
            lines.append(f'{self.namespace}_response_time_seconds{{quantile="{quantile}"}} {value}')
        lines.append("")
        
        # Cache metrics
        lines.append(f"# HELP {self.namespace}_cache_hits_total Total cache hits")
        lines.append(f"# TYPE {self.namespace}_cache_hits_total counter")
        lines.append(f"{self.namespace}_cache_hits_total {metrics['cache']['hits']}")
        lines.append("")
        
        lines.append(f"# HELP {self.namespace}_cache_misses_total Total cache misses")
        lines.append(f"# TYPE {self.namespace}_cache_misses_total counter")
        lines.append(f"{self.namespace}_cache_misses_total {metrics['cache']['misses']}")
        lines.append("")
        
        # Error counters
        lines.append(f"# HELP {self.namespace}_errors_total Total errors by type")
        lines.append(f"# TYPE {self.namespace}_errors_total counter")
        for error_type, count in metrics['errors'].items():
            lines.append(f'{self.namespace}_errors_total{{type="{error_type}"}} {count}')
        lines.append("")
        
        return "\n".join(lines)
