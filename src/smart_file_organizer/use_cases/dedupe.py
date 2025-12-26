from typing import List, Dict, Iterator
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from ..core.entities import FileNode
from ..infra.hashing import HashService


def _hash_file_helper(path: Path) -> tuple[Path, str]:
    service = HashService()
    try:
        return path, service.get_hash(path)
    except OSError:
        return path, None


class DuplicateFinder:
    def __init__(self, hash_service: HashService):
        self.hasher = hash_service

    def find_duplicates(self, files: Iterator[FileNode]) -> Dict[str, List[FileNode]]:
        """
        Identifies duplicates using parallel processing for the hashing stage.
        """
        # Stage 1: Size Filtering (O(1))
        size_groups: Dict[int, List[FileNode]] = defaultdict(list)
        for node in files:
            size_groups[node.size].append(node)

        # Prepare candidates for hashing
        candidates: List[FileNode] = []
        for size, nodes in size_groups.items():
            if size > 0 and len(nodes) > 1:
                candidates.extend(nodes)

        duplicates: Dict[str, List[FileNode]] = defaultdict(list)

        # Stage 2: Parallel Hashing
        # Map paths to nodes for easy lookup after hashing
        path_map = {node.path: node for node in candidates}
        paths_to_hash = [node.path for node in candidates]

        if not paths_to_hash:
            return {}

        print(
            f"Hashing {len(paths_to_hash)} candidate files using parallel processing..."
        )

        with ProcessPoolExecutor() as executor:
            results = executor.map(_hash_file_helper, paths_to_hash)

            for path, file_hash in results:
                if file_hash:
                    node = path_map[path]
                    duplicates[file_hash].append(node)

        # Final Filter
        return {k: v for k, v in duplicates.items() if len(v) > 1}
