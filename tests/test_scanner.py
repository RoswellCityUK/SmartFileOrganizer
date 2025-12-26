from pathlib import Path
from unittest.mock import Mock, patch
from smart_file_organizer.use_cases.scanner import DirectoryScanner
from smart_file_organizer.infra.interfaces import FileSystemProvider


def test_recursive_scan(tmp_path):
    """Verify scanner finds files in nested directories."""
    # Setup: Create /root/file1.txt and /root/subdir/file2.jpg
    d1 = tmp_path / "subdir"
    d1.mkdir()
    f1 = tmp_path / "file1.txt"
    f1.write_text("content")
    f2 = d1 / "file2.jpg"
    f2.write_text("image")

    # Use RealFileSystem for this test (via the interface)
    from smart_file_organizer.infra.fs_real import RealFileSystem

    fs = RealFileSystem()
    scanner = DirectoryScanner(fs)

    results = list(scanner.scan(tmp_path))

    # Should find 2 files
    assert len(results) == 2
    filenames = {node.path.name for node in results}
    assert "file1.txt" in filenames
    assert "file2.jpg" in filenames


def test_scanner_permission_error(caplog):
    """Verify scanner logs warning on PermissionError and continues."""
    mock_fs = Mock(spec=FileSystemProvider)
    scanner = DirectoryScanner(mock_fs)
    root = Path("/root")

    mock_fs.exists.return_value = True
    mock_fs.scandir.side_effect = PermissionError("Access Denied")

    results = list(scanner.scan(root))

    assert len(results) == 0
    assert len(scanner.errors) > 0
    assert "Cannot access directory" in scanner.errors[0]


def test_scanner_root_not_found(caplog):
    mock_fs = Mock(spec=FileSystemProvider)
    scanner = DirectoryScanner(mock_fs)
    mock_fs.exists.return_value = False

    list(scanner.scan(Path("/missing")))
    assert "Root path does not exist" in caplog.text


def test_scanner_inner_entry_error():
    """
    Coverage for scanner.py: Inner try/except block.
    Simulates iteration working, but checking a specific entry failing.
    """
    mock_fs = Mock(spec=FileSystemProvider)
    scanner = DirectoryScanner(mock_fs)
    root = Path("/root")
    mock_fs.exists.return_value = True

    # Create a bad entry that raises PermissionError when inspected
    bad_entry = Mock()
    bad_entry.path = "/root/locked_file"
    bad_entry.name = "locked_file"
    # Calling is_dir() raises the error
    bad_entry.is_dir.side_effect = PermissionError("Locked")

    mock_fs.scandir.return_value = iter([bad_entry])

    results = list(scanner.scan(root))

    # Should have 0 results but 1 recorded error
    assert len(results) == 0
    assert len(scanner.errors) == 1
    assert "Access denied" in scanner.errors[0]
