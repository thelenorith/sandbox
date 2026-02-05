# Service Standards

Standards for building backend services and microservices. Based on the [12-Factor App](https://12factor.net/) methodology and industry best practices.

## General Principles

1. **Stateless processes** - Services should not rely on in-memory state between requests
2. **Configuration via environment** - No hardcoded configuration values
3. **Disposability** - Services should start fast and shut down gracefully
4. **Observability** - Services should be monitorable and debuggable

## The 12-Factor App

These standards build on the 12-Factor methodology. Key factors:

| Factor | Principle |
|--------|-----------|
| I. Codebase | One codebase tracked in version control |
| II. Dependencies | Explicitly declare and isolate dependencies |
| III. Config | Store config in the environment |
| IV. Backing services | Treat backing services as attached resources |
| V. Build, release, run | Strictly separate build and run stages |
| VI. Processes | Execute the app as stateless processes |
| VII. Port binding | Export services via port binding |
| VIII. Concurrency | Scale out via the process model |
| IX. Disposability | Maximize robustness with fast startup and graceful shutdown |
| X. Dev/prod parity | Keep development and production as similar as possible |
| XI. Logs | Treat logs as event streams |
| XII. Admin processes | Run admin tasks as one-off processes |

Reference: [12factor.net](https://12factor.net/)

## Configuration

### Environment Variables

All configuration should come from environment variables:

```python
import os

DATABASE_URL = os.environ["DATABASE_URL"]  # Required
DEBUG = os.getenv("DEBUG", "false").lower() == "true"  # Optional with default
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # Optional with default
```

### Configuration Hierarchy

From lowest to highest priority:

1. Application defaults (code)
2. Configuration file (for development)
3. Environment variables (production)

### Required Environment Variables

Document all required environment variables:

```markdown
## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `REDIS_URL` | Yes | Redis connection string | `redis://localhost:6379` |
| `SECRET_KEY` | Yes | Application secret key | 32+ character random string |
| `LOG_LEVEL` | No | Logging level (default: INFO) | `DEBUG`, `INFO`, `WARNING` |
| `PORT` | No | Server port (default: 8000) | `8000` |
```

### Secrets Management

| Do | Don't |
|----|-------|
| Use secret management services | Commit secrets to git |
| Rotate secrets regularly | Use the same secret everywhere |
| Use different secrets per environment | Log secret values |
| Encrypt secrets at rest | Pass secrets via command line args |

## Health Checks

Every service must expose health check endpoints:

### Endpoint Requirements

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `GET /health` | Basic liveness | `200 OK` if process is running |
| `GET /health/ready` | Readiness probe | `200 OK` if ready to accept traffic |
| `GET /health/live` | Liveness probe | `200 OK` if process should continue |

### Health Check Response

```json
{
  "status": "healthy",
  "version": "1.2.3",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "database": "healthy",
    "cache": "healthy",
    "external_api": "degraded"
  }
}
```

### Implementation

```python
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/health/ready")
async def readiness():
    # Check dependencies
    db_ok = await check_database()
    cache_ok = await check_cache()

    if db_ok and cache_ok:
        return {"status": "ready"}
    else:
        return Response(
            content='{"status": "not ready"}',
            status_code=503,
            media_type="application/json"
        )
```

## Logging

### Structured Logging

Use structured (JSON) logging for production:

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "request_processed",
    request_id="abc123",
    user_id=42,
    duration_ms=150,
    status_code=200
)
```

Output:
```json
{
  "event": "request_processed",
  "request_id": "abc123",
  "user_id": 42,
  "duration_ms": 150,
  "status_code": 200,
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info"
}
```

### Log Levels

| Level | Use For |
|-------|---------|
| `DEBUG` | Detailed diagnostic information |
| `INFO` | Normal operational events |
| `WARNING` | Unexpected but handled situations |
| `ERROR` | Failures that need attention |
| `CRITICAL` | Service-impacting failures |

### What to Log

| Log | Don't Log |
|-----|-----------|
| Request/response metadata | Request/response bodies (unless debugging) |
| Error details and stack traces | Passwords, tokens, API keys |
| Business events and state changes | PII (names, emails, addresses) |
| Performance metrics | Credit card numbers, SSNs |

### Request Context

Include correlation IDs in all log entries:

```python
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    structlog.contextvars.bind_contextvars(request_id=request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

## Error Handling

### Error Response Format

Consistent error responses across all services:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "request_id": "abc123"
  }
}
```

### HTTP Status Codes

| Code | Use For |
|------|---------|
| `400` | Bad request / validation error |
| `401` | Authentication required |
| `403` | Forbidden / insufficient permissions |
| `404` | Resource not found |
| `409` | Conflict (e.g., duplicate resource) |
| `422` | Unprocessable entity |
| `429` | Rate limit exceeded |
| `500` | Internal server error |
| `502` | Bad gateway |
| `503` | Service unavailable |

### Error Handling Pattern

```python
from fastapi import HTTPException

class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": request.state.request_id
            }
        }
    )
```

## Graceful Shutdown

Services must handle shutdown signals gracefully:

```python
import signal
import asyncio

shutdown_event = asyncio.Event()

def handle_shutdown(signum, frame):
    logger.info("shutdown_signal_received", signal=signum)
    shutdown_event.set()

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

async def main():
    # Start server
    server = await start_server()

    # Wait for shutdown signal
    await shutdown_event.wait()

    # Graceful shutdown
    logger.info("starting_graceful_shutdown")
    await server.shutdown(timeout=30)
    await close_database_connections()
    await close_cache_connections()
    logger.info("shutdown_complete")
```

### Shutdown Sequence

1. Stop accepting new requests
2. Wait for in-flight requests to complete (with timeout)
3. Close database connections
4. Close cache connections
5. Flush logs
6. Exit

## Metrics

### Required Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests by method, path, status |
| `http_request_duration_seconds` | Histogram | Request duration |
| `http_requests_in_flight` | Gauge | Current in-flight requests |
| `db_connections_active` | Gauge | Active database connections |
| `db_query_duration_seconds` | Histogram | Database query duration |

### Prometheus Example

```python
from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'path', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'path']
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        path=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_DURATION.labels(
        method=request.method,
        path=request.url.path
    ).observe(duration)

    return response
```

## Database Connections

### Connection Pooling

Always use connection pools:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,           # Minimum connections
    max_overflow=10,       # Additional connections when needed
    pool_timeout=30,       # Wait time for connection
    pool_recycle=1800,     # Recycle connections after 30 min
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

### Connection Management

| Do | Don't |
|----|-------|
| Use connection pools | Create connection per request |
| Close connections on shutdown | Leave connections open |
| Handle connection errors gracefully | Crash on connection failure |
| Monitor pool metrics | Ignore connection warnings |

## Rate Limiting

Implement rate limiting to protect services:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/resource")
@limiter.limit("100/minute")
async def get_resource():
    return {"data": "..."}
```

### Rate Limit Headers

Include rate limit information in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705312800
```

## Security

### Security Headers

Set security headers on all responses:

```python
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### Input Validation

Validate all input:

```python
from pydantic import BaseModel, EmailStr, validator

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('name must not be empty')
        return v.strip()
```

## Container Standards

### Dockerfile Best Practices

```dockerfile
# Use specific version
FROM python:3.12-slim

# Don't run as root
RUN useradd --create-home appuser
WORKDIR /home/appuser

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Industry References

- [12-Factor App](https://12factor.net/)
- [Microsoft Cloud Design Patterns](https://docs.microsoft.com/en-us/azure/architecture/patterns/)
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [Kubernetes Health Checks](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
