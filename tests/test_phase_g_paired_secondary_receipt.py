"""Guard arithmetic and negative results in the secondary complete paired ZIP receipt."""
import json
from pathlib import Path
import unittest

DATA = Path(__file__).resolve().parents[1] / "research/evidence/2026-10-18/phase-g-paired-secondary-recomputed.json"

class PhaseGPairedReceiptTests(unittest.TestCase):
    def test_complete_paired_accounting_and_negative_controls(self):
        r=json.loads(DATA.read_text())
        self.assertEqual((r["task_count"], r["original_candidate_pairs"],r["execution_records"],r["attempts"]), (313,626,1252,1280))
        self.assertEqual(sum(r["category_execution_records"].values()),1252)
        self.assertEqual(len(r["artifact_zip_sha256"]),8)
        self.assertEqual(r["raw_input_stdout_stderr_sha256_checks"],3*r["attempts"])
        self.assertEqual(r["source_original_transformed_template_sha256_checks"],4*r["execution_records"])
        self.assertEqual(r["summary_jsonl_to_category_record_exact_matches"],1252)
        self.assertEqual(r["per_task_failure_matrix_exact_matches"],626)
        self.assertEqual(len(r["source_changed"]),2)
        self.assertEqual(len(r["unchanged_source_acceptance_flips"]),4)
        self.assertTrue(all(f["compiled_input_identical"] for f in r["unchanged_source_acceptance_flips"]))
        self.assertTrue(all(x["baseline_oracle"]=="ACCEPT" and x["modified_oracle"]=="ACCEPT" for x in r["source_changed"]))
        self.assertEqual({k:(v["first"],v["second"],v["union"],v["compile_failures"]) for k,v in r["metrics"].items()},
                         {"baseline":(270,266,290,75),"modified":(271,263,290,75)})
        for v in ("baseline","modified"):
            self.assertEqual(sum(r["failure_counts"][v].values()),626)

if __name__=="__main__":
    unittest.main()
