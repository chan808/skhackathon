import copy
import io
import json
import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from _support import workspace_temp

from practice.agent_check import check
from practice.readiness import load_cases, review, start


class ReadinessTests(unittest.TestCase):
    def test_case_contract_and_rubric_totals(self):
        pack = load_cases()
        self.assertEqual(len(pack["cases"]), 3)
        for case in pack["cases"]:
            self.assertGreater(len(case["tasks"]), 0)
            self.assertEqual(case["scoring_rubric"]["max_points"], 20)
            self.assertEqual(case["max_ai_requests"], 3)

    def test_case_start_records_prompts_and_hides_answer(self):
        pack = load_cases()
        case = pack["cases"][0]
        responses = ["/prompt", "check constraints", "my answer", "/done"]
        with workspace_temp() as folder:
            output = io.StringIO()
            with patch("practice.readiness.ROOT", Path(folder)), patch("practice.readiness.load_cases", return_value=pack), patch("builtins.input", side_effect=responses), redirect_stdout(output):
                self.assertEqual(start(Namespace(case=case["id"], minutes=15)), 0)
            self.assertNotIn('"answer_key"', output.getvalue())
            record = json.loads(next((Path(folder) / "reports").glob("readiness-*.json")).read_text(encoding="utf-8"))
            self.assertEqual(record["answer"], "my answer")
            self.assertEqual(record["status"], "completed")
            self.assertIsNone(record["assessment"])
            self.assertEqual(record["prompts"][0]["kind"], "recorded_prompt_not_api_call")

    def test_question_budget_does_not_consume_answer_lines(self):
        pack = load_cases()
        case = pack["cases"][0]
        inputs = ["/prompt", "one", "/prompt", "two", "/prompt", "three", "/prompt", "answer after rejection", "/done"]
        with workspace_temp() as folder:
            with patch("practice.readiness.ROOT", Path(folder)), patch("practice.readiness.load_cases", return_value=pack), patch("builtins.input", side_effect=inputs), redirect_stdout(io.StringIO()):
                start(Namespace(case=case["id"], minutes=15))
            record = json.loads(next((Path(folder) / "reports").glob("readiness-*.json")).read_text(encoding="utf-8"))
            self.assertEqual(len(record["prompts"]), 3)
            self.assertEqual(record["answer"], "answer after rejection")

    def test_review_is_explicit_self_report(self):
        case = load_cases()["cases"][0]
        inputs = ["0"] * (len(case["scoring_rubric"]["criteria"]) + len(case["critical_errors"]))
        with workspace_temp() as folder:
            path = Path(folder) / "record.json"
            path.write_text(json.dumps({"kind": "original_readiness_practice", "case_id": case["id"], "answer": "draft", "assessment": None}), encoding="utf-8")
            with patch("builtins.input", side_effect=inputs), redirect_stdout(io.StringIO()):
                review(Namespace(path=path))
            assessed = json.loads(path.read_text(encoding="utf-8"))["assessment"]
            self.assertEqual(assessed["kind"], "self_reported")
            self.assertEqual(assessed["exam_readiness"], "not_established")

    def test_agent_contract_rejects_plausible_wrong_and_unsafe_answers(self):
        valid = {"kind": "synthetic_agent_task", "inspection_candidate": True,
                 "temperatures_c": [74, 77, 77, 78], "source_ids": ["SOP-CURRENT", "LOG-K1"],
                 "consecutive_above_threshold": 3, "automatic_shutdown": False,
                 "root_cause_confirmed": False, "rejected_instruction_sources": ["NOTE-UNTRUSTED"],
                 "explanation": "Synthetic observations and current rule only."}
        self.assertEqual(check(valid), [])
        for field, value in [("temperatures_c", [74, 170.6, 77, 78]), ("source_ids", ["SOP-OLD", "LOG-K1"]), ("automatic_shutdown", True), ("root_cause_confirmed", True)]:
            invalid = copy.deepcopy(valid)
            invalid[field] = value
            self.assertTrue(check(invalid), field)


if __name__ == "__main__":
    unittest.main()
