"""
Enterprise logging with structured logs and audit trails.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import hashlib


class StructuredLogger:
    """
    Structured logger that outputs JSON for easy parsing.
    """
    
    def __init__(self, name: str = "slayer", level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Add structured handler if not already added
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(JsonFormatter())
            self.logger.addHandler(handler)
    
    def _log(self, level: str, message: str, **kwargs):
        """Internal log method."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            **kwargs
        }
        
        getattr(self.logger, level.lower())(json.dumps(log_data))
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log('ERROR', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log('CRITICAL', message, **kwargs)


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        """Format log record as JSON."""
        return record.getMessage()


class AuditLogger:
    """
    Audit logger for compliance and security tracking.
    Provides immutable audit trail of all operations.
    """
    
    def __init__(self, log_file: str = "/tmp/slayer_audit.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self._sequence = 0
    
    def log_request(self, 
                   request_id: str,
                   method: str,
                   url: str,
                   user_id: Optional[str] = None,
                   ip_address: Optional[str] = None,
                   **kwargs):
        """Log an HTTP request."""
        entry = {
            'event_type': 'http_request',
            'request_id': request_id,
            'timestamp': datetime.utcnow().isoformat(),
            'method': method,
            'url': self._sanitize_url(url),
            'user_id': user_id,
            'ip_address': ip_address,
            'sequence': self._get_next_sequence(),
            **kwargs
        }
        
        self._write_entry(entry)
    
    def log_response(self,
                    request_id: str,
                    status_code: int,
                    duration_ms: float,
                    response_size: int,
                    **kwargs):
        """Log an HTTP response."""
        entry = {
            'event_type': 'http_response',
            'request_id': request_id,
            'timestamp': datetime.utcnow().isoformat(),
            'status_code': status_code,
            'duration_ms': duration_ms,
            'response_size': response_size,
            'sequence': self._get_next_sequence(),
            **kwargs
        }
        
        self._write_entry(entry)
    
    def log_security_event(self,
                          event_type: str,
                          severity: str,
                          description: str,
                          **kwargs):
        """Log a security event."""
        entry = {
            'event_type': 'security',
            'security_event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'severity': severity,
            'description': description,
            'sequence': self._get_next_sequence(),
            **kwargs
        }
        
        self._write_entry(entry)
    
    def log_error(self,
                 error_type: str,
                 error_message: str,
                 request_id: Optional[str] = None,
                 **kwargs):
        """Log an error."""
        entry = {
            'event_type': 'error',
            'error_type': error_type,
            'timestamp': datetime.utcnow().isoformat(),
            'error_message': error_message,
            'request_id': request_id,
            'sequence': self._get_next_sequence(),
            **kwargs
        }
        
        self._write_entry(entry)
    
    def _write_entry(self, entry: Dict[str, Any]):
        """Write audit entry to file."""
        # Add integrity hash
        entry_json = json.dumps(entry, sort_keys=True)
        entry['hash'] = self._calculate_hash(entry_json)
        
        # Write to file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def _calculate_hash(self, data: str) -> str:
        """Calculate SHA256 hash of entry."""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _sanitize_url(self, url: str) -> str:
        """Sanitize URL for logging (remove sensitive params)."""
        # Remove common sensitive query parameters
        sensitive_params = ['password', 'token', 'api_key', 'secret', 'apikey']
        sanitized = url
        for param in sensitive_params:
            # Simple replacement - would need more robust parsing in production
            if f'{param}=' in sanitized.lower():
                sanitized = sanitized.split(f'{param}=')[0] + f'{param}=***'
        return sanitized
    
    def _get_next_sequence(self) -> int:
        """Get next sequence number."""
        self._sequence += 1
        return self._sequence
    
    def read_logs(self, limit: int = 100) -> list:
        """Read recent audit logs."""
        if not self.log_file.exists():
            return []
        
        logs = []
        with open(self.log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return logs
