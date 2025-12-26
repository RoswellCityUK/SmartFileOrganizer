import pytest
from pathlib import Path
from smart_file_organizer.infra.fs_real import RealFileSystem
from smart_file_organizer.infra.fs_dryrun import DryRunFileSystem
from smart_file_organizer.infra.hashing import HashService


def test_real_fs_operations(tmp_path):
    """Verify RealFileSystem actually modifies the disk."""
    fs = RealFileSystem()

    # Setup
    src = tmp_path / "source.txt"
    dest = tmp_path / "dest.txt"
    subdir = tmp_path / "subdir"

    src.write_text("content")

    # Test exist/mkdir
    assert fs.exists(src)
    fs.mkdir(subdir)
    assert subdir.exists()

    # Test scandir
    entries = list(fs.scandir(tmp_path))
    assert len(entries) >= 2

    # Test move
    fs.move(src, dest)
    assert not src.exists()
    assert dest.exists()

    # Test remove
    fs.remove(dest)
    assert not dest.exists()

    # Test rmdir
    fs.rmdir(subdir)
    assert not subdir.exists()


def test_dryrun_fs_logging(caplog):
    """Verify DryRunFileSystem logs actions but doesn't perform them."""
    fs = DryRunFileSystem()
    path = Path("/fake/path")

    with caplog.at_level("INFO"):
        fs.remove(path)
        fs.rmdir(path)
        fs.mkdir(path)
        fs.move(path, Path("/fake/dest"))

    assert "DELETE: '/fake/path'" in caplog.text
    assert "RMDIR: '/fake/path'" in caplog.text
    assert "MKDIR: '/fake/path'" in caplog.text
    assert "MOVE: '/fake/path'" in caplog.text


def test_hashing_service(tmp_path):
    """Verify SHA256 hashing works on real files."""
    service = HashService()
    f = tmp_path / "test_hash.txt"
    content = b"Hello World"
    f.write_bytes(content)

    # Known SHA256 for "Hello World"
    expected = "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
    assert service.get_hash(f) == expected


def test_hashing_missing_file():
    """Verify error handling for missing files."""
    service = HashService()
    with pytest.raises(OSError):
        service.get_hash(Path("/non/existent/file"))


def test_dryrun_delegation(tmp_path):
    """Verify DryRunFileSystem delegates read-only ops to RealFileSystem."""
    fs = DryRunFileSystem()
    f = tmp_path / "test.txt"
    f.touch()

    # Coverage for fs_dryrun.py:26 (exists)
    assert fs.exists(f) is True
    assert fs.exists(tmp_path / "missing") is False

    # Coverage for fs_dryrun.py:15 (scandir)
    entries = list(fs.scandir(tmp_path))
    assert len(entries) == 1
    assert entries[0].name == "test.txt"


def test_dryrun_virtual_state_exists():
    """Verify exists() returns True for files moved in virtual state."""
    from smart_file_organizer.infra.fs_dryrun import DryRunFileSystem

    fs = DryRunFileSystem()
    src = Path("/source/file.txt")
    dest = Path("/dest/file.txt")

    # Perform a virtual move
    fs.move(src, dest)

    # Check if dest exists in virtual state
    assert fs.exists(dest) is True
