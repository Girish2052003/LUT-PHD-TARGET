"""Scope and published-release provenance guard for new historical-source audit."""
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"research/evidence/2026-10-19/zenodo-version-remote-publisher-audit.json"

class PublisherReleaseRecoveryEvidenceTests(unittest.TestCase):
    def test_versions_are_explicitly_only_known_published_files(self):
        j=json.loads(PATH.read_text())
        self.assertEqual([v["record_id"] for v in j["publisher_versions"]],[17974883,18152253])
        self.assertEqual([f["name"] for f in j["publisher_versions"][0]["files"]],["README.md"])
        self.assertEqual([f["name"] for f in j["publisher_versions"][1]["files"]],["SPDZCoder.tar","README.md"])
        self.assertTrue(j["readme_bytes"]["v1_matches_embedded_v2_tar_root_readme"])
        self.assertFalse(j["readme_bytes"]["v2_separate_matches_v2_tar_root_readme"])

    def test_public_repo_404_is_not_claimed_to_prove_historical_nonexistence(self):
        j=json.loads(PATH.read_text())
        self.assertEqual(j["author_embedded_git_config"]["remote"],"xndong/Spdzcoder")
        self.assertEqual(j["author_embedded_git_config"]["remote_public_http_status"],404)
        self.assertIn("does NOT determine",j["author_embedded_git_config"]["explanation"])
        self.assertTrue(j["historical_llm_generation_not_reproduced"])
        self.assertTrue(j["genuine_spdzcoder_no_refactoring_ablation_not_reproduced"])
        self.assertFalse(j["main_scientific_status_at_review"]["report_authorized"])
        self.assertEqual(j["original_model_api_calls"],0)
        self.assertEqual(j["native_original_mpc_executions_in_this_audit"],0)

if __name__=="__main__":
    unittest.main()
