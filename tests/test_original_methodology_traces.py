"""Fail-closed tests for official historical SPDZCoder methodology stage exporter."""
import io
import json
import tarfile
import unittest

from scripts.export_original_methodology_traces import (
    COUNTS, SAMPLES, STAGES, inspect, records, sha,
)


class OriginalStageTraceTests(unittest.TestCase):
    def test_unique_categories_and_real_task_count(self):
        self.assertEqual(sum(COUNTS.values()), 313)
        self.assertEqual(len(SAMPLES), 7)
        self.assertEqual({s.split("/")[0] for s in SAMPLES}, set(COUNTS))
        self.assertEqual(len(STAGES), 4)

    def test_valid_json_lines(self):
        got = records(b'{"test_name":"x","response_0":"code"}\n{"test_name":"y"}\n', 2)
        self.assertEqual([x[0]["test_name"] for x in got], ["x", "y"])

    def test_duplicate_task_fails(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            records(b'{"test_name":"x"}\n{"test_name":"x"}\n', 2)

    def test_wrong_denominator_fails(self):
        with self.assertRaisesRegex(ValueError, "missing/extra"):
            records(b'{"test_name":"x"}\n', 2)

    def test_malformed_row_fails(self):
        with self.assertRaisesRegex(ValueError, "Malformed"):
            records(b'{"response_0":"x"}\n', 1)

    def test_stage_path_contract(self):
        paths = [p.format(category="math_test") for _, p in STAGES]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertIn("data/stage_3_output/experiment-1-math_test.jsonl", paths)
        self.assertIn("data/input_processed_data/math_test.json", paths)

    def test_empty_tar_cannot_pass_identification(self):
        fake = {"task_records": [{"task_id": "fake"}], "source_files": {}}
        with tarfile.open(fileobj=io.BytesIO(), mode="w") as tar:
            with self.assertRaisesRegex(ValueError, "incomplete"):
                inspect(tar, fake)

    def test_digest_known(self):
        self.assertEqual(sha(b""), "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")


if __name__ == "__main__":
    unittest.main()
