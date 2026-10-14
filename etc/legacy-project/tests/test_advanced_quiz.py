import copy
import io
import json
import random
import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from _support import workspace_temp
from practice.__main__ import BANK_PATHS, quiz
from practice.core import load_quiz


class AdvancedQuizTests(unittest.TestCase):
    def test_synthetic_arithmetic_requires_explicit_provenance(self):
        item = copy.deepcopy(load_quiz()["questions"][0])
        item["source_urls"] = []
        with workspace_temp() as folder:
            path = Path(folder) / "bank.json"
            path.write_text(json.dumps({"questions": [item]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_quiz(path)
            item["source_type"] = "synthetic_arithmetic_or_evidence"
            path.write_text(json.dumps({"questions": [item]}), encoding="utf-8")
            self.assertEqual(len(load_quiz(path)["questions"]), 1)

    def test_priority_filter_and_scoring_preserve_bank(self):
        items = [item for item in load_quiz(BANK_PATHS["advanced"])["questions"]
                 if item["priority"] == "first_round_core"]
        self.assertEqual(len(items), 28)
        random.Random(23).shuffle(items)
        args = Namespace(bank="advanced", priority="first_round_core", category=None,
                         review=None, seed=23, count=12, exam=True)
        with workspace_temp() as folder:
            with patch("practice.__main__.ROOT", Path(folder)), patch("builtins.input", side_effect=[str(item["answer"] + 1) for item in items[:12]]), redirect_stdout(io.StringIO()):
                self.assertEqual(quiz(args), 0)
            saved = next((Path(folder) / "reports").glob("quiz-*.json"))
            result = json.loads(saved.read_text(encoding="utf-8"))
            self.assertEqual(result["bank"], "advanced")
            self.assertEqual(result["priority_filter"], "first_round_core")
            self.assertEqual(result["correct"], 12)
            self.assertEqual([row["id"] for row in result["responses"]], [item["id"] for item in items[:12]])

    def test_review_restores_advanced_bank_without_cli_flag(self):
        item = load_quiz(BANK_PATHS["advanced"])["questions"][0]
        with workspace_temp() as folder:
            previous = Path(folder) / "previous.json"
            previous.write_text(json.dumps({"bank": "advanced", "responses": [{"id": item["id"], "correct": False}]}), encoding="utf-8")
            args = Namespace(bank="basic", priority=None, category=None, review=str(previous),
                             seed=0, count=36, exam=False)
            with patch("practice.__main__.ROOT", Path(folder)), patch("builtins.input", return_value=str(item["answer"] + 1)), redirect_stdout(io.StringIO()):
                self.assertEqual(quiz(args), 0)
            result = json.loads(next((Path(folder) / "reports").glob("quiz-*.json")).read_text(encoding="utf-8"))
            self.assertEqual(result["bank"], "advanced")
            self.assertEqual(result["answered"], 1)
            self.assertEqual(result["responses"][0]["id"], item["id"])
