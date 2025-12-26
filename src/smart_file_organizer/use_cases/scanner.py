import logging
from pathlib import Path
from typing import Iterator, List
from ..core.entities import FileNode
from ..infra.interfaces import FileSystemProvider


class DirectoryScanner:
    def __init__(self, fs_provider: FileSystemProvider):
        self.fs = fs_provider
        self.logger = logging.getLogger(__name__)
        self.errors: List[str] = []

    def scan(self, root_path: Path) -> Iterator[FileNode]:
        """
        Recursively scans the directory tree using the injected file system provider.
        Yields FileNode entities for every file found.
        """
        self.logger.info(f"Scanning root: {root_path}")

        resolved_root = root_path.resolve()

        if not self.fs.exists(resolved_root):
            self.logger.error(f"Root path does not exist: {resolved_root}")
            return

        yield from self._recursive_scan(resolved_root)

    def _recursive_scan(self, path: Path) -> Iterator[FileNode]:
        try:
            for entry in self.fs.scandir(path):
                try:
                    if entry.is_dir(follow_symlinks=False):
                        yield from self._recursive_scan(Path(entry.path))

                    elif entry.is_file(follow_symlinks=False):
                        stat = entry.stat()
                        yield FileNode(
                            path=Path(entry.path).resolve(),
                            size=stat.st_size,
                            mtime=stat.st_mtime,
                        )
                except (PermissionError, OSError) as e:
                    self.errors.append(f"Access denied: {entry.path}")
                    self.logger.warning(f"Skipping entry {entry.name}: {e}")

        except (PermissionError, OSError) as e:
            self.errors.append(f"Cannot access directory: {path}")
            self.logger.warning(f"Cannot traverse {path}: {e}")
