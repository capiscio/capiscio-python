# Tests for capiscio-python CLI

This directory contains unit and E2E tests for the `capiscio` CLI wrapper.

## Directory Structure

```
tests/
├── unit/              # Unit tests with mocks (no server required)
│   ├── test_cli.py
│   └── test_manager.py
└── e2e/               # E2E tests (offline mode, no server required)
    ├── conftest.py    # Pytest fixtures and configuration
    ├── fixtures/      # Test data files
    │   ├── valid-agent-card.json
    │   ├── invalid-agent-card.json
    │   └── malformed.txt
    ├── test_validate_e2e.py  # Validation command tests
    └── test_badge_e2e.py     # Badge issuance/verification tests
```

## Running Tests

### Run All Tests

```bash
pytest               # All tests
pytest tests/unit/   # Unit tests only
pytest tests/e2e/    # E2E tests only
```

### Run Specific Test File

```bash
pytest tests/e2scio --cov-report=html
```

## E2E Test Design

The E2E tests are designed to run **offline** without requiring a server:

- **Validate tests**: Use `--schema-only` flag for local schema validation
- **Badge tests**: Use `--self-sign` for issuance and `--accept-self-signed --offline` for verification

This approach allows E2E tests to run in CI without complex server infrastructure.

## Test Coverage

### Validate Command (`test_validate_e2e.py`)

- ✅ Valid local agent card file (schema-only mode)
- ✅ Invalid local agent card file
- ✅ Malformed JSON file
- ✅ Nonexistent file
- ✅ JSON output format
- ✅ Help command

###     ├── test_validate_e2e.sue self-signed badge
- ✅ Issue badge with custom expiration
- ✅ Issue badge with audience restriction
- ✅ Verify self-signed badge (offline)
- ✅ Verify invalid token (error handling)
- ✅ Help commands (badge, issue, verify)

## CI/CD Integration

The E2E tests run in GitHub Actions without server dependencies:

```yaml
# See .github/workflows/e2e.yml
- name: Run E2E tests
  run: pytest tests/e2e/
```

## Notes

- **Offline Mode**: All E2E tests run offline without server dependencies
- **Download Messages**: On first run, the CLI may download the capiscio-core binary; tests handle this gracefully

## Troubleshooting

### Build/Install Issues

Ensure the project is installed:

```bash
pip install -e .
pytest tests/e2e/
```

### Path Issues

Ensure you're running pytest from the project root:

```bash
cd /path/to/capiscio-python
pytest tests/e2e/
```
