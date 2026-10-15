import copy
import unittest
import json
from pathlib import Path
import shutil
import tempfile

from scripts.summarize_original_replay import aggregate, verify_run


class ReplaySummaryTests(unittest.TestCase):
    def setUp(self):
        self.identity = {"task_records": [
            {"task_id": name, "template_sha256": "b" * 64,
             "candidate_sha256": {"spdzcoder": ["a" * 64, "c" * 64]},
             "archived_acceptance": [True, False]}
            for name in ("array_test/a", "loop_test/b")
        ]}
        self.records = [
            {"task_id": task["task_id"], "category": task["task_id"].split('/')[0],
             "system": "spdzcoder", "candidate_id": c,
             "source_sha256": task["candidate_sha256"]["spdzcoder"][c],
             "template_sha256": task["template_sha256"],
             "oracle_status": "ACCEPT" if (task["task_id"].endswith('/a') and c == 0) or (task["task_id"].endswith('/b') and c == 1) else "REJECT",
             "runtime_status": "PASS", "compile_status": "PASS",
             "failure_class": None, "exception": None, "duration_seconds": 1.0}
            for task in self.identity["task_records"] for c in (0, 1)
        ]

    def test_union_is_by_task_and_each_candidate_has_full_denominator(self):
        got = aggregate(self.records, self.identity, ["spdzcoder"])["systems"]["spdzcoder"]
        self.assertEqual(got["overall"]["tasks"], 2)
        self.assertEqual(got["overall"]["first_accepted"], 1)
        self.assertEqual(got["overall"]["second_accepted"], 1)
        self.assertEqual(got["overall"]["union_accepted"], 2)
        self.assertEqual(got["historical_disagreements"], 2)

    def test_missing_or_duplicate_candidate_is_rejected(self):
        for rows in (self.records[:-1], self.records + [self.records[0]]):
            with self.assertRaises(ValueError):
                aggregate(rows, self.identity, ["spdzcoder"])

    def test_foreign_source_or_template_hash_is_rejected(self):
        for field in ("source_sha256", "template_sha256"):
            rows = copy.deepcopy(self.records)
            rows[0][field] = "d" * 64
            with self.assertRaises(ValueError):
                aggregate(rows, self.identity, ["spdzcoder"])

    def test_boolean_candidate_and_invalid_outcome_are_rejected(self):
        for field, value in (("candidate_id", False), ("oracle_status", "true"), ("category", "other")):
            rows = copy.deepcopy(self.records)
            rows[0][field] = value
            with self.assertRaises(ValueError):
                aggregate(rows, self.identity, ["spdzcoder"])

    def test_oracle_acceptance_does_not_hide_runtime_failure(self):
        rows = copy.deepcopy(self.records)
        rows[0].update(runtime_status="FAIL", failure_class="runtime_failure")
        got = aggregate(rows, self.identity, ["spdzcoder"])["systems"]["spdzcoder"]
        self.assertEqual(got["accepted_without_completed_runtime"], 1)
        self.assertEqual(got["failure_classes"], {"none": 3, "runtime_failure": 1})


class RawReplayEvidenceTests(unittest.TestCase):
    def test_rejects_wrong_command_and_impossible_retry_termination(self):
        original = Path(__file__).resolve().parents[1] / 'research/evidence/2026-10-15/original-smoke/smoke'
        for field, value, expected_error in (("command", "different protocol", "command"), ("timed_out", True, "retry")):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / 'run'
                shutil.copytree(original, root)
                row = json.loads((root / 'outcomes.jsonl').read_text())
                row['attempts'][0][field] = value
                (root / 'outcomes.jsonl').write_text(json.dumps(row) + '\n')
                (root / row['log_path'] / 'outcome.json').write_text(json.dumps(row))
                with self.assertRaisesRegex(ValueError, expected_error):
                    verify_run(root)
