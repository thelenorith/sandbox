"""Tests for Prometheus prompts module."""

from __future__ import annotations

import pytest

from prometheus_mcp_server.prompts import get_prompt_definitions, render_prompt


class TestPromptDefinitions:
    """Tests for prompt definitions."""

    def test_get_prompt_definitions(self) -> None:
        """Test that prompt definitions are returned."""
        definitions = get_prompt_definitions()
        assert len(definitions) > 0

    def test_prompt_definitions_have_required_fields(self) -> None:
        """Test that all prompts have required fields."""
        definitions = get_prompt_definitions()

        for prompt in definitions:
            assert "name" in prompt
            assert "description" in prompt

    def test_analyze_high_cpu_exists(self) -> None:
        """Test that analyze_high_cpu prompt exists."""
        definitions = get_prompt_definitions()
        names = [p["name"] for p in definitions]
        assert "analyze_high_cpu" in names

    def test_investigate_alert_exists(self) -> None:
        """Test that investigate_alert prompt exists."""
        definitions = get_prompt_definitions()
        names = [p["name"] for p in definitions]
        assert "investigate_alert" in names

    def test_capacity_planning_exists(self) -> None:
        """Test that capacity_planning prompt exists."""
        definitions = get_prompt_definitions()
        names = [p["name"] for p in definitions]
        assert "capacity_planning" in names


class TestRenderPrompt:
    """Tests for prompt rendering."""

    def test_render_high_cpu_prompt(self) -> None:
        """Test rendering high CPU prompt."""
        messages = render_prompt("analyze_high_cpu", {})

        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert "CPU" in messages[0]["content"]
        assert "80%" in messages[0]["content"]

    def test_render_high_cpu_with_threshold(self) -> None:
        """Test rendering high CPU prompt with custom threshold."""
        messages = render_prompt("analyze_high_cpu", {"threshold": "90"})

        assert "90%" in messages[0]["content"]

    def test_render_high_cpu_with_server(self) -> None:
        """Test rendering high CPU prompt with server."""
        messages = render_prompt("analyze_high_cpu", {"server": "prod"})

        assert "prod" in messages[0]["content"]

    def test_render_memory_pressure_prompt(self) -> None:
        """Test rendering memory pressure prompt."""
        messages = render_prompt("analyze_memory_pressure", {})

        assert len(messages) == 1
        assert "memory" in messages[0]["content"].lower()
        assert "85%" in messages[0]["content"]

    def test_render_investigate_alert_prompt(self) -> None:
        """Test rendering investigate alert prompt."""
        messages = render_prompt("investigate_alert", {"alert_name": "HighMemoryUsage"})

        assert "HighMemoryUsage" in messages[0]["content"]

    def test_render_capacity_planning_prompt(self) -> None:
        """Test rendering capacity planning prompt."""
        messages = render_prompt(
            "capacity_planning",
            {"service": "my-service", "duration": "30d"},
        )

        assert "my-service" in messages[0]["content"]
        assert "30d" in messages[0]["content"]

    def test_render_service_health_prompt(self) -> None:
        """Test rendering service health prompt."""
        messages = render_prompt("service_health_check", {"service": "api-gateway"})

        assert "api-gateway" in messages[0]["content"]
        assert "availability" in messages[0]["content"].lower()

    def test_render_debug_scrape_prompt(self) -> None:
        """Test rendering debug scrape prompt."""
        messages = render_prompt("debug_scrape_failures", {"job": "node"})

        assert "node" in messages[0]["content"]
        assert "scrape" in messages[0]["content"].lower()

    def test_render_compare_periods_prompt(self) -> None:
        """Test rendering compare periods prompt."""
        messages = render_prompt(
            "compare_periods",
            {
                "metric": "http_requests_total",
                "period1_start": "-48h",
                "period1_end": "-24h",
                "period2_start": "-24h",
                "period2_end": "now",
            },
        )

        assert "http_requests_total" in messages[0]["content"]
        assert "-48h" in messages[0]["content"]
        assert "-24h" in messages[0]["content"]

    def test_render_create_alert_prompt(self) -> None:
        """Test rendering create alert prompt."""
        messages = render_prompt(
            "create_alert_rule",
            {
                "metric": "node_cpu_seconds_total",
                "condition": "above 80%",
                "severity": "critical",
            },
        )

        assert "node_cpu_seconds_total" in messages[0]["content"]
        assert "above 80%" in messages[0]["content"]
        assert "critical" in messages[0]["content"]

    def test_render_unknown_prompt(self) -> None:
        """Test rendering unknown prompt raises error."""
        with pytest.raises(ValueError, match="Unknown prompt"):
            render_prompt("unknown_prompt", {})

    def test_prompt_arguments_optional(self) -> None:
        """Test that most prompt arguments are optional."""
        messages = render_prompt("analyze_high_cpu", {})
        assert len(messages) == 1

    def test_prompt_default_values_used(self) -> None:
        """Test that default values are used when not provided."""
        messages = render_prompt("analyze_memory_pressure", {})
        assert "85%" in messages[0]["content"]

        messages = render_prompt("capacity_planning", {"service": "test"})
        assert "7d" in messages[0]["content"]
