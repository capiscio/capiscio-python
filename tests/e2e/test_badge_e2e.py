"""
E2E tests for capiscio badge commands.

Tests badge issuance and verification using offline/self-signed mode.
No server required.
"""

import pytest
import subprocess


class TestBadgeCommands:
    """Test badge issuance and verification commands."""

    def test_badge_issue_self_signed(self):
        """Test self-signed badge issuance."""
        result = subprocess.run(
            [
                "capiscio", "badge", "issue",
                "--self-sign", "--domain", "test.example.com"
            ],
            capture_output=True,
            text=True
        )
        
        # Self-signed badge issuance should succeed
        assert result.returncode == 0, f"Badge issuance failed: {result.stderr}"
        
        # Output might include download messages on first run, get last line
        lines = result.stdout.strip().split('\n')
        output = lines[-1].strip()
        
        # Output should be a JWT (three dot-separated parts)
        parts = output.split(".")
        assert len(parts) == 3, f"Expected JWT format, got: {output}"

    def test_badge_issue_with_expiration(self):
        """Test badge issuance with custom expiration."""
        result = subprocess.run(
            [
                "capiscio", "badge", "issue",
                "--self-sign", "--exp", "10m"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Badge issuance failed: {result.stderr}"
        lines = result.stdout.strip().split('\n')
        output = lines[-1].strip()
        assert len(output.split(".")) == 3, "Expected JWT format"

    def test_badge_issue_with_audience(self):
        """Test badge issuance with audience restriction."""
        result = subprocess.run(
            [
                "capiscio", "badge", "issue",
                "--self-sign", "--aud", "https://api.example.com"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Badge issuance failed: {result.stderr}"
        lines = result.stdout.strip().split('\n')
        output = lines[-1].strip()
        assert len(output.split(".")) == 3, "Expected JWT format"

    def test_badge_verify_self_signed(self):
        """Test verifying a self-signed badge."""
        # First issue a badge
        issue_result = subprocess.run(
            [
                "capiscio", "badge", "issue",
                "--self-sign", "--domain", "test.example.com"
            ],
            capture_output=True,
            text=True
        )
        assert issue_result.returncode == 0, f"Badge issuance failed: {issue_result.stderr}"
        # Get token from last line (may have download messages on first run)
        lines = issue_result.stdout.strip().split('\n')
        token = lines[-1].strip()
        
        # Then verify it
        verify_result = subprocess.run(
            ["capiscio", "badge", "verify", token, "--accept-self-signed", "--offline"],
            capture_output=True,
            text=True
        )
        
        assert verify_result.returncode == 0, f"Badge verification failed: {verify_result.stderr}"
        output = verify_result.stdout.lower()
        assert "valid" in output or "verified" in output or "ok" in output, \
            f"Expected verification success, got: {verify_result.stdout}"

    def test_badge_verify_invalid_token(self):
        """Test badge verification with invalid token."""
        invalid_token = "invalid.jwt.token"
        
        result = subprocess.run(
            ["capiscio", "badge", "verify", invalid_token, "--accept-self-signed"],
            capture_output=True,
            text=True
        )
        
        # Should fail with verification error
        assert result.returncode != 0, "Should fail for invalid token"
        
        error_output = (result.stderr + result.stdout).lower()
        assert any(keyword in error_output for keyword in ["invalid", "verify", "failed", "malformed", "error"]), \
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
        assert "issue" in help_text or "self-sign" in help_text, \
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
