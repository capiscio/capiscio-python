import sys
from unittest.mock import patch, MagicMock
import pytest
from capiscio.cli import main

def test_cli_pass_through():
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

def test_wrapper_version_flag():
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

def test_wrapper_clean_flag():
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
