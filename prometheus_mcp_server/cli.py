"""Command-line interface for Prometheus MCP Server."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from prometheus_mcp_server import __version__
from prometheus_mcp_server.config import ServerConfig
from prometheus_mcp_server.server import run_server

EXIT_SUCCESS = 0
EXIT_ERROR = 1

logger = logging.getLogger(__name__)


def setup_logging(debug: bool = False, quiet: bool = False) -> None:
    """Configure logging based on flags.

    Args:
        debug: Enable debug output
        quiet: Suppress non-essential output
    """
    if debug:
        level = logging.DEBUG
    elif quiet:
        level = logging.WARNING
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="prometheus-mcp-server",
        description="MCP server for interacting with Prometheus",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="enable debug output",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="suppress non-essential output",
    )

    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        metavar="FILE",
        help="path to configuration file",
    )

    parser.add_argument(
        "--url",
        type=str,
        metavar="URL",
        help="prometheus server URL (overrides config)",
    )

    parser.add_argument(
        "--show-config",
        action="store_true",
        help="show loaded configuration and exit",
    )

    return parser


def main(args: list[str] | None = None) -> int:
    """Main entry point.

    Args:
        args: Command line arguments (uses sys.argv if None)

    Returns:
        Exit code
    """
    parser = create_parser()
    parsed = parser.parse_args(args)

    setup_logging(debug=parsed.debug, quiet=parsed.quiet)

    try:
        config = ServerConfig.load(
            config_file=parsed.config,
            env_url=parsed.url,
        )

        if parsed.show_config:
            print(json.dumps(config.to_dict(), indent=2))
            return EXIT_SUCCESS

        if not config.prometheus_servers:
            logger.error(
                "No Prometheus servers configured. "
                "Set PROMETHEUS_MCP_URL or provide a config file with --config."
            )
            return EXIT_ERROR

        asyncio.run(run_server(config))
        return EXIT_SUCCESS

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return EXIT_SUCCESS
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
