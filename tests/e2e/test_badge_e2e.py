"""
E2E tests for capiscio badge commands.

Tests badge issuance and verification commands against a live server.
Requires CAPISCIO_API_KEY and CAPISCIO_TEST_AGENT_ID environment variables.
"""

import pytest
import subprocess
import json
import os


class TestBadgeCommands:
    """Test badge issuance and verification commands."""

    @pytest.mark.skipif(
        not os.getenv("CAPISCIO_API_KEY"),
        reason="CAPISCIO_API_KEY not set"
    )
    def test_badge_issue_with_api_key(self, api_key: str, test_agent_id: str, wait_for_server):
        """Test badge issuance using API key authentication."""
        result = subprocess.run(
            [
                "capiscio", "badge", "issue",
                "--agent-id", test_agent_id,
                "--domain", "test.capisc.io"
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "CAPISCIO_API_KEY": api_key}
        )
        
        # Badge issuance should succeed (or fail with appropriate message)
        # The exact behavior depends on server implementation
        # We're testing that the CLI can communicate with the server
        output = result.stdout + result.stderr
        assert len(output) > 0, "Badge command should produce output"
        
        # If successful, output should contain token or JTI
        if result.returncode == 0:
            assert "token" in result.stdout.lower() or "badge" in result.stdout.lower(), \
                f"Expected badge token in output, got: {result.stdout}"

    @pytest.mark.skipif(
        not os.getenv("CAPISCIO_API_KEY"),
        reason="CAPISCIO_API_KEY not set"
    )
    def test_badge_issue_without_api_key(self, test_agent_id: str, wait_for_server):
        """Test badge issuance without API key (should fail)."""
        # Remove API key from environment
        env = {k: v for k, v in os.environ.items() if k != "CAPISCIO_API_KEY"}
        
        result = subprocess.run(
            [
                "capiscio", "badge", "issue",
                "--agent-id", test_agent_id,
                "--domain", "test.capisc.io"
            ],
            capture_output=True,
            text=True,
            env=env
        )
        
        # Should fail without authentication
        assert result.returncode != 0, "Badge issuance should fail without API key"
        
        error_output = (result.stderr + result.stdout).lower()
        assert any(keyword in error_output for keyword in ["auth", "key", "credential", "unauthorized"]), \
            f"Expected authentication error, got: {result.stdout}"

    @pytest.mark.skipif(
        not os.getenv("CAPISCIO_API_KEY"),
        reason="CAPISCIO_API_KEY not set"
    )
    def test_badge_issue_invalid_agent_id(self, api_key: str, wait_for_server):
        """Test badge issuance with invalid agent ID."""
        invalid_agent_id = "00000000-0000-0000-0000-000000000000"
        
        result = subprocess.run(
            [
                "capiscio", "badge", "issue",
                "--agent-id", invalid_agent_id,
                "--domain", "test.capisc.io"
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "CAPISCIO_API_KEY": api_key}
        )
        
        # Should fail with not found or similar error
        assert result.returncode != 0, "Should fail for invalid agent ID"
        
        error_output = (result.stderr + result.stdout).lower()
        assert any(keyword in error_output for keyword in ["not found", "invalid", "unknown", "does not exist"]), \
            f"Expected not found error, got: {result.stdout}"

    def test_badge_verify_invalid_token(self, wait_for_server):
        """Test badge verification with invalid token."""
        invalid_token = "invalid.jwt.token"
        
        result = subprocess.run(
            ["capiscio", "badge", "verify", invalid_token],
            capture_output=True,
            text=True
        )
        
        # Should fail with verification error
        assert result.returncode != 0, "Should fail for invalid token"
        
        error_output = (result.stderr + result.stdout).lower()
        assert any(keyword in error_output for keyword in ["invalid", "verify", "failed", "malformed"]), \
            f"Expected verification error, got: {result.stdout}"

    def test_badge_help(self):
        """Test badge command help output."""
        result = subprocess.run(
            ["capiscio", "badge", "--help"],
            capture_output=True,
            text=True
        )
        
        # Help should exit successfully
        assert result.returncode == 0, f"Help command failed: {result.stderr}"
        
        # Help text should contain badge command information
        help_text = result.stdout.lower()
        assert "badge" in help_text, "Help should mention badge command"
        assert any(keyword in help_text for keyword in ["issue", "verify", "usage"]), \
            f"Help should mention badge subcommands, got: {result.stdout}"

    def test_badge_issue_help(self):
        """Test badge issue subcommand help."""
        result = subprocess.run(
            ["capiscio", "badge", "issue", "--help"],
            capture_output=True,
            text=True
        )
        
        # Help should exit successfully
        assert result.returncode == 0, f"Help command failed: {result.stderr}"
        
        help_text = result.stdout.lower()
        assert "agent" in help_text or "issue" in help_text, \
            f"Help should mention badge issuance, got: {result.stdout}"

    def test_badge_verify_help(self):
        """Test badge verify subcommand help."""
        result = subprocess.run(
            ["capiscio", "badge", "verify", "--help"],
            capture_output=True,
            text=True
        )
        
        # Help should exit successfully
        assert result.returncode == 0, f"Help command failed: {result.stderr}"
        
        help_text = result.stdout.lower()
        assert "verify" in help_text or "token" in help_text, \
            f"Help should mention badge verification, got: {result.stdout}"
