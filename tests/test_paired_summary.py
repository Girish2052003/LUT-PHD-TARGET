import copy
import unittest

from scripts.summarize_paired_replay import aggregate_native, paired_binary


class PairedSummaryTests(unittest.TestCase):
    def fixture(self):
        identity = {'task_records': [{'task_id': 'loop_test/example'}]}
        rows = [{'task_id': 'loop_test/example', 'candidate_id': c, 'kind': 'native',
                 'variant': v, 'compile_status': 'PASS', 'runtime_status': 'PASS',
                 'failure_class': None, 'oracle_status': 'ACCEPT' if (c == 0 or v == 'modified') else 'REJECT',
                 'duration_seconds': 1.0, 'original_source_sha256': 'original',
                 'transformed_source_sha256': 'modified' if c == 1 else 'original', 'rewrite_events': []}
                for c in (0, 1) for v in ('baseline', 'modified')]
        return identity, rows

    def test_both_candidate_denominators_and_task_union_preserved(self):
        identity, rows = self.fixture()
        result, matrix = aggregate_native(rows, identity)
        self.assertEqual(result['variants']['baseline']['overall']['first_accepted'], 1)
        self.assertEqual(result['variants']['baseline']['overall']['second_accepted'], 0)
        self.assertEqual(result['variants']['modified']['overall']['second_accepted'], 1)
        self.assertEqual(result['paired_task_outcomes']['union']['difference_percentage_points'], 0)
        self.assertEqual(result['candidate_transitions']['rejected_to_accepted'], 1)
        self.assertEqual(len(matrix), 2)

    def test_incomplete_duplicate_and_diagnostic_native_data_rejected(self):
        identity, rows = self.fixture()
        bad = copy.deepcopy(rows)
        bad[0]['kind'] = 'private_observed'
        for candidate in (rows[:-1], rows + rows[:1], bad):
            with self.assertRaises(ValueError):
                aggregate_native(candidate, identity)

    def test_exact_discordance_test_and_bootstrap_are_deterministic(self):
        result = paired_binary([False, False], [True, True])
        self.assertEqual(result['mcnemar_exact_two_sided_p'], 0.5)
        self.assertEqual(result['difference_percentage_points'], 100)
        self.assertEqual(result, paired_binary([False, False], [True, True]))
        equal = paired_binary([True, False], [True, False])
        self.assertEqual(equal['mcnemar_exact_two_sided_p'], 1)
        self.assertEqual(equal['bootstrap_95_percentile_pp'], [0, 0])
