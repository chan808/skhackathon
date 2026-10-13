import unittest

from examples.agent_loop import OfflineReplay, ResponsesBackend, dispatch, function_call, run


class RepeatingBackend:
    kind = "test_fixture_no_llm"

    def respond(self, history):
        return {"status": "completed", "output": [function_call("read_materials", {}, "repeat")]}


class AgentLoopTests(unittest.TestCase):
    def test_offline_run_executes_tools_and_tags_simulation(self):
        result = run(OfflineReplay())
        self.assertEqual(result["mode"], "offline_scripted_replay_no_llm")
        self.assertEqual(result["status"], "contract_passed")
        self.assertEqual(result["tool_calls"], 3)
        self.assertEqual([step["tool"] for step in result["trace"]], ["read_materials", "normalize_temperatures", "evaluate_streak"])
        self.assertFalse(result["answer"]["automatic_shutdown"])

    def test_materials_never_expose_the_answer_key(self):
        materials = dispatch("read_materials", {})
        self.assertNotIn("answer_key", materials)

    def test_unknown_tools_and_invalid_values_are_rejected(self):
        with self.assertRaises(ValueError):
            dispatch("delete_all_files", {})
        with self.assertRaises(ValueError):
            dispatch("normalize_temperatures", {"values": [True], "units": ["C"]})
        with self.assertRaises(ValueError):
            dispatch("normalize_temperatures", {"values": [100], "units": ["K"]})
        with self.assertRaises(ValueError):
            dispatch("read_materials", {"arbitrary_path": "private.txt"})

    def test_repeated_calls_stop_at_the_budget(self):
        result = run(RepeatingBackend(), max_turns=6, max_calls=2)
        self.assertEqual(result["status"], "tool_budget_exhausted")
        self.assertEqual(result["tool_calls"], 2)

    def test_huge_numeric_arguments_return_errors_without_ending_loop(self):
        class HugeNumericBackend:
            kind = "test_fixture_no_llm"

            def respond(self, history):
                return {"status": "completed", "output": [function_call("normalize_temperatures", {"values": [10**500], "units": ["C"]}, "large")]}

        result = run(HugeNumericBackend(), max_calls=2)
        self.assertEqual(result["status"], "tool_budget_exhausted")
        self.assertTrue(all(not row["success"] for row in result["trace"]))
        with self.assertRaises(ValueError):
            dispatch("evaluate_streak", {"values_c": [76], "threshold_c": 10**500, "required": 1})

    def test_malformed_call_ends_with_explicit_status(self):
        class MalformedBackend:
            kind = "test_fixture_no_llm"

            def respond(self, history):
                return {"status": "completed", "output": [{"type": "function_call", "call_id": "broken"}]}

        self.assertEqual(run(MalformedBackend())["status"], "invalid_function_call")

    def test_huge_final_temperature_fails_contract_without_crashing(self):
        import json

        document = run(OfflineReplay())["answer"]
        document["temperatures_c"][0] = 10**500

        class InvalidFinalBackend:
            kind = "test_fixture_no_llm"

            def respond(self, history):
                return {"status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": json.dumps(document)}]}]}

        result = run(InvalidFinalBackend())
        self.assertEqual(result["status"], "contract_failed")
        self.assertIn("temperature normalization mismatch", result["validation_failures"])

    def test_live_mode_does_not_assume_credentials_or_a_model(self):
        with self.assertRaises(ValueError):
            ResponsesBackend(None, None)
        with self.assertRaises(ValueError):
            ResponsesBackend("unit-test-placeholder", None)


if __name__ == "__main__":
    unittest.main()
