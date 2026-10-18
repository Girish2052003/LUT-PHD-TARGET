"""Negative-path controls for independent 626-candidate stage-2 ZIP audit."""
import unittest
from scripts.audit_stage2_full_zips import COUNTS, audit, measure, original_oracle, sha


class FullStage2RawAuditTests(unittest.TestCase):
    def test_original_loose_oracle_is_reproduced_not_strengthened(self):
        self.assertTrue(original_oracle("a PASS in a filename", "", False))
        self.assertFalse(original_oracle("Pass the test", "Traceback: compile error", False))
        self.assertFalse(original_oracle("Pass the test", "", True))

    def test_requires_exact_seven_original_categories(self):
        with self.assertRaisesRegex(ValueError, "Exactly seven"):
            audit([])
        self.assertEqual(sum(COUNTS.values()), 313)

    def test_denominator_and_union_accounting(self):
        tasks = {"array_test/caseA", "array_test/caseB"}
        rows = [
            {"task_id": "array_test/caseA", "candidate_id": 0, "oracle_status": "ACCEPT", "historical_author_flag": False},
            {"task_id": "array_test/caseA", "candidate_id": 1, "oracle_status": "REJECT", "historical_author_flag": True},
            {"task_id": "array_test/caseB", "candidate_id": 0, "oracle_status": "REJECT", "historical_author_flag": False},
            {"task_id": "array_test/caseB", "candidate_id": 1, "oracle_status": "REJECT", "historical_author_flag": False},
        ]
        self.assertEqual(measure(tasks, rows), {"tasks": 2, "first": 1, "second": 0, "union": 1})
        self.assertEqual(measure(tasks, rows, True), {"tasks": 2, "first": 0, "second": 1, "union": 1})

    def test_empty_digest(self):
        self.assertEqual(sha(b""), "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")


if __name__ == "__main__":
    unittest.main()
