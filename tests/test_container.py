from smart_file_organizer.container import ServiceContainer
from smart_file_organizer.infra.fs_real import RealFileSystem
from smart_file_organizer.infra.fs_dryrun import DryRunFileSystem
from smart_file_organizer.infra.hashing import HashService


def test_container_dependency_injection():
    # Test Dry Run (Default)
    c1 = ServiceContainer(dry_run=True)
    assert isinstance(c1.fs, DryRunFileSystem)

    # Test Real Execution
    c2 = ServiceContainer(dry_run=False)
    assert isinstance(c2.fs, RealFileSystem)

    # Test Singleton-like access properties
    assert c1.fs is c1.fs  # Should return same instance

    # Test Hasher initialization
    assert isinstance(c1.hasher, HashService)
    assert c1.hasher is c1.hasher
