import json
from pathlib import Path
import tempfile
import unittest

from spdz_audit.spdzeval_import import PAPER_SPLITS, TOTAL, load, validate


def item(identifier="demo", split="math"):
    return dict(id=identifier, split=split,
                python_source="def f(x):\n    return x\n",
                mpspdz_reference="def f(x):\n    return x\n",
                tests=[{"args": [2], "expected": 2}])


class SPDZEvalImporterTests(unittest.TestCase):
    def test_published_six_splits_sum_to_313(self):
        self.assertEqual(TOTAL, 313)
        self.assertEqual(PAPER_SPLITS["loop"], 97)

    def test_reject_empty_313_substitute(self):
        with self.assertRaisesRegex(ValueError, "313"):
            validate([item()], require_complete=True)
        self.assertFalse(validate([item()], require_complete=False)["matches_paper_structure"])

    def test_missing_tests_invalid(self):
        task = item()
        task["tests"] = []
        with self.assertRaisesRegex(ValueError, "without original test"):
            validate([task], require_complete=False)

    def test_no_duplicate_source_ids(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate([item(), item()], require_complete=False)

    def test_provenance_required_even_for_partial_import(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "dataset.json"
            payload = dict(format="SPDZCoder-normalized-import-v1",
                           entries=[item()], provenance={})
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError, "source URL"):
                load(path, require_complete=False)
            payload["provenance"] = {"source_url": "https://example.org/original.zip"}
            path.write_text(json.dumps(payload))
            entries, summary = load(path, require_complete=False)
            self.assertEqual(len(entries), 1)
            self.assertEqual(summary["entry_count"], 1)
            self.assertFalse(summary["matches_paper_structure"])


if __name__ == "__main__":
    unittest.main()
