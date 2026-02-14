# HTTP: httpx

**ALWAYS query Context7 before writing httpx code.**

## Context7 (REQUIRED)

```text
Library: /encode/httpx

Suggested queries:
- "async client usage and configuration"
- "timeout and error handling"
- "streaming responses"
- "mock transport for testing"
```

## Why httpx > requests/urllib

- Sync + async in one API
- HTTP/2, connection pooling
- Sensible timeout defaults
- Type-annotated

## Install

```bash
pip install httpx[http2]
```

## Quick Pattern

```python
import httpx

# Sync
response = httpx.get(url, timeout=30.0)
response.raise_for_status()

# Async (preferred)
async with httpx.AsyncClient(base_url="https://api.example.com") as client:
    response = await client.get("/users")
```

## Key Classes

- `httpx.Client` / `httpx.AsyncClient` - Reusable clients
- `httpx.Timeout` - Granular timeout config
- `httpx.HTTPStatusError` - 4xx/5xx errors
- `httpx.RequestError` - Connection errors
