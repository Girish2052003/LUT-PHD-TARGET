import unittest
from scripts.reproduce_official_scores import parse_results, measure

class OriginalScoreParserTests(unittest.TestCase):
    def test_machine_readable_rows(self):
        text = "a, True, False\nb, False, True\nc, False, False\n" + (
            "a                  True False\n# of first generation correct : 1\n")
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

if __name__ == "__main__":
    unittest.main()
