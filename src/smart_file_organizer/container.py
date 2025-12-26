from typing import Optional
from .infra.interfaces import FileSystemProvider
from .infra.fs_real import RealFileSystem
from .infra.fs_dryrun import DryRunFileSystem
from .infra.hashing import HashService


class ServiceContainer:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self._fs_provider: Optional[FileSystemProvider] = None
        self._hash_service: Optional[HashService] = None

    @property
    def fs(self) -> FileSystemProvider:
        if self._fs_provider is None:
            if self.dry_run:
                self._fs_provider = DryRunFileSystem()
            else:
                self._fs_provider = RealFileSystem()
        assert self._fs_provider is not None
        return self._fs_provider

    @property
    def hasher(self) -> HashService:
        if self._hash_service is None:
            self._hash_service = HashService()
        assert self._hash_service is not None
        return self._hash_service
