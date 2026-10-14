import unittest
from spdz_audit.metrics import pass_at_k, paired_counts


class MetricsTests(unittest.TestCase):
    def test_estimator_matches_hand_calculations(self):
        self.assertAlmostEqual(pass_at_k(5, 2, 2), .7)
        self.assertEqual(pass_at_k(2, 1, 1), .5)
        self.assertEqual(pass_at_k(2, 1, 2), 1)
        self.assertEqual(pass_at_k(2, 0, 2), 0)
        self.assertEqual(pass_at_k(2, 2, 1), 1)

    def test_invalid_sample_sizes_fail(self):
        for values in [(0, 0, 1), (2, 3, 1), (2, -1, 1), (2, 1, 3), (2, 1, 0), (2.0, 1, 1), (True, 1, 1)]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                pass_at_k(*values)

    def test_paired_outcomes_keep_regressions_visible(self):
        result = paired_counts([True, False, True, False], [True, True, False, False])
        self.assertEqual(result, {'both_pass': 1, 'improved': 1, 'regressed': 1, 'both_fail': 1})

    def test_no_silent_truncation_of_unpaired_data(self):
        with self.assertRaises(ValueError):
            paired_counts([True], [True, False])
        with self.assertRaises(ValueError):
            paired_counts([1], [True])


if __name__ == '__main__':
    unittest.main()
