# CLI Standards

Command-line interface conventions for consistent, user-friendly tools.

## Options

| Type | Example | Rule |
|------|---------|------|
| Single concept | `--dryrun`, `--debug` | No hyphens |
| Qualified/compound | `--no-overwrite`, `--output-dir` | Hyphen separates qualifier |

## Required Options

All CLI tools must support:

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--debug` | | flag | Enable debug output |
| `--dryrun` | | flag | Perform dry run without side effects |
| `--quiet` | `-q` | flag | Suppress non-essential output (see below) |
| `--help` | `-h` | flag | Show help message |
| `--version` | `-V` | flag | Show version information |

### `--quiet` Flag Behavior

The `--quiet` flag enables minimal output mode for scripting, automation, and clean logging.

**Suppressed when `--quiet` is set:**

| Output Type | Examples |
|-------------|----------|
| Progress indicators | Progress bars, spinners, percentage counters |
| INFO-level logging | "Starting processing", "Found N files" |
| Summary statistics | "Processed 42 files successfully" |

**Never suppressed (always shown):**

| Output Type | Rationale |
|-------------|-----------|
| WARNING messages | Indicate potential issues requiring attention |
| ERROR messages | Critical for diagnosing failures |
| Exit codes | Required for scripting and automation |
| Dry-run output | User explicitly requested this information |

**Use cases:**

- Scripting/automation requiring minimal output
- Cron jobs avoiding unnecessary email notifications
- File logging where progress bars create unwanted artifacts
- CI/CD pipelines with cleaner logs

See [Logging and Progress Standards](logging-progress.md) for implementation patterns.

## Option Naming

| Pattern | Example | Use |
|---------|---------|-----|
| `--<word>` | `--debug`, `--dryrun` | Single-concept flags |
| `--no-<feature>` | `--no-overwrite`, `--no-cache` | Disable default behavior |
| `--<qualifier>-<noun>` | `--output-dir`, `--config-file` | Qualified parameters |
| `--<noun>` | `--format`, `--level` | Value parameters |

## Positional Arguments

Use positional arguments for required inputs that are obvious from context:

```bash
# Good - source/destination are clear
mytool copy source.txt destination.txt

# Good - input file is the primary subject
mytool process input.csv

# Bad - ambiguous without option names
mytool configure production 8080 true
```

**Guidelines:**

- Limit to 2-3 positional arguments maximum
- Use options for optional or ambiguous parameters
- Document positional arguments clearly in help text

## Help Text

| Rule | Example |
|------|---------|
| Start with lowercase | `help="enable debug output"` |
| No period at end | `help="source directory"` |
| Under 60 characters | Keep it brief |
| Use verb phrases for actions | `help="process all files recursively"` |

### Help Output Structure

```
Usage: mytool [OPTIONS] <input> [output]

Brief description of what the tool does.

Arguments:
  input              Input file or directory
  output             Output location (default: stdout)

Options:
  --debug            Enable debug output
  --dryrun           Perform dry run without side effects
  -q, --quiet        Suppress non-essential output
  -f, --format TEXT  Output format [json|csv|table]
  -h, --help         Show this help message
  -V, --version      Show version information

Examples:
  mytool process input.csv
  mytool --format json input.csv output.json
  mytool --dryrun input/
```

## Exit Codes

Define as module-level constants with `EXIT_` prefix:

| Constant | Value | Meaning |
|----------|-------|---------|
| `EXIT_SUCCESS` | 0 | Success |
| `EXIT_ERROR` | 1 | General error |
| `EXIT_USAGE` | 2 | Invalid usage/arguments |
| `EXIT_CONFIG` | 3 | Configuration error |
| `EXIT_IO` | 4 | I/O error (file not found, permission denied) |
| `EXIT_INTERRUPT` | 130 | Interrupted (Ctrl+C) |

**Implementation:**

```python
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_USAGE = 2

def main() -> int:
    try:
        # ... application logic
        return EXIT_SUCCESS
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return EXIT_USAGE
    except Exception as e:
        logger.error(f"Error: {e}")
        return EXIT_ERROR

if __name__ == "__main__":
    sys.exit(main())
```

## Input/Output Conventions

### Standard Streams

| Stream | Use For |
|--------|---------|
| stdin | Input data when no file specified |
| stdout | Primary output (results, data) |
| stderr | Diagnostics (logs, progress, errors) |

### File Arguments

```bash
# Read from stdin when input is "-" or omitted
mytool process -                    # Explicit stdin
cat file.txt | mytool process       # Piped input

# Write to stdout when output is "-" or omitted
mytool process input.txt -          # Explicit stdout
mytool process input.txt > out.txt  # Redirected output
```

## Subcommands

For tools with multiple operations, use subcommands:

```bash
mytool <command> [options] [arguments]

Commands:
  init        Initialize a new project
  build       Build the project
  test        Run tests
  deploy      Deploy to environment
```

**Guidelines:**

- Each subcommand should be a verb
- Share common options across subcommands
- Provide help for each subcommand: `mytool build --help`

## Interactive vs Non-Interactive

| Mode | Behavior |
|------|----------|
| Interactive (TTY) | Prompts, colors, progress bars |
| Non-interactive (pipe/script) | No prompts, no colors, machine-readable output |

**Detection:**

```python
import sys

if sys.stdin.isatty():
    # Interactive mode
    response = input("Continue? [y/N] ")
else:
    # Non-interactive mode - use defaults or fail
    pass
```

## Color Output

- Use colors only when output is a TTY
- Respect `NO_COLOR` environment variable
- Provide `--color` / `--no-color` overrides

## Configuration Precedence

From lowest to highest priority:

1. Built-in defaults
2. System configuration (`/etc/mytool/config`)
3. User configuration (`~/.config/mytool/config`)
4. Project configuration (`./mytool.toml`)
5. Environment variables (`MYTOOL_*`)
6. Command-line options

## Industry References

- [GNU Coding Standards - Command Line Interfaces](https://www.gnu.org/prep/standards/html_node/Command_002dLine-Interfaces.html)
- [POSIX Utility Conventions](https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html)
- [Command Line Interface Guidelines](https://clig.dev/)
- [12 Factor CLI Apps](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46)
