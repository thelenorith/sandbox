"""Shared fixtures for tests."""

from __future__ import annotations

from typing import Any

import pytest

from prometheus_mcp_server.config import PrometheusConfig, ServerConfig


@pytest.fixture
def prometheus_config() -> PrometheusConfig:
    """Create a test Prometheus configuration."""
    return PrometheusConfig(
        name="test-server",
        url="http://localhost:9090",
        timeout=10.0,
        default=True,
    )


@pytest.fixture
def prometheus_config_with_auth() -> PrometheusConfig:
    """Create a test Prometheus configuration with auth."""
    return PrometheusConfig(
        name="auth-server",
        url="http://localhost:9090",
        username="user",
        password="pass",
        timeout=10.0,
    )


@pytest.fixture
def server_config(prometheus_config: PrometheusConfig) -> ServerConfig:
    """Create a test server configuration."""
    return ServerConfig(
        debug=False,
        prometheus_servers=[prometheus_config],
    )


@pytest.fixture
def multi_server_config() -> ServerConfig:
    """Create a configuration with multiple servers."""
    return ServerConfig(
        debug=False,
        prometheus_servers=[
            PrometheusConfig(
                name="prod",
                url="http://prometheus-prod:9090",
                default=True,
            ),
            PrometheusConfig(
                name="staging",
                url="http://prometheus-staging:9090",
            ),
        ],
    )


@pytest.fixture
def mock_query_response() -> dict[str, Any]:
    """Mock response for instant query."""
    return {
        "status": "success",
        "data": {
            "resultType": "vector",
            "result": [
                {
                    "metric": {
                        "__name__": "up",
                        "job": "prometheus",
                        "instance": "localhost:9090",
                    },
                    "value": [1704067200, "1"],
                },
                {
                    "metric": {
                        "__name__": "up",
                        "job": "node",
                        "instance": "localhost:9100",
                    },
                    "value": [1704067200, "1"],
                },
            ],
        },
    }


@pytest.fixture
def mock_range_query_response() -> dict[str, Any]:
    """Mock response for range query."""
    return {
        "status": "success",
        "data": {
            "resultType": "matrix",
            "result": [
                {
                    "metric": {
                        "__name__": "node_cpu_seconds_total",
                        "cpu": "0",
                        "mode": "idle",
                    },
                    "values": [
                        [1704067200, "100.5"],
                        [1704067215, "101.2"],
                        [1704067230, "102.0"],
                        [1704067245, "102.8"],
                    ],
                },
            ],
        },
    }


@pytest.fixture
def mock_labels_response() -> dict[str, Any]:
    """Mock response for labels endpoint."""
    return {
        "status": "success",
        "data": ["__name__", "instance", "job", "mode", "cpu"],
    }


@pytest.fixture
def mock_label_values_response() -> dict[str, Any]:
    """Mock response for label values endpoint."""
    return {
        "status": "success",
        "data": ["prometheus", "node", "alertmanager"],
    }


@pytest.fixture
def mock_metadata_response() -> dict[str, Any]:
    """Mock response for metadata endpoint."""
    return {
        "status": "success",
        "data": {
            "up": [
                {
                    "type": "gauge",
                    "help": "The current health status of the target",
                    "unit": "",
                }
            ],
            "node_cpu_seconds_total": [
                {
                    "type": "counter",
                    "help": "Seconds the CPUs spent in each mode",
                    "unit": "",
                }
            ],
            "node_memory_MemTotal_bytes": [
                {
                    "type": "gauge",
                    "help": "Total memory in bytes",
                    "unit": "bytes",
                }
            ],
        },
    }


@pytest.fixture
def mock_targets_response() -> dict[str, Any]:
    """Mock response for targets endpoint."""
    return {
        "status": "success",
        "data": {
            "activeTargets": [
                {
                    "discoveredLabels": {},
                    "labels": {"job": "prometheus", "instance": "localhost:9090"},
                    "scrapeUrl": "http://localhost:9090/metrics",
                    "health": "up",
                    "lastScrape": "2024-01-01T00:00:00Z",
                    "lastScrapeDuration": 0.005,
                },
                {
                    "discoveredLabels": {},
                    "labels": {"job": "node", "instance": "localhost:9100"},
                    "scrapeUrl": "http://localhost:9100/metrics",
                    "health": "down",
                    "lastScrape": "2024-01-01T00:00:00Z",
                    "lastScrapeDuration": 0.0,
                    "lastError": "connection refused",
                },
            ],
            "droppedTargets": [],
        },
    }


@pytest.fixture
def mock_alerts_response() -> dict[str, Any]:
    """Mock response for alerts endpoint."""
    return {
        "status": "success",
        "data": {
            "alerts": [
                {
                    "labels": {
                        "alertname": "HighMemoryUsage",
                        "severity": "warning",
                        "instance": "localhost:9100",
                    },
                    "annotations": {
                        "summary": "High memory usage detected",
                        "description": "Memory usage is above 80%",
                    },
                    "state": "firing",
                    "activeAt": "2024-01-01T00:00:00Z",
                },
                {
                    "labels": {
                        "alertname": "DiskSpaceLow",
                        "severity": "critical",
                    },
                    "annotations": {
                        "summary": "Disk space is low",
                    },
                    "state": "pending",
                    "activeAt": "2024-01-01T00:00:00Z",
                },
            ],
        },
    }


@pytest.fixture
def mock_rules_response() -> dict[str, Any]:
    """Mock response for rules endpoint."""
    return {
        "status": "success",
        "data": {
            "groups": [
                {
                    "name": "example",
                    "file": "/etc/prometheus/rules/example.yml",
                    "rules": [
                        {
                            "name": "HighMemoryUsage",
                            "query": (
                                "node_memory_MemAvailable_bytes "
                                "/ node_memory_MemTotal_bytes < 0.2"
                            ),
                            "duration": "5m",
                            "labels": {"severity": "warning"},
                            "annotations": {"summary": "High memory usage"},
                            "state": "firing",
                            "type": "alerting",
                        },
                    ],
                },
            ],
        },
    }


@pytest.fixture
def mock_series_response() -> dict[str, Any]:
    """Mock response for series endpoint."""
    return {
        "status": "success",
        "data": [
            {"__name__": "up", "job": "prometheus", "instance": "localhost:9090"},
            {"__name__": "up", "job": "node", "instance": "localhost:9100"},
        ],
    }
