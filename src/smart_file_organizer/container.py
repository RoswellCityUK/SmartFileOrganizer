from .infra.interfaces import FileSystemProvider
from .infra.fs_real import RealFileSystem
from .infra.fs_dryrun import DryRunFileSystem


class ServiceContainer:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self._fs_provider = None

    @property
    def fs(self) -> FileSystemProvider:
        if self._fs_provider is None:
            if self.dry_run:
                self._fs_provider = DryRunFileSystem()
            else:
                self._fs_provider = RealFileSystem()
        return self._fs_provider
