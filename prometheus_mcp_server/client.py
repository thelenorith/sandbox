"""Prometheus HTTP client for querying metrics."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

from prometheus_mcp_server.config import PrometheusConfig

logger = logging.getLogger(__name__)


class PrometheusError(Exception):
    """Base exception for Prometheus client errors."""

    pass


class PrometheusConnectionError(PrometheusError):
    """Error connecting to Prometheus server."""

    pass


class PrometheusQueryError(PrometheusError):
    """Error executing Prometheus query."""

    pass


@dataclass
class QueryResult:
    """Result from a Prometheus query."""

    status: str
    data: dict[str, Any]
    result_type: str
    warnings: list[str] | None = None

    @property
    def results(self) -> list[dict[str, Any]]:
        """Get the result list from the data."""
        return self.data.get("result", [])

    @property
    def is_success(self) -> bool:
        """Check if query was successful."""
        return self.status == "success"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status,
            "data": self.data,
            "result_type": self.result_type,
            "warnings": self.warnings,
        }


@dataclass
class MetricMetadata:
    """Metadata about a metric."""

    name: str
    type: str
    help: str
    unit: str = ""


class PrometheusClient:
    """Async client for Prometheus HTTP API."""

    def __init__(self, config: PrometheusConfig) -> None:
        """Initialize the client with configuration."""
        self.config = config
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "PrometheusClient":
        """Enter async context."""
        await self._ensure_client()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context."""
        await self.close()

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            auth = None
            if self.config.username and self.config.password:
                auth = httpx.BasicAuth(self.config.username, self.config.password)

            self._client = httpx.AsyncClient(
                base_url=self.config.url,
                auth=auth,
                headers=self.config.headers,
                timeout=httpx.Timeout(self.config.timeout),
                verify=self.config.verify_ssl,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Make an HTTP request to Prometheus."""
        client = await self._ensure_client()
        try:
            response = await client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            raise PrometheusConnectionError(
                f"Failed to connect to {self.config.url}: {e}"
            ) from e
        except httpx.HTTPStatusError as e:
            raise PrometheusQueryError(
                f"HTTP {e.response.status_code}: {e.response.text}"
            ) from e
        except httpx.TimeoutException as e:
            raise PrometheusConnectionError(
                f"Request timed out after {self.config.timeout}s: {e}"
            ) from e

    async def query(
        self,
        query: str,
        time: datetime | str | None = None,
        timeout: str | None = None,
    ) -> QueryResult:
        """Execute an instant query.

        Args:
            query: PromQL query string
            time: Evaluation timestamp (optional, defaults to current time)
            timeout: Evaluation timeout (optional)

        Returns:
            QueryResult with the query results
        """
        params: dict[str, Any] = {"query": query}
        if time is not None:
            if isinstance(time, datetime):
                params["time"] = time.isoformat()
            else:
                params["time"] = time
        if timeout:
            params["timeout"] = timeout

        logger.debug(f"Executing instant query: {query}")
        data = await self._request("GET", "/api/v1/query", params=params)

        return QueryResult(
            status=data.get("status", "error"),
            data=data.get("data", {}),
            result_type=data.get("data", {}).get("resultType", "unknown"),
            warnings=data.get("warnings"),
        )

    async def query_range(
        self,
        query: str,
        start: datetime | str,
        end: datetime | str,
        step: str,
        timeout: str | None = None,
    ) -> QueryResult:
        """Execute a range query.

        Args:
            query: PromQL query string
            start: Start timestamp
            end: End timestamp
            step: Query resolution step (e.g., "15s", "1m", "1h")
            timeout: Evaluation timeout (optional)

        Returns:
            QueryResult with the range query results
        """
        params: dict[str, Any] = {
            "query": query,
            "step": step,
        }

        if isinstance(start, datetime):
            params["start"] = start.isoformat()
        else:
            params["start"] = start

        if isinstance(end, datetime):
            params["end"] = end.isoformat()
        else:
            params["end"] = end

        if timeout:
            params["timeout"] = timeout

        logger.debug(f"Executing range query: {query} from {start} to {end}")
        data = await self._request("GET", "/api/v1/query_range", params=params)

        return QueryResult(
            status=data.get("status", "error"),
            data=data.get("data", {}),
            result_type=data.get("data", {}).get("resultType", "unknown"),
            warnings=data.get("warnings"),
        )

    async def get_labels(self, match: list[str] | None = None) -> list[str]:
        """Get all label names.

        Args:
            match: Optional series selectors to filter labels

        Returns:
            List of label names
        """
        params = {}
        if match:
            params["match[]"] = match

        data = await self._request("GET", "/api/v1/labels", params=params)
        return data.get("data", [])

    async def get_label_values(
        self, label: str, match: list[str] | None = None
    ) -> list[str]:
        """Get values for a specific label.

        Args:
            label: Label name to get values for
            match: Optional series selectors to filter values

        Returns:
            List of label values
        """
        params = {}
        if match:
            params["match[]"] = match

        data = await self._request(
            "GET", f"/api/v1/label/{label}/values", params=params
        )
        return data.get("data", [])

    async def get_series(
        self,
        match: list[str],
        start: datetime | str | None = None,
        end: datetime | str | None = None,
    ) -> list[dict[str, str]]:
        """Get series matching label selectors.

        Args:
            match: Series selectors (at least one required)
            start: Start timestamp (optional)
            end: End timestamp (optional)

        Returns:
            List of series label sets
        """
        params: dict[str, Any] = {"match[]": match}

        if start:
            if isinstance(start, datetime):
                params["start"] = start.isoformat()
            else:
                params["start"] = start

        if end:
            if isinstance(end, datetime):
                params["end"] = end.isoformat()
            else:
                params["end"] = end

        data = await self._request("GET", "/api/v1/series", params=params)
        return data.get("data", [])

    async def get_metadata(
        self, metric: str | None = None, limit: int | None = None
    ) -> dict[str, list[MetricMetadata]]:
        """Get metadata about metrics.

        Args:
            metric: Optional metric name to filter
            limit: Maximum number of metrics to return

        Returns:
            Dictionary mapping metric names to their metadata
        """
        params: dict[str, Any] = {}
        if metric:
            params["metric"] = metric
        if limit:
            params["limit"] = limit

        data = await self._request("GET", "/api/v1/metadata", params=params)
        raw_metadata = data.get("data", {})

        result: dict[str, list[MetricMetadata]] = {}
        for name, entries in raw_metadata.items():
            result[name] = [
                MetricMetadata(
                    name=name,
                    type=entry.get("type", "unknown"),
                    help=entry.get("help", ""),
                    unit=entry.get("unit", ""),
                )
                for entry in entries
            ]
        return result

    async def get_targets(
        self, state: str | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        """Get information about scrape targets.

        Args:
            state: Filter by target state ("active", "dropped", "any")

        Returns:
            Dictionary with "activeTargets" and "droppedTargets" lists
        """
        params = {}
        if state:
            params["state"] = state

        data = await self._request("GET", "/api/v1/targets", params=params)
        return data.get("data", {})

    async def get_rules(self, type: str | None = None) -> dict[str, Any]:
        """Get alerting and recording rules.

        Args:
            type: Filter by rule type ("alert" or "record")

        Returns:
            Dictionary with rule groups
        """
        params = {}
        if type:
            params["type"] = type

        data = await self._request("GET", "/api/v1/rules", params=params)
        return data.get("data", {})

    async def get_alerts(self) -> list[dict[str, Any]]:
        """Get active alerts.

        Returns:
            List of active alerts
        """
        data = await self._request("GET", "/api/v1/alerts")
        return data.get("data", {}).get("alerts", [])

    async def check_health(self) -> bool:
        """Check if Prometheus server is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            client = await self._ensure_client()
            response = await client.get("/-/healthy")
            return response.status_code == 200
        except Exception:
            return False

    async def check_ready(self) -> bool:
        """Check if Prometheus server is ready.

        Returns:
            True if ready, False otherwise
        """
        try:
            client = await self._ensure_client()
            response = await client.get("/-/ready")
            return response.status_code == 200
        except Exception:
            return False
