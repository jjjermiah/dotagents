# Logging: structlog

**ALWAYS query Context7 before writing structlog code.**

## Context7 (REQUIRED)

```text
Library: /hynek/structlog

Suggested queries:
- "configure structlog with JSON output"
- "context binding and contextvars"
- "stdlib logging integration"
- "FastAPI middleware logging"
```

## Why structlog > logging

- Structured output (JSON) for log aggregation
- Context binding (request IDs persist)
- Processors pipeline
- Works WITH stdlib handlers

## Install

```bash
pip install structlog
```

## Quick Pattern

```python
import structlog

log = structlog.get_logger()
log = log.bind(request_id="abc-123")
log.info("user_action", action="login", user_id=123)
# {"event": "user_action", "request_id": "abc-123", ...}
```

## Key APIs

- `structlog.configure()` - Global setup
- `structlog.get_logger()` - Get bound logger
- `log.bind()` - Add persistent context
- `structlog.contextvars.bind_contextvars()` - Request-scoped context
- `structlog.processors.JSONRenderer()` - JSON output
- `structlog.dev.ConsoleRenderer()` - Dev colored output
