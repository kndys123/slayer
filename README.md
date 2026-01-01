# SLAYER - Professional Load Testing Tool

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Enterprise-grade HTTP load testing tool with built-in authorization, audit logging, and comprehensive performance metrics.

## 🚀 Features

### Security & Compliance
- ✅ **Authorization Framework** - Token-based target verification
- ✅ **Target Allowlist** - Only authorized endpoints can be tested
- ✅ **Audit Logging** - Comprehensive JSON and text logs for compliance
- ✅ **Rate Limiting** - Configurable safety limits and controls

### Performance Testing
- 📊 **Advanced Metrics** - Response time percentiles (P95, P99), mean, median
- ⚡ **Concurrent Testing** - Multi-threaded request execution
- 🎯 **Multiple HTTP Methods** - GET, POST, PUT, DELETE, HEAD, OPTIONS, PATCH
- 📈 **Real-time Statistics** - Live monitoring during test execution

### Professional Features
- 🔄 **Retry Logic** - Automatic retry with exponential backoff
- 🔐 **Custom Headers** - Add authentication and custom headers
- 📝 **Request Body Support** - JSON payload configuration
- 🎨 **Colorized Output** - Clear, readable terminal interface
- 📊 **Comprehensive Reports** - Detailed performance analysis

## 📋 Requirements

- Python 3.8 or higher
- `requests` library

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/kndys123/slayer.git
cd slayer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the tool:
```bash
python professional_load_tester.py
```

## 💡 Quick Start

### 1. Authorize a Target

First, you must authorize the target endpoint with an API token:

```
authorize https://api.example.com your-secret-token-123
```

You'll be prompted for an optional description for documentation purposes.

### 2. Configure Test Parameters

```
set target https://api.example.com/endpoint
set method POST
set delay 0.5
set threads 10
set duration 60
```

### 3. Run the Test

```
run
```

Press `Ctrl+C` to stop the test at any time.

## 📖 Command Reference

### Configuration Commands

| Command | Description | Example |
|---------|-------------|---------|
| `set target <url>` | Set the target URL | `set target https://api.example.com/v1/users` |
| `set method <METHOD>` | Set HTTP method | `set method POST` |
| `set delay <seconds>` | Delay between requests | `set delay 0.5` |
| `set threads <number>` | Number of concurrent threads | `set threads 10` |
| `set duration <seconds>` | Test duration limit | `set duration 300` |
| `set maxreq <number>` | Maximum request count | `set maxreq 1000` |
| `set header <key> <value>` | Add custom header | `set header X-API-Key abc123` |
| `set body <json>` | Set request body | `set body {"key": "value"}` |

### Authorization Commands

| Command | Description |
|---------|-------------|
| `authorize <url> <token>` | Authorize target with API token |
| `targets` | List all authorized targets |

### Testing Commands

| Command | Description |
|---------|-------------|
| `run` | Start the load test |
| `stop` | Stop running test |
| `status` | Show configuration and stats |

### System Commands

| Command | Description |
|---------|-------------|
| `help` | Display help menu |
| `clear` | Clear screen |
| `logs` | Show audit log location |
| `exit` | Exit application |

## 📊 Performance Metrics

The tool provides comprehensive performance analysis:

- **Response Times**: Min, Max, Mean, Median
- **Percentiles**: P95, P99 for SLA verification
- **Standard Deviation**: Measure response consistency
- **Status Code Distribution**: Track HTTP response codes
- **Error Analysis**: Categorized error types
- **Throughput**: Requests per second

## 🔒 Security Features

### Target Authorization

All targets must be explicitly authorized before testing:

```bash
authorize https://api.example.com my-secret-token-123
```

The tool stores a hashed version of your token for security.

### Audit Logging

All operations are logged to:
- `logs/audit_YYYYMMDD_HHMMSS.log` (text format)
- `logs/audit_YYYYMMDD_HHMMSS.json` (structured format)

Logs include:
- Test configuration
- Authorization events
- Test execution details
- Performance metrics

### Safety Limits

Configurable limits prevent accidental abuse:
- Maximum threads per test
- Maximum test duration
- Maximum requests per second
- Maximum total requests

Edit `load_test_config.json` to adjust limits.

## 📝 Configuration File

The tool creates `load_test_config.json` to store:

```json
{
  "authorized_targets": ["api.example.com"],
  "api_tokens": {
    "api.example.com": {
      "token_hash": "sha256_hash",
      "description": "Production API",
      "added": "2026-01-01T12:00:00"
    }
  },
  "max_rps": 100,
  "max_threads": 20,
  "max_duration": 3600
}
```

## 🎯 Use Cases

### API Load Testing
Test your API endpoints under various load conditions to identify performance bottlenecks.

### Stress Testing
Determine the breaking point of your infrastructure by gradually increasing load.

### Capacity Planning
Gather performance metrics to make informed infrastructure decisions.

### SLA Verification
Verify that response times meet service level agreements (P95, P99).

### CI/CD Integration
Integrate load testing into your continuous integration pipeline.

## ⚠️ Important Usage Notes

### Legal & Ethical Guidelines

1. **Authorization Required**: Only test systems you own or have explicit permission to test
2. **Respect Rate Limits**: Configure appropriate delays to avoid overwhelming targets
3. **Production Caution**: Use care when testing production systems
4. **Coordinate with Teams**: Inform your team before running load tests
5. **Monitor Impact**: Watch system resources during tests

### Best Practices

- Start with low thread counts and increase gradually
- Use appropriate delays between requests
- Monitor both the testing tool and target system
- Run tests during off-peak hours when possible
- Keep audit logs for compliance and analysis
- Review reports to identify performance patterns

## 🐛 Troubleshooting

### Connection Errors

If you encounter connection errors:
- Verify the target URL is correct
- Check network connectivity
- Ensure the target allows incoming connections
- Verify firewall rules

### Authorization Failures

If authorization fails:
- Confirm the token is correct
- Re-authorize the target
- Check `load_test_config.json` for proper configuration

### Performance Issues

If the tool is slow:
- Reduce thread count
- Increase delay between requests
- Check system resources (CPU, memory)
- Verify network bandwidth

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review audit logs for debugging

## 🙏 Acknowledgments

Built for professional security testing and performance analysis.

---

**⚠️ DISCLAIMER**: This tool is intended for authorized security testing and performance analysis only. Users are responsible for ensuring they have proper authorization before testing any system. Unauthorized testing may be illegal in your jurisdiction.
