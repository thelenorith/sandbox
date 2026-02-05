"""MCP tools for Prometheus operations.

These tools offload computation from the LLM by running complex queries
and aggregations server-side, returning summarized results.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from prometheus_mcp_server.client import PrometheusClient, PrometheusError
from prometheus_mcp_server.config import ServerConfig

logger = logging.getLogger(__name__)


def format_bytes(n: float) -> str:
    """Format bytes to human readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(n) < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} PB"


def format_duration(seconds: float) -> str:
    """Format seconds to human readable duration."""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        return f"{seconds / 60:.2f}m"
    elif seconds < 86400:
        return f"{seconds / 3600:.2f}h"
    return f"{seconds / 86400:.2f}d"


def format_value(value: float, metric_name: str = "") -> str:
    """Format a value based on likely metric type."""
    name_lower = metric_name.lower()
    if "bytes" in name_lower or "memory" in name_lower:
        return format_bytes(value)
    elif "seconds" in name_lower or "duration" in name_lower or "latency" in name_lower:
        return format_duration(value)
    elif "percent" in name_lower or "ratio" in name_lower:
        return f"{value * 100:.2f}%"
    elif value > 1_000_000:
        return f"{value:.2e}"
    elif value == int(value):
        return str(int(value))
    return f"{value:.4f}"


class PrometheusTools:
    """Collection of MCP tools for Prometheus operations."""

    def __init__(self, config: ServerConfig) -> None:
        """Initialize tools with server configuration."""
        self.config = config
        self._clients: dict[str, PrometheusClient] = {}

    def _get_client(self, server_name: str | None = None) -> PrometheusClient:
        """Get or create a client for the specified server."""
        server_config = self.config.get_server(server_name)
        if server_config.name not in self._clients:
            self._clients[server_config.name] = PrometheusClient(server_config)
        return self._clients[server_config.name]

    async def close(self) -> None:
        """Close all client connections."""
        for client in self._clients.values():
            await client.close()
        self._clients.clear()

    async def query(
        self,
        query: str,
        server: str | None = None,
        time: str | None = None,
    ) -> dict[str, Any]:
        """Execute an instant PromQL query.

        Args:
            query: PromQL query string
            server: Server name (optional, uses default)
            time: Evaluation timestamp in RFC3339 or Unix format (optional)

        Returns:
            Query results with formatted values
        """
        client = self._get_client(server)
        try:
            async with client:
                result = await client.query(query, time=time)

            formatted_results = []
            for item in result.results:
                metric = item.get("metric", {})
                value = item.get("value", [None, None])
                formatted_results.append(
                    {
                        "labels": metric,
                        "timestamp": value[0] if len(value) > 0 else None,
                        "value": value[1] if len(value) > 1 else None,
                        "formatted_value": (
                            format_value(float(value[1]), metric.get("__name__", ""))
                            if len(value) > 1 and value[1] is not None
                            else None
                        ),
                    }
                )

            return {
                "status": result.status,
                "result_type": result.result_type,
                "result_count": len(formatted_results),
                "results": formatted_results,
                "warnings": result.warnings,
            }
        except PrometheusError as e:
            return {"status": "error", "error": str(e)}

    async def query_range(
        self,
        query: str,
        start: str,
        end: str,
        step: str,
        server: str | None = None,
    ) -> dict[str, Any]:
        """Execute a range query and return aggregated statistics.

        This tool runs the query server-side and computes statistics,
        reducing the amount of data sent to the LLM.

        Args:
            query: PromQL query string
            start: Start timestamp (RFC3339 or relative like "-1h")
            end: End timestamp (RFC3339 or relative like "now")
            step: Query resolution (e.g., "15s", "1m", "5m")
            server: Server name (optional, uses default)

        Returns:
            Aggregated statistics for each series
        """
        client = self._get_client(server)

        now = datetime.now(timezone.utc)
        if start.startswith("-"):
            duration = self._parse_duration(start[1:])
            start_time = (now - duration).isoformat()
        else:
            start_time = start

        if end == "now" or end == "":
            end_time = now.isoformat()
        elif end.startswith("-"):
            duration = self._parse_duration(end[1:])
            end_time = (now - duration).isoformat()
        else:
            end_time = end

        try:
            async with client:
                result = await client.query_range(
                    query, start=start_time, end=end_time, step=step
                )

            aggregated = []
            for item in result.results:
                metric = item.get("metric", {})
                values = item.get("values", [])

                if not values:
                    continue

                numeric_values = [float(v[1]) for v in values if v[1] != "NaN"]
                if not numeric_values:
                    continue

                metric_name = metric.get("__name__", "")
                stats = {
                    "labels": metric,
                    "data_points": len(values),
                    "time_range": {
                        "start": values[0][0] if values else None,
                        "end": values[-1][0] if values else None,
                    },
                    "statistics": {
                        "min": min(numeric_values),
                        "max": max(numeric_values),
                        "avg": sum(numeric_values) / len(numeric_values),
                        "current": numeric_values[-1] if numeric_values else None,
                        "min_formatted": format_value(min(numeric_values), metric_name),
                        "max_formatted": format_value(max(numeric_values), metric_name),
                        "avg_formatted": format_value(
                            sum(numeric_values) / len(numeric_values), metric_name
                        ),
                        "current_formatted": (
                            format_value(numeric_values[-1], metric_name)
                            if numeric_values
                            else None
                        ),
                    },
                }
                aggregated.append(stats)

            return {
                "status": result.status,
                "result_type": result.result_type,
                "series_count": len(aggregated),
                "query_range": {"start": start_time, "end": end_time, "step": step},
                "series": aggregated,
                "warnings": result.warnings,
            }
        except PrometheusError as e:
            return {"status": "error", "error": str(e)}

    async def analyze_metric(
        self,
        metric_name: str,
        duration: str = "1h",
        server: str | None = None,
    ) -> dict[str, Any]:
        """Analyze a metric comprehensively.

        This tool runs multiple queries to provide a complete picture
        of a metric, offloading analysis from the LLM.

        Args:
            metric_name: Name of the metric to analyze
            duration: Time window to analyze (e.g., "1h", "24h", "7d")
            server: Server name (optional, uses default)

        Returns:
            Comprehensive analysis including metadata, current values,
            historical stats, and label cardinality
        """
        client = self._get_client(server)

        try:
            async with client:
                metadata = await client.get_metadata(metric=metric_name)
                meta_info = metadata.get(metric_name, [{}])[0] if metadata else {}

                current = await client.query(metric_name)

                now = datetime.now(timezone.utc)
                dur = self._parse_duration(duration)
                start = now - dur
                step = self._calculate_step(dur)

                historical = await client.query_range(
                    metric_name,
                    start=start.isoformat(),
                    end=now.isoformat(),
                    step=step,
                )

                label_analysis = {}
                series_labels = [item.get("metric", {}) for item in current.results]
                all_labels: set[str] = set()
                for labels in series_labels:
                    all_labels.update(labels.keys())
                all_labels.discard("__name__")

                for label in list(all_labels)[:10]:
                    values = await client.get_label_values(
                        label, match=[f"{{{metric_name}}}"]
                    )
                    label_analysis[label] = {
                        "unique_values": len(values),
                        "sample_values": values[:5],
                    }

            all_historical_values = []
            for item in historical.results:
                for _, val in item.get("values", []):
                    if val != "NaN":
                        all_historical_values.append(float(val))

            meta_dict: dict[str, Any]
            if hasattr(meta_info, "__dict__"):
                meta_dict = {
                    "type": getattr(meta_info, "type", "unknown"),
                    "help": getattr(meta_info, "help", ""),
                    "unit": getattr(meta_info, "unit", ""),
                }
            elif isinstance(meta_info, dict):
                meta_dict = meta_info
            else:
                meta_dict = {}

            return {
                "metric_name": metric_name,
                "metadata": meta_dict,
                "current_state": {
                    "series_count": len(current.results),
                    "samples": [
                        {
                            "labels": item.get("metric", {}),
                            "value": item.get("value", [None, None])[1],
                            "formatted": format_value(
                                float(item.get("value", [None, "0"])[1] or 0),
                                metric_name,
                            ),
                        }
                        for item in current.results[:10]
                    ],
                    "truncated": len(current.results) > 10,
                },
                "historical_analysis": {
                    "duration": duration,
                    "data_points": len(all_historical_values),
                    "statistics": (
                        {
                            "min": (
                                min(all_historical_values)
                                if all_historical_values
                                else None
                            ),
                            "max": (
                                max(all_historical_values)
                                if all_historical_values
                                else None
                            ),
                            "avg": (
                                sum(all_historical_values) / len(all_historical_values)
                                if all_historical_values
                                else None
                            ),
                        }
                        if all_historical_values
                        else None
                    ),
                },
                "label_cardinality": label_analysis,
            }
        except PrometheusError as e:
            return {"status": "error", "error": str(e)}

    async def discover_metrics(
        self,
        pattern: str | None = None,
        server: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Discover available metrics matching a pattern.

        Args:
            pattern: Optional substring to filter metric names
            server: Server name (optional, uses default)
            limit: Maximum number of metrics to return

        Returns:
            List of matching metrics with their metadata
        """
        client = self._get_client(server)

        try:
            async with client:
                all_metadata = await client.get_metadata(limit=1000)

                matching = []
                for name, meta_list in all_metadata.items():
                    if pattern and pattern.lower() not in name.lower():
                        continue
                    meta = meta_list[0] if meta_list else None
                    meta_dict: dict[str, str]
                    if meta and hasattr(meta, "type"):
                        meta_dict = {
                            "type": meta.type,
                            "help": meta.help,
                            "unit": meta.unit,
                        }
                    elif isinstance(meta, dict):
                        meta_dict = {
                            "type": meta.get("type", "unknown"),
                            "help": meta.get("help", ""),
                            "unit": meta.get("unit", ""),
                        }
                    else:
                        meta_dict = {"type": "unknown", "help": "", "unit": ""}
                    matching.append({"name": name, "metadata": meta_dict})

                    if len(matching) >= limit:
                        break

                matching.sort(key=lambda x: x["name"])

            return {
                "total_found": len(matching),
                "pattern": pattern,
                "metrics": matching,
                "truncated": len(all_metadata) > limit,
            }
        except PrometheusError as e:
            return {"status": "error", "error": str(e)}

    async def check_health(
        self,
        server: str | None = None,
    ) -> dict[str, Any]:
        """Check the health of a Prometheus server.

        Args:
            server: Server name (optional, uses default)

        Returns:
            Health status information
        """
        client = self._get_client(server)
        server_config = self.config.get_server(server)

        try:
            async with client:
                healthy = await client.check_health()
                ready = await client.check_ready()

                targets = {}
                alerts = []
                if healthy and ready:
                    targets = await client.get_targets()
                    alerts = await client.get_alerts()

            active_targets = targets.get("activeTargets", [])
            healthy_targets = sum(1 for t in active_targets if t.get("health") == "up")

            return {
                "server": {
                    "name": server_config.name,
                    "url": server_config.url,
                },
                "health": {
                    "healthy": healthy,
                    "ready": ready,
                },
                "targets": {
                    "total": len(active_targets),
                    "healthy": healthy_targets,
                    "unhealthy": len(active_targets) - healthy_targets,
                },
                "alerts": {
                    "total": len(alerts),
                    "firing": sum(1 for a in alerts if a.get("state") == "firing"),
                },
            }
        except PrometheusError as e:
            return {
                "server": {
                    "name": server_config.name,
                    "url": server_config.url,
                },
                "health": {"healthy": False, "ready": False},
                "error": str(e),
            }

    async def get_alerts(
        self,
        server: str | None = None,
    ) -> dict[str, Any]:
        """Get current alerts from Prometheus.

        Args:
            server: Server name (optional, uses default)

        Returns:
            List of current alerts with their status
        """
        client = self._get_client(server)

        try:
            async with client:
                alerts = await client.get_alerts()
                rules = await client.get_rules(type="alert")

            firing = [a for a in alerts if a.get("state") == "firing"]
            pending = [a for a in alerts if a.get("state") == "pending"]

            return {
                "summary": {
                    "total_alerts": len(alerts),
                    "firing": len(firing),
                    "pending": len(pending),
                },
                "firing_alerts": [
                    {
                        "name": a.get("labels", {}).get("alertname"),
                        "severity": a.get("labels", {}).get("severity", "unknown"),
                        "summary": a.get("annotations", {}).get("summary", ""),
                        "labels": a.get("labels", {}),
                        "active_since": a.get("activeAt"),
                    }
                    for a in firing
                ],
                "pending_alerts": [
                    {
                        "name": a.get("labels", {}).get("alertname"),
                        "labels": a.get("labels", {}),
                    }
                    for a in pending[:10]
                ],
                "rule_groups": len(rules.get("groups", [])),
            }
        except PrometheusError as e:
            return {"status": "error", "error": str(e)}

    async def get_targets(
        self,
        server: str | None = None,
        unhealthy_only: bool = False,
    ) -> dict[str, Any]:
        """Get scrape target information.

        Args:
            server: Server name (optional, uses default)
            unhealthy_only: Only return unhealthy targets

        Returns:
            Target information grouped by health status
        """
        client = self._get_client(server)

        try:
            async with client:
                data = await client.get_targets()

            active = data.get("activeTargets", [])
            dropped = data.get("droppedTargets", [])

            def format_target(t: dict[str, Any]) -> dict[str, Any]:
                return {
                    "job": t.get("labels", {}).get("job"),
                    "instance": t.get("labels", {}).get("instance"),
                    "health": t.get("health"),
                    "scrape_url": t.get("scrapeUrl"),
                    "last_scrape": t.get("lastScrape"),
                    "last_error": t.get("lastError") or None,
                    "scrape_duration": t.get("lastScrapeDuration"),
                }

            healthy = [format_target(t) for t in active if t.get("health") == "up"]
            unhealthy = [format_target(t) for t in active if t.get("health") != "up"]

            result: dict[str, Any] = {
                "summary": {
                    "total_active": len(active),
                    "healthy": len(healthy),
                    "unhealthy": len(unhealthy),
                    "dropped": len(dropped),
                },
            }

            if unhealthy_only:
                result["unhealthy_targets"] = unhealthy
            else:
                result["healthy_targets"] = healthy[:20]
                result["unhealthy_targets"] = unhealthy
                if len(healthy) > 20:
                    result["healthy_truncated"] = True

            return result
        except PrometheusError as e:
            return {"status": "error", "error": str(e)}

    async def list_servers(self) -> dict[str, Any]:
        """List all configured Prometheus servers.

        Returns:
            List of configured servers with their status
        """
        servers = []
        for server_config in self.config.prometheus_servers:
            client = PrometheusClient(server_config)
            try:
                async with client:
                    healthy = await client.check_health()
            except Exception:
                healthy = False

            servers.append(
                {
                    "name": server_config.name,
                    "url": server_config.url,
                    "default": server_config.default,
                    "healthy": healthy,
                }
            )

        return {
            "server_count": len(servers),
            "servers": servers,
        }

    def _parse_duration(self, duration: str) -> timedelta:
        """Parse a duration string like '1h', '30m', '7d' to timedelta."""
        unit = duration[-1].lower()
        value = int(duration[:-1])

        if unit == "s":
            return timedelta(seconds=value)
        elif unit == "m":
            return timedelta(minutes=value)
        elif unit == "h":
            return timedelta(hours=value)
        elif unit == "d":
            return timedelta(days=value)
        elif unit == "w":
            return timedelta(weeks=value)
        else:
            raise ValueError(f"Unknown duration unit: {unit}")

    def _calculate_step(self, duration: timedelta) -> str:
        """Calculate appropriate step for a given duration."""
        seconds = duration.total_seconds()
        if seconds <= 3600:
            return "15s"
        elif seconds <= 86400:
            return "1m"
        elif seconds <= 604800:
            return "5m"
        else:
            return "1h"


def get_tool_definitions() -> list[dict[str, Any]]:
    """Get MCP tool definitions for registration."""
    return [
        {
            "name": "prometheus_query",
            "description": (
                "Execute an instant PromQL query against Prometheus. "
                "Returns current values for the query expression. "
                "Use this for point-in-time queries."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "PromQL query expression",
                    },
                    "server": {
                        "type": "string",
                        "description": "Prometheus server name (optional)",
                    },
                    "time": {
                        "type": "string",
                        "description": "Evaluation timestamp RFC3339 (optional)",
                    },
                },
                "required": ["query"],
            },
        },
        {
            "name": "prometheus_query_range",
            "description": (
                "Execute a range query and return aggregated statistics. "
                "Computes min/max/avg server-side to reduce data transfer. "
                "Use for historical analysis over time periods."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "PromQL query expression",
                    },
                    "start": {
                        "type": "string",
                        "description": "Start time (RFC3339 or relative like '-1h')",
                    },
                    "end": {
                        "type": "string",
                        "description": "End time (RFC3339 or 'now')",
                    },
                    "step": {
                        "type": "string",
                        "description": "Query resolution (e.g., '15s', '1m', '5m')",
                    },
                    "server": {
                        "type": "string",
                        "description": "Prometheus server name (optional)",
                    },
                },
                "required": ["query", "start", "end", "step"],
            },
        },
        {
            "name": "prometheus_analyze_metric",
            "description": (
                "Comprehensively analyze a metric including metadata, "
                "current values, historical statistics, and label cardinality. "
                "This tool runs multiple queries to provide a complete picture."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "metric_name": {
                        "type": "string",
                        "description": "Name of the metric to analyze",
                    },
                    "duration": {
                        "type": "string",
                        "description": "Time window to analyze (default: '1h')",
                    },
                    "server": {
                        "type": "string",
                        "description": "Prometheus server name (optional)",
                    },
                },
                "required": ["metric_name"],
            },
        },
        {
            "name": "prometheus_discover_metrics",
            "description": (
                "Discover available metrics matching a pattern. "
                "Returns metric names with their types and descriptions."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Substring to filter metric names (optional)",
                    },
                    "server": {
                        "type": "string",
                        "description": "Prometheus server name (optional)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum metrics to return (default: 100)",
                    },
                },
                "required": [],
            },
        },
        {
            "name": "prometheus_health",
            "description": (
                "Check the health of a Prometheus server including "
                "target status and active alerts summary."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "description": "Prometheus server name (optional)",
                    },
                },
                "required": [],
            },
        },
        {
            "name": "prometheus_alerts",
            "description": (
                "Get current alerts from Prometheus with firing and pending status."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "description": "Prometheus server name (optional)",
                    },
                },
                "required": [],
            },
        },
        {
            "name": "prometheus_targets",
            "description": ("Get scrape target information grouped by health status."),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "description": "Prometheus server name (optional)",
                    },
                    "unhealthy_only": {
                        "type": "boolean",
                        "description": "Only return unhealthy targets (default: false)",
                    },
                },
                "required": [],
            },
        },
        {
            "name": "prometheus_servers",
            "description": "List all configured Prometheus servers and their status.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    ]
