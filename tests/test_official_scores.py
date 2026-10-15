import unittest
from scripts.reproduce_official_scores import parse_results, measure, validate_task_ids

class OriginalScoreParserTests(unittest.TestCase):
    def test_machine_readable_rows(self):
        text = "a, True, False\nb, False, True\nc, False, False\n" + (
            "\n" + "*" * 40 + "\n\na                  True False\n# of first generation correct : 1\n")
        rows = parse_results(text, 3)
        got = measure(rows)
        self.assertEqual(got["first_correct"], 1)
        self.assertEqual(got["second_correct"], 1)
        self.assertEqual(got["at_least_one_correct"], 2)

    def test_rejects_missing_and_duplicate_tasks(self):
        with self.assertRaises(ValueError):
            parse_results("a, True, False\n", 2)
        with self.assertRaises(ValueError):
            parse_results("a, True, False\na, False, True\n", 2)

    def test_exact_task_identity_and_order_are_required(self):
        native = {"a", "b"}
        good = {"processed": ["a", "b"], "generated": ["a", "b"],
                "baseline": ["a", "b"], "outcomes": ["a", "b"]}
        validate_task_ids(native, good)
        for bad in (["a", "invented"], ["b", "a"], ["a", "a"], ["a"]):
            groups = dict(good, outcomes=bad)
            with self.assertRaises(ValueError):
                validate_task_ids(native, groups)

    def test_malformed_outcome_row_is_not_silently_dropped(self):
        for malformed in ("bad, Maybe, False", "bad True False", "unexpected header"):
            with self.assertRaises(ValueError):
                parse_results(malformed + "\na, True, False\n", 1)

if __name__ == "__main__":
    unittest.main()
