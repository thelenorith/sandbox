"""MCP prompts for Prometheus analysis.

Prompts provide pre-built analysis templates that guide the LLM
through common Prometheus workflows, reducing token usage by
providing structured approaches.
"""

from __future__ import annotations

from typing import Any


def get_prompt_definitions() -> list[dict[str, Any]]:
    """Get MCP prompt definitions for registration."""
    return [
        {
            "name": "analyze_high_cpu",
            "description": (
                "Analyze high CPU usage on a system. Guides through checking "
                "CPU metrics, identifying top consumers, and suggesting actions."
            ),
            "arguments": [
                {
                    "name": "threshold",
                    "description": "CPU usage threshold percentage (default: 80)",
                    "required": False,
                },
                {
                    "name": "server",
                    "description": "Prometheus server name",
                    "required": False,
                },
            ],
        },
        {
            "name": "analyze_memory_pressure",
            "description": (
                "Analyze memory pressure and potential OOM risks. "
                "Checks memory usage, swap, and identifies memory-hungry processes."
            ),
            "arguments": [
                {
                    "name": "threshold",
                    "description": "Memory usage threshold percentage (default: 85)",
                    "required": False,
                },
                {
                    "name": "server",
                    "description": "Prometheus server name",
                    "required": False,
                },
            ],
        },
        {
            "name": "investigate_alert",
            "description": (
                "Investigate a specific firing alert. Provides context about "
                "the alert, related metrics, and potential causes."
            ),
            "arguments": [
                {
                    "name": "alert_name",
                    "description": "Name of the alert to investigate",
                    "required": True,
                },
                {
                    "name": "server",
                    "description": "Prometheus server name",
                    "required": False,
                },
            ],
        },
        {
            "name": "capacity_planning",
            "description": (
                "Generate a capacity planning report for a service. "
                "Analyzes trends and projects future resource needs."
            ),
            "arguments": [
                {
                    "name": "service",
                    "description": "Service or job name to analyze",
                    "required": True,
                },
                {
                    "name": "duration",
                    "description": "Historical period to analyze (default: '7d')",
                    "required": False,
                },
                {
                    "name": "server",
                    "description": "Prometheus server name",
                    "required": False,
                },
            ],
        },
        {
            "name": "service_health_check",
            "description": (
                "Perform a comprehensive health check on a service. "
                "Checks availability, latency, error rates, and resource usage."
            ),
            "arguments": [
                {
                    "name": "service",
                    "description": "Service or job name to check",
                    "required": True,
                },
                {
                    "name": "server",
                    "description": "Prometheus server name",
                    "required": False,
                },
            ],
        },
        {
            "name": "debug_scrape_failures",
            "description": (
                "Debug scrape failures for targets. Identifies failing targets "
                "and provides diagnostic information."
            ),
            "arguments": [
                {
                    "name": "job",
                    "description": "Job name to filter (optional, all if not set)",
                    "required": False,
                },
                {
                    "name": "server",
                    "description": "Prometheus server name",
                    "required": False,
                },
            ],
        },
        {
            "name": "compare_periods",
            "description": (
                "Compare metrics between two time periods. Useful for "
                "before/after analysis of changes or incidents."
            ),
            "arguments": [
                {
                    "name": "metric",
                    "description": "Metric name or PromQL expression",
                    "required": True,
                },
                {
                    "name": "period1_start",
                    "description": "Start of first period (e.g., '-48h')",
                    "required": True,
                },
                {
                    "name": "period1_end",
                    "description": "End of first period (e.g., '-24h')",
                    "required": True,
                },
                {
                    "name": "period2_start",
                    "description": "Start of second period (e.g., '-24h')",
                    "required": True,
                },
                {
                    "name": "period2_end",
                    "description": "End of second period (e.g., 'now')",
                    "required": True,
                },
                {
                    "name": "server",
                    "description": "Prometheus server name",
                    "required": False,
                },
            ],
        },
        {
            "name": "create_alert_rule",
            "description": (
                "Help create a new alerting rule. Guides through defining "
                "the query, threshold, duration, and annotations."
            ),
            "arguments": [
                {
                    "name": "metric",
                    "description": "Metric to alert on",
                    "required": True,
                },
                {
                    "name": "condition",
                    "description": "Alert condition description (e.g., 'above 80%')",
                    "required": True,
                },
                {
                    "name": "severity",
                    "description": "Alert severity (critical, warning, info)",
                    "required": False,
                },
            ],
        },
    ]


def render_prompt(name: str, arguments: dict[str, str]) -> list[dict[str, str]]:
    """Render a prompt with the given arguments.

    Returns a list of messages that form the prompt.
    """
    prompts = {
        "analyze_high_cpu": _render_high_cpu_prompt,
        "analyze_memory_pressure": _render_memory_pressure_prompt,
        "investigate_alert": _render_investigate_alert_prompt,
        "capacity_planning": _render_capacity_planning_prompt,
        "service_health_check": _render_service_health_prompt,
        "debug_scrape_failures": _render_debug_scrape_prompt,
        "compare_periods": _render_compare_periods_prompt,
        "create_alert_rule": _render_create_alert_prompt,
    }

    renderer = prompts.get(name)
    if not renderer:
        raise ValueError(f"Unknown prompt: {name}")

    return renderer(arguments)


def _render_high_cpu_prompt(args: dict[str, str]) -> list[dict[str, str]]:
    threshold = args.get("threshold", "80")
    server = args.get("server", "")
    server_clause = f" on server '{server}'" if server else ""

    return [
        {
            "role": "user",
            "content": f"""Analyze high CPU usage{server_clause}. Follow these steps:

1. First, check overall CPU usage across all instances:
   - Use prometheus_query with:
     100 - (avg by(instance) (rate(node_cpu_seconds_total{{mode="idle"}}[5m])) * 100)
   - Identify instances above {threshold}% usage

2. For high-usage instances, break down by CPU mode:
   - Query: sum by(instance, mode) (rate(node_cpu_seconds_total[5m])) * 100
   - Check which modes (user, system, iowait, etc.) are consuming CPU

3. If 'iowait' is high, check disk I/O:
   - Query: rate(node_disk_io_time_seconds_total[5m])

4. Check for process-level CPU if available:
   - Query: topk(10, sum by(process_name) (rate(process_cpu_seconds_total[5m])))

5. Look at CPU usage trends over the last hour:
   - Use prometheus_query_range with 1h window

Based on findings, provide:
- Current CPU status summary
- Top CPU consumers
- Whether this is a spike or sustained high usage
- Recommended actions""",
        }
    ]


def _render_memory_pressure_prompt(args: dict[str, str]) -> list[dict[str, str]]:
    threshold = args.get("threshold", "85")
    server = args.get("server", "")
    server_clause = f" on server '{server}'" if server else ""

    return [
        {
            "role": "user",
            "content": f"""Analyze memory pressure{server_clause}. Follow these steps:

1. Check current memory usage:
   - Query: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
   - Identify instances above {threshold}% usage

2. Get memory breakdown:
   - Total: node_memory_MemTotal_bytes
   - Available: node_memory_MemAvailable_bytes
   - Cached: node_memory_Cached_bytes
   - Buffers: node_memory_Buffers_bytes

3. Check swap usage (indicates memory pressure):
   - Query: node_memory_SwapTotal_bytes - node_memory_SwapFree_bytes
   - High swap usage indicates memory pressure

4. Look for OOM events:
   - Query: increase(node_vmstat_oom_kill[1h])

5. Check memory usage trends:
   - Use prometheus_query_range over last 24h
   - Look for memory leaks (steadily increasing usage)

6. If container metrics available:
   - Query: container_memory_usage_bytes / container_spec_memory_limit_bytes

Provide:
- Current memory status per instance
- Risk assessment for OOM
- Memory trend analysis (leak detection)
- Recommendations (add memory, optimize apps, etc.)""",
        }
    ]


def _render_investigate_alert_prompt(args: dict[str, str]) -> list[dict[str, str]]:
    alert_name = args.get("alert_name", "")
    server = args.get("server", "")
    server_clause = f" on server '{server}'" if server else ""

    return [
        {
            "role": "user",
            "content": f"""Investigate the alert '{alert_name}'{server_clause}. Follow these steps:

1. Get alert details:
   - Use prometheus_alerts to find the alert
   - Note the labels, severity, and annotations

2. Understand the alert rule:
   - Check the PromQL expression that triggers this alert
   - Identify the threshold and duration

3. Query the underlying metric:
   - Use prometheus_query with the alert's expression
   - See current values vs threshold

4. Check historical context:
   - Use prometheus_query_range for the last 24h
   - When did the condition start?
   - Has this happened before?

5. Look for correlated issues:
   - Check related metrics (same instance/job)
   - Look for other firing alerts on the same targets

6. Check recent changes:
   - Look at scrape_samples_scraped for volume changes
   - Check if new targets were added

Provide:
- Alert summary and current status
- Root cause analysis
- Timeline of the issue
- Recommended remediation steps
- Suggestions for alert tuning if needed""",
        }
    ]


def _render_capacity_planning_prompt(args: dict[str, str]) -> list[dict[str, str]]:
    service = args.get("service", "")
    duration = args.get("duration", "7d")
    server = args.get("server", "")
    server_clause = f" on server '{server}'" if server else ""

    return [
        {
            "role": "user",
            "content": f"""Generate capacity planning report for '{service}'{server_clause}.

Analyze the last {duration} of data:

1. CPU Capacity:
   - Query: avg_over_time(rate(process_cpu_seconds_total{{job="{service}"}}[5m])[{duration}:1h])
   - Calculate: current usage, peak usage, average usage
   - Trend: Is usage growing? At what rate?

2. Memory Capacity:
   - Query: process_resident_memory_bytes{{job="{service}"}}
   - Calculate: current, peak, growth rate
   - Project: When will current limits be reached?

3. Request Volume (if applicable):
   - Query: rate(http_requests_total{{job="{service}"}}[5m])
   - Trends in request volume
   - Peak vs average load

4. Latency Trends:
   - Query: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{{job="{service}"}}[5m]))
   - Is latency increasing with load?

5. Error Rates:
   - Query: rate(http_requests_total{{job="{service}",status=~"5.."}}[5m])
   - Correlation between errors and resource usage

Generate a report with:
- Current resource utilization summary
- Growth trends (daily/weekly)
- Projected resource needs (30/60/90 days)
- Scaling recommendations
- Cost implications if applicable""",
        }
    ]


def _render_service_health_prompt(args: dict[str, str]) -> list[dict[str, str]]:
    service = args.get("service", "")
    server = args.get("server", "")
    server_clause = f" on server '{server}'" if server else ""

    return [
        {
            "role": "user",
            "content": f"""Perform health check for service '{service}'{server_clause}.

1. Availability Check:
   - Query: up{{job="{service}"}}
   - Check all instances are up
   - Use prometheus_targets to see scrape status

2. Latency Check:
   - P50: histogram_quantile(0.5, rate(http_request_duration_seconds_bucket{{job="{service}"}}[5m]))
   - P95: histogram_quantile(0.95, ...)
   - P99: histogram_quantile(0.99, ...)
   - Compare against SLO targets

3. Error Rate Check:
   - Query: sum(rate(http_requests_total{{job="{service}",status=~"5.."}}[5m])) / sum(rate(http_requests_total{{job="{service}"}}[5m]))
   - Should be < 1% for healthy service

4. Throughput Check:
   - Query: sum(rate(http_requests_total{{job="{service}"}}[5m]))
   - Compare to expected baseline

5. Resource Health:
   - CPU: rate(process_cpu_seconds_total{{job="{service}"}}[5m])
   - Memory: process_resident_memory_bytes{{job="{service}"}}
   - Open FDs: process_open_fds{{job="{service}"}}

6. Dependency Health:
   - Check metrics for downstream services
   - Database connection pools, cache hit rates

Provide:
- Overall health score (healthy/degraded/unhealthy)
- Status of each check
- Any anomalies detected
- Recommended actions""",
        }
    ]


def _render_debug_scrape_prompt(args: dict[str, str]) -> list[dict[str, str]]:
    job = args.get("job", "")
    server = args.get("server", "")
    server_clause = f" on server '{server}'" if server else ""
    job_filter = f'{{job="{job}"}}' if job else ""

    return [
        {
            "role": "user",
            "content": f"""Debug scrape failures{server_clause}.

1. Get failing targets:
   - Use prometheus_targets with unhealthy_only=true
   {f'- Filter for job: {job}' if job else '- Check all jobs'}

2. Check scrape metrics:
   - up{job_filter} == 0 (which targets are down)
   - scrape_duration_seconds{job_filter} (slow scrapes)
   - scrape_samples_scraped{job_filter} (sample counts)

3. Look for patterns:
   - Are failures isolated or widespread?
   - Did they start at the same time?
   - Any common labels (datacenter, region, etc.)?

4. Check for timeout issues:
   - scrape_timeout_seconds vs scrape_duration_seconds
   - Targets timing out consistently

5. Verify connectivity:
   - Check if targets are reachable
   - Look for network-related labels

6. Check Prometheus health:
   - prometheus_target_scrape_pool_reloads_failed_total
   - prometheus_sd_discovered_targets

Provide:
- List of failing targets with reasons
- Common patterns identified
- Diagnostic information for each failure
- Recommended fixes""",
        }
    ]


def _render_compare_periods_prompt(args: dict[str, str]) -> list[dict[str, str]]:
    metric = args.get("metric", "")
    p1_start = args.get("period1_start", "-48h")
    p1_end = args.get("period1_end", "-24h")
    p2_start = args.get("period2_start", "-24h")
    p2_end = args.get("period2_end", "now")
    server = args.get("server", "")
    server_clause = f" on server '{server}'" if server else ""

    return [
        {
            "role": "user",
            "content": f"""Compare metric '{metric}' between two periods{server_clause}.

Period 1: {p1_start} to {p1_end}
Period 2: {p2_start} to {p2_end}

1. Query Period 1:
   - Use prometheus_query_range
   - start: {p1_start}, end: {p1_end}
   - Calculate: min, max, avg, p95

2. Query Period 2:
   - Use prometheus_query_range
   - start: {p2_start}, end: {p2_end}
   - Calculate: min, max, avg, p95

3. Calculate differences:
   - Average change (absolute and percentage)
   - Peak change
   - Variance change

4. Identify anomalies:
   - Any values outside normal range?
   - Pattern changes (spiky vs smooth)?

5. Statistical significance:
   - Is the change meaningful or noise?

Provide:
- Side-by-side comparison table
- Key changes highlighted
- Visual description of trends
- Assessment of whether change is significant
- Possible explanations for changes""",
        }
    ]


def _render_create_alert_prompt(args: dict[str, str]) -> list[dict[str, str]]:
    metric = args.get("metric", "")
    condition = args.get("condition", "")
    severity = args.get("severity", "warning")

    return [
        {
            "role": "user",
            "content": f"""Help create an alerting rule for metric '{metric}' with condition '{condition}'.

1. First, understand the metric:
   - Use prometheus_analyze_metric to get metadata
   - What type is it? (counter, gauge, histogram, summary)
   - What labels are available?

2. Formulate the PromQL expression:
   - For counters: use rate() or increase()
   - For gauges: may use directly or with aggregations
   - For histograms: use histogram_quantile()

3. Determine appropriate threshold:
   - Query current values
   - Check historical range with query_range
   - Set threshold that avoids false positives

4. Choose alert duration:
   - How long should condition persist before alerting?
   - Short (1m) for critical, longer (5-15m) for warnings

5. Generate the alert rule YAML:

```yaml
groups:
  - name: custom_alerts
    rules:
      - alert: <AlertName>
        expr: <PromQL expression>
        for: <duration>
        labels:
          severity: {severity}
        annotations:
          summary: "<brief description>"
          description: "<detailed description with {{{{ $labels }}}} and {{{{ $value }}}}>"
          runbook_url: "<link to runbook>"
```

Provide:
- Complete alert rule YAML
- Explanation of the expression
- Testing queries to validate
- Suggestions for related alerts""",
        }
    ]
