from pathlib import Path
import sys
from unittest.mock import patch
from smart_file_organizer.cli.main import main
from smart_file_organizer.core.entities import FileNode


def test_cli_scan(capsys):
    """Test 'scan' command."""
    with patch.object(sys, "argv", ["smart-organizer", "scan", "--root", "."]):
        # Mock scanner to return nothing to avoid FS access
        with patch("smart_file_organizer.cli.main.DirectoryScanner") as MockScanner:
            mock_instance = MockScanner.return_value
            mock_instance.scan.return_value = []  # Empty iterator
            mock_instance.errors = []

            main()

    captured = capsys.readouterr()
    assert "Smart File Organizer" in captured.out
    assert "Scan Complete" in captured.out


def test_cli_dedupe(capsys):
    """Test 'dedupe' command."""
    with patch.object(sys, "argv", ["smart-organizer", "dedupe", "--root", "."]):
        with patch(
            "smart_file_organizer.cli.main.DirectoryScanner"
        ) as MockScanner, patch(
            "smart_file_organizer.cli.main.DuplicateFinder"
        ) as MockDedupe:
            # Setup Scanner
            MockScanner.return_value.scan.return_value = []

            # Setup Dedupe
            MockDedupe.return_value.find_duplicates.return_value = {}

            main()

    captured = capsys.readouterr()
    assert "Duplicate Detector" in captured.out
    assert "No duplicates found" in captured.out


def test_cli_organize_dry_run(capsys):
    """Test 'organize' command in dry run (default)."""
    with patch.object(
        sys, "argv", ["smart-organizer", "organize", "--root", ".", "--by-ext"]
    ):
        with patch(
            "smart_file_organizer.cli.main.DirectoryScanner"
        ) as MockScanner, patch("smart_file_organizer.cli.main.Organizer") as MockOrg:
            MockScanner.return_value.scan.return_value = []
            MockOrg.return_value.plan_organization.return_value = []

            main()

    captured = capsys.readouterr()
    assert "Mode: DRY RUN" in captured.out
    assert "Strategy: Sort by Extension" in captured.out


def test_cli_organize_execute_abort(capsys):
    """Test 'organize --execute' aborts if user says No."""
    args = ["smart-organizer", "--execute", "organize", "--root", "."]

    with patch.object(sys, "argv", args):
        with patch(
            "smart_file_organizer.cli.main.DirectoryScanner"
        ) as MockScanner, patch(
            "smart_file_organizer.cli.main.Organizer"
        ) as MockOrg, patch(
            "builtins.input", return_value="n"
        ):
            MockScanner.return_value.scan.return_value = []
            MockOrg.return_value.plan_organization.return_value = ["Action"]

            main()

    captured = capsys.readouterr()
    assert "Operation aborted" in captured.out
    MockOrg.return_value.execute_plan.assert_not_called()


def test_cli_verbose_and_errors(capsys):
    """
    Coverage for cli/main.py: verbose branches and error reporting.
    """
    with patch.object(
        sys, "argv", ["smart-organizer", "--verbose", "scan", "--root", "."]
    ):
        with patch("smart_file_organizer.cli.main.DirectoryScanner") as MockScanner:
            instance = MockScanner.return_value
            # Return one fake file
            node = FileNode(Path("test.txt"), 1024, 0)
            instance.scan.return_value = iter([node])
            instance.errors = []  # No errors yet

            main()

    out = capsys.readouterr().out
    assert "[FOUND] test.txt" in out  # Verbose output

    # 2. Run with errors present (to hit the "encountered errors" print block)
    with patch.object(sys, "argv", ["smart-organizer", "scan", "--root", "."]):
        with patch("smart_file_organizer.cli.main.DirectoryScanner") as MockScanner:
            instance = MockScanner.return_value
            instance.scan.return_value = iter([])
            # Inject fake errors
            instance.errors = ["Some error occurred"]

            main()

    out = capsys.readouterr().out
    assert "[WARNING] Encountered 1 permission errors" in out
