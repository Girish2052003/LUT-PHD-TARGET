"""Saved-stage evaluation inventory must fail closed and never invent results."""
import io
import tarfile
import unittest

from scripts.audit_saved_stage_evaluations import inspect


class HistoricalEvaluationTests(unittest.TestCase):
    def test_missing_stage2_evaluation_is_disclosed(self):
        dummy = {"task_records": [{"task_id": f"test_{x}/record"} for x in range(313)]}
        with tarfile.open(fileobj=io.BytesIO(), mode="w") as archive:
            observed = inspect(archive, dummy)
        self.assertEqual(len(observed["missing_categories"]), 7)
        self.assertTrue(all(r["status"] == "MISSING_STAGE2_EVALUATION"
                            for r in observed["categories"].values()))
        self.assertEqual(observed["fresh_mpc_executions"], 0)
        self.assertEqual(observed["live_llm_calls"], 0)

    def test_incomplete_identity_is_rejected(self):
        with tarfile.open(fileobj=io.BytesIO(), mode="w") as archive:
            with self.assertRaisesRegex(ValueError, "identity ledger"):
                inspect(archive, {"task_records": []})


if __name__ == "__main__":
    unittest.main()
