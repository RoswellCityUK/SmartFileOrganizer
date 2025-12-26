import runpy
import sys
from unittest.mock import patch

def test_main_module_execution():
    """Verify __main__.py runs the CLI entry point."""
    # We patch sys.argv to avoid actually parsing command line args
    # and patch the main function to verify it gets called
    with patch.object(sys, 'argv', ["smart-organizer", "--help"]), \
         patch("smart_file_organizer.cli.main.main") as mock_main:
        
        # This executes the __name__ == "__main__" block
        runpy.run_module("smart_file_organizer", run_name="__main__")
        
        mock_main.assert_called_once()
