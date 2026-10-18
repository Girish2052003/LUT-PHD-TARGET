"""Negative-path tests for the independent passive stage-2 raw-ZIP auditor."""
import tempfile
from pathlib import Path
import unittest
import zipfile

from scripts.audit_stage2_smoke_zip import audit, original_oracle, sha


class Stage2PassiveArtifactTests(unittest.TestCase):
    def test_original_weak_stdout_acceptance_semantics_are_preserved(self):
        self.assertTrue(original_oracle({"timed_out": False, "stdout": "Pass the test", "stderr": ""}))
        self.assertTrue(original_oracle({"timed_out": False, "stdout": "pass_or_not.mpc", "stderr": ""}))
        self.assertFalse(original_oracle({"timed_out": False, "stdout": "", "stderr": ""}))
        self.assertFalse(original_oracle({"timed_out": True, "stdout": "Pass the test", "stderr": ""}))
        self.assertFalse(original_oracle({"timed_out": False, "stdout": "Pass the test", "stderr": "Traceback: X"}))

    def test_sha256_known_empty(self):
        self.assertEqual(sha(b""), "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

    def test_zip_rejects_missing_original_trace(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            smoke, traces = root / "smoke.zip", root / "traces.zip"
            with zipfile.ZipFile(smoke, "w") as z:
                z.writestr("unrelated.txt", "data")
            with zipfile.ZipFile(traces, "w") as z:
                z.writestr("other.json", "{}")
            with self.assertRaises(KeyError):
                audit(smoke, traces)


if __name__ == "__main__":
    unittest.main()
