---
name: write-tests
description: Comprehensive test generation with multiple frameworks, mutation testing & chaos engineering
license: MIT
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Ls, Find, Cp
compatibility:
  - chalilulz
  - Claude Code
  - Cursor
---

# Write Tests (2026 Edition)

Generate comprehensive test suites: unit, integration, property-based, mutation, chaos.

## Why This Matters

- Untested code = technical debt bomb
- 80% of production incidents are regressions of previously working functionality
- Good tests enable safe refactoring, faster development, better design
- 2026 standard: **mutation score > 80%**, **coverage > 90%**

## Testing Pyramid (Modern)

```
      E2E Tests (5%)
      Integration Tests (15%)
   Unit Tests + Property Tests (80%)
```

Don't skip layers. E2E tests catch integration issues, unit tests catch logic bugs.

## Test Types to Implement

### 1. Unit Tests (pytest/unittest)
Test individual functions/classes in isolation.

```python
def test_process_user_data_valid_input():
    """Happy path: valid user data processes correctly."""
    result = process_user_data({"id": 1, "name": "Alice"})
    assert result.status == "success"
    assert result.id == 1
```

**Golden Rules:**
- One assertion per test (or one logical group)
- Test *behavior*, not implementation
- Mock external dependencies (DB, HTTP, file system)
- Use descriptive names: `test_<function>_<scenario>_<expected>`
- Fast: <100ms per test file

### 2. Parameterized Tests
Test multiple inputs efficiently:

```python
import pytest

@pytest.mark.parametrize("user_id,expected", [
    (1, True),      # valid ID
    (0, False),     # zero rejected
    (-1, False),    # negative rejected
    (999999, True), # large ID accepted
])
def test_user_id_validation(user_id, expected):
    assert validate_user_id(user_id) == expected
```

### 3. Property-Based Testing (Hypothesis)
Generate 100s of inputs automatically.

```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=1, max_value=1000))
def test_user_id_always_positive(user_id):
    """Property: user_id should always be positive."""
    result = validate_user_id(user_id)
    assert result >= 1

@given(st.text(min_size=1, max_size=100))
def test_username_no_sql_injection(username):
    """Property: username should never produce SQL."""
    query = build_query(username)
    assert "DROP TABLE" not in query
    assert ";" not in query
```

**Why**: Finds edge cases humans miss. Run 1000 examples per test.

### 4. Mutation Testing (Critical)
Test your tests are effective.

```bash
# Install mutmut
pip install mutmut

# Run mutation testing
mutmut run --paths-to-mutate=src/ tests/
```

**Target**: Mutation score > 80%

If score < 80%:
- Add tests that kill surviving mutants
- Remove dead code (mutants that survive because code is unreachable)
- Lower test thresholds if mutation is unrealistic

### 5. Integration Tests
Test component interactions with real (but isolated) dependencies.

```python
def test_user_service_integration(test_db):  # pytest fixture with isolated DB
    """Test UserService with real database (but test data)."""
    # Setup
    test_db.save(User(id=1, name="Test"))
    
    # Execute
    result = UserService.get_user(1)
    
    # Assert
    assert result.name == "Test"
```

**Rules:**
- Use test containers (Docker) or in-memory DB (SQLite)
- Clean up after each test
- Don't test third-party APIs (mock those)
- Run less frequently than unit tests (hourly, not per commit)

### 6. Contract Tests (Pact/Spring Cloud Contract)
For APIs: ensure provider meets consumer expectations.

```python
def test_api_contract_user_creation():
    """Verify API returns expected fields for /api/users POST."""
    response = client.post("/api/users", json={"name": "Alice"})
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["name"] == "Alice"
```

### 7. Chaos Engineering
Inject failures to test resilience.

```python
def test_service_handles_database_outage(monkeypatch):
    """Service should return 503 when database unavailable."""
    monkeypatch.setattr(db, "query", lambda *args: raise ConnectionError())
    response = app.get("/users")
    assert response.status_code == 503
    assert "temporarily unavailable" in response.json()["error"]
```

## Framework Selection (2026)

| Use Case | Recommended |
|----------|-------------|
| Simple unit tests | `pytest` (Python) or `vitest` (JS) |
| Property-based | `hypothesis` (Python) |
| Mutation testing | `mutmut` (Python), `pits` (Java) |
| Contract testing | `pact` (polyglot) |
| E2E/UI | `playwright` (cross-browser) |
| API testing | `pytest` + `requests` or `httpx` |
| Chaos engineering | Build custom fault injectors |

## Test File Structure

```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/
│   ├── test_database.py
│   └── test_api.py
├── property/
│   └── test_data_contracts.py
├── e2e/
│   └── test_checkout_flow.py
├── conftest.py                    # Shared fixtures
├── mutation.config.json           # Mutmut config
└── README.md                      # How to run tests
```

## Writing Good Tests

### AAA Pattern (Arrange-Act-Assert)

```python
def test_transfer_funds_insufficient_balance():
    # Arrange
    account = Account(balance=100)
    
    # Act
    with pytest.raises(InsufficientFundsError):
        account.transfer(200, to=other_account)
    
    # Assert
    assert account.balance == 100  # unchanged
    assert other_account.balance == 0  # no money moved
```

### Fixtures for Setup

```python
import pytest

@pytest.fixture
def test_user():
    """Creates a fresh user for each test."""
    return UserFactory.create(name="Test User")

@pytest.fixture(scope="module")
def test_database():
    """Shared database for module tests."""
    db = TestDatabase()
    yield db
    db.teardown()
```

### Mocking External Services

```python
from unittest.mock import patch

def test_send_email_calls_smtp():
    with patch("smtplib.SMTP") as mock_smtp:
        send_welcome_email("user@example.com")
        mock_smtp.return_value.sendmail.assert_called_once()
```

## Coverage & Quality Gates

```bash
# Run with coverage
pytest --cov=src --cov-report=html --cov-fail-under=90

# Run mutation testing
mutmut run

# Lint tests (they're code too)
ruff check tests/
```

**CI should fail if:**
- Coverage < 90%
- Mutation score < 80%
- Flaky test detected (test fails intermittently)
- Test runtime increased > 10% from baseline

## Common Testing Mistakes

❌ **Testing private methods directly** → Test through public interface
❌ **Asserting on implementation details** → Break refactors
❌ **Using random data without control** → Flaky tests
❌ **Not testing error paths** → Exceptions untested
❌ **Huge test functions** → One test, one assertion group
❌ **Using real time in tests** → Use freezegun or time machine
❌ **Not cleaning up test data** → Pollutes test DB

## Quick Start with chalilulz

1. `read` the source code you want to test
2. `write` a test file following the structure above
3. Use `bash` to run: `pytest tests/ -v --cov=src`
4. `edit` to fix failing tests
5. Repeat until coverage > 90%

## Remember

- **Tests are documentation**: Show how code *should* be used
- **Tests are safety net**: Catch regressions before production
- **Test failure = code failure** (not test failure)
- **Fast tests run frequently** (per-commit); slow tests run hourly
- **Mutation testing exposes weak tests**
- **No test is too small** — even 3 lines of coverage matters
- **Refactoring without tests = suicide**

## Running Your Test Suite

```bash
# Unit tests (fast)
pytest tests/unit -v

# All tests with coverage
pytest --cov=src --cov-report=xml

# Mutation testing
mutmut run

# E2E tests only
pytest tests/e2e -v
```
