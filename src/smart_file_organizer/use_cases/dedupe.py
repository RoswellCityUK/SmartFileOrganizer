from typing import List, Dict, Iterator
from collections import defaultdict
from pathlib import Path
from ..core.entities import FileNode
from ..infra.hashing import HashService

class DuplicateFinder:
    def __init__(self, hash_service: HashService):
        self.hasher = hash_service

    def find_duplicates(self, files: Iterator[FileNode]) -> Dict[str, List[FileNode]]:
        """
        Identifies duplicates in two stages:
        1. Size Filtering (Fast)
        2. Cryptographic Hashing (Accurate)
        
        Returns: Dict mapping {hash_string: [list_of_duplicate_files]}
        """
        size_groups: Dict[int, List[FileNode]] = defaultdict(list)
        for node in files:
            size_groups[node.size].append(node)

        duplicates: Dict[str, List[FileNode]] = defaultdict(list)
        
        for size, nodes in size_groups.items():
            if size == 0 or len(nodes) < 2:
                continue

            for node in nodes:
                try:
                    file_hash = self.hasher.get_hash(node.path)
                    duplicates[file_hash].append(node)
                except OSError:
                    continue

        # Final Filter: Only return hash groups with > 1 entry
        return {k: v for k, v in duplicates.items() if len(v) > 1}