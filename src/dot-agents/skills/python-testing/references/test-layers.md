# Five-Layer Testing Strategy

**Source**: [dagster fake-driven-testing](https://github.com/dagster-io/erk), [dagster blog](https://dagster.io/blog/pytest-for-agent-generated-code-concrete-testing-strategies-to-put-into-practice)

## Distribution

| Layer | Type                   | %       | Location               |
| ----- | ---------------------- | ------- | ---------------------- |
| 1     | Fake infrastructure    | 5%      | `tests/unit/fakes/`    |
| 2     | Integration sanity     | 10%     | `tests/integration/`   |
| 3     | Pure unit              | 10%     | `tests/unit/`          |
| 4     | Business logic (fakes) | **70%** | `tests/unit/services/` |
| 5     | E2E integration        | 5%      | `tests/e2e/`           |

## Layer 1: Fake Tests

**Purpose**: Verify test infrastructure works.

```python
def test_fake_db_tracks_queries():
    fake = FakeDatabaseAdapter()
    fake.execute("INSERT INTO users VALUES (1, 'alice')")
    assert len(fake.executed_queries) == 1
    assert "INSERT" in fake.executed_queries[0]
```

## Layer 2: Integration Sanity (Mocked I/O)

**Purpose**: Code coverage without slow I/O.

```python
def test_real_db_constructs_query(monkeypatch):
    mock_conn = Mock()
    monkeypatch.setattr("psycopg2.connect", lambda **_: mock_conn)
    db = RealDatabaseAdapter("postgresql://...")
    db.query("SELECT 1")
    mock_conn.cursor().execute.assert_called_with("SELECT 1")
```

## Layer 3: Pure Unit

**Purpose**: Zero-dependency logic. **No fakes, no mocks**.

```python
def test_sanitize_branch_name():
    assert sanitize_branch_name("feat/FOO-123") == "feat-foo-123"

def test_calculate_tax():
    assert calculate_tax(100, rate=0.08) == 8.0
```

## Layer 4: Business Logic (MAJORITY)

**Purpose**: Test features over fakes. Fast, reliable, debuggable.

```python
def test_user_service_creates_user():
    fake_db = FakeDatabaseAdapter()
    fake_email = FakeEmailClient()
    service = UserService(database=fake_db, email_client=fake_email)

    user = service.create_user("alice@example.com")

    assert user.id == 1
    assert "INSERT" in fake_db.executed_queries[0]
    assert fake_email.sent_emails[0]["to"] == "alice@example.com"
```

## Layer 5: E2E Integration

**Purpose**: Smoke tests with real systems. Use sparingly.

```python
def test_user_registration_e2e(test_db_url):
    db = RealDatabaseAdapter(test_db_url)
    service = UserService(database=db, email_client=RealEmailClient())
    user = service.register_user("alice@example.com", "password123")
    assert db.query("SELECT * FROM users WHERE id = %s", user.id)
```

## Decision Tree

```text
Need to test...
├─ Business logic with deps → Layer 4 (fakes)
├─ Pure utility, no deps → Layer 3 (pure unit)
├─ Fake implementation → Layer 1
├─ Real adapter coverage → Layer 2 (mocked)
└─ Critical workflow smoke → Layer 5 (real, sparingly)
```
