# Release Standards

Standards for versioning, releasing, and changelog management.

## Semantic Versioning

This standard follows [Semantic Versioning 2.0.0](https://semver.org/).

### Version Format

```
MAJOR.MINOR.PATCH
  │     │     │
  │     │     └─ Bug fixes, security patches (backwards compatible)
  │     └─────── New features (backwards compatible)
  └───────────── Breaking changes (incompatible API changes)
```

### Version Bumps

| Change Type | Bump | Example | When |
|-------------|------|---------|------|
| Breaking change | MAJOR | `1.2.3` → `2.0.0` | Remove feature, change API signature, rename public function |
| New feature | MINOR | `1.2.3` → `1.3.0` | Add feature, add optional parameter, deprecate (not remove) |
| Bug fix | PATCH | `1.2.3` → `1.2.4` | Fix bug, security patch, documentation fix |

### Pre-release Versions

For versions not yet stable:

| Type | Format | Example | Use |
|------|--------|---------|-----|
| Alpha | `X.Y.Z-alpha.N` | `2.0.0-alpha.1` | Early testing, incomplete features |
| Beta | `X.Y.Z-beta.N` | `2.0.0-beta.1` | Feature complete, testing |
| Release candidate | `X.Y.Z-rc.N` | `2.0.0-rc.1` | Final testing before release |

### Version Rules

1. **Start at `0.1.0`** - Initial development
2. **`0.x.y` is unstable** - Anything may change at any time
3. **`1.0.0` defines public API** - First stable release
4. **Never reuse versions** - Once released, a version is immutable
5. **Reset lower versions** - `1.2.3` → `1.3.0` (not `1.3.3`), `1.2.3` → `2.0.0` (not `2.2.3`)

### Breaking Change Examples

| Breaking | Not Breaking |
|----------|--------------|
| Remove public function | Add new function |
| Change function signature | Add optional parameter with default |
| Rename public class | Add new class |
| Change return type | Add new field to return object |
| Remove configuration option | Add new configuration option |
| Change default behavior | Fix bug in behavior |

## Changelog

Every project must maintain a `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/).

### Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- New feature description

### Changed
- Change description

### Deprecated
- Deprecation notice

### Removed
- Removal description

### Fixed
- Bug fix description

### Security
- Security fix description

## [1.2.0] - 2024-01-15

### Added
- Add user authentication endpoint (#42)

### Fixed
- Fix null pointer in parser (#38)

## [1.1.0] - 2024-01-01

### Added
- Initial release

[Unreleased]: https://github.com/user/repo/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/user/repo/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/user/repo/releases/tag/v1.1.0
```

### Change Categories

| Category | Use For |
|----------|---------|
| `Added` | New features |
| `Changed` | Changes to existing functionality |
| `Deprecated` | Features to be removed in future |
| `Removed` | Removed features (breaking) |
| `Fixed` | Bug fixes |
| `Security` | Security vulnerability fixes |

### Changelog Guidelines

1. **Write for humans** - Clear, concise descriptions
2. **Link to issues/PRs** - Reference with `(#123)`
3. **Group by category** - Use standard categories above
4. **Newest first** - Most recent version at top
5. **Date format** - Use ISO 8601: `YYYY-MM-DD`
6. **Keep Unreleased section** - Accumulate changes between releases

## Release Process

### Prerequisites

Before releasing:

- [ ] All tests pass
- [ ] All CI checks pass
- [ ] CHANGELOG.md is updated
- [ ] Version is bumped in source files
- [ ] Documentation is current

### Release Workflow

```
1. Update CHANGELOG.md
   └── Move [Unreleased] changes to new version section
   └── Add release date
   └── Add comparison links

2. Bump version in source files
   └── pyproject.toml / package.json / version.go
   └── __version__ if applicable

3. Commit version bump
   └── git commit -m "chore: release v1.2.0"

4. Create git tag
   └── git tag -a v1.2.0 -m "Release v1.2.0"

5. Push with tags
   └── git push origin main --tags

6. Create GitHub Release
   └── Use tag as release
   └── Copy changelog section as release notes
```

### Git Tags

| Convention | Example | Notes |
|------------|---------|-------|
| Prefix with `v` | `v1.2.0` | Recommended, clear intent |
| Annotated tags | `git tag -a` | Include message, recommended |
| Lightweight tags | `git tag` | Simple, less metadata |

**Always use annotated tags:**

```bash
# Create annotated tag
git tag -a v1.2.0 -m "Release v1.2.0"

# Push tags
git push origin v1.2.0
# Or push all tags
git push origin --tags
```

### GitHub Releases

Create releases via GitHub UI or CLI:

```bash
# Using GitHub CLI
gh release create v1.2.0 \
  --title "v1.2.0" \
  --notes-file RELEASE_NOTES.md

# Or generate notes from changelog
gh release create v1.2.0 \
  --title "v1.2.0" \
  --generate-notes
```

### Release Notes Template

```markdown
## What's Changed

### ✨ New Features
- Feature description (#PR)

### 🐛 Bug Fixes
- Fix description (#PR)

### 🔒 Security
- Security fix (#PR)

### 📚 Documentation
- Doc update (#PR)

**Full Changelog**: https://github.com/user/repo/compare/v1.1.0...v1.2.0
```

## Automation

### Automated Releases with GitHub Actions

Use workflow to automate release creation when tags are pushed:

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4

      - name: Extract version from tag
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT

      - name: Extract changelog for version
        id: changelog
        run: |
          VERSION=${{ steps.version.outputs.VERSION }}
          # Extract section for this version from CHANGELOG.md
          awk "/## \[${VERSION#v}\]/{flag=1; next} /## \[/{flag=0} flag" CHANGELOG.md > RELEASE_NOTES.md

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          body_path: RELEASE_NOTES.md
          generate_release_notes: false
```

### Version Validation

Add CI check to ensure version consistency:

```yaml
# .github/workflows/version-check.yml
name: Version Check

on:
  pull_request:
    branches: [main]

jobs:
  check-version:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check version consistency
        run: |
          # Extract version from pyproject.toml
          PYPROJECT_VERSION=$(grep '^version' pyproject.toml | cut -d'"' -f2)

          # Extract version from __init__.py if exists
          if [ -f "src/__init__.py" ]; then
            INIT_VERSION=$(grep '__version__' src/__init__.py | cut -d'"' -f2)
            if [ "$PYPROJECT_VERSION" != "$INIT_VERSION" ]; then
              echo "Version mismatch: pyproject.toml=$PYPROJECT_VERSION, __init__.py=$INIT_VERSION"
              exit 1
            fi
          fi

          echo "Version: $PYPROJECT_VERSION"
```

## Version in Code

### Python

```toml
# pyproject.toml
[project]
version = "1.2.0"
```

```python
# package/__init__.py
__version__ = "1.2.0"
```

Or use dynamic versioning:

```toml
# pyproject.toml
[project]
dynamic = ["version"]

[tool.setuptools.dynamic]
version = {attr = "package.__version__"}
```

### JavaScript/TypeScript

```json
{
  "name": "package-name",
  "version": "1.2.0"
}
```

### Go

```go
// version.go
package main

const Version = "1.2.0"
```

Or use build-time injection:

```go
var Version = "dev" // Set via -ldflags
```

```bash
go build -ldflags "-X main.Version=1.2.0"
```

## Conventional Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) to automate changelog generation:

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description | Version Bump |
|------|-------------|--------------|
| `feat` | New feature | MINOR |
| `fix` | Bug fix | PATCH |
| `docs` | Documentation only | None |
| `style` | Formatting, no code change | None |
| `refactor` | Code change, no feature/fix | None |
| `perf` | Performance improvement | PATCH |
| `test` | Adding tests | None |
| `chore` | Maintenance | None |

### Breaking Changes

```
feat!: remove deprecated endpoint

BREAKING CHANGE: The /v1/users endpoint has been removed.
Use /v2/users instead.
```

The `!` after type or `BREAKING CHANGE:` footer triggers MAJOR bump.

### Examples

```
feat: add user authentication

fix: handle null input in parser (#42)

feat(api)!: change response format

BREAKING CHANGE: Response now returns object instead of array.

chore: release v1.2.0
```

## Release Checklist

### Before Release

- [ ] All tests pass locally
- [ ] All CI checks pass
- [ ] No unresolved security vulnerabilities
- [ ] CHANGELOG.md updated with all changes
- [ ] Version bumped in all source files
- [ ] Documentation updated for new features
- [ ] Breaking changes documented with migration guide
- [ ] Pre-release tested if major version

### Release Steps

```bash
# 1. Ensure clean working directory
git status  # Should be clean

# 2. Update CHANGELOG.md
# Move [Unreleased] to new version section

# 3. Bump version
# Edit pyproject.toml, package.json, etc.

# 4. Commit
git add CHANGELOG.md pyproject.toml
git commit -m "chore: release v1.2.0"

# 5. Tag
git tag -a v1.2.0 -m "Release v1.2.0"

# 6. Push
git push origin main --tags

# 7. Create GitHub release (if not automated)
gh release create v1.2.0 --title "v1.2.0" --notes-file RELEASE_NOTES.md
```

### After Release

- [ ] Verify GitHub release created
- [ ] Verify package published (if applicable)
- [ ] Announce release (if applicable)
- [ ] Update [Unreleased] section in CHANGELOG.md for next cycle

## Anti-Patterns

| Avoid | Preferred |
|-------|-----------|
| Reusing version numbers | Each release has unique version |
| Forgetting to tag | Always tag releases |
| Empty changelog | Document all notable changes |
| Version only in one place | Single source of truth, or sync all |
| Manual release process | Automate with CI/CD |
| No pre-release testing | Use alpha/beta/rc versions |
| Breaking changes in PATCH | Only bug fixes in PATCH |
| Features in PATCH | Features require MINOR bump |

## Industry References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [Python Packaging - Versioning](https://packaging.python.org/en/latest/specifications/version-specifiers/)
- [npm semver](https://docs.npmjs.com/about-semantic-versioning)
