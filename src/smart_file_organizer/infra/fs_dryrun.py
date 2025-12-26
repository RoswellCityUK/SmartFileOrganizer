import logging
from pathlib import Path
from typing import Iterator, Dict
from .interfaces import FileSystemProvider
from .fs_real import RealFileSystem


class DryRunFileSystem(FileSystemProvider):
    def __init__(self):
        self._real_fs = RealFileSystem()
        self.logger = logging.getLogger("DryRun")
        self.virtual_state: Dict[Path, Path] = {}

    def scandir(self, path: Path) -> Iterator:
        return self._real_fs.scandir(path)

    def move(self, src: Path, dest: Path) -> None:
        self.logger.info(f"[DRY RUN] MOVE: '{src}' -> '{dest}'")
        self.virtual_state[dest] = src

    def remove(self, path: Path) -> None:
        self.logger.info(f"[DRY RUN] DELETE: '{path}'")

    def exists(self, path: Path) -> bool:
        if path in self.virtual_state:
            return True
        return self._real_fs.exists(path)

    def mkdir(self, path: Path) -> None:
        self.logger.info(f"[DRY RUN] MKDIR: '{path}'")

    def rmdir(self, path: Path) -> None:
        self.logger.info(f"[DRY RUN] RMDIR: '{path}'")
