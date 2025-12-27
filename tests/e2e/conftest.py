"""
pytest configuration for capiscio-python CLI E2E tests.

Provides fixtures for testing the CLI against a live server.
Tests support both local Docker environment and dev.registry.capisc.io.
"""

import os
import time
import pytest
import requests
from pathlib import Path


@pytest.fixture(scope="session")
def api_url() -> str:
    """
    Get API URL from environment.
    
    Supports two modes:
    - Local: http://localhost:8080 (default)
    - Dev: https://dev.registry.capisc.io
    
    Set via CAPISCIO_API_URL environment variable.
    """
    return os.getenv("CAPISCIO_API_URL", "http://localhost:8080")


@pytest.fixture(scope="session")
def api_key() -> str:
    """
    Get API key from environment for authenticated tests.
    
    Set via CAPISCIO_API_KEY environment variable.
    For local testing, this should be a test key.
    For dev environment, use a real API key.
    """
    key = os.getenv("CAPISCIO_API_KEY")
    if not key:
        pytest.skip("CAPISCIO_API_KEY not set - skipping authenticated tests")
    return key


@pytest.fixture(scope="session")
def test_agent_id() -> str:
    """
    Get test agent ID from environment for status/badge tests.
    
    Set via CAPISCIO_TEST_AGENT_ID environment variable.
    This should be a pre-created agent in the test environment.
    """
    agent_id = os.getenv("CAPISCIO_TEST_AGENT_ID")
    if not agent_id:
        pytest.skip("CAPISCIO_TEST_AGENT_ID not set - skipping agent-specific tests")
    return agent_id


@pytest.fixture(scope="session")
def wait_for_server(api_url: str) -> None:
    """
    Wait for server to be ready before running tests.
    
    Checks the /health endpoint and waits up to 30 seconds
    for the server to become available.
    """
    max_retries = 30
    retry_delay = 1
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{api_url}/health", timeout=2)
            if response.status_code == 200:
                print(f"✓ Server ready at {api_url}")
                return
        except requests.exceptions.RequestException:
            pass
        
        if i < max_retries - 1:
            time.sleep(retry_delay)
    
    pytest.fail(f"Server not ready after {max_retries} retries at {api_url}")


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
    return fixtures_dir / "malformed.json"


@pytest.fixture
def nonexistent_path(fixtures_dir: Path) -> Path:
    """Path to a file that doesn't exist."""
    return fixtures_dir / "does-not-exist.json"
