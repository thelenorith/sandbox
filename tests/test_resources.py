"""Tests for Prometheus resources module."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest
import respx

from prometheus_mcp_server.config import PrometheusConfig, ServerConfig
from prometheus_mcp_server.resources import (
    PrometheusResources,
    get_resource_definitions,
)


class TestResourceDefinitions:
    """Tests for resource definitions."""

    def test_get_resource_definitions_empty(self) -> None:
        """Test with no servers configured."""
        config = ServerConfig()
        definitions = get_resource_definitions(config)
        assert definitions == []

    def test_get_resource_definitions_single_server(
        self, server_config: ServerConfig
    ) -> None:
        """Test with single server."""
        definitions = get_resource_definitions(server_config)

        assert len(definitions) > 0

        uris = [r["uri"] for r in definitions]
        assert "prometheus://test-server/info" in uris
        assert "prometheus://test-server/metrics" in uris
        assert "prometheus://default/info" in uris

    def test_get_resource_definitions_multi_server(
        self, multi_server_config: ServerConfig
    ) -> None:
        """Test with multiple servers."""
        definitions = get_resource_definitions(multi_server_config)

        uris = [r["uri"] for r in definitions]
        assert "prometheus://prod/info" in uris
        assert "prometheus://staging/info" in uris

    def test_resource_definitions_have_required_fields(
        self, server_config: ServerConfig
    ) -> None:
        """Test that all resources have required fields."""
        definitions = get_resource_definitions(server_config)

        for resource in definitions:
            assert "uri" in resource
            assert "name" in resource
            assert "description" in resource
            assert "mimeType" in resource
            assert resource["mimeType"] == "application/json"


class TestPrometheusResources:
    """Tests for PrometheusResources class."""

    @pytest.fixture
    def resources(self, server_config: ServerConfig) -> PrometheusResources:
        """Create a resources instance."""
        return PrometheusResources(server_config)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_server_info(
        self,
        resources: PrometheusResources,
        prometheus_config: PrometheusConfig,
        mock_targets_response: dict[str, Any],
        mock_alerts_response: dict[str, Any],
    ) -> None:
        """Test get_server_info resource."""
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

        result_str = await resources.get_server_info()
        result = json.loads(result_str)

        assert result["server"]["healthy"] is True
        assert result["server"]["ready"] is True
        assert result["targets"]["total"] == 2
        assert result["alerts"]["firing"] == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_server_info_unhealthy(
        self,
        resources: PrometheusResources,
        prometheus_config: PrometheusConfig,
    ) -> None:
        """Test get_server_info when server is unhealthy."""
        respx.get(f"{prometheus_config.url}/-/healthy").mock(
            return_value=httpx.Response(503)
        )
        respx.get(f"{prometheus_config.url}/-/ready").mock(
            return_value=httpx.Response(503)
        )

        result_str = await resources.get_server_info()
        result = json.loads(result_str)

        assert result["server"]["healthy"] is False
        assert result["server"]["ready"] is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_server_info_connection_error(
        self,
        resources: PrometheusResources,
        prometheus_config: PrometheusConfig,
    ) -> None:
        """Test get_server_info when connection fails on health check.

        When the health check fails with a connection error, the client
        catches it internally and returns False (not an exception).
        """
        respx.get(f"{prometheus_config.url}/-/healthy").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        respx.get(f"{prometheus_config.url}/-/ready").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        result_str = await resources.get_server_info()
        result = json.loads(result_str)

        assert result["server"]["healthy"] is False
        assert result["server"]["ready"] is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_server_info_error_after_health(
        self,
        resources: PrometheusResources,
        prometheus_config: PrometheusConfig,
    ) -> None:
        """Test get_server_info when error occurs after health check passes."""
        respx.get(f"{prometheus_config.url}/-/healthy").mock(
            return_value=httpx.Response(200, text="OK")
        )
        respx.get(f"{prometheus_config.url}/-/ready").mock(
            return_value=httpx.Response(200, text="OK")
        )
        respx.get(f"{prometheus_config.url}/api/v1/targets").mock(
            side_effect=httpx.ConnectError("Connection lost")
        )

        result_str = await resources.get_server_info()
        result = json.loads(result_str)

        assert result["server"]["healthy"] is False
        assert "error" in result["server"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_metric_catalog(
        self,
        resources: PrometheusResources,
        prometheus_config: PrometheusConfig,
        mock_metadata_response: dict[str, Any],
    ) -> None:
        """Test get_metric_catalog resource."""
        respx.get(f"{prometheus_config.url}/api/v1/metadata").mock(
            return_value=httpx.Response(200, json=mock_metadata_response)
        )

        result_str = await resources.get_metric_catalog()
        result = json.loads(result_str)

        assert result["total_metrics"] == 3
        assert "categories" in result
        assert "memory" in result["categories"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_metric_catalog_with_category(
        self,
        resources: PrometheusResources,
        prometheus_config: PrometheusConfig,
        mock_metadata_response: dict[str, Any],
    ) -> None:
        """Test get_metric_catalog with category filter."""
        respx.get(f"{prometheus_config.url}/api/v1/metadata").mock(
            return_value=httpx.Response(200, json=mock_metadata_response)
        )

        result_str = await resources.get_metric_catalog(category="memory")
        result = json.loads(result_str)

        assert "memory" in result["categories"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_alerting_rules(
        self,
        resources: PrometheusResources,
        prometheus_config: PrometheusConfig,
        mock_rules_response: dict[str, Any],
    ) -> None:
        """Test get_alerting_rules resource."""
        respx.get(f"{prometheus_config.url}/api/v1/rules").mock(
            return_value=httpx.Response(200, json=mock_rules_response)
        )

        result_str = await resources.get_alerting_rules()
        result = json.loads(result_str)

        assert result["total_groups"] == 1
        assert result["total_rules"] == 1
        assert len(result["groups"]) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_recording_rules(
        self,
        resources: PrometheusResources,
        prometheus_config: PrometheusConfig,
    ) -> None:
        """Test get_recording_rules resource."""
        rules_response = {
            "status": "success",
            "data": {
                "groups": [
                    {
                        "name": "recording_rules",
                        "rules": [
                            {
                                "name": "job:http_requests:rate5m",
                                "query": "sum by(job)(rate(http_requests_total[5m]))",
                                "labels": {},
                                "type": "recording",
                            },
                        ],
                    },
                ],
            },
        }
        respx.get(f"{prometheus_config.url}/api/v1/rules").mock(
            return_value=httpx.Response(200, json=rules_response)
        )

        result_str = await resources.get_recording_rules()
        result = json.loads(result_str)

        assert result["total_groups"] == 1
        assert len(result["groups"]) == 1
        assert result["groups"][0]["rules"][0]["name"] == "job:http_requests:rate5m"
