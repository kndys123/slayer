"""
Request builder implementing the Builder pattern.
Provides fluent interface for constructing HTTP requests.
"""

from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, urlencode
import json
from enum import Enum


class HTTPMethod(Enum):
    """Supported HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ContentType(Enum):
    """Common content types."""
    JSON = "application/json"
    FORM = "application/x-www-form-urlencoded"
    MULTIPART = "multipart/form-data"
    XML = "application/xml"
    TEXT = "text/plain"
    HTML = "text/html"


class RequestBuilder:
    """
    Fluent interface for building HTTP requests.
    
    Example:
        request = (RequestBuilder()
            .url("https://api.example.com/users")
            .method(HTTPMethod.POST)
            .json({"name": "John"})
            .header("X-API-Key", "secret")
            .timeout(30)
            .build())
    """
    
    def __init__(self):
        self._url: Optional[str] = None
        self._method: HTTPMethod = HTTPMethod.GET
        self._headers: Dict[str, str] = {}
        self._params: Dict[str, Any] = {}
        self._json_data: Optional[Dict[str, Any]] = None
        self._form_data: Optional[Dict[str, Any]] = None
        self._data: Optional[Any] = None
        self._files: Optional[Dict[str, Any]] = None
        self._timeout: Optional[int] = None
        self._allow_redirects: bool = True
        self._max_redirects: int = 5
        self._auth: Optional[tuple] = None
        self._cookies: Dict[str, str] = {}
        self._proxy: Optional[str] = None
        self._verify_ssl: bool = True
        
    def url(self, url: str) -> 'RequestBuilder':
        """Set request URL."""
        self._url = url
        return self
    
    def base_url(self, base: str) -> 'RequestBuilder':
        """Set base URL (to be combined with path)."""
        self._url = base
        return self
    
    def path(self, path: str) -> 'RequestBuilder':
        """Add path to base URL."""
        if self._url:
            self._url = urljoin(self._url, path)
        else:
            self._url = path
        return self
    
    def method(self, method: HTTPMethod) -> 'RequestBuilder':
        """Set HTTP method."""
        self._method = method
        return self
    
    def get(self) -> 'RequestBuilder':
        """Set method to GET."""
        self._method = HTTPMethod.GET
        return self
    
    def post(self) -> 'RequestBuilder':
        """Set method to POST."""
        self._method = HTTPMethod.POST
        return self
    
    def put(self) -> 'RequestBuilder':
        """Set method to PUT."""
        self._method = HTTPMethod.PUT
        return self
    
    def delete(self) -> 'RequestBuilder':
        """Set method to DELETE."""
        self._method = HTTPMethod.DELETE
        return self
    
    def patch(self) -> 'RequestBuilder':
        """Set method to PATCH."""
        self._method = HTTPMethod.PATCH
        return self
    
    def header(self, key: str, value: str) -> 'RequestBuilder':
        """Add single header."""
        self._headers[key] = value
        return self
    
    def headers(self, headers: Dict[str, str]) -> 'RequestBuilder':
        """Add multiple headers."""
        self._headers.update(headers)
        return self
    
    def param(self, key: str, value: Any) -> 'RequestBuilder':
        """Add single query parameter."""
        self._params[key] = value
        return self
    
    def params(self, params: Dict[str, Any]) -> 'RequestBuilder':
        """Add multiple query parameters."""
        self._params.update(params)
        return self
    
    def json(self, data: Dict[str, Any]) -> 'RequestBuilder':
        """Set JSON body."""
        self._json_data = data
        self.header('Content-Type', ContentType.JSON.value)
        return self
    
    def form(self, data: Dict[str, Any]) -> 'RequestBuilder':
        """Set form data."""
        self._form_data = data
        self.header('Content-Type', ContentType.FORM.value)
        return self
    
    def data(self, data: Any) -> 'RequestBuilder':
        """Set raw data."""
        self._data = data
        return self
    
    def files(self, files: Dict[str, Any]) -> 'RequestBuilder':
        """Set files for upload."""
        self._files = files
        return self
    
    def timeout(self, seconds: int) -> 'RequestBuilder':
        """Set timeout."""
        self._timeout = seconds
        return self
    
    def auth(self, username: str, password: str) -> 'RequestBuilder':
        """Set basic authentication."""
        self._auth = (username, password)
        return self
    
    def bearer_token(self, token: str) -> 'RequestBuilder':
        """Set bearer token authentication."""
        self.header('Authorization', f'Bearer {token}')
        return self
    
    def api_key(self, key: str, value: str) -> 'RequestBuilder':
        """Set API key header."""
        self.header(key, value)
        return self
    
    def cookie(self, key: str, value: str) -> 'RequestBuilder':
        """Add cookie."""
        self._cookies[key] = value
        return self
    
    def cookies(self, cookies: Dict[str, str]) -> 'RequestBuilder':
        """Add multiple cookies."""
        self._cookies.update(cookies)
        return self
    
    def proxy(self, proxy_url: str) -> 'RequestBuilder':
        """Set proxy."""
        self._proxy = proxy_url
        return self
    
    def redirects(self, allow: bool = True, max_redirects: int = 5) -> 'RequestBuilder':
        """Configure redirect behavior."""
        self._allow_redirects = allow
        self._max_redirects = max_redirects
        return self
    
    def verify_ssl(self, verify: bool = True) -> 'RequestBuilder':
        """Set SSL verification."""
        self._verify_ssl = verify
        return self
    
    def content_type(self, content_type: ContentType) -> 'RequestBuilder':
        """Set content type."""
        self.header('Content-Type', content_type.value)
        return self
    
    def accept(self, content_type: ContentType) -> 'RequestBuilder':
        """Set accept header."""
        self.header('Accept', content_type.value)
        return self
    
    def user_agent(self, ua: str) -> 'RequestBuilder':
        """Set user agent."""
        self.header('User-Agent', ua)
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return request configuration."""
        if not self._url:
            raise ValueError("URL is required")
        
        # Build final URL with query params
        url = self._url
        if self._params:
            separator = '&' if '?' in url else '?'
            url = f"{url}{separator}{urlencode(self._params)}"
        
        request = {
            'url': url,
            'method': self._method.value,
            'headers': self._headers.copy(),
            'allow_redirects': self._allow_redirects,
            'max_redirects': self._max_redirects,
            'verify_ssl': self._verify_ssl,
        }
        
        # Add body data
        if self._json_data is not None:
            request['json'] = self._json_data
        elif self._form_data is not None:
            request['data'] = self._form_data
        elif self._data is not None:
            request['data'] = self._data
        
        # Add optional fields
        if self._files:
            request['files'] = self._files
        if self._timeout:
            request['timeout'] = self._timeout
        if self._auth:
            request['auth'] = self._auth
        if self._cookies:
            request['cookies'] = self._cookies
        if self._proxy:
            request['proxy'] = self._proxy
        
        return request
    
    def clone(self) -> 'RequestBuilder':
        """Create a copy of this builder."""
        builder = RequestBuilder()
        builder._url = self._url
        builder._method = self._method
        builder._headers = self._headers.copy()
        builder._params = self._params.copy()
        builder._json_data = self._json_data.copy() if self._json_data else None
        builder._form_data = self._form_data.copy() if self._form_data else None
        builder._data = self._data
        builder._files = self._files.copy() if self._files else None
        builder._timeout = self._timeout
        builder._allow_redirects = self._allow_redirects
        builder._max_redirects = self._max_redirects
        builder._auth = self._auth
        builder._cookies = self._cookies.copy()
        builder._proxy = self._proxy
        builder._verify_ssl = self._verify_ssl
        return builder
