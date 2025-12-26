import unittest
from datetime import datetime
from pathlib import Path
from smart_file_organizer.core.entities import FileNode
from smart_file_organizer.core.rules import ExtensionRule, DateRule


class TestRules(unittest.TestCase):
    def test_extension_rule(self):
        rule = ExtensionRule()
        root = Path("/tmp")

        node = FileNode(path=Path("doc.txt"), size=10, mtime=0)
        dest = rule.get_destination(node, root)
        self.assertEqual(dest, Path("/tmp/TXT"))

        node_none = FileNode(path=Path("README"), size=10, mtime=0)
        dest_none = rule.get_destination(node_none, root)
        self.assertEqual(dest_none, Path("/tmp/Misc"))

    def test_date_rule(self):
        rule = DateRule()
        root = Path("/tmp")

        dt = datetime(2023, 10, 15)
        ts = dt.timestamp()

        node = FileNode(path=Path("photo.jpg"), size=100, mtime=ts)
        dest = rule.get_destination(node, root)
        self.assertEqual(dest, Path("/tmp/2023/10"))


if __name__ == "__main__":
    unittest.main()
