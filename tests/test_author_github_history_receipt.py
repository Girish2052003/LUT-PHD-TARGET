"""Regression for the exact, bounded original author Git-history receipt."""
import json
from pathlib import Path
import unittest

RECEIPT=Path(__file__).resolve().parents[1]/"research/evidence/2026-10-18/original-author-git-history-independent-audit.json"

class AuthorHistoricalGitReceiptTests(unittest.TestCase):
    def test_all_embedded_commits_and_blobs_inspected_without_hidden_packs(self):
        record=json.loads(RECEIPT.read_text())
        self.assertEqual(record["checked_original_git_objects"],{"blob":579,"tree":28,"commit":3})
        self.assertEqual(record["historical_commit_roots_examined"],3)
        self.assertEqual(record["unresolvable_commit_roots"],0)
        self.assertEqual(record["git_packfiles"],0)
        self.assertTrue(record["all_embedded_git_loose_object_history_resolved"])
        self.assertEqual(record["historical_blobs_with_explicit_no_refactoring_or_ablation_markers"],0)
        self.assertEqual(record["historical_tree_paths_matching_ablation_or_refactoring"],0)
        self.assertEqual(record["original_mpc_executions"],0)
        self.assertEqual(record["model_inference_calls"],0)

if __name__=="__main__":
    unittest.main()
