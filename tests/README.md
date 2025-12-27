# E2E Tests for capiscio-python CLI

This directory contains end-to-end tests that test the `capiscio` CLI against a live server.

## Directory Structure

```
tests/
├── unit/              # Unit tests with mocks (no server required)
│   ├── test_cli.py
│   └── test_manager.py
└── e2e/               # E2E tests against live server
    ├── conftest.py    # Pytest fixtures and configuration
    ├── fixtures/      # Test data files
    │   ├── valid-agent-card.json
    │   ├── invalid-agent-card.json
    │   └── malformed.json
    ├── test_validate_e2e.py  # Validation command tests
    ├── test_score_e2e.py     # Score command tests
    ├── test_badge_e2e.py     # Badge issuance/verification tests
    └── test_status_e2e.py    # Status check tests
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Only Unit Tests

```bash
pytest tests/unit/
```

### Run Only E2E Tests

```bash
pytest tests/e2e/
# or
pytest -m e2e
```

### Run Specific Test File

```bash
pytest tests/e2e/test_validate_e2e.py
```

### Run with Coverage

```bash
pytest --cov=capiscio --cov-report=html
```

## Environment Configuration

E2E tests require a running CapiscIO server. Configure the server URL and credentials using environment variables:

### Local Development (Default)

```bash
export CAPISCIO_API_URL=http://localhost:8080
export CAPISCIO_API_KEY=your_test_api_key
export CAPISCIO_TEST_AGENT_ID=your_test_agent_id
```

### Dev Environment

```bash
export CAPISCIO_API_URL=https://dev.registry.capisc.io
export CAPISCIO_API_KEY=your_dev_api_key
export CAPISCIO_TEST_AGENT_ID=your_dev_agent_id
```

### Using .env File (Recommended)

Create a `.env` file in the project root:

```bash
CAPISCIO_API_URL=http://localhost:8080
CAPISCIO_API_KEY=test_api_key_xxx
CAPISCIO_TEST_AGENT_ID=123e4567-e89b-12d3-a456-426614174000
```

Then load it before running tests:

```bash
set -a; source .env; set +a
pytest tests/e2e/
```

## Test Coverage

### Validate Command (`test_validate_e2e.py`)

- ✅ Valid local agent card file
- ✅ Invalid local agent card file
- ✅ Malformed JSON file
- ✅ Nonexistent file
- ✅ Remote URL (error handling)
- ✅ Verbose output flag
- ✅ JSON output format
- ✅ Help command

### Score Command (`test_score_e2e.py`)

- ✅ Valid local agent card
- ✅ Invalid local agent card
- ✅ JSON output format
- ✅ Nonexistent file
- ✅ Remote URL (error handling)
- ✅ Verbose output
- ✅ Minimal agent card
- ✅ Help command

### Badge Commands (`test_badge_e2e.py`)

- ✅ Issue badge with API key (IAL-0)
- ✅ Issue badge without API key (should fail)
- ✅ Issue badge for invalid agent ID
- ✅ Verify invalid token
- ✅ Help commands (badge, issue, verify)

### Status Commands (`test_status_e2e.py`)

- ✅ Agent status - valid agent
- ✅ Agent status - nonexistent agent
- ✅ Agent status - malformed ID
- ✅ Agent status - JSON output
- ✅ Badge status - nonexistent badge
- ✅ Badge status - malformed JTI
- ✅ Help commands (agent, badge)

## CI/CD Integration

The E2E tests are designed to run in CI/CD pipelines with a local test server:

```yaml
# .github/workflows/e2e.yml
- name: Start test server
  run: |
    docker-compose up -d
    sleep 5

- name: Run E2E tests
  run: |
    export CAPISCIO_API_URL=http://localhost:8080
    pytest tests/e2e/
```

## Notes

- **Server Wait**: Tests automatically wait for the server to be ready using the `wait_for_server` fixture
- **Skipped Tests**: Tests requiring `CAPISCIO_API_KEY` or `CAPISCIO_TEST_AGENT_ID` are skipped if these environment variables are not set
- **Timeouts**: Network-related tests have 10-second timeouts to prevent hanging
- **Cleanup**: Temporary test fixtures are automatically cleaned up

## Troubleshooting

### Server Not Ready

If tests fail with "Server not ready":

```bash
# Check if server is running
curl http://localhost:8080/health

# Check Docker containers
docker ps
```

### Authentication Errors

If badge tests fail with auth errors:

```bash
# Verify API key is set
echo $CAPISCIO_API_KEY

# Test API key manually
curl -H "X-Capiscio-Registry-Key: $CAPISCIO_API_KEY" \
  http://localhost:8080/v1/sdk/agents
```

### Path Issues

Ensure you're running pytest from the project root:

```bash
cd /path/to/capiscio-python
pytest tests/e2e/
```
