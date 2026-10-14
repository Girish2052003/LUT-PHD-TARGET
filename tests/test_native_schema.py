import unittest
from scripts.audit_original_archive import summary_shape

class NativeSchemaTests(unittest.TestCase):
    def test_shape_shows_lengths_and_keys_not_private_contents(self):
        sample={"task_id": 1, "program": "sint(1)", "cases": [1, 2]}
        shape=summary_shape(sample)
        self.assertEqual(shape["type"], "dict")
        self.assertEqual(shape["members"]["program"], {"type": "str", "length": 7})
        self.assertEqual(shape["members"]["cases"]["length"], 2)

if __name__ == "__main__":
    unittest.main()
