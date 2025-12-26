from pathlib import Path
from unittest.mock import Mock, patch
from smart_file_organizer.core.entities import FileNode
from smart_file_organizer.use_cases.dedupe import DuplicateFinder, _hash_file_helper
from smart_file_organizer.infra.hashing import HashService

def test_dedupe_filtering():
    """Verify logic: Unique sizes skipped, Same sizes hashed, Collisions returned."""
    mock_hasher = Mock(spec=HashService)
    finder = DuplicateFinder(mock_hasher)
    
    files = [
        FileNode(Path("A"), 10, 0),
        FileNode(Path("B"), 20, 0),
        FileNode(Path("C"), 20, 0),
        FileNode(Path("D"), 20, 0)
    ]
    
    # We mock the ProcessPoolExecutor to run SYNCHRONOUSLY in the main thread.
    # This avoids pickling issues and speeds up tests.
    with patch("smart_file_organizer.use_cases.dedupe.ProcessPoolExecutor") as MockExecutor:
        # The executor is a context manager
        mock_instance = MockExecutor.return_value.__enter__.return_value
        
        # When .map() is called, we just run the function immediately using standard map()
        mock_instance.map.side_effect = map

        # Now we mock the helper function so we control the hashes
        with patch("smart_file_organizer.use_cases.dedupe._hash_file_helper") as mock_helper:
            def side_effect(path):
                if path.name == "B": return (path, "hash_X")
                if path.name == "C": return (path, "hash_X")
                if path.name == "D": return (path, "hash_Y")
                return (path, "unknown")
            mock_helper.side_effect = side_effect

            duplicates = finder.find_duplicates(files)
        
    assert len(duplicates) == 1
    assert "hash_X" in duplicates
    assert len(duplicates["hash_X"]) == 2

def test_hash_helper_coverage():
    """Unit test for the top-level helper function to ensure coverage."""
    # We mock HashService inside the use_cases.dedupe module scope or sys.modules
    with patch("smart_file_organizer.use_cases.dedupe.HashService") as MockService:
        MockService.return_value.get_hash.return_value = "12345"
        
        path = Path("test.txt")
        result_path, result_hash = _hash_file_helper(path)
        
        assert result_path == path
        assert result_hash == "12345"

def test_hash_helper_error_handling():
    """Verify helper returns None on error."""
    with patch("smart_file_organizer.use_cases.dedupe.HashService") as MockService:
        MockService.return_value.get_hash.side_effect = OSError("Read fail")
        
        path = Path("test.txt")
        result_path, result_hash = _hash_file_helper(path)
        
        assert result_path == path
        assert result_hash is None

def test_dedupe_early_return():
    """
    Coverage for dedupe.py: early return when no candidates exist.
    """
    mock_hasher = Mock()
    finder = DuplicateFinder(mock_hasher)
    
    # Case 1: Empty input
    assert finder.find_duplicates([]) == {}
    
    # Case 2: Files exist but all have unique sizes (Stage 1 filters them all)
    files = [
        FileNode(Path("a"), 10, 0),
        FileNode(Path("b"), 20, 0)
    ]
    # Should return empty without even trying to hash (mock_hasher not called)
    assert finder.find_duplicates(files) == {}
    mock_hasher.get_hash.assert_not_called()