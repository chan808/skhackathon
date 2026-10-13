import copy
import io
import json
import math
import random
import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from _support import workspace_temp

from practice.core import analyze, clean_rows, generate_rows, load_quiz, validate_answer, write_dataset


class PracticeTests(unittest.TestCase):
    def test_generated_data_health_and_crosscheck(self):
        with workspace_temp() as folder:
            path = Path(folder) / "lots.csv"
            write_dataset(path)
            result = analyze(path)
            self.assertEqual(result["raw_rows"], 245)
            self.assertEqual(result["clean_rows"], 232)
            self.assertEqual(sum(result["rejected"].values()), 13)
            self.assertEqual(result["temperature_conversions"], 1)
            self.assertTrue(math.isclose(result["weighted_yield"], result["sqlite_weighted_yield"]))
            self.assertGreater(abs(result["weighted_yield"] - result["unweighted_lot_yield"]), 0.01)

    def test_order_does_not_change_accepted_counts(self):
        rows = generate_rows()
        clean, rejected, _ = clean_rows(rows)
        reversed_clean, reversed_rejected, _ = clean_rows(list(reversed(rows)))
        self.assertEqual(sorted(clean, key=lambda row: row["lot_id"]), sorted(reversed_clean, key=lambda row: row["lot_id"]))
        self.assertEqual(rejected, reversed_rejected)

    def test_conflicting_duplicate_is_never_silently_dropped(self):
        rows = generate_rows()
        rows[-1]["good_dies"] = "1"
        with self.assertRaises(ValueError):
            clean_rows(rows)

    def test_fahrenheit_conversion(self):
        rows, _, _ = clean_rows(generate_rows())
        target = next(row for row in rows if row["lot_id"] == "L0100")
        self.assertEqual(target["temperature_c"], 70.0)

    def test_short_csv_row_is_rejected_without_type_error(self):
        row = generate_rows()[0]
        row["good_dies"] = None
        clean, rejected, _ = clean_rows([row])
        self.assertEqual(clean, [])
        self.assertEqual(rejected, {"invalid_row_shape": 1})

    def test_temperature_conversion_overflow_is_rejected(self):
        row = generate_rows()[0]
        row["temperature"], row["temperature_unit"] = "-1.7e308", "F"
        clean, rejected, _ = clean_rows([row])
        self.assertEqual(clean, [])
        self.assertEqual(rejected, {"invalid_temperature": 1})

    def test_out_of_sqlite_integer_range_is_rejected_before_insert(self):
        row = generate_rows()[0]
        row["tested_dies"] = str(2**63)
        clean, rejected, _ = clean_rows([row])
        self.assertEqual(clean, [])
        self.assertEqual(rejected, {"invalid_count_range": 1})

    def test_answer_shape_is_not_truth_validation(self):
        valid = {"answer": "a", "claims": [{"text": "t", "source": "s", "evidence": "e"}], "limitations": []}
        self.assertEqual(validate_answer(valid), [])
        invalid = copy.deepcopy(valid)
        invalid["claims"][0]["evidence"] = ""
        self.assertTrue(validate_answer(invalid))
        self.assertTrue(validate_answer({"answer": "a", "claims": "invalid", "limitations": None}))

    def test_quiz_has_unique_ids_and_supported_answers(self):
        quiz = load_quiz()
        self.assertEqual(len(quiz["questions"]), 40)

    def test_quiz_scoring_and_saved_log_end_to_end(self):
        from practice.__main__ import quiz
        questions = load_quiz()["questions"]
        random.Random(31).shuffle(questions)
        inputs = [str(item["answer"] + 1) for item in questions]
        args = Namespace(category=None, review=None, seed=31, count=40, exam=True)
        with workspace_temp() as folder:
            with patch("practice.__main__.ROOT", Path(folder)), patch("builtins.input", side_effect=inputs), redirect_stdout(io.StringIO()):
                self.assertEqual(quiz(args), 0)
            logs = list((Path(folder) / "reports").glob("quiz-*.json"))
            self.assertEqual(len(logs), 1)
            result = json.loads(logs[0].read_text(encoding="utf-8"))
            self.assertEqual(result["answered"], 40)
            self.assertEqual(result["correct"], 40)
            self.assertEqual(result["wrong_by_category"], {})

    def test_wrong_answer_review_selects_only_prior_errors(self):
        from practice.__main__ import quiz
        question = load_quiz()["questions"][0]
        with workspace_temp() as folder:
            log = Path(folder) / "previous.json"
            log.write_text(json.dumps({"responses": [{"id": question["id"], "correct": False}, {"id": "Q40", "correct": True}]}), encoding="utf-8")
            args = Namespace(category=None, review=str(log), seed=0, count=40, exam=False)
            with patch("practice.__main__.ROOT", Path(folder)), patch("builtins.input", return_value=str(question["answer"] + 1)), redirect_stdout(io.StringIO()):
                quiz(args)
            saved = next((Path(folder) / "reports").glob("quiz-*.json"))
            result = json.loads(saved.read_text(encoding="utf-8"))
            self.assertEqual(result["answered"], 1)
            self.assertEqual(result["responses"][0]["id"], question["id"])

    def test_quit_preserves_partial_progress(self):
        from practice.__main__ import quiz
        args = Namespace(category=None, review=None, seed=17, count=10, exam=False)
        with workspace_temp() as folder:
            with patch("practice.__main__.ROOT", Path(folder)), patch("builtins.input", side_effect=["1", "q"]), redirect_stdout(io.StringIO()):
                quiz(args)
            saved = next((Path(folder) / "reports").glob("quiz-*.json"))
            result = json.loads(saved.read_text(encoding="utf-8"))
            self.assertEqual(result["answered"], 1)
            self.assertEqual(result["planned_questions"], 10)


if __name__ == "__main__":
    unittest.main()
