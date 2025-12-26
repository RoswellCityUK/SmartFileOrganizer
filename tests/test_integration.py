from pathlib import Path
from smart_file_organizer.container import ServiceContainer
from smart_file_organizer.core.entities import FileNode
from smart_file_organizer.core.rules import ExtensionRule
from smart_file_organizer.use_cases.organizer import Organizer


def test_dry_run_organization():
    # 1. Setup Container in Dry Run mode
    container = ServiceContainer(dry_run=True)
    fs = container.fs

    # 2. Fake some input files
    root = Path("/test_root")
    files = [
        FileNode(path=root / "image.png", size=1024, mtime=1000),
        FileNode(path=root / "doc.pdf", size=2048, mtime=1000),
    ]

    # 3. Plan and Execute
    organizer = Organizer(fs)
    rule = ExtensionRule()
    plan = organizer.plan_organization(files, rule, root)

    organizer.execute_plan(plan)

    # 4. Verify Virtual State
    # Expectation: /test_root/image.png -> /test_root/PNG/image.png
    expected_dest_png = root / "PNG" / "image.png"
    assert expected_dest_png in fs.virtual_state
    assert fs.virtual_state[expected_dest_png] == root / "image.png"

    # Expectation: /test_root/doc.pdf -> /test_root/PDF/doc.pdf
    expected_dest_pdf = root / "PDF" / "doc.pdf"
    assert expected_dest_pdf in fs.virtual_state
