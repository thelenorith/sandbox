"""MCP resources for Prometheus.

Resources provide contextual information that can be attached to conversations,
offloading the need for the LLM to query for basic information repeatedly.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from prometheus_mcp_server.client import PrometheusClient
from prometheus_mcp_server.config import ServerConfig

logger = logging.getLogger(__name__)


class PrometheusResources:
    """MCP resources for Prometheus context."""

    def __init__(self, config: ServerConfig) -> None:
        """Initialize resources with server configuration."""
        self.config = config

    async def get_server_info(self, server_name: str | None = None) -> str:
        """Get information about a Prometheus server.

        This resource provides server configuration and status
        that can be used as context for conversations.
        """
        server_config = self.config.get_server(server_name)
        client = PrometheusClient(server_config)

        try:
            async with client:
                healthy = await client.check_health()
                ready = await client.check_ready()

                if healthy and ready:
                    targets_data = await client.get_targets()
                    alerts = await client.get_alerts()
                    active_targets = targets_data.get("activeTargets", [])
                else:
                    active_targets = []
                    alerts = []

            return json.dumps(
                {
                    "server": {
                        "name": server_config.name,
                        "url": server_config.url,
                        "healthy": healthy,
                        "ready": ready,
                    },
                    "targets": {
                        "total": len(active_targets),
                        "healthy": sum(
                            1 for t in active_targets if t.get("health") == "up"
                        ),
                    },
                    "alerts": {
                        "total": len(alerts),
                        "firing": sum(1 for a in alerts if a.get("state") == "firing"),
                    },
                },
                indent=2,
            )
        except Exception as e:
            return json.dumps(
                {
                    "server": {
                        "name": server_config.name,
                        "url": server_config.url,
                        "healthy": False,
                        "ready": False,
                        "error": str(e),
                    },
                },
                indent=2,
            )

    async def get_metric_catalog(
        self,
        server_name: str | None = None,
        category: str | None = None,
    ) -> str:
        """Get a catalog of available metrics.

        This resource provides a structured overview of metrics
        organized by common categories for easier discovery.
        """
        server_config = self.config.get_server(server_name)
        client = PrometheusClient(server_config)

        categories = {
            "cpu": ["cpu", "processor"],
            "memory": ["memory", "mem", "heap", "stack"],
            "disk": ["disk", "filesystem", "fs", "storage"],
            "network": ["network", "net", "tcp", "http", "request"],
            "process": ["process", "thread", "goroutine"],
            "go": ["go_"],
            "prometheus": ["prometheus_", "scrape_"],
        }

        try:
            async with client:
                metadata = await client.get_metadata(limit=500)

            categorized: dict[str, list[dict[str, Any]]] = {
                cat: [] for cat in categories
            }
            categorized["other"] = []

            for name, meta_list in metadata.items():
                meta = meta_list[0] if meta_list else {}
                metric_info = {
                    "name": name,
                    "type": (
                        getattr(meta, "type", "unknown")
                        if hasattr(meta, "type")
                        else meta.get("type", "unknown")
                    ),
                    "help": (
                        getattr(meta, "help", "")
                        if hasattr(meta, "help")
                        else meta.get("help", "")
                    ),
                }

                if category:
                    if category in categories:
                        for keyword in categories[category]:
                            if keyword in name.lower():
                                categorized[category].append(metric_info)
                                break
                else:
                    placed = False
                    for cat, keywords in categories.items():
                        for keyword in keywords:
                            if keyword in name.lower():
                                categorized[cat].append(metric_info)
                                placed = True
                                break
                        if placed:
                            break
                    if not placed:
                        categorized["other"].append(metric_info)

            for cat in categorized:
                categorized[cat].sort(key=lambda x: x["name"])

            result = {
                "server": server_config.name,
                "total_metrics": len(metadata),
                "categories": {
                    cat: {
                        "count": len(metrics),
                        "metrics": metrics[:50],
                        "truncated": len(metrics) > 50,
                    }
                    for cat, metrics in categorized.items()
                    if metrics
                },
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

    async def get_alerting_rules(self, server_name: str | None = None) -> str:
        """Get all alerting rules.

        This resource provides the complete set of alerting rules
        for understanding what conditions are being monitored.
        """
        server_config = self.config.get_server(server_name)
        client = PrometheusClient(server_config)

        try:
            async with client:
                rules_data = await client.get_rules(type="alert")

            groups = rules_data.get("groups", [])
            formatted_groups = []

            for group in groups:
                formatted_rules = []
                for rule in group.get("rules", []):
                    formatted_rules.append(
                        {
                            "name": rule.get("name"),
                            "query": rule.get("query"),
                            "duration": rule.get("duration"),
                            "severity": rule.get("labels", {}).get("severity"),
                            "summary": rule.get("annotations", {}).get("summary"),
                            "state": rule.get("state"),
                        }
                    )

                formatted_groups.append(
                    {
                        "name": group.get("name"),
                        "file": group.get("file"),
                        "rules": formatted_rules,
                    }
                )

            return json.dumps(
                {
                    "server": server_config.name,
                    "total_groups": len(groups),
                    "total_rules": sum(len(g.get("rules", [])) for g in groups),
                    "groups": formatted_groups,
                },
                indent=2,
            )
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

    async def get_recording_rules(self, server_name: str | None = None) -> str:
        """Get all recording rules.

        This resource provides recording rules which pre-compute
        expensive queries for efficiency.
        """
        server_config = self.config.get_server(server_name)
        client = PrometheusClient(server_config)

        try:
            async with client:
                rules_data = await client.get_rules(type="record")

            groups = rules_data.get("groups", [])
            formatted_groups = []

            for group in groups:
                formatted_rules = []
                for rule in group.get("rules", []):
                    formatted_rules.append(
                        {
                            "name": rule.get("name"),
                            "query": rule.get("query"),
                            "labels": rule.get("labels", {}),
                        }
                    )

                if formatted_rules:
                    formatted_groups.append(
                        {
                            "name": group.get("name"),
                            "rules": formatted_rules,
                        }
                    )

            return json.dumps(
                {
                    "server": server_config.name,
                    "total_groups": len(formatted_groups),
                    "groups": formatted_groups,
                },
                indent=2,
            )
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)


def get_resource_definitions(config: ServerConfig) -> list[dict[str, Any]]:
    """Get MCP resource definitions for registration."""
    resources = []

    for server in config.prometheus_servers:
        resources.extend(
            [
                {
                    "uri": f"prometheus://{server.name}/info",
                    "name": f"Prometheus Server Info ({server.name})",
                    "description": (
                        f"Current status and overview of the {server.name} "
                        "Prometheus server including health, targets, and alerts"
                    ),
                    "mimeType": "application/json",
                },
                {
                    "uri": f"prometheus://{server.name}/metrics",
                    "name": f"Metric Catalog ({server.name})",
                    "description": (
                        f"Categorized catalog of available metrics on {server.name}"
                    ),
                    "mimeType": "application/json",
                },
                {
                    "uri": f"prometheus://{server.name}/alerts/rules",
                    "name": f"Alerting Rules ({server.name})",
                    "description": (f"All alerting rules configured on {server.name}"),
                    "mimeType": "application/json",
                },
                {
                    "uri": f"prometheus://{server.name}/recording/rules",
                    "name": f"Recording Rules ({server.name})",
                    "description": (f"All recording rules configured on {server.name}"),
                    "mimeType": "application/json",
                },
            ]
        )

    if config.prometheus_servers:
        default_name = config.get_server().name
        resources.extend(
            [
                {
                    "uri": "prometheus://default/info",
                    "name": "Default Prometheus Server Info",
                    "description": (
                        f"Status of the default Prometheus server ({default_name})"
                    ),
                    "mimeType": "application/json",
                },
                {
                    "uri": "prometheus://default/metrics",
                    "name": "Default Metric Catalog",
                    "description": "Metrics available on the default server",
                    "mimeType": "application/json",
                },
            ]
        )

    return resources
