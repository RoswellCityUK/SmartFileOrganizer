import logging
from typing import List, Iterable, Iterator
from pathlib import Path
from ..core.entities import FileNode, ActionRecord, ActionType
from ..core.rules import OrganizationRule
from ..infra.interfaces import FileSystemProvider


class Organizer:
    def __init__(self, fs_provider: FileSystemProvider):
        self.fs = fs_provider
        self.logger = logging.getLogger(__name__)

    def plan_organization(
        self, files: Iterable[FileNode], rule: OrganizationRule, root: Path
    ) -> List[ActionRecord]:
        """Generates a list of safe move operations based on the rule."""
        plan = []
        for node in files:
            target_dir = rule.get_destination(node, root)
            target_path = target_dir / node.path.name

            safe_target = self._resolve_collision(target_path)

            if safe_target.resolve() == node.path.resolve():
                continue

            plan.append(
                ActionRecord(
                    action_type=ActionType.MOVE,
                    src_path=node.path,
                    dest_path=safe_target,
                    reason=f"Organized by {rule.__class__.__name__}",
                )
            )
        return plan

    def execute_plan(self, plan: List[ActionRecord]) -> None:
        """Executes the action plan using the FileSystemProvider."""
        success_count = 0
        fail_count = 0
        total_actions = len(plan)

        print(f"Executing {total_actions} operations...")

        for index, action in enumerate(plan, 1):
            try:
                print(
                    f"\rProcessing {index}/{total_actions}: {action.src_path.name[:30]}...",
                    end="",
                    flush=True,
                )

                if action.action_type == ActionType.MOVE:
                    if action.dest_path:
                        self.fs.mkdir(action.dest_path.parent)
                        self.fs.move(action.src_path, action.dest_path)
                        success_count += 1

            except (OSError, PermissionError) as e:
                fail_count += 1
                self.logger.error(f"Failed to move {action.src_path}: {e}")

        # Clear progress line
        print("\r" + " " * 60 + "\r", end="")

        self.logger.info(
            f"Execution Complete. Success: {success_count}, Failed: {fail_count}"
        )
        print(f"Execution Summary:")
        print(f"  - Successful Moves: {success_count}")
        print(f"  - Failed Operations: {fail_count}")

    def cleanup_empty_dirs(self, root: Path) -> None:
        """Recursively removes empty directories (Bottom-Up)."""
        self._remove_empty_recursive(root)

    def _remove_empty_recursive(self, path: Path) -> None:
        if not self.fs.exists(path):
            return

        try:
            entries = list(self.fs.scandir(path))
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    self._remove_empty_recursive(Path(entry.path))

            if not any(self.fs.scandir(path)):
                self.logger.info(f"Removing empty directory: {path}")
                self.fs.rmdir(path)
        except (OSError, PermissionError):
            pass  # Skip locked folders

    def _resolve_collision(self, target: Path) -> Path:
        """
        Linear probing: if file.txt exists, try file_1.txt, file_2.txt...
        Uses the FileSystemProvider to check existence (works in Dry Run!).
        """
        if not self.fs.exists(target):
            return target

        stem = target.stem
        suffix = target.suffix
        parent = target.parent
        counter = 1

        while True:
            new_name = f"{stem}_{counter}{suffix}"
            candidate = parent / new_name
            if not self.fs.exists(candidate):
                return candidate
            counter += 1
