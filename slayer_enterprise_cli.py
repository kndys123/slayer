#!/usr/bin/env python3
"""
SLAYER Enterprise - Modern CLI
Professional command-line interface with async support
"""

import asyncio
import sys
import os
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
import json

from slayer_enterprise import SlayerClient
from slayer_enterprise.core.config import SlayerConfig, load_config
from slayer_enterprise.core.request_builder import RequestBuilder


console = Console()


def print_banner():
    """Display professional banner."""
    banner = """
[bold red]╔══════════════════════════════════════════════════════════════════╗[/bold red]
[bold red]║[/bold red]  [bold cyan]███████╗██╗      █████╗ ██╗   ██╗███████╗██████╗[/bold cyan]  [bold red]║[/bold red]
[bold red]║[/bold red]  [bold cyan]██╔════╝██║     ██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗[/bold cyan] [bold red]║[/bold red]
[bold red]║[/bold red]  [bold cyan]███████╗██║     ███████║ ╚████╔╝ █████╗  ██████╔╝[/bold cyan] [bold red]║[/bold red]
[bold red]║[/bold red]  [bold cyan]╚════██║██║     ██╔══██║  ╚██╔╝  ██╔══╝  ██╔══██╗[/bold cyan] [bold red]║[/bold red]
[bold red]║[/bold red]  [bold cyan]███████║███████╗██║  ██║   ██║   ███████╗██║  ██║[/bold cyan] [bold red]║[/bold red]
[bold red]║[/bold red]  [bold cyan]╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝[/bold cyan] [bold red]║[/bold red]
[bold red]║[/bold red]                                                              [bold red]║[/bold red]
[bold red]║[/bold red]  [bold yellow]Enterprise-Grade HTTP Client Framework v3.0.0[/bold yellow]           [bold red]║[/bold red]
[bold red]╚══════════════════════════════════════════════════════════════════╝[/bold red]
"""
    rprint(banner)


@click.group()
@click.version_option(version="3.0.0")
def cli():
    """SLAYER Enterprise - Professional HTTP Client Framework"""
    pass


@cli.command()
@click.option('--url', '-u', required=True, help='Target URL')
@click.option('--method', '-m', default='GET', help='HTTP method')
@click.option('--headers', '-H', multiple=True, help='Headers (key:value)')
@click.option('--data', '-d', help='Request body (JSON)')
@click.option('--config', '-c', help='Configuration file')
@click.option('--output', '-o', help='Output file for response')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def request(url, method, headers, data, config, output, verbose):
    """Make a single HTTP request."""
    asyncio.run(_request(url, method, headers, data, config, output, verbose))


async def _request(url, method, headers, data, config_file, output, verbose):
    """Async request implementation."""
    try:
        # Load configuration
        if config_file:
            config = SlayerConfig.from_file(config_file)
        else:
            config = SlayerConfig.from_env()
        
        # Parse headers
        headers_dict = {}
        for h in headers:
            if ':' in h:
                k, v = h.split(':', 1)
                headers_dict[k.strip()] = v.strip()
        
        # Parse data
        json_data = None
        if data:
            try:
                json_data = json.loads(data)
            except json.JSONDecodeError:
                json_data = {'data': data}
        
        # Make request
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"[cyan]Executing {method} {url}...", total=None)
            
            async with SlayerClient(config) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers_dict,
                    json=json_data
                )
                
                progress.update(task, completed=True)
                
                # Display response
                console.print(f"\n[green]✓[/green] Status: [bold]{response.status}[/bold]")
                console.print(f"[green]✓[/green] Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                console.print(f"[green]✓[/green] Content-Length: {response.headers.get('Content-Length', 'N/A')}")
                
                # Get response body
                body = await response.text()
                
                if output:
                    with open(output, 'w') as f:
                        f.write(body)
                    console.print(f"\n[green]Response saved to {output}[/green]")
                else:
                    if verbose:
                        console.print("\n[bold]Response Body:[/bold]")
                        console.print(body[:500] + "..." if len(body) > 500 else body)
                
    except Exception as e:
        console.print(f"\n[red]✗ Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--url', '-u', required=True, help='Target URL')
@click.option('--requests', '-n', default=100, help='Number of requests')
@click.option('--concurrency', '-c', default=10, help='Concurrent requests')
@click.option('--method', '-m', default='GET', help='HTTP method')
@click.option('--duration', '-d', type=int, help='Test duration in seconds')
def load_test(url, requests, concurrency, method, duration):
    """Run load test against URL."""
    asyncio.run(_load_test(url, requests, concurrency, method, duration))


async def _load_test(url, num_requests, concurrency, method, duration):
    """Async load test implementation."""
    print_banner()
    
    console.print(Panel.fit(
        f"[bold]Load Test Configuration[/bold]\n\n"
        f"Target: {url}\n"
        f"Requests: {num_requests}\n"
        f"Concurrency: {concurrency}\n"
        f"Method: {method}",
        border_style="cyan"
    ))
    
    config = SlayerConfig.from_env()
    
    results = {
        'success': 0,
        'errors': 0,
        'total_time': 0
    }
    
    async def make_request(client, sem):
        async with sem:
            import time
            start = time.time()
            try:
                response = await client.request(method, url)
                results['success'] += 1
                return time.time() - start
            except Exception as e:
                results['errors'] += 1
                return 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Running load test...", total=num_requests)
        
        async with SlayerClient(config) as client:
            sem = asyncio.Semaphore(concurrency)
            tasks = [make_request(client, sem) for _ in range(num_requests)]
            
            import time
            start_time = time.time()
            times = await asyncio.gather(*tasks)
            total_duration = time.time() - start_time
            
            progress.update(task, completed=num_requests)
    
    # Display results
    table = Table(title="Load Test Results", border_style="green")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")
    
    successful_times = [t for t in times if t > 0]
    avg_time = sum(successful_times) / len(successful_times) if successful_times else 0
    
    table.add_row("Total Requests", str(num_requests))
    table.add_row("Successful", f"[green]{results['success']}[/green]")
    table.add_row("Errors", f"[red]{results['errors']}[/red]")
    table.add_row("Duration", f"{total_duration:.2f}s")
    table.add_row("Requests/sec", f"{num_requests/total_duration:.2f}")
    table.add_row("Avg Response Time", f"{avg_time*1000:.2f}ms")
    
    console.print("\n")
    console.print(table)


@cli.command()
@click.option('--config', '-c', help='Configuration file')
def stats(config):
    """Display client statistics."""
    asyncio.run(_stats(config))


async def _stats(config_file):
    """Display statistics."""
    print_banner()
    
    if config_file:
        cfg = SlayerConfig.from_file(config_file)
    else:
        cfg = SlayerConfig.from_env()
    
    async with SlayerClient(cfg) as client:
        stats = client.get_stats()
        
        # Display stats in table
        table = Table(title="SLAYER Statistics", border_style="cyan")
        table.add_column("Component", style="cyan")
        table.add_column("Metric", style="yellow")
        table.add_column("Value", style="green")
        
        # Version info
        table.add_row("System", "Version", stats['version'])
        table.add_row("System", "Environment", stats['environment'])
        
        # Metrics
        if 'metrics' in stats:
            m = stats['metrics']
            table.add_row("Metrics", "Total Requests", str(m.get('total_requests', 0)))
            table.add_row("Metrics", "Req/sec", f"{m.get('requests_per_second', 0):.2f}")
            table.add_row("Metrics", "Active Requests", str(m.get('active_requests', 0)))
        
        # Cache
        if 'cache' in stats:
            c = stats['cache']
            table.add_row("Cache", "Hit Rate", f"{c.get('hit_rate', 0)*100:.1f}%")
            table.add_row("Cache", "Hits", str(c.get('hits', 0)))
            table.add_row("Cache", "Misses", str(c.get('misses', 0)))
        
        console.print("\n")
        console.print(table)


@cli.command()
def config_template():
    """Generate configuration template."""
    config = SlayerConfig()
    print(config.to_json())


@cli.command()
@click.option('--config', '-c', help='Configuration file')
def health(config):
    """Check client health."""
    asyncio.run(_health(config))


async def _health(config_file):
    """Health check."""
    if config_file:
        cfg = SlayerConfig.from_file(config_file)
    else:
        cfg = SlayerConfig.from_env()
    
    async with SlayerClient(cfg) as client:
        health = client.health_check()
        
        if health['status'] == 'healthy':
            console.print("[green]✓ System is healthy[/green]")
        else:
            console.print(f"[red]✗ System status: {health['status']}[/red]")


if __name__ == '__main__':
    print_banner()
    cli()
