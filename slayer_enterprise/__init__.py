"""
SLAYER Enterprise - Professional HTTP Request Framework
========================================================

A production-ready, enterprise-grade HTTP request framework with advanced
features including caching, security, monitoring, and resilience patterns.

Copyright (c) 2026 SLAYER Enterprise
Licensed under MIT License
"""

__version__ = "3.0.0"
__author__ = "SLAYER Enterprise Team"
__license__ = "MIT"

from .core.client import SlayerClient
from .core.config import SlayerConfig
from .core.exceptions import (
    SlayerException,
    RateLimitExceeded,
    CircuitBreakerOpen,
    ValidationError
)

__all__ = [
    'SlayerClient',
    'SlayerConfig',
    'SlayerException',
    'RateLimitExceeded',
    'CircuitBreakerOpen',
    'ValidationError',
]
