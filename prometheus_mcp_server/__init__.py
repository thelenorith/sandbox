"""Prometheus MCP Server - MCP server for interacting with Prometheus."""

__version__ = "0.1.0"

from prometheus_mcp_server.server import create_server
from prometheus_mcp_server.config import PrometheusConfig, ServerConfig

__all__ = ["create_server", "PrometheusConfig", "ServerConfig", "__version__"]
