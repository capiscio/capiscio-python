"""
E2E tests for capiscio validate command.

Tests the validate command locally with --schema-only flag for offline validation.
"""

import pytest
import subprocess
import json
from pathlib import Path


class TestValidateCommand:
    """Test the validate command."""

    def test_validate_local_valid_file(self, valid_agent_card_path: Path):
        """Test validating a valid local agent card file."""
        result = subprocess.run(
            ["capiscio", "validate", str(valid_agent_card_path), "--schema-only"],
            capture_output=True,
            text=True
        )
        
        # Validate command should succeed for valid agent card
        assert result.returncode == 0, f"Validation failed: {result.stderr}"
        
        # Output should indicate success
        output = result.stdout.lower()
        assert "pass" in output or "valid" in output or "✅" in output, \
            f"Expected validation success message, got: {result.stdout}"

    def test_validate_local_invalid_file(self, invalid_agent_card_path: Path):
        """Test validating an invalid local agent card file."""
        result = subprocess.run(
            ["capiscio", "validate", str(invalid_agent_card_path), "--schema-only"],
            capture_output=True,
            text=True
        )
        
        # Validate command should fail for invalid agent card
        assert result.returncode != 0, "Validation should have failed for invalid card"
        
        # Error message should indicate validation failure
        error_output = (result.stderr + result.stdout).lower()
        assert "fail" in error_output or "error" in error_output or "❌" in error_output, \
            f"Expected validation error message, got: stdout={result.stdout}, stderr={result.stderr}"

    def test_validate_malformed_json(self, malformed_json_path: Path):
        """Test validating a malformed JSON file."""
        result = subprocess.run(
            ["capiscio", "validate", str(malformed_json_path), "--schema-only"],
            capture_output=True,
            text=True
        )
        
        # Should fail with parse error
        assert result.returncode != 0, "Should fail on malformed JSON"
        
        error_output = (result.stderr + result.stdout).lower()
        assert "json" in error_output or "parse" in error_output or "invalid" in error_output or "syntax" in error_output, \
            f"Expected JSON parse error, got: stdout={result.stdout}, stderr={result.stderr}"

    def test_validate_nonexistent_file(self, nonexistent_path: Path):
        """Test validating a file that doesn't exist."""
        result = subprocess.run(
            ["capiscio", "validate", str(nonexistent_path), "--schema-only"],
            capture_output=True,
            text=True
        )
        
        # Should fail with file not found error
        assert result.returncode != 0, "Should fail for nonexistent file"
        
        error_output = (result.stderr + result.stdout).lower()
        assert "not found" in error_output or "no such file" in error_output or "does not exist" in error_output or "failed" in error_output or "error" in error_output, \
            f"Expected file not found error, got: stdout={result.stdout}, stderr={result.stderr}"

    def test_validate_schema_only_mode(self, valid_agent_card_path: Path):
        """Test validate command with schema-only mode."""
        result = subprocess.run(
            ["capiscio", "validate", str(valid_agent_card_path), "--schema-only"],
            capture_output=True,
            text=True
        )
        
        # Should succeed
        assert result.returncode == 0, f"Validation failed: {result.stderr}"
        assert len(result.stdout) > 0, "Should produce output"

    def test_validate_with_json_output(self, valid_agent_card_path: Path):
        """Test validate command with JSON output format."""
        result = subprocess.run(
            ["capiscio", "validate", str(valid_agent_card_path), "--schema-only", "--json"],
            capture_output=True,
            text=True
        )
        
        # Should succeed
        assert result.returncode == 0, f"Validation failed: {result.stderr}"
        
        # Output should be valid JSON
        try:
            output_data = json.loads(result.stdout)
            assert isinstance(output_data, dict), "JSON output should be a dictionary"
        except json.JSONDecodeError as e:
            pytest.fail(f"Output is not valid JSON: {e}\nOutput: {result.stdout}")

    def test_validate_help(self):
        """Test validate command help output."""
        result = subprocess.run(
            ["capiscio", "validate", "--help"],
            capture_output=True,
            text=True
        )
        
        # Help should exit successfully
        assert result.returncode == 0, f"Help command failed: {result.stderr}"
        
        # Help text should contain usage information
        help_text = result.stdout.lower()
        assert "validate" in help_text, "Help should mention validate command"
        assert "usage" in help_text or "options" in help_text or "flags" in help_text, \
            f"Help should contain usage information, got: {result.stdout}"
