import os
import shutil
from pathlib import Path
from typing import Iterator
from .interfaces import FileSystemProvider


class RealFileSystem(FileSystemProvider):
    def scandir(self, path: Path) -> Iterator[os.DirEntry]:
        return os.scandir(str(path))

    def move(self, src: Path, dest: Path) -> None:
        shutil.move(str(src), str(dest))

    def remove(self, path: Path) -> None:
        os.remove(str(path))

    def exists(self, path: Path) -> bool:
        return path.exists()

    def mkdir(self, path: Path) -> None:
        os.makedirs(str(path), exist_ok=True)
