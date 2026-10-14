import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

from _support import workspace_temp

spec = importlib.util.spec_from_file_location("laptop_kit", Path(__file__).absolute().parents[1] / "scripts/build_laptop_kit.py")
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)


class LaptopKitTests(unittest.TestCase):
    def test_git_without_path_uses_installed_desktop_bundle(self):
        with workspace_temp() as folder:
            bundled = Path(folder) / ".cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe"
            bundled.parent.mkdir(parents=True)
            bundled.touch()
            with patch.object(kit.shutil, "which", return_value=None), patch.dict(kit.os.environ, {"USERPROFILE": folder}):
                self.assertEqual(Path(kit.find_git()), bundled)

    def test_explicit_git_path_with_spaces_does_not_fall_back(self):
        with workspace_temp() as folder:
            executable = Path(folder) / "Git with spaces" / "git.exe"
            executable.parent.mkdir()
            executable.touch()
            with patch.object(kit.shutil, "which", side_effect=AssertionError("Do not ignore an explicit path")):
                self.assertEqual(Path(kit.find_git(str(executable))), executable)
                with self.assertRaisesRegex(ValueError, "--git-path"):
                    kit.find_git(str(executable.parent / "missing.exe"))

    def test_missing_git_reports_recovery_before_export(self):
        with patch.object(kit.shutil, "which", return_value=None), patch.dict(kit.os.environ, {}, clear=True), patch.object(kit.subprocess, "check_output") as run:
            with self.assertRaisesRegex(SystemExit, "--git-path"):
                kit.main([])
            run.assert_not_called()

    def test_zip_guard_rejects_private_records_and_traversal(self):
        kit.validate_members(["skhackathon/README.md", "skhackathon/.env.example", "skhackathon/reports/verification.json"])
        for name in ["skhackathon/reports/local-verification.json", "skhackathon/reports/quiz-private.json", "skhackathon/data/private/invite.txt", "skhackathon/.env", "skhackathon/../outside.txt"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                kit.validate_members([name])


if __name__ == "__main__":
    unittest.main()
