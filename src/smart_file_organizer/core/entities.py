from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class FileNode:
    """Represents a file in the system with cached metadata."""
    path: Path
    size: int
    mtime: float
    hash: Optional[str] = None


class ActionType(Enum):
    MOVE = auto()
    DELETE = auto()
    COPY = auto()


@dataclass(frozen=True)
class ActionRecord:
    """Immutable record of a planned operation."""
    action_type: ActionType
    src_path: Path
    dest_path: Optional[Path]
    reason: str
