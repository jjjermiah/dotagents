# Testing: pytest

**ALWAYS query Context7 before writing pytest code.**

**For comprehensive patterns, load the `python-testing` skill.**

## Context7 (REQUIRED)

```text
Library: /pytest-dev/pytest

Suggested queries:
- "fixtures and conftest"
- "parametrize decorator"
- "async tests with pytest-asyncio"
- "markers and skip conditions"

Library: /lundberg/pytest-httpx

Suggested queries:
- "mock httpx requests"
- "assert request was made"
```

## Why pytest > unittest

- Less boilerplate
- Better assertions (`assert x == y`)
- Powerful fixtures
- Plugin ecosystem

## Install

```bash
pip install pytest pytest-cov pytest-asyncio pytest-httpx
```

## Quick Pattern

```python
import pytest

@pytest.fixture
def sample_user():
    return {"id": 1, "name": "Alice"}

def test_user(sample_user):
    assert sample_user["name"] == "Alice"

@pytest.mark.asyncio
async def test_async():
    result = await async_function()
    assert result
```

## CLI Testing (typer)

```python
from typer.testing import CliRunner
runner = CliRunner()
result = runner.invoke(app, ["command", "--flag"])
assert result.exit_code == 0
```
