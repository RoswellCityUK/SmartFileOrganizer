from abc import ABC, abstractmethod
from typing import Iterator, Any
from pathlib import Path


class FileSystemProvider(ABC):
    """Abstract interface for file system operations."""

    @abstractmethod
    def scandir(self, path: Path) -> Iterator[Any]:
        """Return an iterator of directory entries."""
        pass

    @abstractmethod
    def move(self, src: Path, dest: Path) -> None:
        """Move a file from src to dest."""
        pass

    @abstractmethod
    def remove(self, path: Path) -> None:
        """Permanently delete a file."""
        pass

    @abstractmethod
    def exists(self, path: Path) -> bool:
        """Check if a path exists."""
        pass

    @abstractmethod
    def mkdir(self, path: Path) -> None:
        """Create directory recursively."""
        pass
