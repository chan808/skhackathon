import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from _support import workspace_temp


spec = importlib.util.spec_from_file_location("study_launcher", Path(__file__).absolute().parents[1] / "scripts" / "study.py")
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


class StudyLauncherTests(unittest.TestCase):
    def test_partial_environment_is_preserved_with_recovery_instructions(self):
        with workspace_temp() as folder:
            root = Path(folder)
            (root / ".venv-study").mkdir()
            saved = root / ".venv-study" / "keep.txt"
            saved.write_text("existing data", encoding="utf-8")
            with patch.object(study.subprocess, "run") as run:
                with self.assertRaisesRegex(RuntimeError, "Rename that folder"):
                    study.prepare_environment(root)
                run.assert_not_called()
            self.assertEqual(saved.read_text(encoding="utf-8"), "existing data")

    def test_new_environment_uses_installed_python_without_pip(self):
        with workspace_temp() as folder:
            root = Path(folder)
            python = study.environment_python(root)

            def complete(command, **kwargs):
                if command[1:3] == ["-m", "venv"]:
                    python.parent.mkdir(parents=True)
                    python.touch()
                    return subprocess.CompletedProcess(command, 0)
                return subprocess.CompletedProcess(command, 0, stdout="[3, 12]\n")

            with patch.object(study.subprocess, "run", side_effect=complete) as run:
                self.assertEqual(study.prepare_environment(root), python)
            created = run.call_args_list[0].args[0]
            self.assertEqual(created[1:3], ["-m", "venv"])
            self.assertIn("--without-pip", created)
            self.assertEqual(len(run.call_args_list), 2)

    def test_existing_unsupported_environment_is_never_replaced(self):
        with workspace_temp() as folder:
            root = Path(folder)
            python = study.environment_python(root)
            python.parent.mkdir(parents=True)
            python.write_text("keep", encoding="utf-8")
            with patch.object(study.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout="[3, 9]\n")) as run:
                with self.assertRaisesRegex(RuntimeError, "was kept"):
                    study.prepare_environment(root)
                self.assertEqual(run.call_count, 1)
            self.assertEqual(python.read_text(encoding="utf-8"), "keep")

    def test_modes_preserve_backend_twenty_questions_and_case_selection(self):
        timed = study.command_for("timed", Path("python"))
        self.assertEqual(timed[timed.index("--bank") + 1], "backend")
        self.assertEqual(timed[timed.index("--count") + 1], "20")
        self.assertEqual(timed[timed.index("--minutes") + 1], "30")
        self.assertEqual(study.command_for("case", Path("python"), "RC03")[-2:], ["--case", "RC03"])


if __name__ == "__main__":
    unittest.main()
