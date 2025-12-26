from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from .entities import FileNode

class OrganizationRule(ABC):
    """Strategy interface for determining file destinations."""
    
    @abstractmethod
    def get_destination(self, node: FileNode, root: Path) -> Path:
        """Returns the target folder for a given file."""
        pass

class ExtensionRule(OrganizationRule):
    """Sorts files into folders by extension (e.g., /Images/jpg/)."""
    def get_destination(self, node: FileNode, root: Path) -> Path:
        ext = node.path.suffix.lower().lstrip('.')
        if not ext:
            return root / "Misc"
        return root / ext.upper()

class DateRule(OrganizationRule):
    """Sorts files by Year/Month (e.g., /2023/10/)."""
    def get_destination(self, node: FileNode, root: Path) -> Path:
        dt = datetime.fromtimestamp(node.mtime)
        year = str(dt.year)
        month = f"{dt.month:02d}"
        return root / year / month