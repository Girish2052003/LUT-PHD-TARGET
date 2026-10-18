"""Logic regression for Phase G raw stage-2 receipt; not a replay of MPC."""
import json
from pathlib import Path
import unittest

from scripts.audit_stage2_phase_g_secondary import EXPECTED_TOTALS, EXPECTED_ZIPS, audit

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "research/evidence/2026-10-18/phase-g-stage2-raw-secondary-independent-audit.json"


class RawEvidenceGateTests(unittest.TestCase):
    def test_phase_g_receipt_arithmetic(self):
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        categories = receipt["category_metrics"]
        self.assertEqual(set(categories), set(EXPECTED_ZIPS))
        for key, expected in (("tasks", 313), ("candidates", 626),
                              ("first", 229), ("second", 216), ("union", 262),
                              ("compiler_failures", 147)):
            self.assertEqual(sum(row[key] for row in categories.values()), expected)
        self.assertEqual(receipt["candidate_record_count"], 626)
        self.assertEqual(receipt["task_count"], 313)
        self.assertEqual(receipt["checked_raw_mpc_stdout_stderr_sha256"], 1932)
        self.assertEqual(receipt["native_attempt_count"], 644)
        self.assertEqual(receipt["recovery_zip_sha256"], __import__(
            "scripts.audit_stage2_phase_g_secondary",
            fromlist=["RECOVERY_SHA256"]).RECOVERY_SHA256)
        self.assertEqual(receipt["original_source_zip_sha256_by_category"], EXPECTED_ZIPS)
        self.assertEqual(receipt["failure_classes"]["compile_failure"] +
                         receipt["failure_classes"]["oracle_reject"] +
                         receipt["failure_classes"]["none"], 626)
        self.assertEqual(len(receipt["saved_vs_fresh_disagreements"]), 3)

    def test_missing_raw_artifacts_fail_closed(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as scratch:
            with self.assertRaises(FileNotFoundError):
                audit(Path(scratch))


if __name__ == "__main__":
    unittest.main()
