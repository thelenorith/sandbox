# README Format Standards

Standard structure and content for project README files.

## General Principles

1. **Scannable** - Users should quickly understand what the project does
2. **Action-oriented** - Focus on what users can do with the project
3. **Example-driven** - Show, don't just tell
4. **Concise** - Avoid verbose explanations; link to detailed docs

## Required Sections

| Section | Purpose |
|---------|---------|
| Title | Project name |
| Badges | Quick status indicators |
| Description | One to two sentences explaining purpose |
| Installation | How to install |
| Usage | Basic usage examples |

## Optional Sections

| Section | Include When |
|---------|--------------|
| Features | Project has multiple capabilities |
| Requirements | Non-obvious prerequisites exist |
| Configuration | Project is configurable |
| API Reference | Project exposes an API |
| Contributing | Accepting contributions |
| License | Not obvious from LICENSE file |

## Template

```markdown
# project-name

[![Test](https://github.com/org/project-name/actions/workflows/test.yml/badge.svg)](https://github.com/org/project-name/actions/workflows/test.yml)
[![Coverage](https://img.shields.io/codecov/c/github/org/project-name)](https://codecov.io/gh/org/project-name)
[![PyPI](https://img.shields.io/pypi/v/project-name)](https://pypi.org/project/project-name/)
[![Python](https://img.shields.io/pypi/pyversions/project-name)](https://pypi.org/project/project-name/)
[![License](https://img.shields.io/github/license/org/project-name)](LICENSE)

Brief description of what this project does and why it exists. State the problem it solves or the value it provides.

## Installation

```bash
pip install project-name
```

Or install from source:

```bash
git clone https://github.com/org/project-name.git
cd project-name
make install-dev
```

## Usage

Basic usage example:

```bash
project-name process input.txt --output result.txt
```

With options:

```bash
project-name process input.txt \
    --format json \
    --verbose
```

### Options

| Option | Description |
|--------|-------------|
| `--format` | Output format: `json`, `csv`, `table` |
| `--verbose` | Enable verbose output |
| `--dryrun` | Show what would be done without doing it |
| `-q, --quiet` | Suppress non-essential output |

## Features

- Feature one with brief explanation
- Feature two with brief explanation
- Feature three with brief explanation

## Configuration

Configuration can be provided via:

1. Command-line options (highest priority)
2. Environment variables
3. Configuration file (`~/.config/project-name/config.toml`)

Example configuration:

```toml
[defaults]
format = "json"
verbose = false
```

## Development

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Run all checks
make all
```

## License

MIT License - see [LICENSE](LICENSE) for details.
```

## Section Guidelines

### Title

- Use the package/project name
- Match repository name when possible
- Use lowercase with hyphens for URL-friendly names

### Badges

Standard badges in order:

| Badge | Purpose |
|-------|---------|
| Build/Test | CI status |
| Coverage | Test coverage percentage |
| Version | Package version (PyPI, npm) |
| Language version | Python/Node version support |
| License | License type |
| Code style | Formatter used (optional) |

Badge sources:
- GitHub Actions: `https://github.com/org/repo/actions/workflows/name.yml/badge.svg`
- Shields.io: `https://shields.io/`
- Codecov: `https://codecov.io/`

### Description

| Do | Don't |
|----|-------|
| State what the tool does | Describe implementation details |
| Explain the problem solved | List technologies used |
| Keep to 1-2 sentences | Write paragraphs |

**Good:**
> A CLI tool for organizing image files based on EXIF metadata.

**Bad:**
> This project uses Python 3.12 with click for CLI parsing and Pillow for image processing to read EXIF data from image files and organize them into directories.

### Installation

Show the simplest path first:

```markdown
## Installation

```bash
pip install project-name
```
```

Then show alternatives (source install, development setup) in order of complexity.

### Usage

- Start with the most common use case
- Show actual commands that work
- Include expected output when helpful
- Use realistic but simple examples

```markdown
## Usage

Process a single file:

```bash
mytool process input.csv
# Output: Processed 42 records
```

Process a directory:

```bash
mytool process ./data/ --recursive
```
```

### Options Table

Format options as a table for scannability:

```markdown
| Option | Short | Description |
|--------|-------|-------------|
| `--output` | `-o` | Output file path |
| `--format` | `-f` | Output format [json|csv] |
| `--verbose` | `-v` | Enable verbose output |
| `--help` | `-h` | Show help message |
```

## What NOT to Include

| Avoid | Rationale |
|-------|-----------|
| Changelog | Use CHANGELOG.md or GitHub Releases |
| Detailed API docs | Use separate documentation |
| Contributor list | Use GitHub contributors page |
| Full license text | Use LICENSE file |
| Implementation details | Keep focus on usage |
| Verbose explanations | Link to documentation |
| Every possible option | Show common cases, reference `--help` |

## Length Guidelines

| README Type | Target Length |
|-------------|---------------|
| Small library/tool | 50-150 lines |
| Medium project | 150-300 lines |
| Large project | 300-500 lines, link to docs |

If your README exceeds 500 lines, consider moving content to dedicated documentation.

## Documentation Links

For projects with extensive documentation:

```markdown
## Documentation

- [Getting Started](docs/getting-started.md)
- [Configuration Guide](docs/configuration.md)
- [API Reference](docs/api.md)
- [Contributing](CONTRIBUTING.md)
```

Or link to hosted documentation:

```markdown
## Documentation

Full documentation is available at [project-name.readthedocs.io](https://project-name.readthedocs.io/).
```

## Anti-Patterns

| Avoid | Preferred |
|-------|-----------|
| Wall of text | Use headers, lists, tables |
| Screenshots of text | Use code blocks |
| Outdated badges | Remove or fix broken badges |
| "TODO" sections | Remove until complete |
| Placeholder content | Ship with real content only |
| Duplicating `--help` output | Reference the command |

## Industry References

- [Make a README](https://www.makeareadme.com/)
- [Awesome README](https://github.com/matiassingers/awesome-readme)
- [Standard Readme](https://github.com/RichardLitt/standard-readme)
- [Art of README](https://github.com/noffle/art-of-readme)
