"""Tests for CLI module."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from prometheus_mcp_server.cli import (
    EXIT_ERROR,
    EXIT_SUCCESS,
    create_parser,
    main,
    setup_logging,
)


class TestSetupLogging:
    """Tests for logging setup."""

    def test_default_logging(self) -> None:
        """Test default logging level."""
        setup_logging()

    def test_debug_logging(self) -> None:
        """Test debug logging level."""
        setup_logging(debug=True)

    def test_quiet_logging(self) -> None:
        """Test quiet logging level."""
        setup_logging(quiet=True)

    def test_debug_overrides_quiet(self) -> None:
        """Test that debug overrides quiet."""
        setup_logging(debug=True, quiet=True)


class TestParser:
    """Tests for argument parser."""

    def test_create_parser(self) -> None:
        """Test parser creation."""
        parser = create_parser()
        assert parser is not None

    def test_parse_no_args(self) -> None:
        """Test parsing with no arguments."""
        parser = create_parser()
        args = parser.parse_args([])

        assert args.debug is False
        assert args.quiet is False
        assert args.config is None
        assert args.url is None

    def test_parse_debug(self) -> None:
        """Test parsing --debug flag."""
        parser = create_parser()
        args = parser.parse_args(["--debug"])

        assert args.debug is True

    def test_parse_quiet(self) -> None:
        """Test parsing --quiet flag."""
        parser = create_parser()
        args = parser.parse_args(["--quiet"])

        assert args.quiet is True

    def test_parse_quiet_short(self) -> None:
        """Test parsing -q flag."""
        parser = create_parser()
        args = parser.parse_args(["-q"])

        assert args.quiet is True

    def test_parse_config(self) -> None:
        """Test parsing --config option."""
        parser = create_parser()
        args = parser.parse_args(["--config", "/path/to/config.json"])

        assert args.config == Path("/path/to/config.json")

    def test_parse_config_short(self) -> None:
        """Test parsing -c option."""
        parser = create_parser()
        args = parser.parse_args(["-c", "/path/to/config.json"])

        assert args.config == Path("/path/to/config.json")

    def test_parse_url(self) -> None:
        """Test parsing --url option."""
        parser = create_parser()
        args = parser.parse_args(["--url", "http://localhost:9090"])

        assert args.url == "http://localhost:9090"

    def test_parse_show_config(self) -> None:
        """Test parsing --show-config flag."""
        parser = create_parser()
        args = parser.parse_args(["--show-config"])

        assert args.show_config is True


class TestMain:
    """Tests for main function."""

    def test_show_config(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test --show-config output."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({"servers": [{"name": "test", "url": "http://localhost:9090"}]})
        )

        result = main(["--config", str(config_file), "--show-config"])

        assert result == EXIT_SUCCESS
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "servers" in output

    def test_no_servers_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test error when no servers configured."""
        monkeypatch.delenv("PROMETHEUS_MCP_URL", raising=False)

        result = main([])

        assert result == EXIT_ERROR

    def test_keyboard_interrupt(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test handling keyboard interrupt."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({"servers": [{"name": "test", "url": "http://localhost:9090"}]})
        )

        with patch("prometheus_mcp_server.cli.asyncio.run") as mock_run:
            mock_run.side_effect = KeyboardInterrupt()
            result = main(["--config", str(config_file)])

        assert result == EXIT_SUCCESS

    def test_fatal_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test handling fatal errors."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({"servers": [{"name": "test", "url": "http://localhost:9090"}]})
        )

        with patch("prometheus_mcp_server.cli.asyncio.run") as mock_run:
            mock_run.side_effect = RuntimeError("Fatal error")
            result = main(["--config", str(config_file)])

        assert result == EXIT_ERROR

    def test_url_override(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test URL override via --url."""
        result = main(
            [
                "--url",
                "http://override:9090",
                "--show-config",
            ]
        )

        assert result == EXIT_SUCCESS
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["servers"][0]["url"] == "http://override:9090"
