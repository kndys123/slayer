"""Request tracing for distributed systems."""

import uuid
from typing import Optional, Dict
from datetime import datetime


class RequestTracer:
    """
    Distributed tracing for requests.
    Generates and propagates trace IDs.
    """
    
    def __init__(self, service_name: str = "slayer-enterprise"):
        self.service_name = service_name
    
    def generate_trace_id(self) -> str:
        """Generate unique trace ID."""
        return str(uuid.uuid4())
    
    def generate_span_id(self) -> str:
        """Generate unique span ID."""
        return str(uuid.uuid4())[:16]
    
    def create_trace_headers(self, 
                            trace_id: Optional[str] = None,
                            parent_span_id: Optional[str] = None) -> Dict[str, str]:
        """
        Create tracing headers for HTTP requests.
        Follows W3C Trace Context specification.
        """
        trace_id = trace_id or self.generate_trace_id()
        span_id = self.generate_span_id()
        
        headers = {
            'X-Trace-Id': trace_id,
            'X-Span-Id': span_id,
            'X-Service-Name': self.service_name,
        }
        
        if parent_span_id:
            headers['X-Parent-Span-Id'] = parent_span_id
        
        # W3C Trace Context
        headers['traceparent'] = f"00-{trace_id.replace('-', '')[:32]}-{span_id}-01"
        
        return headers
    
    def extract_trace_context(self, headers: Dict[str, str]) -> Dict[str, Optional[str]]:
        """Extract trace context from headers."""
        return {
            'trace_id': headers.get('X-Trace-Id') or headers.get('traceparent', '').split('-')[1] if 'traceparent' in headers else None,
            'span_id': headers.get('X-Span-Id'),
            'parent_span_id': headers.get('X-Parent-Span-Id')
        }
