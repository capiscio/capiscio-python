"""Tests for capiscio.manager module."""
import os
import platform
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import pytest

from capiscio.manager import (
    get_platform_info,
    get_binary_filename,
    get_cache_dir,
    get_binary_path,
    download_binary,
    run_core,
    _fetch_expected_checksum,
    _verify_checksum,
    CORE_VERSION,
    GITHUB_REPO,
)


class TestGetPlatformInfo:
    """Tests for get_platform_info function."""

    @patch.object(platform, 'system', return_value='Darwin')
    @patch.object(platform, 'machine', return_value='arm64')
    def test_darwin_arm64(self, mock_machine, mock_system):
        """Test macOS arm64 detection."""
        os_name, arch = get_platform_info()
        assert os_name == "darwin"
        assert arch == "arm64"

    @patch.object(platform, 'system', return_value='Darwin')
    @patch.object(platform, 'machine', return_value='x86_64')
    def test_darwin_amd64(self, mock_machine, mock_system):
        """Test macOS Intel detection."""
        os_name, arch = get_platform_info()
        assert os_name == "darwin"
        assert arch == "amd64"

    @patch.object(platform, 'system', return_value='Linux')
    @patch.object(platform, 'machine', return_value='x86_64')
    def test_linux_amd64(self, mock_machine, mock_system):
        """Test Linux x86_64 detection."""
        os_name, arch = get_platform_info()
        assert os_name == "linux"
        assert arch == "amd64"

    @patch.object(platform, 'system', return_value='Linux')
    @patch.object(platform, 'machine', return_value='aarch64')
    def test_linux_arm64_aarch64(self, mock_machine, mock_system):
        """Test Linux aarch64 (alias for arm64) detection."""
        os_name, arch = get_platform_info()
        assert os_name == "linux"
        assert arch == "arm64"

    @patch.object(platform, 'system', return_value='Windows')
    @patch.object(platform, 'machine', return_value='AMD64')
    def test_windows_amd64(self, mock_machine, mock_system):
        """Test Windows AMD64 detection."""
        os_name, arch = get_platform_info()
        assert os_name == "windows"
        assert arch == "amd64"

    @patch.object(platform, 'system', return_value='FreeBSD')
    @patch.object(platform, 'machine', return_value='x86_64')
    def test_unsupported_os(self, mock_machine, mock_system):
        """Test that unsupported OS raises RuntimeError."""
        with pytest.raises(RuntimeError, match="Unsupported operating system"):
            get_platform_info()

    @patch.object(platform, 'system', return_value='Linux')
    @patch.object(platform, 'machine', return_value='i386')
    def test_unsupported_arch(self, mock_machine, mock_system):
        """Test that unsupported architecture raises RuntimeError."""
        with pytest.raises(RuntimeError, match="Unsupported architecture"):
            get_platform_info()


class TestGetBinaryFilename:
    """Tests for get_binary_filename function."""

    def test_darwin_amd64(self):
        """Test filename for macOS Intel."""
        filename = get_binary_filename("darwin", "amd64")
        assert filename == "capiscio-darwin-amd64"

    def test_linux_arm64(self):
        """Test filename for Linux ARM64."""
        filename = get_binary_filename("linux", "arm64")
        assert filename == "capiscio-linux-arm64"

    def test_windows_amd64(self):
        """Test filename for Windows (has .exe extension)."""
        filename = get_binary_filename("windows", "amd64")
        assert filename == "capiscio-windows-amd64.exe"


class TestGetCacheDir:
    """Tests for get_cache_dir function."""

    @patch('capiscio.manager.user_cache_dir')
    def test_returns_bin_subdir(self, mock_user_cache_dir):
        """Test that cache dir is in bin subdirectory."""
        mock_user_cache_dir.return_value = "/home/user/.cache/capiscio"
        with patch.object(Path, 'mkdir'):
            cache_dir = get_cache_dir()
            assert str(cache_dir).endswith("bin")

    @patch('capiscio.manager.user_cache_dir')
    def test_creates_directory(self, mock_user_cache_dir):
        """Test that cache directory is created."""
        mock_user_cache_dir.return_value = "/home/user/.cache/capiscio"
        mock_path = MagicMock(spec=Path)
        
        with patch('capiscio.manager.Path', return_value=mock_path) as mock_path_cls:
            mock_path_cls.return_value.__truediv__ = MagicMock(return_value=mock_path)
            mock_path.mkdir = MagicMock()
            
            get_cache_dir()
            mock_path.mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestGetBinaryPath:
    """Tests for get_binary_path function."""

    @patch('capiscio.manager.get_cache_dir')
    @patch('capiscio.manager.get_platform_info', return_value=('darwin', 'arm64'))
    def test_includes_version(self, mock_platform, mock_cache_dir):
        """Test that binary path includes version directory."""
        mock_cache_dir.return_value = Path("/cache/bin")
        path = get_binary_path("1.0.0")
        assert "1.0.0" in str(path)
        assert str(path).endswith("capiscio-darwin-arm64")


class TestDownloadBinary:
    """Tests for download_binary function."""

    @patch('capiscio.manager.get_binary_path')
    def test_returns_existing_binary(self, mock_get_path):
        """Test that existing binary is returned without download."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_get_path.return_value = mock_path
        
        result = download_binary("1.0.0")
        assert result == mock_path

    @patch.dict(os.environ, {"CAPISCIO_SKIP_CHECKSUM": "true"})
    @patch('capiscio.manager._fetch_expected_checksum', return_value=(None, "fetch_failed"))
    @patch('capiscio.manager.get_platform_info', return_value=('linux', 'amd64'))
    @patch('capiscio.manager.get_binary_path')
    @patch('capiscio.manager.requests.get')
    @patch('capiscio.manager.console')
    def test_downloads_binary_on_missing(self, mock_console, mock_requests, mock_get_path, mock_platform, mock_fetch_checksum):
        """Test that binary is downloaded when missing (with checksum skip)."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = False
        mock_path.parent = MagicMock()
        mock_path.name = "capiscio-linux-amd64"
        mock_get_path.return_value = mock_path
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content.return_value = [b'x' * 1024]
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_requests.return_value = mock_response
        
        with patch('builtins.open', mock_open()):
            with patch.object(os, 'stat') as mock_stat:
                with patch.object(os, 'chmod'):
                    mock_stat.return_value = MagicMock(st_mode=0o644)
                    result = download_binary("1.0.0")
        
        assert result == mock_path

    @patch('capiscio.manager.get_platform_info', return_value=('linux', 'amd64'))
    @patch('capiscio.manager.get_binary_path')
    @patch('capiscio.manager.requests.get')
    @patch('capiscio.manager.console')
    def test_cleans_up_on_download_error(self, mock_console, mock_requests, mock_get_path, mock_platform):
        """Test that partial downloads are cleaned up on error."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.side_effect = [False, True]  # First check: not exists, cleanup check: exists
        mock_path.parent = MagicMock()
        mock_get_path.return_value = mock_path
        
        # Mock request error
        import requests.exceptions
        mock_requests.side_effect = requests.exceptions.RequestException("Network error")
        
        with pytest.raises(RuntimeError, match="Failed to download"):
            download_binary("1.0.0")
        
        # Verify cleanup was attempted
        mock_path.unlink.assert_called_once()


class TestFetchExpectedChecksum:
    """Tests for _fetch_expected_checksum function."""

    @patch('capiscio.manager.requests.get')
    def test_returns_checksum_on_match(self, mock_get):
        """Test successful checksum lookup."""
        mock_resp = MagicMock()
        mock_resp.text = "abc123  capiscio-linux-amd64\ndef456  capiscio-darwin-arm64\n"
        mock_resp.raise_for_status = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_get.return_value = mock_resp

        checksum, status = _fetch_expected_checksum("1.0.0", "capiscio-linux-amd64")
        assert checksum == "abc123"
        assert status == "ok"

    @patch('capiscio.manager.requests.get')
    def test_returns_entry_missing_when_not_found(self, mock_get):
        """Test that missing entry returns entry_missing status."""
        mock_resp = MagicMock()
        mock_resp.text = "abc123  capiscio-linux-amd64\n"
        mock_resp.raise_for_status = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_get.return_value = mock_resp

        checksum, status = _fetch_expected_checksum("1.0.0", "capiscio-darwin-arm64")
        assert checksum is None
        assert status == "entry_missing"

    @patch('capiscio.manager.requests.get')
    def test_returns_fetch_failed_on_network_error(self, mock_get):
        """Test that network errors return fetch_failed status."""
        import requests.exceptions
        mock_get.side_effect = requests.exceptions.ConnectionError("timeout")

        checksum, status = _fetch_expected_checksum("1.0.0", "capiscio-linux-amd64")
        assert checksum is None
        assert status == "fetch_failed"


class TestChecksumVerificationIntegration:
    """Tests for checksum verification during download."""

    def _make_download_mocks(self):
        """Helper: set up common mocks for download_binary tests."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = False
        mock_path.parent = MagicMock()
        mock_path.name = "capiscio-linux-amd64"
        return mock_path

    @patch('capiscio.manager._fetch_expected_checksum', return_value=("abc123", "ok"))
    @patch('capiscio.manager._verify_checksum', return_value=True)
    @patch('capiscio.manager.get_platform_info', return_value=('linux', 'amd64'))
    @patch('capiscio.manager.get_binary_path')
    @patch('capiscio.manager.requests.get')
    @patch('capiscio.manager.console')
    def test_checksum_verified_match(self, mock_console, mock_requests, mock_get_path,
                                      mock_platform, mock_verify, mock_fetch):
        """Test that download succeeds when checksum matches."""
        mock_path = self._make_download_mocks()
        mock_get_path.return_value = mock_path

        mock_response = MagicMock()
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content.return_value = [b'x' * 1024]
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_requests.return_value = mock_response

        with patch('builtins.open', mock_open()):
            with patch.object(os, 'stat') as mock_stat:
                with patch.object(os, 'chmod'):
                    mock_stat.return_value = MagicMock(st_mode=0o644)
                    result = download_binary("1.0.0")

        assert result == mock_path
        mock_verify.assert_called_once_with(mock_path, "abc123")

    @patch('capiscio.manager._fetch_expected_checksum', return_value=("abc123", "ok"))
    @patch('capiscio.manager._verify_checksum', return_value=False)
    @patch('capiscio.manager.get_platform_info', return_value=('linux', 'amd64'))
    @patch('capiscio.manager.get_binary_path')
    @patch('capiscio.manager.requests.get')
    @patch('capiscio.manager.console')
    def test_checksum_mismatch_cleans_up(self, mock_console, mock_requests, mock_get_path,
                                          mock_platform, mock_verify, mock_fetch):
        """Test that a checksum mismatch deletes the binary and raises."""
        mock_path = self._make_download_mocks()
        mock_get_path.return_value = mock_path

        mock_response = MagicMock()
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content.return_value = [b'x' * 1024]
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_requests.return_value = mock_response

        with patch('builtins.open', mock_open()):
            with pytest.raises(RuntimeError, match="integrity check failed"):
                download_binary("1.0.0")

        mock_path.unlink.assert_called()

    @patch('capiscio.manager._fetch_expected_checksum', return_value=(None, "fetch_failed"))
    @patch('capiscio.manager.get_platform_info', return_value=('linux', 'amd64'))
    @patch('capiscio.manager.get_binary_path')
    @patch('capiscio.manager.requests.get')
    @patch('capiscio.manager.console')
    def test_fail_closed_on_fetch_failed(self, mock_console, mock_requests,
                                          mock_get_path, mock_platform, mock_fetch):
        """Test fail-closed when checksums.txt fetch fails (default behavior)."""
        mock_path = self._make_download_mocks()
        mock_get_path.return_value = mock_path

        mock_response = MagicMock()
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content.return_value = [b'x' * 1024]
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_requests.return_value = mock_response

        with patch('builtins.open', mock_open()):
            with pytest.raises(RuntimeError, match="could not be fetched"):
                download_binary("1.0.0")

        mock_path.unlink.assert_called()

    @patch('capiscio.manager._fetch_expected_checksum', return_value=(None, "entry_missing"))
    @patch('capiscio.manager.get_platform_info', return_value=('linux', 'amd64'))
    @patch('capiscio.manager.get_binary_path')
    @patch('capiscio.manager.requests.get')
    @patch('capiscio.manager.console')
    def test_fail_closed_on_entry_missing(self, mock_console, mock_requests,
                                           mock_get_path, mock_platform, mock_fetch):
        """Test fail-closed when entry is missing in checksums.txt (default behavior)."""
        mock_path = self._make_download_mocks()
        mock_get_path.return_value = mock_path

        mock_response = MagicMock()
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content.return_value = [b'x' * 1024]
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_requests.return_value = mock_response

        with patch('builtins.open', mock_open()):
            with pytest.raises(RuntimeError, match="no entry for"):
                download_binary("1.0.0")

        mock_path.unlink.assert_called()


class TestRunCore:
    """Tests for run_core function."""

    @patch('capiscio.manager.download_binary')
    @patch('capiscio.manager.platform.system', return_value='Windows')
    @patch('capiscio.manager.subprocess.call', return_value=0)
    def test_runs_subprocess_on_windows(self, mock_call, mock_system, mock_download):
        """Test that subprocess.call is used on Windows."""
        mock_download.return_value = Path("/bin/capiscio.exe")
        
        result = run_core(["validate", "--help"])
        
        mock_call.assert_called_once()
        assert result == 0

    @patch('capiscio.manager.download_binary')
    @patch('capiscio.manager.platform.system', return_value='Linux')
    @patch.object(os, 'execv')
    def test_runs_execv_on_unix(self, mock_execv, mock_system, mock_download):
        """Test that os.execv is used on Unix systems."""
        binary_path = Path("/tmp/capiscio")
        mock_download.return_value = binary_path
        
        run_core(["validate", "--help"])
        
        mock_execv.assert_called_once()
        args = mock_execv.call_args[0]
        # Compare as strings since Path normalization differs by OS
        assert args[0] == str(binary_path)
        assert "validate" in args[1]
        assert "--help" in args[1]

    @patch('capiscio.manager.download_binary')
    @patch('capiscio.manager.console')
    def test_handles_download_error(self, mock_console, mock_download):
        """Test that download errors are handled gracefully."""
        mock_download.side_effect = RuntimeError("Download failed")
        
        result = run_core(["validate"])
        
        assert result == 1
        mock_console.print.assert_called()


class TestConstants:
    """Tests for module constants."""

    def test_core_version_format(self):
        """Test that CORE_VERSION follows semver format."""
        parts = CORE_VERSION.split('.')
        assert len(parts) == 3
        for part in parts:
            assert part.isdigit()

    def test_github_repo_format(self):
        """Test that GITHUB_REPO is in owner/repo format."""
        assert '/' in GITHUB_REPO
        parts = GITHUB_REPO.split('/')
        assert len(parts) == 2
        assert all(part for part in parts)
