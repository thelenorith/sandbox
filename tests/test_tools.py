"""Tests for Prometheus tools module."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from prometheus_mcp_server.config import PrometheusConfig, ServerConfig
from prometheus_mcp_server.tools import (
    PrometheusTools,
    format_bytes,
    format_duration,
    format_value,
    get_tool_definitions,
)


class TestFormatters:
    """Tests for formatting functions."""

    def test_format_bytes_bytes(self) -> None:
        """Test formatting bytes."""
        assert format_bytes(500) == "500.00 B"

    def test_format_bytes_kb(self) -> None:
        """Test formatting kilobytes."""
        assert format_bytes(1536) == "1.50 KB"

    def test_format_bytes_mb(self) -> None:
        """Test formatting megabytes."""
        assert format_bytes(1_500_000) == "1.43 MB"

    def test_format_bytes_gb(self) -> None:
        """Test formatting gigabytes."""
        assert format_bytes(2_000_000_000) == "1.86 GB"

    def test_format_duration_seconds(self) -> None:
        """Test formatting seconds."""
        assert format_duration(45) == "45.00s"

    def test_format_duration_minutes(self) -> None:
        """Test formatting minutes."""
        assert format_duration(120) == "2.00m"

    def test_format_duration_hours(self) -> None:
        """Test formatting hours."""
        assert format_duration(7200) == "2.00h"

    def test_format_duration_days(self) -> None:
        """Test formatting days."""
        assert format_duration(172800) == "2.00d"

    def test_format_value_bytes_metric(self) -> None:
        """Test formatting based on metric name."""
        assert "MB" in format_value(1_500_000, "node_memory_bytes")

    def test_format_value_duration_metric(self) -> None:
        """Test formatting duration metrics."""
        assert "s" in format_value(45.5, "request_duration_seconds")

    def test_format_value_percent_metric(self) -> None:
        """Test formatting percentage metrics."""
        assert "%" in format_value(0.85, "cpu_percent")

    def test_format_value_large_number(self) -> None:
        """Test formatting large numbers."""
        result = format_value(1_500_000_000, "requests_total")
        assert "e" in result

    def test_format_value_integer(self) -> None:
        """Test formatting integers."""
        assert format_value(42.0, "count") == "42"


class TestToolDefinitions:
    """Tests for tool definitions."""

    def test_get_tool_definitions(self) -> None:
        """Test that tool definitions are returned."""
        definitions = get_tool_definitions()
        assert len(definitions) > 0

    def test_tool_definitions_have_required_fields(self) -> None:
        """Test that all tools have required fields."""
        definitions = get_tool_definitions()
        for tool in definitions:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            assert tool["inputSchema"]["type"] == "object"

    def test_query_tool_exists(self) -> None:
        """Test that query tool exists."""
        definitions = get_tool_definitions()
        names = [t["name"] for t in definitions]
        assert "prometheus_query" in names

    def test_query_range_tool_exists(self) -> None:
        """Test that query_range tool exists."""
        definitions = get_tool_definitions()
        names = [t["name"] for t in definitions]
        assert "prometheus_query_range" in names

    def test_analyze_metric_tool_exists(self) -> None:
        """Test that analyze_metric tool exists."""
        definitions = get_tool_definitions()
        names = [t["name"] for t in definitions]
        assert "prometheus_analyze_metric" in names


class TestPrometheusTools:
    """Tests for PrometheusTools class."""

    @pytest.fixture
    def tools(self, server_config: ServerConfig) -> PrometheusTools:
        """Create a tools instance."""
        return PrometheusTools(server_config)

    @pytest.mark.asyncio
    @respx.mock
    async def test_query(
        self,
        tools: PrometheusTools,
        prometheus_config: PrometheusConfig,
        mock_query_response: dict[str, Any],
    ) -> None:
        """Test query tool."""
        respx.get(f"{prometheus_config.url}/api/v1/query").mock(
            return_value=httpx.Response(200, json=mock_query_response)
        )

        result = await tools.query("up")

        assert result["status"] == "success"
        assert result["result_count"] == 2
        assert len(result["results"]) == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_query_formats_values(
        self,
        tools: PrometheusTools,
        prometheus_config: PrometheusConfig,
    ) -> None:
        """Test that query formats values."""
        response = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {"__name__": "node_memory_bytes"},
                        "value": [1704067200, "1073741824"],
                    },
                ],
            },
        }
        respx.get(f"{prometheus_config.url}/api/v1/query").mock(
            return_value=httpx.Response(200, json=response)
        )

        result = await tools.query("node_memory_bytes")

        assert "GB" in result["results"][0]["formatted_value"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_query_error(
        self,
        tools: PrometheusTools,
        prometheus_config: PrometheusConfig,
    ) -> None:
        """Test query error handling."""
        respx.get(f"{prometheus_config.url}/api/v1/query").mock(
            return_value=httpx.Response(400, text="Bad Request")
        )

        result = await tools.query("invalid{")

        assert result["status"] == "error"
        assert "error" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_query_range(
        self,
        tools: PrometheusTools,
        prometheus_config: PrometheusConfig,
        mock_range_query_response: dict[str, Any],
    ) -> None:
        """Test query_range tool."""
        respx.get(f"{prometheus_config.url}/api/v1/query_range").mock(
            return_value=httpx.Response(200, json=mock_range_query_response)
        )

        result = await tools.query_range(
            query="node_cpu_seconds_total",
            start="-1h",
            end="now",
            step="15s",
        )

        assert result["status"] == "success"
        assert result["series_count"] == 1
        assert "statistics" in result["series"][0]

    @pytest.mark.asyncio
    @respx.mock
    async def test_query_range_statistics(
        self,
        tools: PrometheusTools,
        prometheus_config: PrometheusConfig,
        mock_range_query_response: dict[str, Any],
    ) -> None:
        """Test that query_range computes statistics."""
        respx.get(f"{prometheus_config.url}/api/v1/query_range").mock(
            return_value=httpx.Response(200, json=mock_range_query_response)
        )

        result = await tools.query_range(
            query="node_cpu_seconds_total",
            start="-1h",
            end="now",
            step="15s",
        )

        stats = result["series"][0]["statistics"]
        assert "min" in stats
        assert "max" in stats
        assert "avg" in stats
        assert "current" in stats
        assert stats["min"] == 100.5
        assert stats["max"] == 102.8

    @pytest.mark.asyncio
    @respx.mock
    async def test_discover_metrics(
        self,
        tools: PrometheusTools,
        prometheus_config: PrometheusConfig,
        mock_metadata_response: dict[str, Any],
    ) -> None:
        """Test discover_metrics tool."""
        respx.get(f"{prometheus_config.url}/api/v1/metadata").mock(
            return_value=httpx.Response(200, json=mock_metadata_response)
        )

        result = await tools.discover_metrics()

        assert result["total_found"] == 3
        assert len(result["metrics"]) == 3

    @pytest.mark.asyncio
    @respx.mock
    async def test_discover_metrics_with_pattern(
        self,
        tools: PrometheusTools,
        prometheus_config: PrometheusConfig,
        mock_metadata_response: dict[str, Any],
    ) -> None:
        """Test discover_metrics with pattern filter."""
        respx.get(f"{prometheus_config.url}/api/v1/metadata").mock(
            return_value=httpx.Response(200, json=mock_metadata_response)
        )

        result = await tools.discover_metrics(pattern="node")

        assert result["total_found"] == 2
        for metric in result["metrics"]:
            assert "node" in metric["name"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_check_health(
        self,
        tools: PrometheusTools,
        prometheus_config: PrometheusConfig,
        mock_targets_response: dict[str, Any],
        mock_alerts_response: dict[str, Any],
    ) -> None:
        """Test check_health tool."""
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

        result = await tools.check_health()

        assert result["health"]["healthy"] is True
        assert result["health"]["ready"] is True
        assert result["targets"]["total"] == 2
        assert result["targets"]["healthy"] == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_alerts(
        self,
        tools: PrometheusTools,
        prometheus_config: PrometheusConfig,
        mock_alerts_response: dict[str, Any],
        mock_rules_response: dict[str, Any],
    ) -> None:
        """Test get_alerts tool."""
        respx.get(f"{prometheus_config.url}/api/v1/alerts").mock(
            return_value=httpx.Response(200, json=mock_alerts_response)
        )
        respx.get(f"{prometheus_config.url}/api/v1/rules").mock(
            return_value=httpx.Response(200, json=mock_rules_response)
        )

        result = await tools.get_alerts()

        assert result["summary"]["total_alerts"] == 2
        assert result["summary"]["firing"] == 1
        assert result["summary"]["pending"] == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_targets(
        self,
        tools: PrometheusTools,
        prometheus_config: PrometheusConfig,
        mock_targets_response: dict[str, Any],
    ) -> None:
        """Test get_targets tool."""
        respx.get(f"{prometheus_config.url}/api/v1/targets").mock(
            return_value=httpx.Response(200, json=mock_targets_response)
        )

        result = await tools.get_targets()

        assert result["summary"]["total_active"] == 2
        assert result["summary"]["healthy"] == 1
        assert result["summary"]["unhealthy"] == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_targets_unhealthy_only(
        self,
        tools: PrometheusTools,
        prometheus_config: PrometheusConfig,
        mock_targets_response: dict[str, Any],
    ) -> None:
        """Test get_targets with unhealthy_only filter."""
        respx.get(f"{prometheus_config.url}/api/v1/targets").mock(
            return_value=httpx.Response(200, json=mock_targets_response)
        )

        result = await tools.get_targets(unhealthy_only=True)

        assert "healthy_targets" not in result
        assert len(result["unhealthy_targets"]) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_servers(
        self,
        tools: PrometheusTools,
        prometheus_config: PrometheusConfig,
    ) -> None:
        """Test list_servers tool."""
        respx.get(f"{prometheus_config.url}/-/healthy").mock(
            return_value=httpx.Response(200, text="OK")
        )

        result = await tools.list_servers()

        assert result["server_count"] == 1
        assert result["servers"][0]["name"] == "test-server"
        assert result["servers"][0]["healthy"] is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_analyze_metric(
        self,
        tools: PrometheusTools,
        prometheus_config: PrometheusConfig,
        mock_metadata_response: dict[str, Any],
        mock_query_response: dict[str, Any],
        mock_range_query_response: dict[str, Any],
        mock_label_values_response: dict[str, Any],
    ) -> None:
        """Test analyze_metric tool."""
        respx.get(f"{prometheus_config.url}/api/v1/metadata").mock(
            return_value=httpx.Response(200, json=mock_metadata_response)
        )
        respx.get(f"{prometheus_config.url}/api/v1/query").mock(
            return_value=httpx.Response(200, json=mock_query_response)
        )
        respx.get(f"{prometheus_config.url}/api/v1/query_range").mock(
            return_value=httpx.Response(200, json=mock_range_query_response)
        )
        respx.get(url__regex=r".*/api/v1/label/.*/values").mock(
            return_value=httpx.Response(200, json=mock_label_values_response)
        )

        result = await tools.analyze_metric("up")

        assert result["metric_name"] == "up"
        assert "metadata" in result
        assert "current_state" in result
        assert "historical_analysis" in result
        assert "label_cardinality" in result

    def test_parse_duration(self, tools: PrometheusTools) -> None:
        """Test duration parsing."""
        assert tools._parse_duration("30s").total_seconds() == 30
        assert tools._parse_duration("5m").total_seconds() == 300
        assert tools._parse_duration("2h").total_seconds() == 7200
        assert tools._parse_duration("1d").total_seconds() == 86400
        assert tools._parse_duration("1w").total_seconds() == 604800

    def test_parse_duration_invalid(self, tools: PrometheusTools) -> None:
        """Test invalid duration parsing."""
        with pytest.raises(ValueError, match="Unknown duration unit"):
            tools._parse_duration("5x")

    def test_calculate_step(self, tools: PrometheusTools) -> None:
        """Test step calculation."""
        from datetime import timedelta

        assert tools._calculate_step(timedelta(minutes=30)) == "15s"
        assert tools._calculate_step(timedelta(hours=6)) == "1m"
        assert tools._calculate_step(timedelta(days=3)) == "5m"
        assert tools._calculate_step(timedelta(days=14)) == "1h"

    @pytest.mark.asyncio
    async def test_close(self, tools: PrometheusTools) -> None:
        """Test closing tool connections."""
        await tools.close()
        assert tools._clients == {}
