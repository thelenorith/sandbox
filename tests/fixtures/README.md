# Test Fixtures

This directory contains test fixtures for the prometheus-mcp-server tests.

## Purpose

Test fixtures provide sample data for testing without requiring a live Prometheus server.

## Current Fixtures

Currently, all fixtures are defined programmatically in `conftest.py`:

- `mock_query_response` - Sample instant query response
- `mock_range_query_response` - Sample range query response
- `mock_labels_response` - Sample labels endpoint response
- `mock_label_values_response` - Sample label values response
- `mock_metadata_response` - Sample metric metadata response
- `mock_targets_response` - Sample targets endpoint response
- `mock_alerts_response` - Sample alerts endpoint response
- `mock_rules_response` - Sample rules endpoint response
- `mock_series_response` - Sample series endpoint response

## Adding New Fixtures

When adding new test data:

1. Prefer programmatic generation over large JSON files
2. Keep fixtures minimal and focused
3. Document the purpose of each fixture
4. Avoid Git LFS due to CI constraints
