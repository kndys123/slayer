#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional HTTP Load Testing Tool
Enterprise-grade load testing with authorization, logging, and safety controls
"""

import os
import sys
import time
import random
import threading
import hashlib
import json
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import deque
from urllib.parse import urlparse
import statistics

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("Error: 'requests' library not found. Install with: pip install requests")
    sys.exit(1)


class Color:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class AuditLogger:
    """Comprehensive audit logging for compliance"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"audit_{self.session_id}.log"
        self.json_log = self.log_dir / f"audit_{self.session_id}.json"
        self.events = []
        
    def log(self, event_type: str, message: str, data: Optional[Dict] = None):
        """Log an audit event"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "message": message,
            "data": data or {}
        }
        self.events.append(log_entry)
        
        # Write to text log
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {event_type}: {message}\n")
            if data:
                f.write(f"  Data: {json.dumps(data, indent=2)}\n")
        
        # Write to JSON log
        with open(self.json_log, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, indent=2)
    
    def generate_report(self) -> str:
        """Generate a summary report"""
        return self.json_log


class AuthorizationManager:
    """Manages authorization tokens and target allowlists"""
    
    def __init__(self):
        self.config_file = Path("load_test_config.json")
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load configuration file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            "authorized_targets": [],
            "api_tokens": {},
            "max_rps": 100,
            "max_threads": 20,
            "max_duration": 3600
        }
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def add_authorized_target(self, url: str, token: str, description: str = ""):
        """Add a target to the allowlist"""
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        
        # Generate token hash for security
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        if domain not in self.config["authorized_targets"]:
            self.config["authorized_targets"].append(domain)
        
        self.config["api_tokens"][domain] = {
            "token_hash": token_hash,
            "description": description,
            "added": datetime.now().isoformat()
        }
        self._save_config()
        return True
    
    def verify_target(self, url: str, token: str) -> bool:
        """Verify if target is authorized"""
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        
        if domain not in self.config["authorized_targets"]:
            return False
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        stored_hash = self.config["api_tokens"].get(domain, {}).get("token_hash")
        
        return token_hash == stored_hash
    
    def list_targets(self) -> List[str]:
        """List all authorized targets"""
        return self.config["authorized_targets"]
    
    def get_limits(self) -> Dict:
        """Get configured safety limits"""
        return {
            "max_rps": self.config.get("max_rps", 100),
            "max_threads": self.config.get("max_threads", 20),
            "max_duration": self.config.get("max_duration", 3600)
        }


class PerformanceMetrics:
    """Advanced performance metrics collection and analysis"""
    
    def __init__(self):
        self.response_times = deque(maxlen=10000)
        self.status_codes = {}
        self.errors = {}
        self.lock = threading.Lock()
        
    def add_response(self, response_time: float, status_code: int):
        """Add a successful response metric"""
        with self.lock:
            self.response_times.append(response_time)
            self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1
    
    def add_error(self, error_type: str):
        """Add an error metric"""
        with self.lock:
            self.errors[error_type] = self.errors.get(error_type, 0) + 1
    
    def get_statistics(self) -> Dict:
        """Calculate comprehensive statistics"""
        with self.lock:
            if not self.response_times:
                return {}
            
            times = list(self.response_times)
            return {
                "min": min(times),
                "max": max(times),
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "p95": self._percentile(times, 95),
                "p99": self._percentile(times, 99),
                "stdev": statistics.stdev(times) if len(times) > 1 else 0
            }
    
    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


class ProfessionalLoadTester:
    """Enterprise-grade HTTP load testing tool"""
    
    def __init__(self):
        self.target_url = ""
        self.method = "GET"
        self.delay = 1.0
        self.threads = 1
        self.duration = None
        self.max_requests = None
        self.running = False
        self.requests_count = 0
        self.success_count = 0
        self.error_count = 0
        self.start_time = None
        self.session = None
        self.auth_token = ""
        self.custom_headers = {}
        self.request_body = None
        self.content_type = "application/json"
        
        # Advanced features
        self.auth_manager = AuthorizationManager()
        self.audit_logger = AuditLogger()
        self.metrics = PerformanceMetrics()
        self.rate_limiter = None
        
        self.audit_logger.log("SYSTEM", "Load tester initialized")
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry logic"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_maxsize=50)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        session.headers.update({
            'User-Agent': 'ProfessionalLoadTester/3.0',
            'Accept': '*/*',
        })
        return session
    
    def display_banner(self):
        """Display professional banner"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        banner = f"""
{Color.CYAN}{Color.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██████╗  ██████╗ ███████╗███████╗███████╗███████╗██╗ ██████╗      ║
║   ██╔══██╗██╔══██╗██╔═══██╗██╔════╝██╔════╝██╔════╝██╔════╝██║██╔═══██╗     ║
║   ██████╔╝██████╔╝██║   ██║█████╗  █████╗  ███████╗███████╗██║██║   ██║     ║
║   ██╔═══╝ ██╔══██╗██║   ██║██╔══╝  ██╔══╝  ╚════██║╚════██║██║██║   ██║     ║
║   ██║     ██║  ██║╚██████╔╝██║     ███████╗███████║███████║██║╚██████╔╝     ║
║   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝╚══════╝╚══════╝╚═╝ ╚═════╝      ║
║                                                                              ║
║                    {Color.GREEN}ENTERPRISE LOAD TESTING TOOL v3.0{Color.CYAN}                       ║
║                                                                              ║
║  {Color.YELLOW}Features:{Color.CYAN}                                                               ║
║    ✓ Authorization & Target Verification                                    ║
║    ✓ Comprehensive Audit Logging                                            ║
║    ✓ Advanced Performance Metrics                                           ║
║    ✓ Safety Limits & Rate Controls                                          ║
║    ✓ Professional Reporting                                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Color.END}
        """
        print(banner)
    
    def display_status(self):
        """Display current configuration and stats"""
        limits = self.auth_manager.get_limits()
        status = f"""
{Color.CYAN}{Color.BOLD}╔═══ CURRENT CONFIGURATION ═══╗{Color.END}
{Color.YELLOW}Target URL:{Color.END} {self.target_url or 'Not set'}
{Color.YELLOW}HTTP Method:{Color.END} {self.method}
{Color.YELLOW}Delay:{Color.END} {self.delay} seconds
{Color.YELLOW}Threads:{Color.END} {self.threads} (max: {limits['max_threads']})
{Color.YELLOW}Duration:{Color.END} {self.duration or 'Unlimited'} seconds (max: {limits['max_duration']})
{Color.YELLOW}Max Requests:{Color.END} {self.max_requests or 'Unlimited'}
{Color.YELLOW}Authorization:{Color.END} {'✓ Configured' if self.auth_token else '✗ Not set'}
{Color.YELLOW}Status:{Color.END} {Color.GREEN if self.running else Color.RED}{'ACTIVE' if self.running else 'INACTIVE'}{Color.END}
"""
        if self.running and self.start_time:
            elapsed = time.time() - self.start_time
            rps = self.requests_count / elapsed if elapsed > 0 else 0
            stats = self.metrics.get_statistics()
            
            status += f"""
{Color.CYAN}{Color.BOLD}╔═══ REAL-TIME STATISTICS ═══╗{Color.END}
{Color.YELLOW}Requests:{Color.END} {self.requests_count}
{Color.YELLOW}Success:{Color.END} {Color.GREEN}{self.success_count}{Color.END}
{Color.YELLOW}Errors:{Color.END} {Color.RED}{self.error_count}{Color.END}
{Color.YELLOW}Elapsed:{Color.END} {elapsed:.1f} seconds
{Color.YELLOW}Requests/sec:{Color.END} {rps:.2f}
"""
            if stats:
                status += f"""
{Color.CYAN}{Color.BOLD}╔═══ PERFORMANCE METRICS ═══╗{Color.END}
{Color.YELLOW}Response Time (ms):{Color.END}
  Min: {stats['min']:.2f} | Max: {stats['max']:.2f} | Mean: {stats['mean']:.2f}
  Median: {stats['median']:.2f} | P95: {stats['p95']:.2f} | P99: {stats['p99']:.2f}
  StdDev: {stats['stdev']:.2f}
"""
        print(status)
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent string"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        return random.choice(user_agents)
    
    def make_request(self, thread_id: int):
        """Execute HTTP requests"""
        while self.running:
            # Check limits
            if self.max_requests and self.requests_count >= self.max_requests:
                break
            
            if self.duration and self.start_time:
                if time.time() - self.start_time >= self.duration:
                    break
            
            try:
                start_time = time.time()
                
                headers = {
                    'User-Agent': self._get_random_user_agent(),
                    'Accept': '*/*',
                    **self.custom_headers
                }
                
                if self.auth_token:
                    headers['Authorization'] = f'Bearer {self.auth_token}'
                
                if self.request_body and self.content_type:
                    headers['Content-Type'] = self.content_type
                
                # Execute request
                response = self.session.request(
                    self.method,
                    self.target_url,
                    headers=headers,
                    json=self.request_body if self.content_type == 'application/json' else None,
                    data=self.request_body if self.content_type != 'application/json' else None,
                    timeout=30
                )
                
                elapsed_ms = (time.time() - start_time) * 1000
                
                self.requests_count += 1
                self.metrics.add_response(elapsed_ms, response.status_code)
                
                if 200 <= response.status_code < 300:
                    self.success_count += 1
                    status_color = Color.GREEN
                    status_text = "SUCCESS"
                elif 400 <= response.status_code < 500:
                    self.error_count += 1
                    status_color = Color.YELLOW
                    status_text = "CLIENT_ERR"
                else:
                    self.error_count += 1
                    status_color = Color.RED
                    status_text = "SERVER_ERR"
                
                print(f"{Color.WHITE}[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
                      f"{status_color}[{status_text}] {Color.CYAN}T{thread_id:02d} "
                      f"{Color.WHITE}| {Color.MAGENTA}{response.status_code} "
                      f"{Color.WHITE}| {Color.BLUE}{elapsed_ms:.0f}ms "
                      f"{Color.WHITE}| {Color.YELLOW}{len(response.content)}B{Color.END}")
                
            except requests.exceptions.Timeout:
                self.error_count += 1
                self.requests_count += 1
                self.metrics.add_error("Timeout")
                print(f"{Color.WHITE}[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
                      f"{Color.RED}[TIMEOUT] {Color.CYAN}T{thread_id:02d}{Color.END}")
            
            except requests.exceptions.ConnectionError as e:
                self.error_count += 1
                self.requests_count += 1
                self.metrics.add_error("ConnectionError")
                print(f"{Color.WHITE}[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
                      f"{Color.RED}[CONN_ERR] {Color.CYAN}T{thread_id:02d} "
                      f"{Color.WHITE}| {str(e)[:40]}{Color.END}")
            
            except Exception as e:
                self.error_count += 1
                self.requests_count += 1
                self.metrics.add_error(type(e).__name__)
                print(f"{Color.WHITE}[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
                      f"{Color.RED}[ERROR] {Color.CYAN}T{thread_id:02d} "
                      f"{Color.WHITE}| {str(e)[:40]}{Color.END}")
            
            time.sleep(self.delay)
    
    def start_test(self):
        """Start the load test"""
        if not self.target_url:
            print(f"{Color.RED}✗ Error: Target URL not set{Color.END}")
            return
        
        if not self.auth_token:
            print(f"{Color.RED}✗ Error: Authorization token not configured{Color.END}")
            print(f"{Color.YELLOW}Use 'authorize <url> <token>' to set up authorization{Color.END}")
            return
        
        # Verify authorization
        if not self.auth_manager.verify_target(self.target_url, self.auth_token):
            print(f"{Color.RED}✗ Error: Target not authorized or invalid token{Color.END}")
            print(f"{Color.YELLOW}Use 'authorize <url> <token>' to authorize this target{Color.END}")
            return
        
        # Apply safety limits
        limits = self.auth_manager.get_limits()
        if self.threads > limits['max_threads']:
            print(f"{Color.YELLOW}⚠ Warning: Thread count limited to {limits['max_threads']}{Color.END}")
            self.threads = limits['max_threads']
        
        if self.duration and self.duration > limits['max_duration']:
            print(f"{Color.YELLOW}⚠ Warning: Duration limited to {limits['max_duration']} seconds{Color.END}")
            self.duration = limits['max_duration']
        
        if not self.target_url.startswith(('http://', 'https://')):
            self.target_url = 'https://' + self.target_url
        
        # Log test start
        self.audit_logger.log("TEST_START", f"Load test initiated against {self.target_url}", {
            "url": self.target_url,
            "method": self.method,
            "threads": self.threads,
            "delay": self.delay,
            "duration": self.duration,
            "max_requests": self.max_requests
        })
        
        print(f"\n{Color.GREEN}✓ Starting load test{Color.END}")
        print(f"{Color.CYAN}Target:{Color.END} {self.target_url}")
        print(f"{Color.CYAN}Method:{Color.END} {self.method} | {Color.CYAN}Delay:{Color.END} {self.delay}s | "
              f"{Color.CYAN}Threads:{Color.END} {self.threads}")
        if self.duration:
            print(f"{Color.CYAN}Duration:{Color.END} {self.duration} seconds")
        if self.max_requests:
            print(f"{Color.CYAN}Max Requests:{Color.END} {self.max_requests}")
        print(f"{Color.YELLOW}Press Ctrl+C to stop the test{Color.END}\n")
        
        self.running = True
        self.start_time = time.time()
        self.requests_count = 0
        self.success_count = 0
        self.error_count = 0
        self.session = self._create_session()
        
        # Create worker threads
        thread_pool = []
        for i in range(self.threads):
            thread = threading.Thread(target=self.make_request, args=(i+1,), daemon=True)
            thread_pool.append(thread)
            thread.start()
        
        try:
            # Monitor threads
            while self.running and any(t.is_alive() for t in thread_pool):
                time.sleep(0.5)
                
                # Auto-stop on limits
                if self.max_requests and self.requests_count >= self.max_requests:
                    self.stop_test()
                    break
                
                if self.duration and (time.time() - self.start_time) >= self.duration:
                    self.stop_test()
                    break
        
        except KeyboardInterrupt:
            self.stop_test()
        
        # Wait for cleanup
        for thread in thread_pool:
            thread.join(timeout=2)
    
    def stop_test(self):
        """Stop the load test"""
        self.running = False
        print(f"\n{Color.YELLOW}⚠ Stopping load test...{Color.END}")
        time.sleep(0.5)
        self.display_final_stats()
        
        # Log test completion
        self.audit_logger.log("TEST_COMPLETE", "Load test completed", {
            "total_requests": self.requests_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "duration": time.time() - self.start_time if self.start_time else 0
        })
    
    def display_final_stats(self):
        """Display comprehensive final statistics"""
        if not self.start_time:
            return
        
        elapsed = time.time() - self.start_time
        rps = self.requests_count / elapsed if elapsed > 0 else 0
        success_rate = (self.success_count / self.requests_count * 100) if self.requests_count > 0 else 0
        stats = self.metrics.get_statistics()
        
        print(f"\n{Color.CYAN}{Color.BOLD}{'═' * 80}{Color.END}")
        print(f"{Color.CYAN}{Color.BOLD}║{'FINAL TEST REPORT'.center(78)}║{Color.END}")
        print(f"{Color.CYAN}{Color.BOLD}{'═' * 80}{Color.END}\n")
        
        print(f"{Color.GREEN}Test Duration:{Color.END} {elapsed:.2f} seconds")
        print(f"{Color.GREEN}Total Requests:{Color.END} {self.requests_count}")
        print(f"{Color.GREEN}Successful:{Color.END} {self.success_count} ({success_rate:.1f}%)")
        print(f"{Color.RED}Failed:{Color.END} {self.error_count}")
        print(f"{Color.CYAN}Throughput:{Color.END} {rps:.2f} requests/second")
        
        if stats:
            print(f"\n{Color.CYAN}{Color.BOLD}Response Time Statistics (ms):{Color.END}")
            print(f"  {Color.YELLOW}Min:{Color.END} {stats['min']:.2f}")
            print(f"  {Color.YELLOW}Max:{Color.END} {stats['max']:.2f}")
            print(f"  {Color.YELLOW}Mean:{Color.END} {stats['mean']:.2f}")
            print(f"  {Color.YELLOW}Median:{Color.END} {stats['median']:.2f}")
            print(f"  {Color.YELLOW}95th Percentile:{Color.END} {stats['p95']:.2f}")
            print(f"  {Color.YELLOW}99th Percentile:{Color.END} {stats['p99']:.2f}")
            print(f"  {Color.YELLOW}Std Deviation:{Color.END} {stats['stdev']:.2f}")
        
        # Status code distribution
        status_codes = self.metrics.status_codes
        if status_codes:
            print(f"\n{Color.CYAN}{Color.BOLD}Status Code Distribution:{Color.END}")
            for code, count in sorted(status_codes.items()):
                pct = (count / self.requests_count * 100) if self.requests_count > 0 else 0
                print(f"  {Color.YELLOW}{code}:{Color.END} {count} ({pct:.1f}%)")
        
        # Error distribution
        errors = self.metrics.errors
        if errors:
            print(f"\n{Color.CYAN}{Color.BOLD}Error Distribution:{Color.END}")
            for error_type, count in sorted(errors.items(), key=lambda x: x[1], reverse=True):
                print(f"  {Color.RED}{error_type}:{Color.END} {count}")
        
        # Audit log location
        report_path = self.audit_logger.generate_report()
        print(f"\n{Color.GREEN}✓ Audit log saved:{Color.END} {report_path}")
        print(f"{Color.CYAN}{Color.BOLD}{'═' * 80}{Color.END}\n")
    
    def show_help(self):
        """Display comprehensive help menu"""
        help_text = f"""
{Color.CYAN}{Color.BOLD}╔═══ AVAILABLE COMMANDS ═══╗{Color.END}

{Color.GREEN}Configuration:{Color.END}
  {Color.YELLOW}set target <url>{Color.END}           Set target URL for load testing
  {Color.YELLOW}set method <METHOD>{Color.END}        Set HTTP method (GET, POST, PUT, DELETE, etc.)
  {Color.YELLOW}set delay <seconds>{Color.END}        Set delay between requests (e.g., 0.5)
  {Color.YELLOW}set threads <number>{Color.END}       Set number of concurrent threads
  {Color.YELLOW}set duration <seconds>{Color.END}     Set test duration limit
  {Color.YELLOW}set maxreq <number>{Color.END}        Set maximum request limit
  {Color.YELLOW}set header <key> <value>{Color.END}   Add custom HTTP header
  {Color.YELLOW}set body <json>{Color.END}            Set request body (JSON)

{Color.GREEN}Authorization:{Color.END}
  {Color.YELLOW}authorize <url> <token>{Color.END}    Authorize target with API token
  {Color.YELLOW}targets{Color.END}                    List authorized targets
  
{Color.GREEN}Testing:{Color.END}
  {Color.YELLOW}run{Color.END}                        Start load test
  {Color.YELLOW}stop{Color.END}                       Stop running test
  {Color.YELLOW}status{Color.END}                     Show current configuration and stats
  
{Color.GREEN}System:{Color.END}
  {Color.YELLOW}help{Color.END}                       Show this help menu
  {Color.YELLOW}clear{Color.END}                      Clear screen
  {Color.YELLOW}logs{Color.END}                       Show audit log location
  {Color.YELLOW}exit{Color.END}                       Exit application

{Color.GREEN}Examples:{Color.END}
  {Color.WHITE}authorize https://api.example.com my-secret-token-123{Color.END}
  {Color.WHITE}set target https://api.example.com/endpoint{Color.END}
  {Color.WHITE}set method POST{Color.END}
  {Color.WHITE}set delay 0.5{Color.END}
  {Color.WHITE}set threads 10{Color.END}
  {Color.WHITE}set duration 60{Color.END}
  {Color.WHITE}set header X-API-Key your-key-here{Color.END}
  {Color.WHITE}set body {{"key": "value"}}{Color.END}
  {Color.WHITE}run{Color.END}
"""
        print(help_text)
    
    def handle_command(self, cmd: str):
        """Handle user commands"""
        parts = cmd.strip().split(maxsplit=1)
        if not parts:
            return
        
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if command == 'exit' or command == 'quit':
            if self.running:
                self.stop_test()
            print(f"{Color.GREEN}✓ Exiting... Goodbye!{Color.END}")
            self.audit_logger.log("SYSTEM", "Application terminated")
            sys.exit(0)
        
        elif command == 'help':
            self.show_help()
        
        elif command == 'clear':
            self.display_banner()
        
        elif command == 'status':
            self.display_status()
        
        elif command == 'logs':
            print(f"{Color.CYAN}Audit logs location:{Color.END} {self.audit_logger.log_dir.absolute()}")
            print(f"{Color.CYAN}Current session log:{Color.END} {self.audit_logger.log_file}")
        
        elif command == 'targets':
            targets = self.auth_manager.list_targets()
            if targets:
                print(f"{Color.GREEN}Authorized Targets:{Color.END}")
                for target in targets:
                    print(f"  • {target}")
            else:
                print(f"{Color.YELLOW}No authorized targets configured{Color.END}")
        
        elif command == 'run':
            if self.running:
                print(f"{Color.YELLOW}⚠ Test already running{Color.END}")
            else:
                self.start_test()
        
        elif command == 'stop':
            if self.running:
                self.stop_test()
            else:
                print(f"{Color.YELLOW}⚠ No test running{Color.END}")
        
        elif command == 'set':
            self.handle_set_command(args)
        
        elif command == 'authorize':
            self.handle_authorize_command(args)
        
        else:
            print(f"{Color.RED}✗ Unknown command: {command}{Color.END}")
            print(f"{Color.YELLOW}Type 'help' for available commands{Color.END}")
    
    def handle_set_command(self, args: str):
        """Handle set subcommands"""
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            print(f"{Color.RED}✗ Usage: set <option> <value>{Color.END}")
            return
        
        option, value = parts
        option = option.lower()
        
        if option == 'target':
            self.target_url = value
            self.audit_logger.log("CONFIG", f"Target set to {value}")
            print(f"{Color.GREEN}✓ Target set:{Color.END} {value}")
        
        elif option == 'method':
            valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH']
            if value.upper() in valid_methods:
                self.method = value.upper()
                self.audit_logger.log("CONFIG", f"Method set to {self.method}")
                print(f"{Color.GREEN}✓ Method set:{Color.END} {self.method}")
            else:
                print(f"{Color.RED}✗ Invalid method. Valid: {', '.join(valid_methods)}{Color.END}")
        
        elif option == 'delay':
            try:
                self.delay = float(value)
                if self.delay < 0:
                    raise ValueError("Delay cannot be negative")
                self.audit_logger.log("CONFIG", f"Delay set to {self.delay}s")
                print(f"{Color.GREEN}✓ Delay set:{Color.END} {self.delay}s")
            except ValueError as e:
                print(f"{Color.RED}✗ Invalid delay: {e}{Color.END}")
        
        elif option == 'threads':
            try:
                self.threads = int(value)
                if self.threads < 1:
                    raise ValueError("Must have at least 1 thread")
                limits = self.auth_manager.get_limits()
                if self.threads > limits['max_threads']:
                    print(f"{Color.YELLOW}⚠ Warning: Maximum {limits['max_threads']} threads allowed{Color.END}")
                self.audit_logger.log("CONFIG", f"Threads set to {self.threads}")
                print(f"{Color.GREEN}✓ Threads set:{Color.END} {self.threads}")
            except ValueError as e:
                print(f"{Color.RED}✗ Invalid thread count: {e}{Color.END}")
        
        elif option == 'duration':
            try:
                self.duration = int(value)
                if self.duration < 1:
                    raise ValueError("Duration must be positive")
                self.audit_logger.log("CONFIG", f"Duration set to {self.duration}s")
                print(f"{Color.GREEN}✓ Duration set:{Color.END} {self.duration}s")
            except ValueError as e:
                print(f"{Color.RED}✗ Invalid duration: {e}{Color.END}")
        
        elif option == 'maxreq':
            try:
                self.max_requests = int(value)
                if self.max_requests < 1:
                    raise ValueError("Max requests must be positive")
                self.audit_logger.log("CONFIG", f"Max requests set to {self.max_requests}")
                print(f"{Color.GREEN}✓ Max requests set:{Color.END} {self.max_requests}")
            except ValueError as e:
                print(f"{Color.RED}✗ Invalid max requests: {e}{Color.END}")
        
        elif option == 'header':
            header_parts = value.split(maxsplit=1)
            if len(header_parts) == 2:
                key, val = header_parts
                self.custom_headers[key] = val
                print(f"{Color.GREEN}✓ Header added:{Color.END} {key}: {val}")
            else:
                print(f"{Color.RED}✗ Usage: set header <key> <value>{Color.END}")
        
        elif option == 'body':
            try:
                self.request_body = json.loads(value)
                self.audit_logger.log("CONFIG", "Request body configured")
                print(f"{Color.GREEN}✓ Request body set{Color.END}")
            except json.JSONDecodeError:
                print(f"{Color.RED}✗ Invalid JSON body{Color.END}")
        
        else:
            print(f"{Color.RED}✗ Unknown option: {option}{Color.END}")
    
    def handle_authorize_command(self, args: str):
        """Handle authorization command"""
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            print(f"{Color.RED}✗ Usage: authorize <url> <token>{Color.END}")
            return
        
        url, token = parts
        
        # Request description
        try:
            description = input(f"{Color.CYAN}Description (optional):{Color.END} ").strip()
        except KeyboardInterrupt:
            print(f"\n{Color.YELLOW}Cancelled{Color.END}")
            return
        
        self.auth_manager.add_authorized_target(url, token, description)
        self.auth_token = token
        self.audit_logger.log("AUTH", f"Target authorized: {url}")
        print(f"{Color.GREEN}✓ Target authorized and token configured{Color.END}")
    
    def run(self):
        """Main application loop"""
        self.display_banner()
        self.show_help()
        
        while True:
            try:
                cmd = input(f"\n{Color.CYAN}{Color.BOLD}loadtest{Color.END}> ").strip()
                if cmd:
                    self.handle_command(cmd)
            
            except KeyboardInterrupt:
                print(f"\n{Color.YELLOW}⚠ Use 'exit' to quit{Color.END}")
            
            except Exception as e:
                print(f"{Color.RED}✗ Error: {str(e)}{Color.END}")
                self.audit_logger.log("ERROR", f"Command error: {str(e)}")


def main():
    """Application entry point"""
    try:
        tester = ProfessionalLoadTester()
        tester.run()
    except KeyboardInterrupt:
        print(f"\n{Color.CYAN}Application terminated{Color.END}")
    except Exception as e:
        print(f"{Color.RED}✗ Critical error: {str(e)}{Color.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()
