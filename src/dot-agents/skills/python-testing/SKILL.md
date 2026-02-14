---
name: python-testing
description: Pytest-first Python testing with emphasis on fakes over mocks. Covers unit, integration, and async tests; fixture design; coverage setup; and debugging test failures. Use when writing tests, reviewing test quality, designing fixtures, setting up pytest, or debugging failures—e.g., "write unit tests for new feature", "fixture design patterns", "fakes vs mocks comparison", "fix failing tests".
---

# Python Testing Skill

## Purpose

Pytest-first testing emphasizing **fakes over mocks** and behavior-driven assertions. This skill applies to all Python testing work—always follow its guidance.

## Core Philosophy

Bias toward business logic tests over fakes (Layer 4). Fakes track mutations without coupling to implementation. See `references/test-doubles.md` for details.

## Required Tools

`pytest`, `pytest-cov`, `pytest-asyncio`, `pytest-mock`, `hypothesis`

## Directory Structure

```text
project/
├── src/mypackage/
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── fakes/          # Layer 1: Fake tests
    │   └── services/       # Layer 4: Business logic
    ├── integration/        # Layer 2: Sanity tests
    └── e2e/                # Layer 5: Real systems
```

See `references/test-layers.md` for layer distribution and decision tree.

## Quick Patterns

### Prefer Fakes Over Mocks

**YOU MUST use fakes for business logic tests. Never use mocks when testing behavior—mocks couple tests to implementation and break on every refactor.**

```python
# CORRECT: Fake tests behavior (use this approach)
def test_user_creation():
    fake_db = FakeDatabaseAdapter()
    service = UserService(database=fake_db)
    user = service.create_user("alice@example.com")
    assert user.id == 1
    assert "INSERT" in fake_db.executed_queries[0]

# WRONG: Mock couples to implementation—this pattern causes test breakage every time you refactor
def test_user_creation(mocker):
    mock_db = mocker.patch("myapp.service.database")
    # Breaks on refactor
```

### Factory Fixtures

```python
@pytest.fixture
def make_user():
    def _make(name="test", **kwargs):
        return User(name=name, email=f"{name}@example.com", **kwargs)
    return _make
```

### Capture Side Effects

```python
@pytest.fixture
def capture_emails(monkeypatch):
    sent = []
    monkeypatch.setattr("myapp.email.send", lambda **kw: sent.append(kw))
    return sent
```

## YOU MUST

- Test behavior, not implementation—tests that verify implementation details are technical debt
- Use fakes for business logic (mocks without fakes = brittle tests that fail on refactoring)
- Name tests descriptively: `test_<what>_<condition>_<expected>`
- Use `tmp_path` for all file operations in tests—never hardcode paths

## NEVER

- Use subprocess in unit tests—always use CliRunner from click.testing
- Hardcode paths in tests
- Test private methods directly (test public API behavior instead)
- Use `time.sleep()` in unit tests (use monkeypatch or freezegun)

## References (Load on Demand)

- **[references/test-doubles.md](references/test-doubles.md)** - Fakes vs mocks, when to use each
- **[references/anti-patterns.md](references/anti-patterns.md)** - Common mistakes
- **[references/test-layers.md](references/test-layers.md)** - Five-layer strategy, distribution
- **[references/fixture-patterns.md](references/fixture-patterns.md)** - Factory fixtures, scope, teardown
- **[references/agentic-testing.md](references/agentic-testing.md)** - AI-assisted test writing
