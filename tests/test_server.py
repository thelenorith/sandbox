"""Tests for MCP server module."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest
import respx

from prometheus_mcp_server.config import PrometheusConfig, ServerConfig
from prometheus_mcp_server.server import create_server
from prometheus_mcp_server.tools import PrometheusTools


class TestCreateServer:
    """Tests for server creation."""

    def test_create_server(self, server_config: ServerConfig) -> None:
        """Test creating a server."""
        server = create_server(server_config)
        assert server is not None
        assert server.name == "prometheus-mcp-server"


class TestServerIntegration:
    """Integration tests for MCP server functionality.

    These tests verify the server components work together correctly
    without testing internal MCP server implementation details.
    """

    @pytest.mark.asyncio
    @respx.mock
    async def test_tools_query_integration(
        self,
        server_config: ServerConfig,
        prometheus_config: PrometheusConfig,
        mock_query_response: dict[str, Any],
    ) -> None:
        """Test that tools can be executed through the server."""
        respx.get(f"{prometheus_config.url}/api/v1/query").mock(
            return_value=httpx.Response(200, json=mock_query_response)
        )

        tools = PrometheusTools(server_config)
        result = await tools.query("up")

        assert result["status"] == "success"
        assert result["result_count"] == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_tools_health_integration(
        self,
        server_config: ServerConfig,
        prometheus_config: PrometheusConfig,
        mock_targets_response: dict[str, Any],
        mock_alerts_response: dict[str, Any],
    ) -> None:
        """Test health check tool integration."""
        respx.get(f"{prometheus_config.url}/-/healthy").mock(
            return_value=httpx.Response(200, text="OK")
        )
        respx.get(f"{prometheus_config.url}/-/ready").mock(
            return_value=httpx.Response(200, text="OK")
        )
        respx.get(f"{prometheus_config.url}/api/v1/targets").mock(
            return_value=httpx.Response(200, json=mock_targets_response)
        )
        respx.get(f"{prometheus_config.url}/api/v1/alerts").mock(
            return_value=httpx.Response(200, json=mock_alerts_response)
        )

        tools = PrometheusTools(server_config)
        result = await tools.check_health()

        assert result["health"]["healthy"] is True
        assert result["health"]["ready"] is True

    @pytest.mark.asyncio
    async def test_tools_list_servers(
        self,
        multi_server_config: ServerConfig,
    ) -> None:
        """Test listing servers tool."""
        with respx.mock:
            respx.get(url__regex=r".*/-/healthy").mock(return_value=httpx.Response(503))

            tools = PrometheusTools(multi_server_config)
            result = await tools.list_servers()

            assert result["server_count"] == 2
            assert len(result["servers"]) == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_resources_server_info_integration(
        self,
        server_config: ServerConfig,
        prometheus_config: PrometheusConfig,
        mock_targets_response: dict[str, Any],
        mock_alerts_response: dict[str, Any],
    ) -> None:
        """Test server info resource integration."""
        from prometheus_mcp_server.resources import PrometheusResources

        respx.get(f"{prometheus_config.url}/-/healthy").mock(
            return_value=httpx.Response(200, text="OK")
        )
        respx.get(f"{prometheus_config.url}/-/ready").mock(
            return_value=httpx.Response(200, text="OK")
        )
        respx.get(f"{prometheus_config.url}/api/v1/targets").mock(
            return_value=httpx.Response(200, json=mock_targets_response)
        )
        respx.get(f"{prometheus_config.url}/api/v1/alerts").mock(
            return_value=httpx.Response(200, json=mock_alerts_response)
        )

        resources = PrometheusResources(server_config)
        result_str = await resources.get_server_info()
        result = json.loads(result_str)

        assert result["server"]["healthy"] is True
        assert result["targets"]["total"] == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_resources_metric_catalog_integration(
        self,
        server_config: ServerConfig,
        prometheus_config: PrometheusConfig,
        mock_metadata_response: dict[str, Any],
    ) -> None:
        """Test metric catalog resource integration."""
        from prometheus_mcp_server.resources import PrometheusResources

        respx.get(f"{prometheus_config.url}/api/v1/metadata").mock(
            return_value=httpx.Response(200, json=mock_metadata_response)
        )

        resources = PrometheusResources(server_config)
        result_str = await resources.get_metric_catalog()
        result = json.loads(result_str)

        assert result["total_metrics"] == 3
        assert "categories" in result


class TestServerToolDefinitions:
    """Tests for tool definitions used by the server."""

    def test_tool_definitions_complete(self) -> None:
        """Test that all expected tools are defined."""
        from prometheus_mcp_server.tools import get_tool_definitions

        definitions = get_tool_definitions()
        expected_tools = [
            "prometheus_query",
            "prometheus_query_range",
            "prometheus_analyze_metric",
            "prometheus_discover_metrics",
            "prometheus_health",
            "prometheus_alerts",
            "prometheus_targets",
            "prometheus_servers",
        ]

        tool_names = [t["name"] for t in definitions]
        for expected in expected_tools:
            assert expected in tool_names, f"Missing tool: {expected}"

    def test_tool_definitions_valid_schema(self) -> None:
        """Test that all tool definitions have valid schemas."""
        from prometheus_mcp_server.tools import get_tool_definitions

        definitions = get_tool_definitions()
        for tool in definitions:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            assert tool["inputSchema"]["type"] == "object"
            assert "properties" in tool["inputSchema"]
            assert "required" in tool["inputSchema"]


class TestServerResourceDefinitions:
    """Tests for resource definitions used by the server."""

    def test_resource_definitions_for_server(self, server_config: ServerConfig) -> None:
        """Test that resources are defined for configured servers."""
        from prometheus_mcp_server.resources import get_resource_definitions

        definitions = get_resource_definitions(server_config)

        uris = [r["uri"] for r in definitions]
        assert any("test-server" in uri for uri in uris)
        assert any("/info" in uri for uri in uris)
        assert any("/metrics" in uri for uri in uris)

    def test_resource_definitions_valid_format(
        self, server_config: ServerConfig
    ) -> None:
        """Test that all resource definitions have valid format."""
        from prometheus_mcp_server.resources import get_resource_definitions

        definitions = get_resource_definitions(server_config)
        for resource in definitions:
            assert "uri" in resource
            assert "name" in resource
            assert "description" in resource
            assert "mimeType" in resource
            assert resource["uri"].startswith("prometheus://")


class TestServerPromptDefinitions:
    """Tests for prompt definitions used by the server."""

    def test_prompt_definitions_complete(self) -> None:
        """Test that all expected prompts are defined."""
        from prometheus_mcp_server.prompts import get_prompt_definitions

        definitions = get_prompt_definitions()
        expected_prompts = [
            "analyze_high_cpu",
            "analyze_memory_pressure",
            "investigate_alert",
            "capacity_planning",
            "service_health_check",
            "debug_scrape_failures",
            "compare_periods",
            "create_alert_rule",
        ]

        prompt_names = [p["name"] for p in definitions]
        for expected in expected_prompts:
            assert expected in prompt_names, f"Missing prompt: {expected}"

    def test_prompt_definitions_valid_format(self) -> None:
        """Test that all prompt definitions have valid format."""
        from prometheus_mcp_server.prompts import get_prompt_definitions

        definitions = get_prompt_definitions()
        for prompt in definitions:
            assert "name" in prompt
            assert "description" in prompt

    def test_prompt_rendering(self) -> None:
        """Test that prompts can be rendered."""
        from prometheus_mcp_server.prompts import render_prompt

        messages = render_prompt("analyze_high_cpu", {"threshold": "90"})
        assert len(messages) > 0
        assert "90%" in messages[0]["content"]
