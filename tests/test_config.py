"""Tests for configuration module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from prometheus_mcp_server.config import PrometheusConfig, ServerConfig


class TestPrometheusConfig:
    """Tests for PrometheusConfig."""

    def test_basic_config(self) -> None:
        """Test creating a basic configuration."""
        config = PrometheusConfig(
            name="test",
            url="http://localhost:9090",
        )
        assert config.name == "test"
        assert config.url == "http://localhost:9090"
        assert config.username is None
        assert config.password is None
        assert config.timeout == 30.0
        assert config.verify_ssl is True
        assert config.default is False

    def test_url_trailing_slash_removed(self) -> None:
        """Test that trailing slash is removed from URL."""
        config = PrometheusConfig(
            name="test",
            url="http://localhost:9090/",
        )
        assert config.url == "http://localhost:9090"

    def test_config_with_auth(self) -> None:
        """Test configuration with authentication."""
        config = PrometheusConfig(
            name="test",
            url="http://localhost:9090",
            username="admin",
            password="secret",
        )
        assert config.username == "admin"
        assert config.password == "secret"

    def test_config_with_headers(self) -> None:
        """Test configuration with custom headers."""
        config = PrometheusConfig(
            name="test",
            url="http://localhost:9090",
            headers={"X-Custom": "value"},
        )
        assert config.headers == {"X-Custom": "value"}

    def test_invalid_name_rejected(self) -> None:
        """Test that invalid names are rejected."""
        with pytest.raises(ValueError, match="alphanumeric"):
            PrometheusConfig(
                name="test server!",
                url="http://localhost:9090",
            )

    def test_valid_name_with_hyphens(self) -> None:
        """Test that names with hyphens are valid."""
        config = PrometheusConfig(
            name="test-server-1",
            url="http://localhost:9090",
        )
        assert config.name == "test-server-1"

    def test_valid_name_with_underscores(self) -> None:
        """Test that names with underscores are valid."""
        config = PrometheusConfig(
            name="test_server_1",
            url="http://localhost:9090",
        )
        assert config.name == "test_server_1"

    def test_timeout_must_be_positive(self) -> None:
        """Test that timeout must be positive."""
        with pytest.raises(ValueError):
            PrometheusConfig(
                name="test",
                url="http://localhost:9090",
                timeout=0,
            )


class TestServerConfig:
    """Tests for ServerConfig."""

    def test_empty_config(self) -> None:
        """Test creating an empty configuration."""
        config = ServerConfig()
        assert config.debug is False
        assert config.prometheus_servers == []

    def test_get_server_no_servers(self) -> None:
        """Test get_server raises when no servers configured."""
        config = ServerConfig()
        with pytest.raises(ValueError, match="No Prometheus servers"):
            config.get_server()

    def test_get_server_by_name(self, multi_server_config: ServerConfig) -> None:
        """Test getting a server by name."""
        server = multi_server_config.get_server("staging")
        assert server.name == "staging"
        assert "staging" in server.url

    def test_get_server_not_found(self, multi_server_config: ServerConfig) -> None:
        """Test get_server raises for unknown name."""
        with pytest.raises(ValueError, match="not found"):
            multi_server_config.get_server("unknown")

    def test_get_default_server(self, multi_server_config: ServerConfig) -> None:
        """Test getting the default server."""
        server = multi_server_config.get_server()
        assert server.name == "prod"
        assert server.default is True

    def test_get_first_server_when_no_default(self) -> None:
        """Test getting first server when no default is set."""
        config = ServerConfig(
            prometheus_servers=[
                PrometheusConfig(name="first", url="http://first:9090"),
                PrometheusConfig(name="second", url="http://second:9090"),
            ]
        )
        server = config.get_server()
        assert server.name == "first"

    def test_get_server_names(self, multi_server_config: ServerConfig) -> None:
        """Test getting all server names."""
        names = multi_server_config.get_server_names()
        assert names == ["prod", "staging"]

    def test_to_dict_hides_password(self) -> None:
        """Test that to_dict excludes sensitive data."""
        config = ServerConfig(
            prometheus_servers=[
                PrometheusConfig(
                    name="test",
                    url="http://localhost:9090",
                    username="admin",
                    password="secret",
                )
            ]
        )
        result = config.to_dict()
        assert "password" not in str(result)
        assert result["servers"][0]["has_auth"] is True

    def test_load_from_environment(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test loading configuration from environment variables."""
        monkeypatch.setenv("PROMETHEUS_MCP_URL", "http://env-server:9090")
        monkeypatch.setenv("PROMETHEUS_MCP_NAME", "env-test")
        monkeypatch.setenv("PROMETHEUS_MCP_DEBUG", "true")

        config = ServerConfig.load()

        assert config.debug is True
        assert len(config.prometheus_servers) == 1
        assert config.prometheus_servers[0].name == "env-test"
        assert config.prometheus_servers[0].url == "http://env-server:9090"

    def test_load_from_file(self, tmp_path: Path) -> None:
        """Test loading configuration from a JSON file."""
        config_file = tmp_path / "config.json"
        config_data = {
            "servers": [
                {"name": "file-server", "url": "http://file:9090"},
                {"name": "file-server-2", "url": "http://file2:9090"},
            ]
        }
        config_file.write_text(json.dumps(config_data))

        config = ServerConfig.load(config_file=config_file)

        assert len(config.prometheus_servers) == 2
        assert config.prometheus_servers[0].name == "file-server"

    def test_load_single_server_format(self, tmp_path: Path) -> None:
        """Test loading single-server format config file."""
        config_file = tmp_path / "config.json"
        config_data = {"name": "single", "url": "http://single:9090"}
        config_file.write_text(json.dumps(config_data))

        config = ServerConfig.load(config_file=config_file)

        assert len(config.prometheus_servers) == 1
        assert config.prometheus_servers[0].name == "single"

    def test_env_overrides_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that environment variables override file config."""
        config_file = tmp_path / "config.json"
        config_data = {
            "servers": [
                {"name": "file-server", "url": "http://file:9090"},
            ]
        }
        config_file.write_text(json.dumps(config_data))

        monkeypatch.setenv("PROMETHEUS_MCP_URL", "http://env:9090")
        monkeypatch.setenv("PROMETHEUS_MCP_NAME", "file-server")

        config = ServerConfig.load(config_file=config_file)

        file_server = config.get_server("file-server")
        assert file_server.url == "http://env:9090"
        assert file_server.default is True

    def test_env_adds_new_server(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that env adds new server if name differs."""
        config_file = tmp_path / "config.json"
        config_data = {
            "servers": [
                {"name": "file-server", "url": "http://file:9090"},
            ]
        }
        config_file.write_text(json.dumps(config_data))

        monkeypatch.setenv("PROMETHEUS_MCP_URL", "http://env:9090")
        monkeypatch.setenv("PROMETHEUS_MCP_NAME", "env-server")

        config = ServerConfig.load(config_file=config_file)

        assert len(config.prometheus_servers) == 2
        assert config.prometheus_servers[0].name == "env-server"
