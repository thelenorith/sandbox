# Work Standards

A comprehensive, generic set of standards for software development projects. These standards are designed to be adopted by reference, allowing project-specific customization while maintaining consistency.

## Documents

### Core Standards

| Standard | Description |
|----------|-------------|
| [Naming](naming.md) | Project, package, and code naming conventions |
| [Project Structure](project-structure.md) | Directory layout and required files |
| [README Format](readme-format.md) | README structure and content |
| [Testing](testing.md) | Unit testing conventions |

### Build & CI/CD

| Standard | Description |
|----------|-------------|
| [Makefile](makefile.md) | Build targets and conventions |
| [GitHub Workflows](github-workflows.md) | CI/CD pipeline configuration |

### Interface Standards

| Standard | Description |
|----------|-------------|
| [CLI](cli.md) | Command-line interface conventions |
| [Logging & Progress](logging-progress.md) | Logging, progress indicators, and output |
| [Services](services.md) | Backend service and microservice standards |
| [User Interface](user-interface.md) | Frontend and UI/UX standards |
| [API Design](api-design.md) | REST, GraphQL, and API conventions |

### Automation

| Standard | Description |
|----------|-------------|
| [Agents](agents.md) | Claude Code skills and subagents |

## Guiding Principles

1. **Consistency** - All projects follow the same patterns
2. **Simplicity** - Minimal configuration, sensible defaults
3. **Automation** - CI catches issues before merge
4. **Discoverability** - Standard locations for everything
5. **Industry Alignment** - Build on established standards rather than reinventing

## Industry Standards Referenced

These standards build upon and reference established industry practices:

| Standard | Reference |
|----------|-----------|
| Semantic Versioning | [SemVer 2.0.0](https://semver.org/) |
| Conventional Commits | [conventionalcommits.org](https://www.conventionalcommits.org/) |
| 12-Factor App | [12factor.net](https://12factor.net/) |
| Python Style | [PEP 8](https://peps.python.org/pep-0008/), [PEP 257](https://peps.python.org/pep-0257/) |
| REST API Design | [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines) |
| OpenAPI | [OpenAPI Specification](https://spec.openapis.org/oas/latest.html) |
| Web Accessibility | [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/) |

## Adopting These Standards

To adopt these standards in your project, reference them in your documentation:

```markdown
This project follows the [Work Standards](https://github.com/thelenorith/sandbox/tree/main/standards)
with the following project-specific modifications:

- [List any deviations or extensions]
```

## Critical Constraints

Projects adopting these standards should document their own critical constraints. Common examples include:

- **Budget limitations** (e.g., Git LFS, cloud resources)
- **Compliance requirements** (e.g., HIPAA, GDPR, SOC2)
- **Platform restrictions** (e.g., supported Python versions, browsers)
- **Performance targets** (e.g., response times, uptime SLAs)
