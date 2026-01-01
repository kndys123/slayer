"""
SSRF (Server-Side Request Forgery) Protection.
Prevents malicious requests to internal network resources.
"""

import ipaddress
import socket
from urllib.parse import urlparse
from typing import Set, List
import re

from ..core.exceptions import SSRFDetected, ValidationError


class SSRFProtection:
    """
    Protects against SSRF attacks by validating URLs and IP addresses.
    
    Blocks:
    - Private IP ranges (RFC1918)
    - Loopback addresses
    - Link-local addresses
    - Cloud metadata endpoints
    - Blacklisted domains
    """
    
    # Private IP ranges
    PRIVATE_NETWORKS = [
        ipaddress.ip_network('10.0.0.0/8'),
        ipaddress.ip_network('172.16.0.0/12'),
        ipaddress.ip_network('192.168.0.0/16'),
        ipaddress.ip_network('127.0.0.0/8'),  # Loopback
        ipaddress.ip_network('169.254.0.0/16'),  # Link-local
        ipaddress.ip_network('::1/128'),  # IPv6 loopback
        ipaddress.ip_network('fe80::/10'),  # IPv6 link-local
        ipaddress.ip_network('fc00::/7'),  # IPv6 unique local
    ]
    
    # Cloud metadata endpoints
    METADATA_ENDPOINTS = [
        '169.254.169.254',  # AWS, Azure, GCP
        'metadata.google.internal',
        'metadata.azure.com',
    ]
    
    # Blacklisted domains
    BLACKLISTED_DOMAINS = [
        'localhost',
        'metadata',
        'internal',
        '.local',
        '.internal',
    ]
    
    def __init__(self, 
                 allowed_schemes: List[str] = None,
                 custom_blacklist: List[str] = None,
                 enable_dns_resolution: bool = True):
        self.allowed_schemes = set(allowed_schemes or ['http', 'https'])
        self.custom_blacklist = set(custom_blacklist or [])
        self.enable_dns_resolution = enable_dns_resolution
        
    def validate_url(self, url: str) -> bool:
        """
        Validate URL for SSRF vulnerabilities.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is safe
            
        Raises:
            SSRFDetected: If URL is potentially malicious
            ValidationError: If URL is malformed
        """
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValidationError(f"Invalid URL format: {str(e)}")
        
        # Check scheme
        if parsed.scheme not in self.allowed_schemes:
            raise SSRFDetected(
                f"Scheme '{parsed.scheme}' not allowed",
                details={'url': url, 'allowed_schemes': list(self.allowed_schemes)}
            )
        
        # Extract hostname
        hostname = parsed.hostname
        if not hostname:
            raise ValidationError("URL must contain a hostname")
        
        # Check against blacklisted domains
        if self._is_blacklisted_domain(hostname):
            raise SSRFDetected(
                f"Domain '{hostname}' is blacklisted",
                details={'url': url, 'hostname': hostname}
            )
        
        # Check if hostname is an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            self._validate_ip(ip, url)
        except ValueError:
            # Not an IP address, try DNS resolution
            if self.enable_dns_resolution:
                self._validate_hostname_via_dns(hostname, url)
        
        return True
    
    def _validate_ip(self, ip: ipaddress._BaseAddress, url: str):
        """Validate IP address."""
        # Check if IP is in private networks
        for network in self.PRIVATE_NETWORKS:
            if ip in network:
                raise SSRFDetected(
                    f"Access to private IP address is blocked: {ip}",
                    details={'url': url, 'ip': str(ip), 'network': str(network)}
                )
        
        # Check metadata endpoints
        if str(ip) in self.METADATA_ENDPOINTS:
            raise SSRFDetected(
                f"Access to cloud metadata endpoint is blocked: {ip}",
                details={'url': url, 'ip': str(ip)}
            )
    
    def _validate_hostname_via_dns(self, hostname: str, url: str):
        """Validate hostname by resolving DNS and checking IPs."""
        try:
            # Resolve hostname to IP addresses
            addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
            
            for info in addr_info:
                ip_str = info[4][0]
                try:
                    ip = ipaddress.ip_address(ip_str)
                    self._validate_ip(ip, url)
                except ValueError:
                    continue  # Skip invalid IPs
                    
        except socket.gaierror as e:
            raise ValidationError(
                f"Failed to resolve hostname: {hostname}",
                details={'error': str(e)}
            )
    
    def _is_blacklisted_domain(self, domain: str) -> bool:
        """Check if domain is in blacklist."""
        domain_lower = domain.lower()
        
        # Check exact matches
        if domain_lower in self.BLACKLISTED_DOMAINS or domain_lower in self.custom_blacklist:
            return True
        
        # Check suffix matches
        for blocked in self.BLACKLISTED_DOMAINS:
            if blocked.startswith('.') and domain_lower.endswith(blocked):
                return True
            if domain_lower.endswith(blocked):
                return True
        
        for blocked in self.custom_blacklist:
            if blocked.startswith('.') and domain_lower.endswith(blocked):
                return True
            if domain_lower.endswith(blocked):
                return True
        
        return False
    
    def add_to_blacklist(self, domain: str):
        """Add domain to custom blacklist."""
        self.custom_blacklist.add(domain.lower())
    
    def remove_from_blacklist(self, domain: str):
        """Remove domain from custom blacklist."""
        self.custom_blacklist.discard(domain.lower())
