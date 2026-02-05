"""Tests for Prometheus client module."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx
import pytest
import respx

from prometheus_mcp_server.client import (
    PrometheusClient,
    PrometheusConnectionError,
    PrometheusQueryError,
    QueryResult,
)
from prometheus_mcp_server.config import PrometheusConfig


class TestQueryResult:
    """Tests for QueryResult."""

    def test_results_property(self) -> None:
        """Test results property extracts result list."""
        qr = QueryResult(
            status="success",
            data={"result": [{"metric": {}, "value": [1, "1"]}]},
            result_type="vector",
        )
        assert len(qr.results) == 1

    def test_results_empty(self) -> None:
        """Test results returns empty list when no result."""
        qr = QueryResult(status="success", data={}, result_type="vector")
        assert qr.results == []

    def test_is_success(self) -> None:
        """Test is_success property."""
        qr = QueryResult(status="success", data={}, result_type="vector")
        assert qr.is_success is True

        qr2 = QueryResult(status="error", data={}, result_type="vector")
        assert qr2.is_success is False

    def test_to_dict(self) -> None:
        """Test to_dict serialization."""
        qr = QueryResult(
            status="success",
            data={"result": []},
            result_type="vector",
            warnings=["test warning"],
        )
        d = qr.to_dict()
        assert d["status"] == "success"
        assert d["warnings"] == ["test warning"]


class TestPrometheusClient:
    """Tests for PrometheusClient."""

    @pytest.mark.asyncio
    async def test_context_manager(self, prometheus_config: PrometheusConfig) -> None:
        """Test async context manager."""
        async with PrometheusClient(prometheus_config) as client:
            assert client._client is not None
        assert client._client is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_query_success(
        self,
        prometheus_config: PrometheusConfig,
        mock_query_response: dict[str, Any],
    ) -> None:
        """Test successful instant query."""
        respx.get(f"{prometheus_config.url}/api/v1/query").mock(
            return_value=httpx.Response(200, json=mock_query_response)
        )

        async with PrometheusClient(prometheus_config) as client:
            result = await client.query("up")

        assert result.is_success
        assert result.result_type == "vector"
        assert len(result.results) == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_query_with_time(
        self,
        prometheus_config: PrometheusConfig,
        mock_query_response: dict[str, Any],
    ) -> None:
        """Test query with explicit time."""
        route = respx.get(f"{prometheus_config.url}/api/v1/query").mock(
            return_value=httpx.Response(200, json=mock_query_response)
        )

        async with PrometheusClient(prometheus_config) as client:
            await client.query("up", time="2024-01-01T00:00:00Z")

        assert "time=2024-01-01T00" in str(route.calls[0].request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_query_with_datetime(
        self,
        prometheus_config: PrometheusConfig,
        mock_query_response: dict[str, Any],
    ) -> None:
        """Test query with datetime object."""
        respx.get(f"{prometheus_config.url}/api/v1/query").mock(
            return_value=httpx.Response(200, json=mock_query_response)
        )

        async with PrometheusClient(prometheus_config) as client:
            dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
            result = await client.query("up", time=dt)

        assert result.is_success

    @pytest.mark.asyncio
    @respx.mock
    async def test_query_range_success(
        self,
        prometheus_config: PrometheusConfig,
        mock_range_query_response: dict[str, Any],
    ) -> None:
        """Test successful range query."""
        respx.get(f"{prometheus_config.url}/api/v1/query_range").mock(
            return_value=httpx.Response(200, json=mock_range_query_response)
        )

        async with PrometheusClient(prometheus_config) as client:
            result = await client.query_range(
                "node_cpu_seconds_total",
                start="2024-01-01T00:00:00Z",
                end="2024-01-01T01:00:00Z",
                step="15s",
            )

        assert result.is_success
        assert result.result_type == "matrix"
        assert len(result.results) == 1
        assert len(result.results[0]["values"]) == 4

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_labels(
        self,
        prometheus_config: PrometheusConfig,
        mock_labels_response: dict[str, Any],
    ) -> None:
        """Test getting label names."""
        respx.get(f"{prometheus_config.url}/api/v1/labels").mock(
            return_value=httpx.Response(200, json=mock_labels_response)
        )

        async with PrometheusClient(prometheus_config) as client:
            labels = await client.get_labels()

        assert "job" in labels
        assert "__name__" in labels

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_label_values(
        self,
        prometheus_config: PrometheusConfig,
        mock_label_values_response: dict[str, Any],
    ) -> None:
        """Test getting label values."""
        respx.get(f"{prometheus_config.url}/api/v1/label/job/values").mock(
            return_value=httpx.Response(200, json=mock_label_values_response)
        )

        async with PrometheusClient(prometheus_config) as client:
            values = await client.get_label_values("job")

        assert "prometheus" in values
        assert "node" in values

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_series(
        self,
        prometheus_config: PrometheusConfig,
        mock_series_response: dict[str, Any],
    ) -> None:
        """Test getting series."""
        respx.get(f"{prometheus_config.url}/api/v1/series").mock(
            return_value=httpx.Response(200, json=mock_series_response)
        )

        async with PrometheusClient(prometheus_config) as client:
            series = await client.get_series(match=["up"])

        assert len(series) == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_metadata(
        self,
        prometheus_config: PrometheusConfig,
        mock_metadata_response: dict[str, Any],
    ) -> None:
        """Test getting metadata."""
        respx.get(f"{prometheus_config.url}/api/v1/metadata").mock(
            return_value=httpx.Response(200, json=mock_metadata_response)
        )

        async with PrometheusClient(prometheus_config) as client:
            metadata = await client.get_metadata()

        assert "up" in metadata
        assert metadata["up"][0].type == "gauge"
        assert "health" in metadata["up"][0].help

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_targets(
        self,
        prometheus_config: PrometheusConfig,
        mock_targets_response: dict[str, Any],
    ) -> None:
        """Test getting targets."""
        respx.get(f"{prometheus_config.url}/api/v1/targets").mock(
            return_value=httpx.Response(200, json=mock_targets_response)
        )

        async with PrometheusClient(prometheus_config) as client:
            targets = await client.get_targets()

        assert len(targets["activeTargets"]) == 2
        assert targets["activeTargets"][0]["health"] == "up"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_alerts(
        self,
        prometheus_config: PrometheusConfig,
        mock_alerts_response: dict[str, Any],
    ) -> None:
        """Test getting alerts."""
        respx.get(f"{prometheus_config.url}/api/v1/alerts").mock(
            return_value=httpx.Response(200, json=mock_alerts_response)
        )

        async with PrometheusClient(prometheus_config) as client:
            alerts = await client.get_alerts()

        assert len(alerts) == 2
        assert alerts[0]["state"] == "firing"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_rules(
        self,
        prometheus_config: PrometheusConfig,
        mock_rules_response: dict[str, Any],
    ) -> None:
        """Test getting rules."""
        respx.get(f"{prometheus_config.url}/api/v1/rules").mock(
            return_value=httpx.Response(200, json=mock_rules_response)
        )

        async with PrometheusClient(prometheus_config) as client:
            rules = await client.get_rules()

        assert "groups" in rules
        assert len(rules["groups"]) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_check_health(self, prometheus_config: PrometheusConfig) -> None:
        """Test health check."""
        respx.get(f"{prometheus_config.url}/-/healthy").mock(
            return_value=httpx.Response(200, text="OK")
        )

        async with PrometheusClient(prometheus_config) as client:
            healthy = await client.check_health()

        assert healthy is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_check_health_unhealthy(
        self, prometheus_config: PrometheusConfig
    ) -> None:
        """Test health check when unhealthy."""
        respx.get(f"{prometheus_config.url}/-/healthy").mock(
            return_value=httpx.Response(503)
        )

        async with PrometheusClient(prometheus_config) as client:
            healthy = await client.check_health()

        assert healthy is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_check_ready(self, prometheus_config: PrometheusConfig) -> None:
        """Test ready check."""
        respx.get(f"{prometheus_config.url}/-/ready").mock(
            return_value=httpx.Response(200, text="OK")
        )

        async with PrometheusClient(prometheus_config) as client:
            ready = await client.check_ready()

        assert ready is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_connection_error(self, prometheus_config: PrometheusConfig) -> None:
        """Test handling connection errors."""
        respx.get(f"{prometheus_config.url}/api/v1/query").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        async with PrometheusClient(prometheus_config) as client:
            with pytest.raises(PrometheusConnectionError, match="Connection refused"):
                await client.query("up")

    @pytest.mark.asyncio
    @respx.mock
    async def test_timeout_error(self, prometheus_config: PrometheusConfig) -> None:
        """Test handling timeout errors."""
        respx.get(f"{prometheus_config.url}/api/v1/query").mock(
            side_effect=httpx.TimeoutException("Timeout")
        )

        async with PrometheusClient(prometheus_config) as client:
            with pytest.raises(PrometheusConnectionError, match="timed out"):
                await client.query("up")

    @pytest.mark.asyncio
    @respx.mock
    async def test_http_error(self, prometheus_config: PrometheusConfig) -> None:
        """Test handling HTTP errors."""
        respx.get(f"{prometheus_config.url}/api/v1/query").mock(
            return_value=httpx.Response(400, text="Bad Request")
        )

        async with PrometheusClient(prometheus_config) as client:
            with pytest.raises(PrometheusQueryError, match="400"):
                await client.query("invalid{")

    @pytest.mark.asyncio
    @respx.mock
    async def test_client_with_auth(
        self,
        prometheus_config_with_auth: PrometheusConfig,
        mock_query_response: dict[str, Any],
    ) -> None:
        """Test client with basic auth."""
        route = respx.get(f"{prometheus_config_with_auth.url}/api/v1/query").mock(
            return_value=httpx.Response(200, json=mock_query_response)
        )

        async with PrometheusClient(prometheus_config_with_auth) as client:
            await client.query("up")

        assert "Authorization" in route.calls[0].request.headers
