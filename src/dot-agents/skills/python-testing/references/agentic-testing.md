# Agentic Testing Patterns

**Source**: [dagster blog](https://dagster.io/blog/pytest-for-agent-generated-code-concrete-testing-strategies-to-put-into-practice)

## Context Isolation

Test-writing agents run as **sub-agents with constrained context**:
- Prevents "fixing" failing tests by modifying code under test
- Each invocation is stateless (no accumulated history)
- Task-specific context only

## Workflow: Bug Fixes

1. Write failing test reproducing bug
2. Fix the bug
3. Confirm test passes
4. Leave test as regression guard

## Workflow: New Features

TDD encouraged:
1. Write test for feature being implemented NOW
2. Implement feature
3. Test passes

**Never write tests for "maybe later" features**.

## Test Level Routing

Explicit rules for where tests go:

```text
New business logic with deps → Layer 4 (fakes, 70%)
Pure utility function → Layer 3 (pure unit, 10%)
Real adapter coverage → Layer 2 (mocked I/O, 10%)
Critical user workflow → Layer 5 (real systems, 5%)
New/changed fake → Layer 1 (fake tests, 5%)
```

## Anti-Patterns for Agents

1. **Speculative tests** - Only test code being actively implemented
2. **Performance erosion** - Unit tests must stay fast (<2s total)
3. **subprocess in unit tests** - Use CliRunner, not subprocess
4. **Hardcoded paths** - Always use tmp_path fixture
5. **Testing implementation** - Test behavior, not method calls

## Macro Constraints

Define global test suite constraints:
- Total unit test runtime < 5 seconds
- No `time.sleep()` in unit tests
- No subprocess calls in unit tests
- All paths via fixtures (tmp_path)

## Intent Over Correctness

When agents write tests, **intent matters as much as correctness**:

```python
# BAD: Correct but unclear intent
def test_user():
    u = User("a@b.com")
    assert u.email == "a@b.com"

# GOOD: Clear intent
def test_user_stores_email_on_creation():
    """Verify user email is stored correctly during initialization."""
    user = User(email="alice@example.com")
    assert user.email == "alice@example.com"
```
