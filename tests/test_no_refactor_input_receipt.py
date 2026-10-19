"""Fail-closed arithmetic/source boundary tests for read-only ablation preflight receipt."""
import json
from pathlib import Path
import unittest

P=Path(__file__).resolve().parents[1]/"research/evidence/2026-10-19/no-refactor-input-final-receipt.json"

class NoRefactorInputReceiptTests(unittest.TestCase):
    def test_313_complete_inputs_and_all_six_syntactic_exceptions(self):
        r=json.loads(P.read_text())
        self.assertEqual(sum(r["category_counts"].values()),313)
        self.assertEqual(r["original_task_count"],313)
        self.assertEqual(r["raw_input_and_instruction_strings_present"],313)
        self.assertEqual(r["raw_input_and_instruction_sha256_pairs_verified"],313)
        self.assertEqual(r["directly_python_parseable_original_input_count"],307)
        self.assertEqual(len(r["unparseable_original_input_ids"]),6)
        self.assertEqual(313-307,len(r["unparseable_original_input_ids"]))
        self.assertTrue(all(t.startswith("numpy_operation_test/") for t in r["unparseable_original_input_ids"]))

    def test_historical_experiment_and_professor_report_remain_locked(self):
        r=json.loads(P.read_text())
        self.assertFalse(r["original_author_no_refactor_pass1_reproduced"])
        self.assertFalse(r["original_author_no_refactor_pass2_reproduced"])
        self.assertEqual(r["historical_ablated_generated_output_count"],0)
        self.assertEqual(r["actual_llm_api_calls"],0)
        self.assertEqual(r["actual_mpc_executions"],0)
        self.assertFalse(r["report_authorized"])
        self.assertTrue(r["unmodified_original_scientific_results"])

if __name__=="__main__":
    unittest.main()
