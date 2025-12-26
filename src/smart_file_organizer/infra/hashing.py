import hashlib
from pathlib import Path


class HashService:
    """Service to calculate file checksums safely and efficiently."""

    BLOCK_SIZE = 65536  # 64KB chunks

    def get_hash(self, path: Path) -> str:
        """
        Calculates SHA-256 hash of a file using buffered reading.
        Returns the hex digest string.
        """
        hasher = hashlib.sha256()

        try:
            with open(path, "rb") as f:
                while True:
                    data = f.read(self.BLOCK_SIZE)
                    if not data:
                        break
                    hasher.update(data)
            return hasher.hexdigest()
        except OSError:
            # If file becomes inaccessible during read, return empty or handle upstream
            # For now, we return a distinct marker or re-raise.
            # Re-raising is safer so the scanner knows it failed.
            raise
