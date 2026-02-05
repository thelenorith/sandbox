# Logging, Progress, and Output Standards

Guidelines for output methods in CLI tools and services. Based on industry best practices including the 12-Factor App methodology and standard logging conventions.

## Overview

| Output Method | Purpose | Stream | When to Use |
|---------------|---------|--------|-------------|
| Logging | Operational/diagnostic | stderr | Debug info, warnings, errors |
| Progress | User feedback | stderr | Long-running operations |
| Print | Program output | stdout | Results, summaries, piped data |

## Logging

### When to Use Logging

Use logging for **operational and diagnostic information**:

| Log Level | Use For |
|-----------|---------|
| `DEBUG` | Detailed diagnostic info, variable values, execution flow |
| `INFO` | Normal operational messages, milestones |
| `WARNING` | Unexpected situations that don't prevent operation |
| `ERROR` | Failures that prevent completing a specific operation |
| `CRITICAL` | Severe errors that prevent program continuation |

### Configuration

Configure logging once at the application entry point:

```python
import logging

def setup_logging(name: str, debug: bool = False, quiet: bool = False) -> logging.Logger:
    """Configure logging with standard settings."""
    logger = logging.getLogger(name)

    if debug:
        level = logging.DEBUG
    elif quiet:
        level = logging.WARNING
    else:
        level = logging.INFO

    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(handler)

    return logger
```

| Rule | Rationale |
|------|-----------|
| Configure once at entry point | Prevents duplicate handlers |
| Use tool-specific logger name | Enables filtering by source |
| Control level via `--debug` and `--quiet` flags | User controls verbosity |

### Logging Level Behavior

| Flags | Effective Level | Output |
|-------|-----------------|--------|
| Default | INFO | INFO, WARNING, ERROR |
| `--quiet` | WARNING | WARNING, ERROR only |
| `--debug` | DEBUG | DEBUG, INFO, WARNING, ERROR |
| `--debug --quiet` | DEBUG | DEBUG, INFO, WARNING, ERROR (debug overrides quiet) |

### Logger Naming

Use hierarchical names for filtering:

```python
# Main module
logger = setup_logging(name="mytool", debug=debug)

# Submodules
logger = logging.getLogger("mytool.submodule")
```

### What to Log

```python
# DEBUG: Detailed diagnostic information
logger.debug(f"Processing file: {filename}")
logger.debug(f"Configuration values: {config}")

# INFO: Operational milestones
logger.info("Starting processing")
logger.info(f"Found {count} files to process")

# INFO: Multi-parameter information (single statement, key=value format)
logger.info(
    f"Connecting to database: host={host}, port={port}, "
    f"database={database}, pool_size={pool_size}"
)

# WARNING: Recoverable issues
logger.warning(f"Missing optional configuration key: {key}")
logger.warning(f"File exists, skipping: {dest}")

# ERROR: Operation failures
logger.error(f"Failed to read file: {filename}")
logger.error(f"Invalid format in {path}")
```

### What NOT to Log

| Avoid | Use Instead |
|-------|-------------|
| User-facing summaries | Print to stdout |
| Progress updates | Progress indicators |
| Primary program output | Print to stdout |

**Anti-Pattern: Multiple log calls with whitespace padding**

```python
# BAD: Multiple separate log calls with whitespace padding
logger.info("Connecting to database...")
logger.info(f"  Host: {host}")
logger.info(f"  Port: {port}")
logger.info(f"  Database: {database}")

# GOOD: Single log statement with key=value format
logger.info(
    f"Connecting to database: host={host}, port={port}, database={database}"
)
```

## Progress Indicators

### When to Use Progress

Use progress indicators for **long-running operations** that process multiple items:

| Scenario | Progress Type |
|----------|--------------|
| Processing known file list | Iterator-based progress |
| Dynamic status updates needed | Progress tracker |
| Unknown total count | Spinner or manual updates |
| < 3 items or instant operations | None needed |

### Progress Configuration

| Parameter | Purpose |
|-----------|---------|
| `desc` | Action being performed (e.g., "Moving files") |
| `unit` | What's being counted (e.g., "files", "dirs") |
| `enabled` | Control via CLI flag (default: True) |

### Controlling Progress Display

Progress should be controllable via CLI:

| Flag | Effect on Progress |
|------|-------------------|
| `--quiet` / `-q` | Suppress progress indicators |
| Default (no flag) | Show progress indicators |

Note: The `--quiet` flag also suppresses INFO-level logging and summary statistics. See [CLI Standards](cli.md#--quiet-flag-behavior) for full specification.

### What NOT to Use for Progress

| Avoid | Why |
|-------|-----|
| Manual dot printing (`print(".", end="")`) | Inconsistent, no metrics |
| Logging progress updates | Wrong abstraction level |
| Custom implementations | Use established libraries |

### Recommended Libraries

| Language | Library |
|----------|---------|
| Python | [tqdm](https://github.com/tqdm/tqdm), [rich](https://github.com/Textualize/rich) |
| JavaScript | [ora](https://github.com/sindresorhus/ora), [cli-progress](https://github.com/npkgz/cli-progress) |
| Go | [progressbar](https://github.com/schollz/progressbar) |
| Rust | [indicatif](https://github.com/console-rs/indicatif) |

## Print Statements (stdout)

### When to Use Print

Use print for **primary program output** that may be piped or captured:

| Use Case | Example |
|----------|---------|
| Final results/summaries | "Moved 42 files to /data" |
| Data output | File lists, JSON output |
| User decisions | "REJECTED: file.fits (low quality)" |
| Dry-run output | "Would move: src -> dest" |

### Print Guidelines

```python
# Final summary (always shown)
print(f"Processed {count} files successfully")

# Dry-run output
if dryrun:
    print(f"Would move: {src} -> {dest}")

# Rejection/decision output
print(f"REJECTED: {filename} (reason: {reason})")
```

### What NOT to Print

| Avoid | Use Instead |
|-------|-------------|
| Debug information | `logger.debug()` |
| Operational status | `logger.info()` |
| Warnings | `logger.warning()` |
| Progress dots | Progress library |

## Decision Matrix

Use this matrix to choose the right output method:

| Question | Yes -> Use |
|----------|-----------|
| Is this diagnostic/debugging information? | Logging |
| Is this a warning or error condition? | Logging |
| Is this showing progress through a list? | Progress indicator |
| Is this the primary output/result? | Print |
| Should this appear in piped output? | Print |
| Is this dry-run information? | Print |

## Common Patterns

### Standard CLI Tool Structure

```python
def main():
    args = parse_args()
    logger = setup_logging(name="mytool", debug=args.debug, quiet=args.quiet)

    logger.info("Starting processing")  # Suppressed by --quiet

    results = []
    for f in tqdm(files, desc="Processing", disable=args.quiet):
        logger.debug(f"Processing: {f}")
        result = process(f)
        if result:
            results.append(result)

    logger.info(f"Completed with {len(results)} results")  # Suppressed by --quiet

    # Summary output (suppressed by --quiet)
    if not args.quiet:
        print(f"Processed {len(results)} files")
```

### Dry-Run Pattern

```python
for src, dest in tqdm(moves, desc="Moving files", disable=quiet):
    if dryrun:
        print(f"Would move: {src} -> {dest}")
    else:
        shutil.move(src, dest)
        logger.debug(f"Moved: {src} -> {dest}")

if not dryrun:
    print(f"Moved {len(moves)} files")
```

### Error Handling Pattern

```python
try:
    result = process_file(path)
except FileNotFoundError:
    logger.error(f"File not found: {path}")
    return None
except PermissionError:
    logger.error(f"Permission denied: {path}")
    return None
except Exception as e:
    logger.exception(f"Unexpected error processing {path}")
    raise
```

## Summary Table

| Output Type | Stream | Controlled By |
|-------------|--------|---------------|
| Logging (DEBUG) | stderr | `--debug` |
| Logging (INFO) | stderr | `--quiet` (suppresses) |
| Logging (WARNING+) | stderr | Always shown |
| Progress | stderr | `--quiet` (suppresses) |
| Summary output | stdout | `--quiet` (suppresses) |
| Dry-run output | stdout | Always shown |

## Required CLI Flags

Per [CLI Standards](cli.md), all tools must support these flags:

| Flag | Purpose |
|------|---------|
| `--debug` | Enable DEBUG-level logging |
| `--quiet` / `-q` | Suppress non-essential output (progress, INFO logs, summaries) |

See [CLI Standards - --quiet Flag Behavior](cli.md#--quiet-flag-behavior) for full specification.

## Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| `print("Processing...")` for status | Clutters stdout | Use logging or progress |
| `print(".", end="")` for progress | No metrics, inconsistent | Use progress library |
| Logging final results | Results don't appear in piped output | Use print |
| Debug info to stdout | Breaks piped workflows | Use `logger.debug()` |
| Per-module logging setup | Duplicate handlers | Configure once at entry |
| Ignoring `--debug` flag | Users can't diagnose issues | Pass to logging setup |
| `if debug: logger.debug(...)` | Redundant conditional | Logger handles level filtering |
| Multiple log calls for one event | Hard to read, fragmented | Combine into single statement |
| Whitespace padding in logs | Logs aren't structured output | Use key=value format |

## Service Logging

For services (not CLI tools), additional considerations apply:

| Consideration | Guideline |
|---------------|-----------|
| Structured logging | Use JSON format for log aggregation |
| Request correlation | Include request IDs in all log entries |
| Sensitive data | Never log passwords, tokens, or PII |
| Log levels in production | Default to INFO, allow runtime adjustment |

See [Services Standards](services.md) for service-specific logging patterns.

## Industry References

- [12-Factor App - Logs](https://12factor.net/logs)
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Structured Logging Best Practices](https://www.structlog.org/en/stable/why.html)
