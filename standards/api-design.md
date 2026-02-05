# API Design Standards

Standards for designing consistent, intuitive, and maintainable APIs. Based on [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines), [JSON:API](https://jsonapi.org/), and industry best practices.

## General Principles

1. **Consistency** - Similar operations should work the same way
2. **Predictability** - Developers should be able to guess how things work
3. **Discoverability** - APIs should be self-documenting
4. **Versioning** - APIs should evolve without breaking clients

## REST API Design

### URL Structure

```
https://api.example.com/v1/users/123/orders?status=pending
└──────────┬─────────┘ └┬┘ └──┬──┘ └┬┘ └──┬──┘ └─────┬─────┘
         host       version resource  id  sub-     query
                                      resource  parameters
```

### Resource Naming

| Rule | Good | Bad |
|------|------|-----|
| Use plural nouns | `/users`, `/orders` | `/user`, `/getOrders` |
| Use kebab-case | `/order-items` | `/orderItems`, `/order_items` |
| No verbs in URLs | `/users` (POST to create) | `/createUser` |
| Hierarchical relationships | `/users/123/orders` | `/orders?user_id=123` |

### HTTP Methods

| Method | Use For | Idempotent | Safe |
|--------|---------|------------|------|
| GET | Retrieve resource(s) | Yes | Yes |
| POST | Create resource | No | No |
| PUT | Replace resource | Yes | No |
| PATCH | Partial update | Yes | No |
| DELETE | Remove resource | Yes | No |

### Standard Endpoints

For a resource `/users`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | List users |
| POST | `/users` | Create user |
| GET | `/users/{id}` | Get user |
| PUT | `/users/{id}` | Replace user |
| PATCH | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Delete user |

## HTTP Status Codes

### Success Codes

| Code | Use For |
|------|---------|
| `200 OK` | Successful GET, PUT, PATCH, DELETE |
| `201 Created` | Successful POST that creates resource |
| `204 No Content` | Successful DELETE with no body |

### Client Error Codes

| Code | Use For |
|------|---------|
| `400 Bad Request` | Malformed request syntax |
| `401 Unauthorized` | Missing or invalid authentication |
| `403 Forbidden` | Valid auth but insufficient permissions |
| `404 Not Found` | Resource doesn't exist |
| `409 Conflict` | Resource state conflict (duplicate) |
| `422 Unprocessable Entity` | Validation errors |
| `429 Too Many Requests` | Rate limit exceeded |

### Server Error Codes

| Code | Use For |
|------|---------|
| `500 Internal Server Error` | Unexpected server error |
| `502 Bad Gateway` | Invalid response from upstream |
| `503 Service Unavailable` | Server temporarily unavailable |
| `504 Gateway Timeout` | Upstream timeout |

## Request/Response Format

### Request Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes (POST/PUT/PATCH) | `application/json` |
| `Accept` | Recommended | `application/json` |
| `Authorization` | When auth required | `Bearer <token>` |
| `X-Request-ID` | Recommended | Correlation ID for tracing |

### Response Headers

| Header | Include | Description |
|--------|---------|-------------|
| `Content-Type` | Always | `application/json` |
| `X-Request-ID` | Always | Echo request ID |
| `X-RateLimit-*` | When rate limiting | Rate limit info |
| `Location` | On 201 | URL of created resource |

### JSON Conventions

```json
{
  "id": "123",
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-01-15T14:45:00Z",
  "firstName": "John",
  "lastName": "Doe",
  "emailAddress": "john@example.com",
  "isActive": true,
  "roleIds": ["admin", "user"]
}
```

| Convention | Example | Rationale |
|------------|---------|-----------|
| camelCase for properties | `firstName` | JavaScript convention |
| ISO 8601 for dates | `2024-01-15T10:30:00Z` | Unambiguous, sortable |
| String IDs | `"id": "123"` | Avoid integer overflow |
| Boolean prefix | `isActive`, `hasPermission` | Clear intent |

## Pagination

### Offset-Based Pagination

```
GET /users?page=2&per_page=20
```

Response:

```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "perPage": 20,
    "total": 150,
    "totalPages": 8
  }
}
```

### Cursor-Based Pagination

For large datasets or real-time data:

```
GET /events?cursor=abc123&limit=20
```

Response:

```json
{
  "data": [...],
  "pagination": {
    "nextCursor": "def456",
    "hasMore": true
  }
}
```

### Link Headers

Include navigation links:

```
Link: <https://api.example.com/users?page=3>; rel="next",
      <https://api.example.com/users?page=1>; rel="prev",
      <https://api.example.com/users?page=8>; rel="last"
```

## Filtering, Sorting, and Searching

### Filtering

```
GET /users?status=active&role=admin
GET /orders?created_after=2024-01-01&amount_min=100
```

### Sorting

```
GET /users?sort=created_at         # Ascending (default)
GET /users?sort=-created_at        # Descending (prefix with -)
GET /users?sort=last_name,-created_at  # Multiple fields
```

### Searching

```
GET /users?q=john                  # General search
GET /users?search[name]=john       # Field-specific search
```

### Field Selection

Allow clients to request specific fields:

```
GET /users?fields=id,name,email
GET /users/123?include=orders,profile
```

## Error Responses

### Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid parameters",
    "details": [
      {
        "field": "email",
        "code": "INVALID_FORMAT",
        "message": "Email address is not valid"
      },
      {
        "field": "age",
        "code": "OUT_OF_RANGE",
        "message": "Age must be between 0 and 150"
      }
    ],
    "requestId": "abc-123-def"
  }
}
```

### Error Codes

Use consistent error codes:

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `AUTHENTICATION_REQUIRED` | Missing authentication |
| `PERMISSION_DENIED` | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | Resource doesn't exist |
| `RESOURCE_CONFLICT` | Resource state conflict |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Unexpected server error |

## Versioning

### URL Versioning (Recommended)

```
GET /v1/users
GET /v2/users
```

### Header Versioning (Alternative)

```
GET /users
Accept: application/vnd.api+json; version=2
```

### Versioning Guidelines

| Rule | Description |
|------|-------------|
| Use integers | `v1`, `v2` not `v1.2` |
| Version at release | Only increment on breaking changes |
| Support previous version | Minimum 6-12 months overlap |
| Document deprecations | Clear migration guides |

### Breaking vs Non-Breaking Changes

| Breaking (New Version) | Non-Breaking (Safe) |
|------------------------|---------------------|
| Removing endpoint | Adding endpoint |
| Removing field | Adding optional field |
| Changing field type | Adding optional parameter |
| Changing URL structure | Adding new response field |
| Changing error codes | Expanding enum values |

## Authentication

### Bearer Token

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### API Keys

```
X-API-Key: your-api-key
```

Or as query parameter (less secure, for webhooks):

```
GET /webhook?api_key=your-api-key
```

### OAuth 2.0 Scopes

```
Authorization: Bearer <token>
X-OAuth-Scopes: read:users, write:orders
```

## Rate Limiting

### Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1705312800
Retry-After: 60
```

### Rate Limit Response

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 60 seconds.",
    "retryAfter": 60
  }
}
```

## Documentation

### OpenAPI Specification

Document APIs with [OpenAPI 3.0+](https://spec.openapis.org/oas/latest.html):

```yaml
openapi: 3.0.3
info:
  title: User API
  version: 1.0.0
  description: API for managing users

paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        '200':
          description: List of users
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
```

### Documentation Requirements

| Element | Required |
|---------|----------|
| Endpoint description | Yes |
| Request/response examples | Yes |
| Authentication requirements | Yes |
| Error responses | Yes |
| Rate limits | Yes |
| Deprecation notices | When applicable |

## GraphQL Considerations

When GraphQL is appropriate:

| Use GraphQL When | Use REST When |
|-----------------|---------------|
| Clients need flexible queries | Fixed data requirements |
| Multiple related resources | Simple CRUD operations |
| Mobile/bandwidth-sensitive | Caching is critical |
| Rapid frontend iteration | Public/third-party API |

### GraphQL Standards

```graphql
type User {
  id: ID!
  email: String!
  firstName: String
  lastName: String
  createdAt: DateTime!
  orders(first: Int, after: String): OrderConnection!
}

type Query {
  user(id: ID!): User
  users(first: Int, after: String, filter: UserFilter): UserConnection!
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
}
```

## Anti-Patterns

| Avoid | Preferred |
|-------|-----------|
| Verbs in URLs | HTTP methods for actions |
| Nested resources > 2 levels | Flatten or use query params |
| Returning 200 for errors | Use appropriate status codes |
| Inconsistent naming | Stick to one convention |
| Undocumented breaking changes | Semantic versioning |
| No pagination | Always paginate lists |
| Exposing internal IDs | Use stable public identifiers |
| Leaking implementation details | Abstract behind API |

## Industry References

- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)
- [Google API Design Guide](https://cloud.google.com/apis/design)
- [JSON:API Specification](https://jsonapi.org/)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)
- [Zalando RESTful API Guidelines](https://opensource.zalando.com/restful-api-guidelines/)
