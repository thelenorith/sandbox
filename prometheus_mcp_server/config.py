"""Configuration management for Prometheus MCP Server."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class PrometheusConfig(BaseModel):
    """Configuration for a single Prometheus server."""

    name: str = Field(description="unique identifier for this prometheus instance")
    url: str = Field(description="base URL of the prometheus server")
    username: str | None = Field(
        default=None, description="username for basic auth (optional)"
    )
    password: str | None = Field(
        default=None, description="password for basic auth (optional)"
    )
    headers: dict[str, str] = Field(
        default_factory=dict, description="additional headers to send with requests"
    )
    timeout: float = Field(default=30.0, description="request timeout in seconds", gt=0)
    verify_ssl: bool = Field(default=True, description="verify SSL certificates")
    default: bool = Field(
        default=False, description="use this server as default when not specified"
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensure URL doesn't have trailing slash."""
        return v.rstrip("/")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is a valid identifier."""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("name must be alphanumeric with hyphens/underscores")
        return v


class ServerConfig(BaseSettings):
    """Main server configuration loaded from environment and config files."""

    model_config = SettingsConfigDict(
        env_prefix="PROMETHEUS_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    debug: bool = Field(default=False, description="enable debug logging")
    config_file: Path | None = Field(
        default=None, description="path to JSON/YAML config file"
    )
    prometheus_servers: list[PrometheusConfig] = Field(
        default_factory=list, description="list of prometheus server configurations"
    )

    @classmethod
    def load(
        cls,
        config_file: Path | None = None,
        env_url: str | None = None,
    ) -> ServerConfig:
        """Load configuration from file and environment.

        Priority (highest to lowest):
        1. Environment variables (PROMETHEUS_MCP_*)
        2. Config file specified via argument or PROMETHEUS_MCP_CONFIG_FILE
        3. Default config locations (~/.config/prometheus-mcp/config.json)
        4. Defaults
        """
        servers: list[PrometheusConfig] = []

        config_path = config_file or os.environ.get("PROMETHEUS_MCP_CONFIG_FILE")
        if config_path:
            config_path = Path(config_path)

        if not config_path:
            default_paths = [
                Path.home() / ".config" / "prometheus-mcp" / "config.json",
                Path("prometheus-mcp.json"),
            ]
            for p in default_paths:
                if p.exists():
                    config_path = p
                    break

        if config_path and config_path.exists():
            servers = cls._load_from_file(config_path)
            logger.info(f"Loaded configuration from {config_path}")

        url_from_env = env_url or os.environ.get("PROMETHEUS_MCP_URL")
        if url_from_env:
            env_server = PrometheusConfig(
                name=os.environ.get("PROMETHEUS_MCP_NAME", "default"),
                url=url_from_env,
                username=os.environ.get("PROMETHEUS_MCP_USERNAME"),
                password=os.environ.get("PROMETHEUS_MCP_PASSWORD"),
                timeout=float(os.environ.get("PROMETHEUS_MCP_TIMEOUT", "30")),
                verify_ssl=os.environ.get("PROMETHEUS_MCP_VERIFY_SSL", "true").lower()
                == "true",
                default=True,
            )
            existing_names = {s.name for s in servers}
            if env_server.name in existing_names:
                servers = [
                    env_server if s.name == env_server.name else s for s in servers
                ]
            else:
                servers.insert(0, env_server)
            logger.info(f"Added/updated server from environment: {env_server.name}")

        debug = os.environ.get("PROMETHEUS_MCP_DEBUG", "false").lower() == "true"

        return cls(
            debug=debug,
            config_file=config_path,
            prometheus_servers=servers,
        )

    @staticmethod
    def _load_from_file(path: Path) -> list[PrometheusConfig]:
        """Load server configurations from a JSON file."""
        with open(path) as f:
            data = json.load(f)

        servers_data = data.get("servers", [])
        if not servers_data and "url" in data:
            servers_data = [data]

        return [PrometheusConfig(**s) for s in servers_data]

    def get_server(self, name: str | None = None) -> PrometheusConfig:
        """Get a prometheus server configuration by name or return default."""
        if not self.prometheus_servers:
            raise ValueError(
                "No Prometheus servers configured. "
                "Set PROMETHEUS_MCP_URL or provide a config file."
            )

        if name:
            for server in self.prometheus_servers:
                if server.name == name:
                    return server
            raise ValueError(f"Prometheus server '{name}' not found")

        for server in self.prometheus_servers:
            if server.default:
                return server

        return self.prometheus_servers[0]

    def get_server_names(self) -> list[str]:
        """Get list of all configured server names."""
        return [s.name for s in self.prometheus_servers]

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary (excluding sensitive data)."""
        return {
            "debug": self.debug,
            "config_file": str(self.config_file) if self.config_file else None,
            "servers": [
                {
                    "name": s.name,
                    "url": s.url,
                    "has_auth": bool(s.username),
                    "timeout": s.timeout,
                    "verify_ssl": s.verify_ssl,
                    "default": s.default,
                }
                for s in self.prometheus_servers
            ],
        }
