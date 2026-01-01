"""
Enterprise configuration management for SLAYER.
Supports environment variables, config files, and runtime configuration.
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from pathlib import Path
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CacheBackend(Enum):
    """Cache backend types."""
    MEMORY = "memory"
    REDIS = "redis"
    MEMCACHED = "memcached"


@dataclass
class SecurityConfig:
    """Security-related configuration."""
    enable_ssrf_protection: bool = True
    allowed_schemes: List[str] = field(default_factory=lambda: ['http', 'https'])
    blocked_ips: List[str] = field(default_factory=list)
    max_redirects: int = 5
    verify_ssl: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    enable_rate_limiting: bool = True
    rate_limit_requests: int = 1000
    rate_limit_period: int = 60  # seconds
    enable_authentication: bool = False
    auth_token: Optional[str] = None
    api_keys: Dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceConfig:
    """Performance-related configuration."""
    enable_caching: bool = True
    cache_backend: str = CacheBackend.MEMORY.value
    cache_ttl: int = 300  # seconds
    redis_url: Optional[str] = None
    redis_db: int = 0
    enable_connection_pooling: bool = True
    pool_connections: int = 100
    pool_maxsize: int = 100
    max_concurrent_requests: int = 100
    request_timeout: int = 30
    connect_timeout: int = 10
    read_timeout: int = 30
    enable_compression: bool = True
    enable_http2: bool = True
    enable_retry: bool = True
    max_retries: int = 3
    retry_backoff_factor: float = 0.5
    retry_statuses: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])


@dataclass
class ResilienceConfig:
    """Resilience patterns configuration."""
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60  # seconds
    circuit_breaker_half_open_max_calls: int = 3
    enable_bulkhead: bool = True
    bulkhead_max_concurrent: int = 50


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    enable_metrics: bool = True
    metrics_port: int = 9090
    enable_prometheus: bool = True
    enable_audit_logging: bool = True
    audit_log_path: str = "/var/log/slayer/audit.log"
    enable_performance_logging: bool = True
    log_level: str = LogLevel.INFO.value
    log_format: str = "json"
    enable_distributed_tracing: bool = False
    jaeger_endpoint: Optional[str] = None


@dataclass
class PluginConfig:
    """Plugin system configuration."""
    enable_plugins: bool = True
    plugin_dir: str = "./plugins"
    auto_load_plugins: bool = True
    allowed_plugins: List[str] = field(default_factory=list)


@dataclass
class SlayerConfig:
    """
    Master configuration for SLAYER Enterprise.
    
    This class consolidates all configuration aspects of the system,
    providing a single source of truth for operational parameters.
    """
    
    # Core settings
    app_name: str = "SLAYER Enterprise"
    version: str = "3.0.0"
    environment: str = "production"  # development, staging, production
    debug: bool = False
    
    # Component configurations
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    resilience: ResilienceConfig = field(default_factory=ResilienceConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    plugins: PluginConfig = field(default_factory=PluginConfig)
    
    # Custom headers and user agents
    default_headers: Dict[str, str] = field(default_factory=dict)
    user_agents: List[str] = field(default_factory=lambda: [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ])
    
    @classmethod
    def from_file(cls, file_path: str) -> 'SlayerConfig':
        """Load configuration from JSON file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SlayerConfig':
        """Create configuration from dictionary."""
        # Extract nested configs
        security_data = data.pop('security', {})
        performance_data = data.pop('performance', {})
        resilience_data = data.pop('resilience', {})
        monitoring_data = data.pop('monitoring', {})
        plugins_data = data.pop('plugins', {})
        
        return cls(
            security=SecurityConfig(**security_data),
            performance=PerformanceConfig(**performance_data),
            resilience=ResilienceConfig(**resilience_data),
            monitoring=MonitoringConfig(**monitoring_data),
            plugins=PluginConfig(**plugins_data),
            **data
        )
    
    @classmethod
    def from_env(cls) -> 'SlayerConfig':
        """Load configuration from environment variables."""
        config = cls()
        
        # Core settings
        config.environment = os.getenv('SLAYER_ENV', config.environment)
        config.debug = os.getenv('SLAYER_DEBUG', 'false').lower() == 'true'
        
        # Security
        config.security.enable_ssrf_protection = os.getenv('SLAYER_SSRF_PROTECTION', 'true').lower() == 'true'
        config.security.verify_ssl = os.getenv('SLAYER_VERIFY_SSL', 'true').lower() == 'true'
        config.security.auth_token = os.getenv('SLAYER_AUTH_TOKEN')
        
        # Performance
        config.performance.redis_url = os.getenv('SLAYER_REDIS_URL')
        config.performance.cache_ttl = int(os.getenv('SLAYER_CACHE_TTL', str(config.performance.cache_ttl)))
        config.performance.request_timeout = int(os.getenv('SLAYER_REQUEST_TIMEOUT', str(config.performance.request_timeout)))
        
        # Monitoring
        config.monitoring.log_level = os.getenv('SLAYER_LOG_LEVEL', config.monitoring.log_level)
        config.monitoring.metrics_port = int(os.getenv('SLAYER_METRICS_PORT', str(config.monitoring.metrics_port)))
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    def to_json(self, file_path: Optional[str] = None) -> str:
        """Convert configuration to JSON."""
        data = self.to_dict()
        json_str = json.dumps(data, indent=2)
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(json_str)
        
        return json_str
    
    def validate(self) -> bool:
        """Validate configuration."""
        errors = []
        
        # Validate timeouts
        if self.performance.request_timeout <= 0:
            errors.append("request_timeout must be positive")
        
        # Validate rate limiting
        if self.security.enable_rate_limiting:
            if self.security.rate_limit_requests <= 0:
                errors.append("rate_limit_requests must be positive")
            if self.security.rate_limit_period <= 0:
                errors.append("rate_limit_period must be positive")
        
        # Validate circuit breaker
        if self.resilience.enable_circuit_breaker:
            if self.resilience.circuit_breaker_threshold <= 0:
                errors.append("circuit_breaker_threshold must be positive")
        
        # Validate cache
        if self.performance.enable_caching:
            if self.performance.cache_backend == CacheBackend.REDIS.value:
                if not self.performance.redis_url:
                    errors.append("redis_url required when using Redis cache")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        return True


def load_config(
    config_file: Optional[str] = None,
    use_env: bool = True
) -> SlayerConfig:
    """
    Load configuration with precedence:
    1. Config file (if provided)
    2. Environment variables (if use_env=True)
    3. Defaults
    """
    if config_file:
        config = SlayerConfig.from_file(config_file)
    elif use_env:
        config = SlayerConfig.from_env()
    else:
        config = SlayerConfig()
    
    config.validate()
    return config
