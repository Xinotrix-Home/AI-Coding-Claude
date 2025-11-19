# Test Suite Documentation

This directory contains the test suite for the Vectal.ai Clone backend.

## Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests
│   ├── test_password.py     # Password utilities tests
│   └── test_jwt.py          # JWT token tests
└── integration/             # Integration tests
    ├── test_auth_registration.py  # User registration tests
    ├── test_auth_login.py         # Login and token tests
    ├── test_auth_oauth.py         # OAuth authentication tests
    └── test_auth_security.py      # Security features tests
```

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure PostgreSQL test database is running:
```bash
docker-compose up -d postgres
```

3. Create test database:
```bash
createdb vectal_test
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_password.py

# Specific test class
pytest tests/integration/test_auth_login.py::TestUserLogin

# Specific test method
pytest tests/integration/test_auth_login.py::TestUserLogin::test_login_success
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Failed Tests Only

```bash
pytest --lf
```

## Test Coverage

### Phase 2: Authentication System ✅

- ✅ Password hashing and verification
- ✅ Password strength validation
- ✅ Email validation
- ✅ JWT token creation and verification
- ✅ User registration (success and error cases)
- ✅ User login (success and error cases)
- ✅ Token refresh
- ✅ Logout
- ✅ OAuth authentication (Google and GitHub)
- ✅ Rate limiting
- ✅ Account lockout
- ✅ Password security
- ✅ Token security
- ✅ Inactive user handling

## Writing New Tests

### Unit Tests

Unit tests should test individual functions or methods in isolation:

```python
def test_function_name():
    """Test description"""
    result = function_to_test(input)
    assert result == expected_output
```

### Integration Tests

Integration tests should test API endpoints with database:

```python
@pytest.mark.asyncio
async def test_endpoint_name(client: AsyncClient, db_session: AsyncSession):
    """Test description"""
    response = await client.post("/api/v1/endpoint", json={...})
    assert response.status_code == 200
```

### Using Fixtures

Common fixtures available in `conftest.py`:

- `client`: HTTP test client
- `db_session`: Database session
- `test_user`: Regular test user
- `test_user_unverified`: Unverified test user
- `oauth_user`: OAuth test user
- `auth_headers`: Authentication headers with valid token

## Best Practices

1. **Test Naming**: Use descriptive names that explain what is being tested
2. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification
3. **Isolation**: Each test should be independent and not rely on other tests
4. **Cleanup**: Use fixtures to ensure proper setup and teardown
5. **Mocking**: Mock external services (OAuth providers, email services, etc.)
6. **Coverage**: Aim for >80% code coverage
7. **Documentation**: Add docstrings to explain complex test scenarios

## Continuous Integration

Tests are automatically run on:
- Every pull request
- Every commit to main branch
- Nightly builds

CI configuration is in `.github/workflows/test.yml`

## Troubleshooting

### Database Connection Issues

If tests fail with database connection errors:

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres

# Recreate test database
dropdb vectal_test
createdb vectal_test
```

### Import Errors

If tests fail with import errors:

```bash
# Ensure you're in the backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### Async Test Issues

If async tests hang or fail:

```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Check pytest.ini has asyncio_mode = auto
```
