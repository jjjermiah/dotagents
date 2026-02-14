# Advanced Fixture Patterns

## Factory Fixtures

When fixtures need arguments:

```python
@pytest.fixture
def make_user():
    def _make_user(name="test", email=None, **kwargs):
        email = email or f"{name}@example.com"
        return User(name=name, email=email, **kwargs)
    return _make_user

def test_user_display(make_user):
    admin = make_user(name="admin", role="admin")
    guest = make_user(name="guest", role="guest")
```

## Composing Fixtures

Fixtures can depend on other fixtures:

```python
@pytest.fixture
def db_session():
    session = create_session()
    yield session
    session.close()

@pytest.fixture
def user_repo(db_session):
    return UserRepository(db_session)

@pytest.fixture
def user_service(user_repo, email_client):
    return UserService(repo=user_repo, email=email_client)
```

## Two-Way Binding with Closures

Capture state changes from code under test:

```python
@pytest.fixture
def capture_emails(monkeypatch):
    sent = []
    def mock_send(to, subject, body):
        sent.append({"to": to, "subject": subject, "body": body})
    monkeypatch.setattr("myapp.email.send", mock_send)
    return sent

def test_welcome_email(capture_emails, user_service):
    user_service.create_user("alice@example.com")
    assert len(capture_emails) == 1
    assert "Welcome" in capture_emails[0]["subject"]
```

## Yield for Teardown

```python
@pytest.fixture
def temp_config(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("debug: true")
    original = os.environ.get("CONFIG_PATH")
    os.environ["CONFIG_PATH"] = str(config_file)
    yield config_file
    # Teardown
    if original:
        os.environ["CONFIG_PATH"] = original
    else:
        del os.environ["CONFIG_PATH"]
```

## Scope Guidance

| Scope      | Use Case                    | Example           |
| ---------- | --------------------------- | ----------------- |
| `function` | Default, fresh per test     | Most fixtures     |
| `class`    | Shared across class methods | Test class setup  |
| `module`   | Expensive, shared in file   | DB connection     |
| `session`  | Global, once per run        | Docker containers |

**Rule**: Use narrowest scope that works. Wider scope = shared state risk.

## Autouse: Use Sparingly

```python
# OK: Truly global, non-interfering
@pytest.fixture(autouse=True)
def reset_singletons():
    yield
    SingletonRegistry.clear()

# BAD: Hidden side effects
@pytest.fixture(autouse=True)
def mock_time():  # Affects all tests silently
    ...
```

**Prefer explicit fixture requests** over autouse.
