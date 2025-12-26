import pytest
import logging
from unittest.mock import Mock, MagicMock
from pathlib import Path
from smart_file_organizer.core.entities import FileNode, ActionRecord, ActionType
from smart_file_organizer.use_cases.organizer import Organizer
from smart_file_organizer.infra.interfaces import FileSystemProvider

class MockFS(FileSystemProvider):
    """A controllable mock for testing specific edge cases."""
    def __init__(self):
        self.existing_files = set()
        self.dirs = {} # path -> list of children
    
    def exists(self, path: Path) -> bool:
        return path in self.existing_files
    
    # Required abstract methods we might not use directly in these tests
    def move(self, src, dest): pass
    def remove(self, path): pass
    def mkdir(self, path): pass
    def scandir(self, path): 
        return self.dirs.get(path, [])
    def rmdir(self, path): pass

def test_collision_resolution_linear_probing():
    """Verify file.txt becomes file_2.txt if file.txt and file_1.txt exist."""
    fs = MockFS()
    organizer = Organizer(fs)
    
    target = Path("/data/doc.txt")
    
    # Setup collision scenario
    fs.existing_files.add(Path("/data/doc.txt"))
    fs.existing_files.add(Path("/data/doc_1.txt"))
    
    # Run resolution
    safe_path = organizer._resolve_collision(target)
    
    assert safe_path == Path("/data/doc_2.txt")

def test_cleanup_empty_dirs_logic():
    """Verify recursive cleanup of empty folders."""
    mock_fs = Mock(spec=FileSystemProvider)
    organizer = Organizer(mock_fs)
    
    root = Path("/root")
    empty_dir = root / "empty_dir"
    kept_dir = root / "kept_dir"
    
    # Setup Mock behavior
    mock_fs.exists.return_value = True
    
    # scandir returns iterators of DirEntry-like objects
    def scandir_side_effect(path):
        if path == root:
            d1 = Mock(); d1.is_dir.return_value = True; d1.path = str(empty_dir)
            d2 = Mock(); d2.is_dir.return_value = True; d2.path = str(kept_dir)
            return iter([d1, d2])
        if path == empty_dir:
            return iter([]) # Empty
        if path == kept_dir:
            f = Mock(); f.is_dir.return_value = False # Contains a file
            return iter([f])
        return iter([])

    mock_fs.scandir.side_effect = scandir_side_effect
    
    # Run
    organizer.cleanup_empty_dirs(root)
    
    # Assert
    mock_fs.rmdir.assert_called_with(empty_dir)
    # Ensure kept_dir was NOT removed
    call_args = [args[0] for args in mock_fs.rmdir.call_args_list]
    assert kept_dir not in call_args

def test_execute_plan_error_handling(caplog):
    """Verify execute_plan handles OS errors gracefully."""
    caplog.set_level(logging.INFO)
    
    mock_fs = Mock(spec=FileSystemProvider)
    organizer = Organizer(mock_fs)
    
    # Make move raise an error
    mock_fs.move.side_effect = PermissionError("Access Denied")
    
    plan = [
        ActionRecord(ActionType.MOVE, Path("src"), Path("dest"), "test")
    ]
    
    organizer.execute_plan(plan)
    
    assert "Failed to move src" in caplog.text
    assert "Execution Complete. Success: 0, Failed: 1" in caplog.text

def test_organizer_skips_same_location():
    """Coverage for organizer.py:26 (continue if src == dest)."""
    mock_fs = Mock(spec=FileSystemProvider)
    organizer = Organizer(mock_fs)
    root = Path("/tmp")
    
    # File is already where the rule wants it to be
    node = FileNode(Path("/tmp/TXT/doc.txt"), 100, 1000)
    
    rule = Mock()
    rule.get_destination.return_value = Path("/tmp/TXT")
    
    # This ensures _resolve_collision returns the original path immediately,
    # allowing the 'if safe_target == node.path' check to pass and trigger 'continue'.
    mock_fs.exists.return_value = False 
    
    plan = organizer.plan_organization([node], rule, root)
    
    # Should be empty because we skipped the move
    assert len(plan) == 0

def test_cleanup_early_return():
    """Coverage for organizer.py:80 (return if path doesn't exist)."""
    mock_fs = Mock(spec=FileSystemProvider)
    organizer = Organizer(mock_fs)
    
    mock_fs.exists.return_value = False
    
    organizer._remove_empty_recursive(Path("/missing"))
    
    # Should simply return without error
    mock_fs.scandir.assert_not_called()

def test_cleanup_exception_handling():
    """Coverage for organizer.py:91-92 (except OSError: pass)."""
    mock_fs = Mock(spec=FileSystemProvider)
    organizer = Organizer(mock_fs)
    
    p = Path("/locked")
    mock_fs.exists.return_value = True
    
    # Simulate a crash when trying to read directory
    mock_fs.scandir.side_effect = OSError("Locked")
    
    organizer._remove_empty_recursive(p)
    
    # Should suppress error and finish
    mock_fs.scandir.assert_called_with(p)