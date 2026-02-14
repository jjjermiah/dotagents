---
name: python-production-libs
description: Production-grade Python library selection and recommendations. Use when choosing libraries for HTTP clients, CLI frameworks, data validation, structured logging, JSON serialization, terminal output, or async patterns—e.g., "which library for HTTP", "modern alternatives to requests", "pydantic vs dataclasses", "structured logging setup".
---

# Python Production Libraries

## Purpose

Canonical library choices for production Python. Third-party when stdlib is painful; stdlib when it's good enough.

## CRITICAL: Use Context7 for Implementation

**YOU MUST NOT rely on pre-trained knowledge for these libraries.** APIs change frequently, and stale knowledge causes bugs. No exceptions.

**IMMEDIATELY upon loading this skill:**

1. Announce: "Using python-production-libs - will query Context7 for all library implementations"
2. Load the appropriate reference from this skill to get the Context7 library slug
3. Query Context7 with the suggested queries BEFORE writing any code
4. Write code based on Context7 results, NOT memory

**Library without Context7 query = implementation based on stale knowledge. Every time.**

Example workflow:

```text
1. Need HTTP client → Load references/http.md
2. Get slug: /encode/httpx
3. Query: mcp_context7_query-docs(libraryId="/encode/httpx", query="async client timeout configuration")
4. Write code from fresh docs
```

## Core Principle

**Stdlib is often outdated or painful** (`urllib`, `argparse`, `unittest`, `logging` for structured output). Our recommendations reflect modern Python production standards—third-party libs that have become the de facto standard.

## Quick Reference

| Domain     | Use This            | Not This                               |
| ---------- | ------------------- | -------------------------------------- |
| HTTP       | `httpx`             | `urllib`, `requests`                   |
| Logging    | `structlog`         | `logging` (for structured)             |
| CLI        | `typer`             | `argparse`                             |
| Validation | `pydantic`          | `dataclasses` (when validation needed) |
| JSON       | `orjson`            | `json` (when perf matters)             |
| Terminal   | `rich`              | `print()`                              |
| Env vars   | `pydantic-settings` | `os.environ`                           |
| Paths      | `pathlib` (stdlib)  | `os.path`                              |
| Dates/TZ   | `zoneinfo` (stdlib) | `pytz`                                 |
| Testing    | `pytest`            | `unittest`                             |
| Async      | `anyio`             | `asyncio` (for library code)           |

## References (Load as Needed)

Load the appropriate reference when working in that domain:

- **[references/http.md](references/http.md)** - HTTP requests, API clients, async HTTP
- **[references/logging.md](references/logging.md)** - Structured logging, context binding, JSON output
- **[references/cli.md](references/cli.md)** - CLI argument parsing, commands, options
- **[references/validation.md](references/validation.md)** - Data validation, serialization, settings
- **[references/json-perf.md](references/json-perf.md)** - Fast JSON, datetime/UUID handling
- **[references/terminal.md](references/terminal.md)** - Rich output, tables, progress bars
- **[references/config-env.md](references/config-env.md)** - Config files, environment variables
- **[references/async.md](references/async.md)** - Async patterns, anyio, task groups
- **[references/testing.md](references/testing.md)** - pytest patterns (defer to python-testing skill)
- **[references/stdlib-good.md](references/stdlib-good.md)** - When stdlib IS the right choice

## Minimum Production Stack

```toml
[project]
dependencies = [
    "httpx[http2]>=0.27.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.5.0",
    "structlog>=24.0.0",
    "typer[all]>=0.15.0",
    "orjson>=3.9.0",
    "rich>=13.9.0",
    "python-dotenv>=1.0.0",
    "anyio>=4.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "ruff>=0.9.0",
    "mypy>=1.16.0",
]
```

## YOU MUST

- **Query Context7 BEFORE writing any implementation code** - Each reference has the library slug and suggested queries
- **Announce which library you're choosing and why** when making recommendations
- Check this skill before adding new dependencies
- Use type hints with all these libraries
- Prefer async variants when available
- Pin major versions in production

## NEVER

- **Rely on pre-trained knowledge** - Library APIs change; stale knowledge causes bugs
- Use `requests` (use `httpx` - same API, async support, modern standard)
- Use `argparse` for new CLIs (use `typer` - industry standard)
- Use stdlib `logging` for JSON output (use `structlog` - required for structured logging)
- Use `json` for high-throughput (use `orjson` - 10x faster)
