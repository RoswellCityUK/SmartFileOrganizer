from datetime import datetime
from pathlib import Path
from smart_file_organizer.core.entities import FileNode
from smart_file_organizer.core.rules import ExtensionRule, DateRule


def test_extension_rule():
    rule = ExtensionRule()
    root = Path("/tmp")

    # Test .txt
    node = FileNode(path=Path("doc.txt"), size=10, mtime=0)
    dest = rule.get_destination(node, root)
    assert dest == Path("/tmp/TXT")

    # Test no extension
    node_none = FileNode(path=Path("README"), size=10, mtime=0)
    dest_none = rule.get_destination(node_none, root)
    assert dest_none == Path("/tmp/Misc")


def test_date_rule():
    rule = DateRule()
    root = Path("/tmp")

    # Create a timestamp for 2023-10-15
    dt = datetime(2023, 10, 15)
    ts = dt.timestamp()

    node = FileNode(path=Path("photo.jpg"), size=100, mtime=ts)
    dest = rule.get_destination(node, root)
    assert dest == Path("/tmp/2023/10")
