# Test Doubles: Fakes vs Mocks

**Source**: [pytest-with-eric.com](https://pytest-with-eric.com/mocking/pytest-common-mocking-problems/), [dagster fake-driven-testing](https://github.com/dagster-io/erk)

## The Hierarchy

| Type     | Behavior              | State            | When                     |
| -------- | --------------------- | ---------------- | ------------------------ |
| **Fake** | Real logic, in-memory | Tracks mutations | Business logic (70%)     |
| **Stub** | Canned responses      | None             | Simple returns           |
| **Mock** | Verifies calls        | Call tracking    | Interaction verification |
| **Spy**  | Real + tracking       | Both             | Partial verification     |

## Prefer Fakes Over Mocks

**Mocks couple tests to implementation**. Refactoring breaks tests even when behavior is unchanged.

```python
# BAD: Mock couples to implementation
def test_user_service(mocker):
    mock_db = mocker.patch("myapp.service.database")
    mock_db.execute.return_value = {"id": 1}
    # Breaks if you rename execute() to run_query()

# GOOD: Fake tests behavior
def test_user_service():
    fake_db = FakeDatabaseAdapter()
    service = UserService(database=fake_db)
    user = service.create_user("alice@example.com")
    assert user.id == 1
    assert "INSERT" in fake_db.executed_queries[0]
```

## When Mocks ARE Appropriate

1. **Verifying side effects** - email sent, API called
2. **Error injection** - simulate network failures
3. **Third-party boundaries** - external APIs you don't control
4. **Expensive operations** - when fakes would be complex

## Fake Design Principles

```python
class FakeDatabaseAdapter(DatabaseAdapter):
    def __init__(self):
        self._data: dict[str, list] = {}
        self.executed_queries: list[str] = []  # Tracking

    def execute(self, sql: str) -> None:
        self.executed_queries.append(sql)  # Track
        # Minimal real logic
        if sql.startswith("INSERT"):
            table = self._parse_table(sql)
            self._data.setdefault(table, []).append(...)
```

**Rules**:

- In-memory only (no I/O)
- Track mutations for assertions
- Minimal logic (just enough to work)
- Same interface as real implementation
