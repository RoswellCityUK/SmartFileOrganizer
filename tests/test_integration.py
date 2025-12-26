import unittest
from pathlib import Path
from smart_file_organizer.container import ServiceContainer
from smart_file_organizer.core.entities import FileNode
from smart_file_organizer.core.rules import ExtensionRule
from smart_file_organizer.use_cases.organizer import Organizer

class TestIntegration(unittest.TestCase):
    def test_dry_run_organization(self):
        # 1. Setup Container in Dry Run mode
        container = ServiceContainer(dry_run=True)
        fs = container.fs
        
        # 2. Fake some input files (We skip the scanner and create entities directly)
        root = Path("/test_root")
        files = [
            FileNode(path=root / "image.png", size=1024, mtime=1000),
            FileNode(path=root / "doc.pdf", size=2048, mtime=1000)
        ]
        
        # 3. Plan and Execute
        organizer = Organizer(fs)
        rule = ExtensionRule()
        plan = organizer.plan_organization(files, rule, root)
        
        organizer.execute_plan(plan)
        
        # 4. Verify Virtual State
        # The virtual FS should record that files were "moved"
        
        # Expectation: /test_root/image.png -> /test_root/PNG/image.png
        expected_dest_png = root / "PNG" / "image.png"
        self.assertIn(expected_dest_png, fs.virtual_state)
        self.assertEqual(fs.virtual_state[expected_dest_png], root / "image.png")

        # Expectation: /test_root/doc.pdf -> /test_root/PDF/doc.pdf
        expected_dest_pdf = root / "PDF" / "doc.pdf"
        self.assertIn(expected_dest_pdf, fs.virtual_state)

if __name__ == '__main__':
    unittest.main()