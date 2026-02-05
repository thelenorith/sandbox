# Naming Standards

Consistent naming conventions across all projects.

## General Principles

| Principle | Description |
|-----------|-------------|
| Clarity over brevity | Names should be self-documenting |
| Consistency | Same concept = same name everywhere |
| Searchability | Names should be easy to grep/find |
| Pronounceable | Names should be speakable in conversation |

## Project Naming

### Repository Names

| Convention | Example | Use |
|------------|---------|-----|
| `{prefix}-{noun}` | `my-app`, `api-gateway` | Simple projects |
| `{prefix}-{verb}-{noun}` | `data-sync-service` | Action-oriented tools |
| `{org}-{project}` | `acme-billing` | Organization-scoped projects |

**Rules:**

- Use lowercase with hyphens (kebab-case)
- Keep names under 30 characters
- Avoid generic names like `utils`, `common`, `misc` for top-level projects
- Use singular nouns: `light` not `lights`, `user` not `users`

### Package/Module Names

| Language | Convention | Example |
|----------|------------|---------|
| Python | snake_case | `my_package`, `data_processor` |
| JavaScript/TypeScript | kebab-case or camelCase | `my-package`, `myPackage` |
| Go | lowercase, no separators | `mypackage` |
| Java | lowercase, dots | `com.example.mypackage` |

## Code Naming

### Variables and Functions

| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case (Python) / camelCase (JS) | `user_count`, `userCount` |
| Functions | snake_case (Python) / camelCase (JS) | `get_user()`, `getUser()` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Classes | PascalCase | `UserService`, `DataProcessor` |
| Private | Leading underscore (Python) | `_internal_helper()` |

### Boolean Naming

| Pattern | Example | Use |
|---------|---------|-----|
| `is_*` | `is_valid`, `is_active` | State check |
| `has_*` | `has_permission`, `has_children` | Possession check |
| `can_*` | `can_edit`, `can_delete` | Capability check |
| `should_*` | `should_retry`, `should_cache` | Recommendation |

### Function Naming Patterns

| Pattern | Example | Use |
|---------|---------|-----|
| `get_*` | `get_user()` | Retrieve existing data |
| `create_*` | `create_user()` | Create new entity |
| `update_*` | `update_user()` | Modify existing entity |
| `delete_*` | `delete_user()` | Remove entity |
| `find_*` | `find_users_by_role()` | Search with criteria |
| `validate_*` | `validate_email()` | Check validity |
| `parse_*` | `parse_config()` | Transform input |
| `build_*` | `build_query()` | Construct complex object |

## CLI Tool Naming

### Command Names

| Pattern | Example | Use |
|---------|---------|-----|
| `{verb}` | `build`, `test`, `lint` | Simple actions |
| `{verb}-{noun}` | `create-user`, `delete-cache` | Targeted actions |
| `{noun}:{action}` | `user:create`, `db:migrate` | Namespaced commands |

### Option Naming

| Type | Example | Rule |
|------|---------|------|
| Single concept | `--dryrun`, `--debug` | No hyphens |
| Qualified/compound | `--no-overwrite`, `--output-dir` | Hyphen separates qualifier |
| Negation | `--no-cache`, `--no-verify` | Prefix with `no-` |

## File Naming

| Type | Convention | Example |
|------|------------|---------|
| Source files | snake_case (Python) / kebab-case (JS) | `user_service.py`, `user-service.ts` |
| Test files | `test_*.py` or `*.test.ts` | `test_user_service.py` |
| Config files | lowercase with dots | `pyproject.toml`, `.eslintrc.json` |
| Documentation | UPPERCASE or lowercase | `README.md`, `CONTRIBUTING.md` |

## Database Naming

| Element | Convention | Example |
|---------|------------|---------|
| Tables | snake_case, plural | `users`, `order_items` |
| Columns | snake_case | `created_at`, `user_id` |
| Primary keys | `id` or `{table}_id` | `id`, `user_id` |
| Foreign keys | `{referenced_table}_id` | `user_id`, `order_id` |
| Indexes | `idx_{table}_{columns}` | `idx_users_email` |
| Constraints | `{type}_{table}_{columns}` | `uq_users_email`, `fk_orders_user` |

## API Naming

| Element | Convention | Example |
|---------|------------|---------|
| Endpoints | kebab-case, plural nouns | `/api/users`, `/api/order-items` |
| Query params | snake_case or camelCase | `?page_size=10`, `?pageSize=10` |
| JSON fields | camelCase (JS) or snake_case (Python) | `{ "firstName": "..." }` |

## Abbreviations

| Rule | Good | Bad |
|------|------|-----|
| Avoid unless universal | `id`, `url`, `http` | `usr`, `cnt`, `btn` |
| Capitalize consistently | `userId`, `httpClient` | `userID`, `HTTPClient` |
| Expand in documentation | `cfg` -> "configuration" | Undefined abbreviations |

## Industry References

- [PEP 8 - Python Naming Conventions](https://peps.python.org/pep-0008/#naming-conventions)
- [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html#naming)
- [Effective Go - Names](https://go.dev/doc/effective_go#names)
- [Oracle Java Naming Conventions](https://www.oracle.com/java/technologies/javase/codeconventions-namingconventions.html)
