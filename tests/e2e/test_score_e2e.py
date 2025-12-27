"""
E2E tests for capiscio score command.

Tests the score command against a live server, verifying trust score
calculation for agent cards.
"""

import pytest
import subprocess
import json
from pathlib import Path


class TestScoreCommand:
    """Test the score command with real server integration."""

    def test_score_local_valid_file(self, valid_agent_card_path: Path, wait_for_server):
        """Test scoring a valid local agent card file."""
        result = subprocess.run(
            ["capiscio", "score", str(valid_agent_card_path)],
            capture_output=True,
            text=True
        )
        
        # Score command should succeed
        assert result.returncode == 0, f"Score command failed: {result.stderr}"
        
        # Output should contain score information
        output = result.stdout.lower()
        assert "score" in output or "trust" in output or any(char.isdigit() for char in result.stdout), \
            f"Expected score output, got: {result.stdout}"

    def test_score_local_invalid_file(self, invalid_agent_card_path: Path, wait_for_server):
        """Test scoring an invalid agent card."""
        result = subprocess.run(
            ["capiscio", "score", str(invalid_agent_card_path)],
            capture_output=True,
            text=True
        )
        
        # Score command may fail or return low score
        # Check if it handled the invalid card appropriately
        if result.returncode != 0:
            error_output = (result.stderr + result.stdout).lower()
            assert "invalid" in error_output or "error" in error_output, \
                f"Expected error for invalid card, got: {result.stdout}"
        else:
            # If it succeeds, it should at least produce some output
            assert len(result.stdout) > 0, "Score command should produce output"

    def test_score_with_json_output(self, valid_agent_card_path: Path, wait_for_server):
        """Test score command with JSON output format."""
        result = subprocess.run(
            ["capiscio", "score", str(valid_agent_card_path), "--output", "json"],
            capture_output=True,
            text=True
        )
        
        # Should succeed
        assert result.returncode == 0, f"Score command failed: {result.stderr}"
        
        # Output should be valid JSON with score information
        try:
            output_data = json.loads(result.stdout)
            assert isinstance(output_data, dict), "JSON output should be a dictionary"
            # Should contain score-related fields
            assert any(key in output_data for key in ["score", "trust_score", "trustScore", "level"]), \
                f"JSON output should contain score information, got: {output_data}"
        except json.JSONDecodeError as e:
            pytest.fail(f"Output is not valid JSON: {e}\nOutput: {result.stdout}")

    def test_score_nonexistent_file(self, nonexistent_path: Path, wait_for_server):
        """Test scoring a file that doesn't exist."""
        result = subprocess.run(
            ["capiscio", "score", str(nonexistent_path)],
            capture_output=True,
            text=True
        )
        
        # Should fail with file not found error
        assert result.returncode != 0, "Should fail for nonexistent file"
        
        error_output = (result.stderr + result.stdout).lower()
        assert "not found" in error_output or "no such file" in error_output or "does not exist" in error_output, \
            f"Expected file not found error, got: {result.stdout}"

    def test_score_remote_url(self, api_url: str, wait_for_server):
        """Test scoring a remote agent card URL."""
        # Test error handling for unreachable URL
        remote_url = "https://nonexistent-domain-12345.com/.well-known/agent.json"
        
        result = subprocess.run(
            ["capiscio", "score", remote_url],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should fail with network error
        assert result.returncode != 0, "Should fail for unreachable URL"
        
        error_output = (result.stderr + result.stdout).lower()
        assert any(keyword in error_output for keyword in ["network", "connection", "fetch", "unreachable", "failed"]), \
            f"Expected network error, got: {result.stdout}"

    def test_score_verbose_output(self, valid_agent_card_path: Path, wait_for_server):
        """Test score command with verbose flag."""
        result = subprocess.run(
            ["capiscio", "score", str(valid_agent_card_path), "--verbose"],
            capture_output=True,
            text=True
        )
        
        # Should succeed
        assert result.returncode == 0, f"Score command failed: {result.stderr}"
        
        # Verbose mode should produce more detailed output
        assert len(result.stdout) > 0, "Verbose mode should produce output"

    def test_score_help(self):
        """Test score command help output."""
        result = subprocess.run(
            ["capiscio", "score", "--help"],
            capture_output=True,
            text=True
        )
        
        # Help should exit successfully
        assert result.returncode == 0, f"Help command failed: {result.stderr}"
        
        # Help text should contain usage information
        help_text = result.stdout.lower()
        assert "score" in help_text, "Help should mention score command"
        assert "usage" in help_text or "options" in help_text or "arguments" in help_text, \
            f"Help should contain usage information, got: {result.stdout}"

    def test_score_minimal_agent_card(self, fixtures_dir: Path, wait_for_server):
        """Test scoring a minimal agent card with few fields."""
        # Create a minimal agent card fixture
        minimal_card = {
            "version": "1.0",
            "did": "did:web:minimal.example.com",
            "name": "Minimal Agent"
        }
        
        minimal_path = fixtures_dir / "minimal-agent-card.json"
        with open(minimal_path, "w") as f:
            json.dump(minimal_card, f)
        
        try:
            result = subprocess.run(
                ["capiscio", "score", str(minimal_path)],
                capture_output=True,
                text=True
            )
            
            # Should succeed and return a score (likely low)
            assert result.returncode == 0, f"Score command failed: {result.stderr}"
            assert len(result.stdout) > 0, "Should produce score output"
        finally:
            # Cleanup
            if minimal_path.exists():
                minimal_path.unlink()
