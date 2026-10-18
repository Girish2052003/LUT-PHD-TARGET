"""Negative-path tests for the independent original/modified artifact verifier."""
import json
import tempfile
import unittest
from pathlib import Path
import zipfile
from scripts.audit_paired_controls import audit, digest


class PairedControlAuditTests(unittest.TestCase):
    def test_sha256_known_value(self):
        self.assertEqual(
            digest(b""),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )

    def test_empty_records_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "test.zip"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("summary.json", "{}")
                z.writestr("paired-records.jsonl", "")
            with self.assertRaisesRegex(ValueError, "1,252 unique"):
                audit(p, [])

    def test_duplicate_records_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "test.zip"
            row = {"task_id": "demo", "candidate_id": 0, "variant": "baseline"}
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("summary.json", "{}")
                z.writestr("paired-records.jsonl", json.dumps(row) + "\n" + json.dumps(row) + "\n")
            with self.assertRaisesRegex(ValueError, "1,252 unique"):
                audit(p, [])


if __name__ == "__main__":
    unittest.main()
