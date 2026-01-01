# SLAYER Enterprise - Quick Start Guide

## Installation

```bash
# Clone repository
git clone https://github.com/kndys123/slayer.git
cd slayer

# Install dependencies
pip install -r requirements.txt
```

## First Request

```python
import asyncio
from slayer_enterprise import SlayerClient

async def main():
    async with SlayerClient() as client:
        response = await client.get('https://httpbin.org/get')
        print(await response.json())

asyncio.run(main())
```

## CLI Usage

```bash
# Simple request
python slayer_enterprise_cli.py request -u https://httpbin.org/get

# Load test
python slayer_enterprise_cli.py load-test -u https://httpbin.org/get -n 100 -c 10

# View stats
python slayer_enterprise_cli.py stats
```

## Configuration

### Environment Variables
```bash
export SLAYER_ENV=production
export SLAYER_LOG_LEVEL=INFO
```

### Config File
```python
from slayer_enterprise.core.config import SlayerConfig

config = SlayerConfig.from_file('config/production.json')
client = SlayerClient(config)
```

## Testing

```bash
pytest tests/ -v
```

## Documentation

- Full documentation: [README_ENTERPRISE.md](README_ENTERPRISE.md)
- Executive report: [docs/EXECUTIVE_REPORT.md](docs/EXECUTIVE_REPORT.md)
- Examples: [examples/](examples/)

## Support

GitHub Issues: https://github.com/kndys123/slayer/issues
