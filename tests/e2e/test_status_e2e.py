"""
E2E tests for capiscio status commands.

Tests agent and badge status check commands against a live server.
Requires CAPISCIO_TEST_AGENT_ID environment variable.
"""

import pytest
import subprocess
import json
import os
import uuid


class TestStatusCommands:
    """Test agent and badge status check commands."""

    @pytest.mark.skipif(
        not os.getenv("CAPISCIO_TEST_AGENT_ID"),
        reason="CAPISCIO_TEST_AGENT_ID not set"
    )
    def test_agent_status_valid_agent(self, test_agent_id: str, wait_for_server):
        """Test checking status of a valid agent."""
        result = subprocess.run(
            ["capiscio", "agent", "status", test_agent_id],
            capture_output=True,
            text=True
        )
        
        # Status check should succeed
        assert result.returncode == 0, f"Agent status check failed: {result.stderr}"
        
        # Output should contain status information
        output = result.stdout.lower()
        assert "status" in output or "active" in output or "enabled" in output or "disabled" in output, \
            f"Expected status information in output, got: {result.stdout}"

    def test_agent_status_invalid_agent(self, wait_for_server):
        """Test checking status of a nonexistent agent."""
        invalid_agent_id = str(uuid.uuid4())
        
        result = subprocess.run(
            ["capiscio", "agent", "status", invalid_agent_id],
            capture_output=True,
            text=True
        )
        
        # Should fail with not found error
        assert result.returncode != 0, "Should fail for nonexistent agent"
        
        error_output = (result.stderr + result.stdout).lower()
        assert "not found" in error_output or "unknown" in error_output or "does not exist" in error_output, \
            f"Expected not found error, got: stdout={result.stdout}, stderr={result.stderr}"

    def test_agent_status_malformed_id(self, wait_for_server):
        """Test checking status with malformed agent ID."""
        malformed_id = "not-a-valid-uuid"
        
        result = subprocess.run(
            ["capiscio", "agent", "status", malformed_id],
            capture_output=True,
            text=True
        )
        
        # Should fail with validation error
        assert result.returncode != 0, "Should fail for malformed ID"
        
        error_output = (result.stderr + result.stdout).lower()
        assert "invalid" in error_output or "malformed" in error_output or "uuid" in error_output, \
            f"Expected validation error, got: stdout={result.stdout}, stderr={result.stderr}"

    @pytest.mark.skipif(
        not os.getenv("CAPISCIO_TEST_AGENT_ID"),
        reason="CAPISCIO_TEST_AGENT_ID not set"
    )
    def test_agent_status_json_output(self, test_agent_id: str, wait_for_server):
        """Test agent status with JSON output format."""
        result = subprocess.run(
            ["capiscio", "agent", "status", test_agent_id, "--output", "json"],
            capture_output=True,
            text=True
        )
        
        # Should succeed
        assert result.returncode == 0, f"Agent status check failed: {result.stderr}"
        
        # Output should be valid JSON
        try:
            output_data = json.loads(result.stdout)
            assert isinstance(output_data, dict), "JSON output should be a dictionary"
            # Should contain status-related fields
            assert any(key in output_data for key in ["status", "active", "enabled", "state"]), \
                f"JSON output should contain status information, got: {output_data}"
        except json.JSONDecodeError as e:
            pytest.fail(f"Output is not valid JSON: {e}\nOutput: {result.stdout}")

    def test_badge_status_nonexistent(self, wait_for_server):
        """Test checking status of a nonexistent badge."""
        nonexistent_jti = str(uuid.uuid4())
        
        result = subprocess.run(
            ["capiscio", "badge", "status", nonexistent_jti],
            capture_output=True,
            text=True
        )
        
        # Should fail with not found error
        assert result.returncode != 0, "Should fail for nonexistent badge"
        
        error_output = (result.stderr + result.stdout).lower()
        assert "not found" in error_output or "unknown" in error_output or "does not exist" in error_output, \
            f"Expected not found error, got: stdout={result.stdout}, stderr={result.stderr}"

    def test_badge_status_malformed_jti(self, wait_for_server):
        """Test checking badge status with malformed JTI."""
        malformed_jti = "not-a-valid-jti"
        
        result = subprocess.run(
            ["capiscio", "badge", "status", malformed_jti],
            capture_output=True,
            text=True
        )
        
        # Should fail with validation error
        assert result.returncode != 0, "Should fail for malformed JTI"
        
        error_output = (result.stderr + result.stdout).lower()
        assert any(keyword in error_output for keyword in ["invalid", "malformed", "uuid"]), \
            f"Expected validation error, got: stdout={result.stdout}, stderr={result.stderr}"

    def test_agent_status_help(self):
        """Test agent status command help."""
        result = subprocess.run(
            ["capiscio", "agent", "status", "--help"],
            capture_output=True,
            text=True
        )
        
        # Help should exit successfully
        assert result.returncode == 0, f"Help command failed: {result.stderr}"
        
        help_text = result.stdout.lower()
        assert "status" in help_text or "agent" in help_text, \
            f"Help should mention agent status, got: {result.stdout}"

    def test_badge_status_help(self):
        """Test badge status command help."""
        result = subprocess.run(
            ["capiscio", "badge", "status", "--help"],
            capture_output=True,
            text=True
        )
        
        # Help should exit successfully
        assert result.returncode == 0, f"Help command failed: {result.stderr}"
        
        help_text = result.stdout.lower()
        assert "status" in help_text or "badge" in help_text or "jti" in help_text, \
            f"Help should mention badge status, got: {result.stdout}"
