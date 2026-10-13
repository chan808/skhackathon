import io
import json
import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from _support import workspace_temp
from practice.__main__ import load_bank, quiz


class TimedQuizTests(unittest.TestCase):
    def test_backend_bank_composes_twenty_original_questions(self):
        questions = load_bank("backend")["questions"]
        self.assertEqual(len(questions), 20)
        self.assertEqual(len({item["id"] for item in questions}), 20)
        self.assertEqual(sum(item["id"].startswith("AQ") for item in questions), 3)

    def test_advisory_timer_records_overrun_and_question_duration(self):
        clock = [0]

        def answer(_):
            clock[0] = 90
            return "1"

        args = Namespace(bank="backend", priority=None, category=None, review=None, seed=17, count=1, exam=True, minutes=1)
        with workspace_temp() as folder:
            with patch("practice.__main__.ROOT", Path(folder)), patch("practice.__main__.time.monotonic", side_effect=lambda: clock[0]), patch("builtins.input", side_effect=answer), redirect_stdout(io.StringIO()):
                self.assertEqual(quiz(args), 0)
            result = json.loads(next((Path(folder) / "reports").glob("quiz-*.json")).read_text(encoding="utf-8"))
            self.assertFalse(result["within_practice_budget"])
            self.assertEqual(result["elapsed_seconds"], 90)
            self.assertEqual(result["responses"][0]["question_seconds"], 90)
            self.assertEqual(result["timer_mode"], "advisory_no_forced_input_cutoff")

    def test_invalid_time_budget_is_rejected(self):
        for minutes in [0, -1, float("nan"), float("inf")]:
            args = Namespace(bank="backend", priority=None, category=None, review=None, seed=17, count=1, exam=True, minutes=minutes)
            with redirect_stdout(io.StringIO()), self.assertRaises(ValueError):
                quiz(args)

    def test_backend_review_preserves_bank_and_original_ids(self):
        question = load_bank("backend")["questions"][0]
        with workspace_temp() as folder:
            prior = Path(folder) / "prior.json"
            prior.write_text(json.dumps({"bank": "backend", "responses": [{"id": question["id"], "correct": False}]}), encoding="utf-8")
            args = Namespace(bank="basic", priority=None, category=None, review=str(prior), seed=17, count=20, exam=True, minutes=30)
            with patch("practice.__main__.ROOT", Path(folder)), patch("builtins.input", return_value=str(question["answer"] + 1)), redirect_stdout(io.StringIO()):
                quiz(args)
            result = json.loads(next((Path(folder) / "reports").glob("quiz-*.json")).read_text(encoding="utf-8"))
            self.assertEqual(result["bank"], "backend")
            self.assertEqual(result["correct"], 1)
            self.assertEqual(result["responses"][0]["id"], question["id"])
