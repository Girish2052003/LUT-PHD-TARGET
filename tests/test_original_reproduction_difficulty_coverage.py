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
if __name__=="__main__":unittest.main()
