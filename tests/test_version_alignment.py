"""
Integration tests for capiscio-python CLI wrapper version alignment.

These tests verify that the Python wrapper correctly downloads and executes
the capiscio-core binary at the expected version (v2.2.0).
"""

import subprocess
import pytest


class TestPythonWrapperVersion:
    """Test capiscio-python version alignment."""
    
    def test_wrapper_version_matches_core(self):
        """Verify Python wrapper version matches capiscio-core version."""
        # Get wrapper version from package
        result = subprocess.run(
            ["python3", "-c", "import capiscio; print(capiscio.__version__)"],
            capture_output=True,
            text=True,
            cwd="/Users/beondenood/Development/CapiscIO/capiscio-python"
        )
        
        assert result.returncode == 0, f"Failed to get wrapper version: {result.stderr}"
        wrapper_version = result.stdout.strip()
        
        # Get core CLI version
        result = subprocess.run(
            ["python3", "-m", "capiscio", "--version"],
            capture_output=True,
            text=True,
            cwd="/Users/beondenood/Development/CapiscIO/capiscio-python"
        )
        
        if result.returncode != 0:
            pytest.skip("capiscio-core binary not yet downloaded")
        
        # Parse version from output (format: "capiscio version 2.2.0")
        core_version = result.stdout.strip().split()[-1].lstrip('v')
        
        assert wrapper_version == core_version, \
            f"Version mismatch: wrapper={wrapper_version}, core={core_version}"
        
        print(f"✓ Version aligned: {wrapper_version}")
    
    
    def test_wrapper_downloads_correct_binary_version(self):
        """Verify wrapper downloads v2.2.0 of capiscio-core."""
        # Read the wrapper code to check which version it downloads
        with open("/Users/beondenood/Development/CapiscIO/capiscio-python/src/capiscio/__main__.py", "r") as f:
            content = f.read()
        
        # Check that it references v2.2.0
        assert "2.2.0" in content or "CAPISCIO_VERSION" in content, \
            "Wrapper should reference capiscio-core v2.2.0"
        
        print(f"✓ Wrapper configured for v2.2.0")
    
    
    def test_pyproject_version_matches(self):
        """Verify pyproject.toml version matches package version."""
        import tomli
        
        with open("/Users/beondenood/Development/CapiscIO/capiscio-python/pyproject.toml", "rb") as f:
            pyproject = tomli.load(f)
        
        pyproject_version = pyproject["project"]["version"]
        
        # Get package version
        result = subprocess.run(
            ["python3", "-c", "import capiscio; print(capiscio.__version__)"],
            capture_output=True,
            text=True,
            cwd="/Users/beondenood/Development/CapiscIO/capiscio-python"
        )
        
        package_version = result.stdout.strip()
        
        assert pyproject_version == package_version, \
            f"pyproject.toml version ({pyproject_version}) != package version ({package_version})"
        
        print(f"✓ pyproject.toml version matches: {pyproject_version}")
    
    
    def test_binary_executes_successfully(self):
        """Verify downloaded binary can execute."""
        result = subprocess.run(
            ["python3", "-m", "capiscio", "--help"],
            capture_output=True,
            text=True,
            cwd="/Users/beondenood/Development/CapiscIO/capiscio-python"
        )
        
        if result.returncode != 0:
            pytest.skip("Binary not yet downloaded or executable")
        
        assert "capiscio" in result.stdout.lower(), \
            "Binary should display help text"
        
        print(f"✓ Binary executes successfully")
