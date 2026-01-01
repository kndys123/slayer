"""
Custom exceptions for SLAYER Enterprise.
Provides a comprehensive exception hierarchy for error handling.
"""

from typing import Optional, Dict, Any


class SlayerException(Exception):
    """Base exception for all SLAYER errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            'error': self.code,
            'message': self.message,
            'details': self.details
        }


class ValidationError(SlayerException):
    """Raised when input validation fails."""
    pass


class AuthenticationError(SlayerException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(SlayerException):
    """Raised when authorization fails."""
    pass


class RateLimitExceeded(SlayerException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class CircuitBreakerOpen(SlayerException):
    """Raised when circuit breaker is open."""
    
    def __init__(self, message: str, failure_count: int = 0, **kwargs):
        super().__init__(message, **kwargs)
        self.failure_count = failure_count


class TimeoutError(SlayerException):
    """Raised when request times out."""
    pass


class ConnectionError(SlayerException):
    """Raised when connection fails."""
    pass


class SSRFDetected(SlayerException):
    """Raised when potential SSRF is detected."""
    pass


class CacheError(SlayerException):
    """Raised when cache operation fails."""
    pass


class PluginError(SlayerException):
    """Raised when plugin execution fails."""
    pass


class ConfigurationError(SlayerException):
    """Raised when configuration is invalid."""
    pass
