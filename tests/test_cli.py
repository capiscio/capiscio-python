"""Tests for capiscio.cli module."""
import sys
from unittest.mock import patch, MagicMock
import pytest
from capiscio.cli import main


class TestMainCLI:
    """Tests for the main CLI entry point."""

    def test_cli_pass_through(self):
        """
        Verify that arguments passed to the CLI are forwarded 
        exactly as-is to the run_core function.
        """
        test_args = ["capiscio", "validate", "https://example.com", "--verbose"]
        
        # Mock sys.argv
        with patch.object(sys, 'argv', test_args):
            # Mock run_core to avoid actual execution/download
            with patch('capiscio.cli.run_core') as mock_run_core:
                # Mock sys.exit to prevent test from exiting
                with patch.object(sys, 'exit') as mock_exit:
                    main()
                    
                    # Check that run_core was called with the correct arguments
                    # sys.argv[1:] slices off the script name ("capiscio")
                    expected_args = ["validate", "https://example.com", "--verbose"]
                    mock_run_core.assert_called_once_with(expected_args)

    def test_cli_empty_args(self):
        """Test CLI with no arguments passes empty list to run_core."""
        test_args = ["capiscio"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('capiscio.cli.run_core') as mock_run_core:
                with patch.object(sys, 'exit'):
                    main()
                    mock_run_core.assert_called_once_with([])


class TestWrapperCommands:
    """Tests for wrapper-specific commands."""

    def test_wrapper_version_flag(self):
        """Verify that --wrapper-version is intercepted and not passed to core."""
        test_args = ["capiscio", "--wrapper-version"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('capiscio.cli.run_core') as mock_run_core:
                with patch.object(sys, 'exit') as mock_exit:
                    # We need to mock importlib.metadata.version since package might not be installed
                    with patch('importlib.metadata.version', return_value="1.2.3"):
                        main()
                        
                        # Should NOT call run_core
                        mock_run_core.assert_not_called()
                        # Should exit with 0
                        mock_exit.assert_called_with(0)

    def test_wrapper_version_unknown(self):
        """Test --wrapper-version when version cannot be determined."""
        test_args = ["capiscio", "--wrapper-version"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('capiscio.cli.run_core') as mock_run_core:
                with patch.object(sys, 'exit') as mock_exit:
                    with patch('importlib.metadata.version', side_effect=Exception("Not found")):
                        with patch('capiscio.cli.console') as mock_console:
                            main()
                            
                            mock_run_core.assert_not_called()
                            # Should still print something about version
                            mock_console.print.assert_called()
                            mock_exit.assert_called_with(0)

    def test_wrapper_clean_flag(self):
        """Verify that --wrapper-clean is intercepted."""
        test_args = ["capiscio", "--wrapper-clean"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('capiscio.cli.run_core') as mock_run_core:
                with patch.object(sys, 'exit') as mock_exit:
                    with patch('shutil.rmtree') as mock_rmtree:
                        with patch('capiscio.cli.get_cache_dir') as mock_get_dir:
                            mock_dir = MagicMock()
                            mock_dir.exists.return_value = True
                            mock_get_dir.return_value = mock_dir
                            
                            main()
                            
                            mock_rmtree.assert_called_once()
                            mock_run_core.assert_not_called()
                            mock_exit.assert_called_with(0)

    def test_wrapper_clean_nonexistent_dir(self):
        """Test --wrapper-clean when cache directory doesn't exist."""
        test_args = ["capiscio", "--wrapper-clean"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('capiscio.cli.run_core') as mock_run_core:
                with patch.object(sys, 'exit') as mock_exit:
                    with patch('shutil.rmtree') as mock_rmtree:
                        with patch('capiscio.cli.get_cache_dir') as mock_get_dir:
                            with patch('capiscio.cli.console') as mock_console:
                                mock_dir = MagicMock()
                                mock_dir.exists.return_value = False
                                mock_get_dir.return_value = mock_dir
                                
                                main()
                                
                                mock_rmtree.assert_not_called()
                                mock_run_core.assert_not_called()
                                mock_exit.assert_called_with(0)

    def test_wrapper_clean_error(self):
        """Test --wrapper-clean when cleanup fails."""
        test_args = ["capiscio", "--wrapper-clean"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('capiscio.cli.run_core') as mock_run_core:
                with patch.object(sys, 'exit') as mock_exit:
                    with patch('shutil.rmtree', side_effect=PermissionError("Access denied")):
                        with patch('capiscio.cli.get_cache_dir') as mock_get_dir:
                            with patch('capiscio.cli.console') as mock_console:
                                mock_dir = MagicMock()
                                mock_dir.exists.return_value = True
                                mock_get_dir.return_value = mock_dir
                                
                                main()
                                
                                mock_run_core.assert_not_called()
                                # Should exit with 1 on error
                                mock_exit.assert_called_with(1)

    def test_unknown_wrapper_command_returns(self):
        """Test that unknown --wrapper-* commands don't crash."""
        test_args = ["capiscio", "--wrapper-unknown"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('capiscio.cli.run_core') as mock_run_core:
                with patch.object(sys, 'exit'):
                    # Should return early, not call run_core
                    main()
                    mock_run_core.assert_not_called()


class TestCommandDelegation:
    """Tests for command delegation to core binary."""

    def test_validate_command(self):
        """Test that validate command is passed to core."""
        test_args = ["capiscio", "validate", "agent-card.json"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('capiscio.cli.run_core') as mock_run_core:
                with patch.object(sys, 'exit'):
                    main()
                    mock_run_core.assert_called_once_with(["validate", "agent-card.json"])

    def test_score_command(self):
        """Test that score command is passed to core."""
        test_args = ["capiscio", "score", "https://example.com/agent"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('capiscio.cli.run_core') as mock_run_core:
                with patch.object(sys, 'exit'):
                    main()
                    mock_run_core.assert_called_once_with(["score", "https://example.com/agent"])

    def test_help_command(self):
        """Test that help is passed to core."""
        test_args = ["capiscio", "--help"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('capiscio.cli.run_core') as mock_run_core:
                with patch.object(sys, 'exit'):
                    main()
                    mock_run_core.assert_called_once_with(["--help"])

    def test_version_command(self):
        """Test that --version (without wrapper prefix) is passed to core."""
        test_args = ["capiscio", "--version"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('capiscio.cli.run_core') as mock_run_core:
                with patch.object(sys, 'exit'):
                    main()
                    mock_run_core.assert_called_once_with(["--version"])

    def test_complex_args(self):
        """Test complex argument combinations are passed correctly."""
        test_args = [
            "capiscio", "validate", 
            "--url", "https://example.com",
            "--output", "json",
            "--verbose",
            "--strict"
        ]
        
        with patch.object(sys, 'argv', test_args):
            with patch('capiscio.cli.run_core') as mock_run_core:
                with patch.object(sys, 'exit'):
                    main()
                    expected = [
                        "validate",
                        "--url", "https://example.com",
                        "--output", "json",
                        "--verbose",
                        "--strict"
                    ]
                    mock_run_core.assert_called_once_with(expected)


class TestExitCodes:
    """Tests for exit code handling."""

    def test_run_core_exit_code_propagated(self):
        """Test that run_core exit code is propagated."""
        test_args = ["capiscio", "validate", "nonexistent.json"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('capiscio.cli.run_core', return_value=1) as mock_run_core:
                with patch.object(sys, 'exit') as mock_exit:
                    main()
                    mock_exit.assert_called_with(1)

    def test_run_core_success_exit_code(self):
        """Test that successful run_core exit code is propagated."""
        test_args = ["capiscio", "validate", "valid.json"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('capiscio.cli.run_core', return_value=0):
                with patch.object(sys, 'exit') as mock_exit:
                    main()
                    mock_exit.assert_called_with(0)

