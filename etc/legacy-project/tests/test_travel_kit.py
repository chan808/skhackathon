import importlib.util
import unittest
import zipfile
from pathlib import Path

from _support import workspace_temp

spec = importlib.util.spec_from_file_location("travel_kit", Path(__file__).absolute().parents[1] / "scripts/build_travel_kit.py")
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)


class TravelKitTests(unittest.TestCase):
    def make_public_fixture(self, root):
        for name in kit.REQUIRED:
            if name == kit.SKILL_INSTALLED:
                name = kit.SKILL_SOURCE
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("public", encoding="utf-8")

    def test_private_records_credentials_and_installers_are_not_exported(self):
        with workspace_temp() as folder:
            root = Path(folder)
            self.make_public_fixture(root)
            for name in [".env", ".venv-study/Scripts/python.exe", "data/private/invite.md",
                         "reports/environment.json", "reports/travel-readiness.json", "reports/quiz-personal.json",
                         "output/laptop-kit/installers/setup.exe", ".agents/private-settings.json",
                         "templates/private/notes.md", "practice/__pycache__/personal.py"]:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("private", encoding="utf-8")
            result = kit.build_bundle(root, root / "output/laptop-kit")
            with zipfile.ZipFile(root / "output/laptop-kit" / result["archive"]) as bundle:
                names = bundle.namelist()
                self.assertTrue(all(bundle.read(name) == b"public" for name in names))
                self.assertIn("skhackathon/" + kit.SKILL_INSTALLED, names)
                self.assertFalse(any("invite" in name or "environment.json" in name or "setup.exe" in name for name in names))

    def test_current_public_edits_are_included_without_git(self):
        with workspace_temp() as folder:
            root = Path(folder)
            self.make_public_fixture(root)
            (root / "TRAVEL-RUNBOOK.md").write_text("current edit", encoding="utf-8")
            result = kit.build_bundle(root, root / "output/laptop-kit")
            with zipfile.ZipFile(root / "output/laptop-kit" / result["archive"]) as bundle:
                self.assertEqual(bundle.read("skhackathon/TRAVEL-RUNBOOK.md"), b"current edit")

    def test_missing_required_document_stops_export(self):
        with workspace_temp() as folder:
            with self.assertRaisesRegex(ValueError, "Required public file"):
                kit.build_bundle(Path(folder), Path(folder) / "output")
