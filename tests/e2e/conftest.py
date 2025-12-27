"""
pytest configuration for capiscio-python CLI E2E tests.

Provides fixtures for testing the CLI offline using:
- validate --schema-only
- badge issue --self-sign
- badge verify --accept-self-signed --offline
"""

import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Get path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_agent_card_path(fixtures_dir: Path) -> Path:
    """Path to valid agent card fixture."""
    return fixtures_dir / "valid-agent-card.json"


@pytest.fixture
def invalid_agent_card_path(fixtures_dir: Path) -> Path:
    """Path to invalid agent card fixture."""
    return fixtures_dir / "invalid-agent-card.json"


@pytest.fixture
def malformed_json_path(fixtures_dir: Path) -> Path:
    """Path to malformed JSON fixture."""
    return fixtures_dir / "malformed.txt"


@pytest.fixture
def nonexistent_path(fixtures_dir: Path) -> Path:
    """Path to a file that doesn't exist."""
    return fixtures_dir / "does-not-exist.json"
