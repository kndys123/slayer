"""Authentication and authorization management."""

import hashlib
import hmac
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt

from ..core.exceptions import AuthenticationError, AuthorizationError


class AuthenticationManager:
    """Manages authentication tokens and credentials."""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self._api_keys: Dict[str, Dict[str, Any]] = {}
        
    def generate_api_key(self, 
                        user_id: str, 
                        name: str,
                        expires_in_days: Optional[int] = None) -> str:
        """Generate a new API key."""
        api_key = f"sk_{secrets.token_urlsafe(32)}"
        key_hash = self._hash_api_key(api_key)
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        self._api_keys[key_hash] = {
            'user_id': user_id,
            'name': name,
            'created_at': datetime.now(),
            'expires_at': expires_at,
            'last_used': None,
            'usage_count': 0
        }
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """Validate API key and return user info."""
        key_hash = self._hash_api_key(api_key)
        
        if key_hash not in self._api_keys:
            raise AuthenticationError("Invalid API key")
        
        key_info = self._api_keys[key_hash]
        
        # Check expiration
        if key_info['expires_at'] and datetime.now() > key_info['expires_at']:
            raise AuthenticationError("API key expired")
        
        # Update usage
        key_info['last_used'] = datetime.now()
        key_info['usage_count'] += 1
        
        return {
            'user_id': key_info['user_id'],
            'name': key_info['name']
        }
    
    def revoke_api_key(self, api_key: str):
        """Revoke an API key."""
        key_hash = self._hash_api_key(api_key)
        if key_hash in self._api_keys:
            del self._api_keys[key_hash]
    
    def generate_jwt(self, 
                    user_id: str, 
                    claims: Optional[Dict[str, Any]] = None,
                    expires_in_hours: int = 24) -> str:
        """Generate JWT token."""
        payload = {
            'user_id': user_id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours)
        }
        
        if claims:
            payload.update(claims)
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token
    
    def validate_jwt(self, token: str) -> Dict[str, Any]:
        """Validate JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
    
    def create_signature(self, data: str, secret: Optional[str] = None) -> str:
        """Create HMAC signature for data."""
        key = (secret or self.secret_key).encode()
        signature = hmac.new(key, data.encode(), hashlib.sha256).hexdigest()
        return signature
    
    def verify_signature(self, data: str, signature: str, secret: Optional[str] = None) -> bool:
        """Verify HMAC signature."""
        expected = self.create_signature(data, secret)
        return hmac.compare_digest(expected, signature)
    
    def _hash_api_key(self, api_key: str) -> str:
        """Hash API key for storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()
