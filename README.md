# prometheus-mcp-server

[![Test](https://github.com/thelenorith/prometheus-mcp-server/actions/workflows/test.yml/badge.svg)](https://github.com/thelenorith/prometheus-mcp-server/actions/workflows/test.yml)
[![Coverage](https://github.com/thelenorith/prometheus-mcp-server/actions/workflows/coverage.yml/badge.svg)](https://github.com/thelenorith/prometheus-mcp-server/actions/workflows/coverage.yml)
[![Lint](https://github.com/thelenorith/prometheus-mcp-server/actions/workflows/lint.yml/badge.svg)](https://github.com/thelenorith/prometheus-mcp-server/actions/workflows/lint.yml)
[![Format](https://github.com/thelenorith/prometheus-mcp-server/actions/workflows/format.yml/badge.svg)](https://github.com/thelenorith/prometheus-mcp-server/actions/workflows/format.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

MCP server for querying and analyzing Prometheus metrics with server-side computation to reduce token usage.

## Overview

prometheus-mcp-server provides a Model Context Protocol (MCP) server that enables LLMs to interact with Prometheus monitoring systems. It offloads computation from the LLM client by performing aggregations, analysis, and formatting server-side.

**Key features:**

- Query Prometheus metrics using PromQL
- Server-side aggregation and statistics to reduce token consumption
- Multi-server support with easy configuration
- Pre-built analysis prompts for common scenarios
- Resources for metric catalogs, alerting rules, and server status

## Installation

### Development Installation

```bash
git clone https://github.com/thelenorith/prometheus-mcp-server.git
cd prometheus-mcp-server
make install-dev
```

### pip Installation

```bash
pip install git+https://github.com/thelenorith/prometheus-mcp-server.git
```

## Configuration

### Environment Variables

The simplest way to configure a single Prometheus server:

```bash
export PROMETHEUS_MCP_URL="http://prometheus.example.com:9090"
export PROMETHEUS_MCP_NAME="production"  # optional, defaults to "default"
export PROMETHEUS_MCP_USERNAME="admin"    # optional, for basic auth
export PROMETHEUS_MCP_PASSWORD="secret"   # optional, for basic auth
export PROMETHEUS_MCP_DEBUG="true"        # optional, enable debug logging
```

### Configuration File

For multiple servers or advanced configuration, create a JSON config file:

```json
{
  "servers": [
    {
      "name": "production",
      "url": "http://prometheus-prod.example.com:9090",
      "default": true,
      "timeout": 30,
      "verify_ssl": true
    },
    {
      "name": "staging",
      "url": "http://prometheus-staging.example.com:9090",
      "username": "readonly",
      "password": "secret",
      "headers": {
        "X-Custom-Header": "value"
      }
    }
  ]
}
```

Default config file locations (checked in order):
1. `~/.config/prometheus-mcp/config.json`
2. `./prometheus-mcp.json`

Or specify explicitly:

```bash
prometheus-mcp-server --config /path/to/config.json
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | string | required | Unique identifier for the server |
| `url` | string | required | Prometheus server base URL |
| `username` | string | null | Username for basic auth |
| `password` | string | null | Password for basic auth |
| `headers` | object | {} | Additional HTTP headers |
| `timeout` | float | 30.0 | Request timeout in seconds |
| `verify_ssl` | bool | true | Verify SSL certificates |
| `default` | bool | false | Use as default server |

## Usage

### Running the Server

```bash
# With environment variable
export PROMETHEUS_MCP_URL="http://localhost:9090"
prometheus-mcp-server

# With config file
prometheus-mcp-server --config ./config.json

# With URL override
prometheus-mcp-server --url http://localhost:9090

# Show loaded configuration
prometheus-mcp-server --show-config

# Enable debug logging
prometheus-mcp-server --debug
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--config`, `-c` | Path to configuration file |
| `--url` | Prometheus URL (overrides config) |
| `--debug` | Enable debug output |
| `--quiet`, `-q` | Suppress non-essential output |
| `--show-config` | Show loaded configuration and exit |
| `--version` | Show version and exit |

### MCP Client Configuration

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "prometheus": {
      "command": "prometheus-mcp-server",
      "args": ["--config", "/path/to/config.json"],
      "env": {
        "PROMETHEUS_MCP_URL": "http://localhost:9090"
      }
    }
  }
}
```

## Tools

The server provides these MCP tools:

| Tool | Description |
|------|-------------|
| `prometheus_query` | Execute instant PromQL queries |
| `prometheus_query_range` | Execute range queries with server-side statistics |
| `prometheus_analyze_metric` | Comprehensive metric analysis (metadata, values, trends) |
| `prometheus_discover_metrics` | Discover metrics matching a pattern |
| `prometheus_health` | Check Prometheus server health and status |
| `prometheus_alerts` | Get current alerts with firing/pending status |
| `prometheus_targets` | Get scrape target information |
| `prometheus_servers` | List configured Prometheus servers |

### Example Tool Usage

```
# Query current values
prometheus_query(query="up")

# Range query with statistics
prometheus_query_range(
  query="rate(http_requests_total[5m])",
  start="-1h",
  end="now",
  step="1m"
)

# Analyze a metric comprehensively
prometheus_analyze_metric(
  metric_name="node_cpu_seconds_total",
  duration="24h"
)

# Discover memory-related metrics
prometheus_discover_metrics(pattern="memory")
```

## Resources

The server exposes these MCP resources:

| Resource | Description |
|----------|-------------|
| `prometheus://{server}/info` | Server status and health overview |
| `prometheus://{server}/metrics` | Categorized metric catalog |
| `prometheus://{server}/alerts/rules` | Alerting rules configuration |
| `prometheus://{server}/recording/rules` | Recording rules configuration |

## Prompts

Pre-built analysis prompts that guide the LLM through common workflows:

| Prompt | Description |
|--------|-------------|
| `analyze_high_cpu` | Investigate high CPU usage |
| `analyze_memory_pressure` | Check memory and OOM risks |
| `investigate_alert` | Deep-dive into a firing alert |
| `capacity_planning` | Generate capacity planning report |
| `service_health_check` | Comprehensive service health check |
| `debug_scrape_failures` | Debug failing scrape targets |
| `compare_periods` | Compare metrics between time periods |
| `create_alert_rule` | Help create new alerting rules |

## Development

```bash
# Install development dependencies
make install-dev

# Run all checks
make

# Individual targets
make format      # Format code with black
make lint        # Lint with flake8
make typecheck   # Type check with mypy
make test        # Run tests
make coverage    # Run tests with coverage report
```

## License

MIT License - see [LICENSE](LICENSE) for details.
