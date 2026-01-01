"""Request and response validators."""

import re
from typing import Dict, Any, List
from urllib.parse import urlparse

from ..core.exceptions import ValidationError


class RequestValidator:
    """Validates HTTP requests before execution."""
    
    # Common injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
        r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
        r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
    ]
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate complete request."""
        self.validate_url(request.get('url'))
        self.validate_headers(request.get('headers', {}))
        self.validate_body(request.get('json') or request.get('data'))
        return True
    
    def validate_url(self, url: str) -> bool:
        """Validate URL structure and content."""
        if not url:
            raise ValidationError("URL is required")
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValidationError(f"Invalid URL: {str(e)}")
        
        # Check scheme
        if parsed.scheme not in ['http', 'https', '']:
            raise ValidationError(f"Invalid URL scheme: {parsed.scheme}")
        
        # Check for null bytes
        if '\x00' in url:
            raise ValidationError("URL contains null bytes")
        
        # Check for injection patterns in strict mode
        if self.strict_mode:
            self._check_injection_patterns(url, "URL")
        
        return True
    
    def validate_headers(self, headers: Dict[str, str]) -> bool:
        """Validate HTTP headers."""
        for key, value in headers.items():
            # Check for null bytes
            if '\x00' in key or '\x00' in str(value):
                raise ValidationError(f"Header contains null bytes: {key}")
            
            # Check for CRLF injection
            if '\r' in str(value) or '\n' in str(value):
                raise ValidationError(f"Header contains CRLF: {key}")
            
            # Validate specific headers
            if key.lower() == 'content-length':
                try:
                    int(value)
                except ValueError:
                    raise ValidationError("Invalid Content-Length header")
        
        return True
    
    def validate_body(self, body: Any) -> bool:
        """Validate request body."""
        if body is None:
            return True
        
        # Convert to string for pattern matching
        body_str = str(body)
        
        # Check size limit (10MB)
        if len(body_str) > 10 * 1024 * 1024:
            raise ValidationError("Request body too large (max 10MB)")
        
        # Check for injection patterns in strict mode
        if self.strict_mode:
            self._check_injection_patterns(body_str, "Request body")
        
        return True
    
    def _check_injection_patterns(self, text: str, context: str):
        """Check for common injection patterns."""
        # SQL injection
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValidationError(
                    f"Potential SQL injection detected in {context}",
                    details={'pattern': pattern}
                )
        
        # XSS
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValidationError(
                    f"Potential XSS detected in {context}",
                    details={'pattern': pattern}
                )


class ResponseValidator:
    """Validates HTTP responses."""
    
    def __init__(self, max_size: int = 100 * 1024 * 1024):  # 100MB
        self.max_size = max_size
    
    def validate_response(self, response: Any) -> bool:
        """Validate response."""
        # Check response size
        if hasattr(response, 'content'):
            if len(response.content) > self.max_size:
                raise ValidationError(
                    f"Response too large: {len(response.content)} bytes (max {self.max_size})"
                )
        
        return True
    
    def sanitize_response_data(self, data: str) -> str:
        """Sanitize response data for logging."""
        # Truncate large responses
        max_log_size = 1000
        if len(data) > max_log_size:
            return data[:max_log_size] + f"... ({len(data) - max_log_size} more bytes)"
        return data
