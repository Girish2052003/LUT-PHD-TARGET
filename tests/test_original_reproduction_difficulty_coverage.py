"""Regression guard for original author R8 difficulty accounting; no native code."""
import copy
import json
from pathlib import Path
import unittest
from scripts.verify_reproduction_difficulty_coverage import verify,ROOT,FIRST,SECOND,DIFFICULTIES

class OriginalR8CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage=json.loads((ROOT/FIRST).read_text())
        cls.secondary=json.loads((ROOT/SECOND).read_text())
        cls.issues=json.loads((ROOT/DIFFICULTIES).read_text())
    def test_all_original_failures_and_native_attempts_are_accounted(self):
        x=verify(self.stage,self.secondary,self.issues)
        self.assertEqual(x["candidates"],626)
        self.assertEqual(x["attempts"],644)
        self.assertEqual(x["original_oracle_acceptances"],445)
        self.assertEqual(x["nonaccepted"],181)
        self.assertFalse(x["historical_GPT4_Azure_model_stage_reproduced"])
        self.assertFalse(x["paper_original_no_refactoring_ablation_reproduced"])
        self.assertFalse(x["professor_report_authorized"])
    def test_missing_failure_classification_is_rejected(self):
        issues=copy.deepcopy(self.issues)
        issues["original_native_candidate_status_totals"]["compile_fail"]-=1
        with self.assertRaises(ValueError):verify(self.stage,self.secondary,issues)
    def test_original_failed_aggregator_must_remain_red(self):
        stage=copy.deepcopy(self.stage)
        stage["original_native_run_conclusion"]="success"
        with self.assertRaisesRegex(ValueError,"aggregator"):verify(stage,self.secondary,self.issues)
    def test_unverified_runtime_acceptance_rejected(self):
        stage=copy.deepcopy(self.stage)
        stage["accepted_without_completed_runtime"]=1
        with self.assertRaisesRegex(ValueError,"never completed"):verify(stage,self.secondary,self.issues)

    def test_wrong_original_archive_pin_is_rejected(self):
        stage=copy.deepcopy(self.stage)
        stage["original_source_archive_sha256"]="0"*64
        with self.assertRaises(ValueError):verify(stage,self.secondary,self.issues)
    def test_wrong_original_run_identity_is_rejected(self):
        stage=copy.deepcopy(self.stage)
        stage["original_native_run_id"]=1
        with self.assertRaises(ValueError):verify(stage,self.secondary,self.issues)
    def test_unknown_category_is_rejected_even_when_totals_match(self):
        issues=copy.deepcopy(self.issues)
        issues["failure_counts_by_category"]["fabricated_test"]=issues["failure_counts_by_category"].pop("array_test")
        with self.assertRaises(ValueError):verify(self.stage,self.secondary,issues)
    def test_per_category_failures_must_match_independent_audit(self):
        issues=copy.deepcopy(self.issues)
        issues["failure_counts_by_category"]["array_test"]["compile_fail"]-=1
        issues["failure_counts_by_category"]["loop_test"]["compile_fail"]+=1
        with self.assertRaises(ValueError):verify(self.stage,self.secondary,issues)
    def test_disagreement_identities_must_match(self):
        secondary=copy.deepcopy(self.secondary)
        secondary["saved_vs_fresh_disagreements"][0]["task_id"]="branch_test/fabricated"
        with self.assertRaises(ValueError):verify(self.stage,secondary,self.issues)
    def test_runtime_partition_must_match(self):
        stage=copy.deepcopy(self.stage)
        stage["runtime_statuses"]={"PASS":478,"NOT_RUN":148}
        with self.assertRaises(ValueError):verify(stage,self.secondary,self.issues)


    def test_same_total_taxonomy_cannot_hide_unclassified_errors(self):
        issues=copy.deepcopy(self.issues)
        issues["compile_terminal_exception_types"]["AttributeError"]+=2
        del issues["compile_terminal_exception_types"]["unclassified_terminal_stderr"]
        with self.assertRaises(ValueError):verify(self.stage,self.secondary,issues)
    def test_recovery_artifact_identity_must_match(self):
        secondary=copy.deepcopy(self.secondary)
        secondary["recovery_zip_artifact_id"]=1
        with self.assertRaises(ValueError):verify(self.stage,secondary,self.issues)
    def test_project_register_rejects_missing_family(self):
        from scripts.verify_reproduction_difficulty_coverage import verify_register
        register=json.loads((ROOT/"research/reproduction_difficulties.json").read_text())
        register["entries"]=[r for r in register["entries"] if r["id"]!="final_native_failures"]
        with self.assertRaises(ValueError):verify_register(register,ROOT)
    def test_project_register_requires_inspectable_evidence(self):
        from scripts.verify_reproduction_difficulty_coverage import verify_register
        register=json.loads((ROOT/"research/reproduction_difficulties.json").read_text())
        register["entries"][0]["evidence_paths"]=["does-not-exist.json"]
        with self.assertRaises(ValueError):verify_register(register,ROOT)

if __name__=="__main__":unittest.main()

