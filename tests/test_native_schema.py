import unittest
from scripts.audit_original_archive import summary_shape, inspection_errors, PAPER_SPLITS

class NativeSchemaTests(unittest.TestCase):
    def test_shape_shows_lengths_and_keys_not_private_contents(self):
        sample={"task_id": 1, "program": "sint(1)", "cases": [1, 2]}
        shape=summary_shape(sample)
        self.assertEqual(shape["type"], "dict")
        self.assertEqual(shape["members"]["program"], {"type": "str", "length": 7})
        self.assertEqual(shape["members"]["cases"]["length"], 2)

    def test_discovery_error_cannot_look_like_completed_inspection(self):
        report = {"raw_mpc_task_count": 313, "raw_mpc_categories": PAPER_SPLITS,
                  "split": {s: {"length": n} for s, n in PAPER_SPLITS.items()},
                  "stage3": {s: {"records": n} for s, n in PAPER_SPLITS.items()},
                  "baseline": {s: {"records": n} for s, n in PAPER_SPLITS.items()}}
        self.assertEqual(inspection_errors(report), [])
        report["split"]["array_test"] = {"error": "bad JSON"}
        self.assertTrue(inspection_errors(report))

if __name__ == "__main__":
    unittest.main()
