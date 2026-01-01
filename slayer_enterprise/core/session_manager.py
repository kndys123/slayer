"""
Advanced session management with connection pooling and lifecycle management.
Implements the Factory pattern for session creation.
"""

import asyncio
import aiohttp
import ssl
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import certifi

from .config import SlayerConfig
from .exceptions import ConfigurationError


class SessionManager:
    """
    Manages HTTP client sessions with advanced features:
    - Connection pooling
    - Automatic session renewal
    - SSL/TLS configuration
    - Custom connector settings
    """
    
    def __init__(self, config: SlayerConfig):
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._connector: Optional[aiohttp.TCPConnector] = None
        self._created_at: Optional[datetime] = None
        self._request_count: int = 0
        self._lock = asyncio.Lock()
        
    async def get_session(self) -> aiohttp.ClientSession:
        """
        Get or create HTTP session.
        Implements lazy initialization and automatic renewal.
        """
        async with self._lock:
            if self._should_renew_session():
                await self._create_new_session()
            
            return self._session
    
    def _should_renew_session(self) -> bool:
        """Check if session should be renewed."""
        if self._session is None or self._session.closed:
            return True
        
        # Renew after 1 hour or 10000 requests
        if self._created_at:
            age = datetime.now() - self._created_at
            if age > timedelta(hours=1):
                return True
        
        if self._request_count > 10000:
            return True
        
        return False
    
    async def _create_new_session(self):
        """Create a new HTTP session with optimized settings."""
        # Close existing session
        if self._session and not self._session.closed:
            await self._session.close()
        
        # Create SSL context
        ssl_context = self._create_ssl_context()
        
        # Create connector with connection pooling
        self._connector = aiohttp.TCPConnector(
            limit=self.config.performance.pool_maxsize,
            limit_per_host=self.config.performance.pool_connections,
            ttl_dns_cache=300,
            ssl=ssl_context,
            enable_cleanup_closed=True,
            force_close=False,  # Keep connections alive
            keepalive_timeout=30
        )
        
        # Create timeout configuration
        timeout = aiohttp.ClientTimeout(
            total=self.config.performance.request_timeout,
            connect=self.config.performance.connect_timeout,
            sock_read=self.config.performance.read_timeout
        )
        
        # Build headers
        headers = self._build_default_headers()
        
        # Create session
        self._session = aiohttp.ClientSession(
            connector=self._connector,
            timeout=timeout,
            headers=headers,
            trust_env=True,  # Respect system proxy settings
            auto_decompress=self.config.performance.enable_compression,
            raise_for_status=False  # Handle status codes manually
        )
        
        self._created_at = datetime.now()
        self._request_count = 0
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context with security settings."""
        if not self.config.security.verify_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            return ssl_context
        
        # Create secure SSL context
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        # Load custom certificates if provided
        if self.config.security.ssl_cert_path and self.config.security.ssl_key_path:
            try:
                ssl_context.load_cert_chain(
                    self.config.security.ssl_cert_path,
                    self.config.security.ssl_key_path
                )
            except Exception as e:
                raise ConfigurationError(
                    f"Failed to load SSL certificates: {str(e)}",
                    details={'cert': self.config.security.ssl_cert_path}
                )
        
        # Security settings
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        
        return ssl_context
    
    def _build_default_headers(self) -> Dict[str, str]:
        """Build default headers for requests."""
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br' if self.config.performance.enable_compression else 'identity',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }
        
        # Add custom headers from config
        headers.update(self.config.default_headers)
        
        # Add authentication if configured
        if self.config.security.enable_authentication and self.config.security.auth_token:
            headers['Authorization'] = f'Bearer {self.config.security.auth_token}'
        
        return headers
    
    def increment_request_count(self):
        """Increment request counter."""
        self._request_count += 1
    
    async def close(self):
        """Close session and cleanup resources."""
        if self._session and not self._session.closed:
            await self._session.close()
        
        if self._connector:
            await self._connector.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return await self.get_session()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        return {
            'session_age_seconds': (datetime.now() - self._created_at).total_seconds() if self._created_at else 0,
            'request_count': self._request_count,
            'is_active': self._session is not None and not self._session.closed,
            'pool_size': self.config.performance.pool_maxsize
        }
