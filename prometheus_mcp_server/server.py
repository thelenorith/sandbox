"""MCP Server implementation for Prometheus."""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    Resource,
    TextContent,
    Tool,
)

from prometheus_mcp_server.config import ServerConfig
from prometheus_mcp_server.prompts import get_prompt_definitions, render_prompt
from prometheus_mcp_server.resources import (
    PrometheusResources,
    get_resource_definitions,
)
from prometheus_mcp_server.tools import PrometheusTools, get_tool_definitions

logger = logging.getLogger(__name__)


def create_server(config: ServerConfig) -> Server:
    """Create and configure the MCP server.

    Args:
        config: Server configuration

    Returns:
        Configured MCP Server instance
    """
    server = Server("prometheus-mcp-server")
    tools = PrometheusTools(config)
    resources = PrometheusResources(config)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        tool_defs = get_tool_definitions()
        return [
            Tool(
                name=t["name"],
                description=t["description"],
                inputSchema=t["inputSchema"],
            )
            for t in tool_defs
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute a tool with the given arguments."""
        logger.debug(f"Calling tool: {name} with args: {arguments}")

        try:
            if name == "prometheus_query":
                result = await tools.query(
                    query=arguments["query"],
                    server=arguments.get("server"),
                    time=arguments.get("time"),
                )
            elif name == "prometheus_query_range":
                result = await tools.query_range(
                    query=arguments["query"],
                    start=arguments["start"],
                    end=arguments["end"],
                    step=arguments["step"],
                    server=arguments.get("server"),
                )
            elif name == "prometheus_analyze_metric":
                result = await tools.analyze_metric(
                    metric_name=arguments["metric_name"],
                    duration=arguments.get("duration", "1h"),
                    server=arguments.get("server"),
                )
            elif name == "prometheus_discover_metrics":
                result = await tools.discover_metrics(
                    pattern=arguments.get("pattern"),
                    server=arguments.get("server"),
                    limit=arguments.get("limit", 100),
                )
            elif name == "prometheus_health":
                result = await tools.check_health(
                    server=arguments.get("server"),
                )
            elif name == "prometheus_alerts":
                result = await tools.get_alerts(
                    server=arguments.get("server"),
                )
            elif name == "prometheus_targets":
                result = await tools.get_targets(
                    server=arguments.get("server"),
                    unhealthy_only=arguments.get("unhealthy_only", False),
                )
            elif name == "prometheus_servers":
                result = await tools.list_servers()
            else:
                result = {"error": f"Unknown tool: {name}"}

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            logger.exception(f"Error executing tool {name}")
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)}, indent=2),
                )
            ]

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """List available resources."""
        resource_defs = get_resource_definitions(config)
        return [
            Resource(
                uri=r["uri"],
                name=r["name"],
                description=r["description"],
                mimeType=r["mimeType"],
            )
            for r in resource_defs
        ]

    @server.read_resource()
    async def read_resource(uri: str) -> str:
        """Read a resource by URI."""
        logger.debug(f"Reading resource: {uri}")

        try:
            if not uri.startswith("prometheus://"):
                raise ValueError(f"Invalid URI scheme: {uri}")

            parts = uri.replace("prometheus://", "").split("/")
            if len(parts) < 2:
                raise ValueError(f"Invalid URI format: {uri}")

            server_name = parts[0]
            resource_type = "/".join(parts[1:])

            if server_name == "default":
                server_name = None

            if resource_type == "info":
                return await resources.get_server_info(server_name)
            elif resource_type == "metrics":
                return await resources.get_metric_catalog(server_name)
            elif resource_type == "alerts/rules":
                return await resources.get_alerting_rules(server_name)
            elif resource_type == "recording/rules":
                return await resources.get_recording_rules(server_name)
            else:
                raise ValueError(f"Unknown resource type: {resource_type}")

        except Exception as e:
            logger.exception(f"Error reading resource {uri}")
            return json.dumps({"error": str(e)})

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """List available prompts."""
        prompt_defs = get_prompt_definitions()
        return [
            Prompt(
                name=p["name"],
                description=p["description"],
                arguments=[
                    PromptArgument(
                        name=a["name"],
                        description=a["description"],
                        required=a["required"],
                    )
                    for a in p.get("arguments", [])
                ],
            )
            for p in prompt_defs
        ]

    @server.get_prompt()
    async def get_prompt(
        name: str, arguments: dict[str, str] | None
    ) -> GetPromptResult:
        """Get a prompt with rendered content."""
        logger.debug(f"Getting prompt: {name} with args: {arguments}")

        try:
            messages = render_prompt(name, arguments or {})
            return GetPromptResult(
                description=f"Prompt: {name}",
                messages=[
                    PromptMessage(
                        role=m["role"],
                        content=TextContent(type="text", text=m["content"]),
                    )
                    for m in messages
                ],
            )
        except Exception as e:
            logger.exception(f"Error rendering prompt {name}")
            return GetPromptResult(
                description=f"Error: {e}",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(type="text", text=f"Error: {e}"),
                    )
                ],
            )

    return server


async def run_server(config: ServerConfig) -> None:
    """Run the MCP server.

    Args:
        config: Server configuration
    """
    server = create_server(config)

    async with stdio_server() as (read_stream, write_stream):
        logger.info("Starting Prometheus MCP Server")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
