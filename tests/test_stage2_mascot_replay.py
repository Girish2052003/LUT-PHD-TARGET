"""Deterministic, no-candidate-execution checks of saved original stage-2 replay."""
from pathlib import Path
import hashlib
import json
import tempfile
import unittest

from scripts.prepare_stage2_replay import build_stage2_ledger
from scripts.replay_stage2 import stage2_candidates
from scripts.verify_stage2_replay import summarize_full
from scripts.reproduce_official_scores import COUNTS
from scripts.prepare_original_replay import AUTHOR_SHA


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def fixture(directory):
    baseline = Path(directory)
    source_manifest = {"author_archive_sha256": AUTHOR_SHA, "baseline_files": []}
    original = {"task_records": []}
    for category, count in COUNTS.items():
        candidates = []
        report = []
        for pos in range(count):
            task = f"unit_test_{pos:03d}"
            candidates.append({"test_name": task, "response_0": f"def x(): return {pos}",
                               "response_1": f"def y(): return {pos}"})
            report.append(f"{task}, True, False")
            original["task_records"].append({
                "task_id": f"{category}/{task}", "position_in_split": pos,
                "template_sha256": digest((category + "/" + task).encode()),
            })
        paths = {
            f"data/stage_2_SPDZ_output/experiment-1-{category}.jsonl":
                ("\n".join(json.dumps(row) for row in candidates) + "\n").encode(),
            f"evaluation/experiment-1-stage_2_SPDZ_output_{category}.txt":
                ("\n".join(report) + "\n").encode(),
        }
        for p, raw in paths.items():
            target = baseline / p
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            source_manifest["baseline_files"].append({"path": p, "sha256": digest(raw)})
    return original, source_manifest


class AuthenticStage2Tests(unittest.TestCase):
    def test_original_313_task_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            original, manifest = fixture(tmp)
            ledger = build_stage2_ledger(Path(tmp), original, manifest)
            self.assertEqual(len(ledger["task_records"]), 313)
            self.assertEqual(sum(c["tasks"] for c in ledger["categories"].values()), 313)
            self.assertEqual(sum(sum(x["historical_stage2_evaluator_flags"])
                                 for x in ledger["task_records"]), 313)
            records = stage2_candidates(Path(tmp), ledger, "math_test")
            self.assertEqual(len(records), 38)
            self.assertEqual(records[0][1]["task_id"], "math_test/unit_test_000")
            self.assertEqual(len(stage2_candidates(Path(tmp), ledger, "math_test", "unit_test_003")), 1)

    def test_reject_altered_source_even_if_task_order_correct(self):
        with tempfile.TemporaryDirectory() as tmp:
            original, manifest = fixture(tmp)
            ledger = build_stage2_ledger(Path(tmp), original, manifest)
            candidate = Path(tmp) / "data/stage_2_SPDZ_output/experiment-1-loop_test.jsonl"
            candidate.write_bytes(candidate.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "digest changed"):
                stage2_candidates(Path(tmp), ledger, "loop_test")

    def test_reject_wrong_saved_flag_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            original, manifest = fixture(tmp)
            path = Path(tmp) / "evaluation/experiment-1-stage_2_SPDZ_output_math_test.txt"
            rows = path.read_text().splitlines()
            rows[0] = "unknown_case, True, False"
            raw = ("\n".join(rows) + "\n").encode()
            path.write_bytes(raw)
            for record in manifest["baseline_files"]:
                if record["path"].endswith("stage_2_SPDZ_output_math_test.txt"):
                    record["sha256"] = digest(raw)
            with self.assertRaisesRegex(ValueError, "disagree"):
                build_stage2_ledger(Path(tmp), original, manifest)

    def test_missing_original_source_manifest_entry_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            original, manifest = fixture(tmp)
            manifest["baseline_files"] = [r for r in manifest["baseline_files"]
                                          if "experiment-1-math_test.jsonl" not in r["path"]]
            with self.assertRaisesRegex(ValueError, "pinned archive"):
                build_stage2_ledger(Path(tmp), original, manifest)

    def test_reject_unpinned_original_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            original, manifest = fixture(tmp)
            manifest["author_archive_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "Zenodo"):
                build_stage2_ledger(Path(tmp), original, manifest)

    def test_accept_and_reject_accounting_but_no_causal_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            original, manifest = fixture(tmp)
            ledger = build_stage2_ledger(Path(tmp), original, manifest)
            rows = []
            for r in ledger["task_records"]:
                for c in (0, 1):
                    rows.append({"task_id": r["task_id"], "candidate_id": c,
                                 "oracle_status": "ACCEPT" if c == 0 else "REJECT",
                                 "compile_status": "PASS", "runtime_status": "PASS",
                                 "failure_class": None})
            summary = summarize_full(rows, ledger)
            self.assertEqual(summary["candidate_records"], 626)
            self.assertEqual(summary["fresh"], {"tasks": 313, "first": 313, "second": 0, "union": 313})
            self.assertEqual(summary["historical"], summary["fresh"])
            self.assertEqual(summary["saved_to_fresh_disagreements"], [])

    def test_incomplete_or_duplicate_full_replay_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            original, manifest = fixture(tmp)
            ledger = build_stage2_ledger(Path(tmp), original, manifest)
            rows = [{"task_id": r["task_id"], "candidate_id": c,
                     "oracle_status": "REJECT", "compile_status": "FAIL",
                     "runtime_status": "NOT_RUN", "failure_class": "compile_failure"}
                    for r in ledger["task_records"] for c in (0, 1)]
            with self.assertRaisesRegex(ValueError, "incomplete"):
                summarize_full(rows[:-1], ledger)
            with self.assertRaisesRegex(ValueError, "duplicate"):
                summarize_full(rows + [rows[0]], ledger)


if __name__ == "__main__":
    unittest.main()
