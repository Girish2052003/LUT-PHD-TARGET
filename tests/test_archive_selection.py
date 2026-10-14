import unittest
from scripts.export_official_snapshot import wanted

class ArchiveSelectionTests(unittest.TestCase):
    def test_keep_source_data_and_authors_requirements(self):
        self.assertTrue(wanted("SPDZCoder/src/pipeline-mp.py"))
        self.assertTrue(wanted("SPDZCoder/data/input_data/a.mpc"))
        self.assertTrue(wanted("SPDZCoder/requirement.txt"))

    def test_reject_git_cache_secrets_and_traversal(self):
        for p in ["SPDZCoder/.git/config", "SPDZCoder/src/__pycache__/x.pyc",
                  "SPDZCoder/../secret.py", "SPDZCoder/utility/.env",
                  "SPDZCoder/Player-Data/key", "OTHER/src/pipeline.py"]:
            self.assertFalse(wanted(p), p)

if __name__ == "__main__":
    unittest.main()
