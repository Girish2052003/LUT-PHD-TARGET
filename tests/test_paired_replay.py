import copy
import json
import re
import unittest

from scripts.replay_modified import expected_openings, validate_pairs
from scripts.verify_paired_replay import check_observations


class PairedReplayTests(unittest.TestCase):
    def fixture(self):
        spec = {'pair_id': 'private-example', 'task_id': 'loop_test/count_distinct',
                'candidate_id': 1, 'kind': 'private_observed', 'inputs': [1, 1, 2],
                'expected_output': 2, 'expected_baseline_openings': [[0, 0.0], [0, 1.0], [0, 1.0]]}
        records = [{'pair_id': spec['pair_id'], 'variant': v, 'compile_status': 'PASS',
                    'runtime_status': 'PASS', 'exception': None, 'authorized_outputs': ['2'],
                    'public_openings': spec['expected_baseline_openings'] if v == 'baseline' else [],
                    'oracle_status': 'REJECT', 'template_sha256': 't', 'inputs_sha256': 'i',
                    'original_source_sha256': 's'} for v in ('baseline', 'modified')]
        return [spec], records

    def test_private_comparison_demands_outputs_and_removed_openings(self):
        specs, records = self.fixture()
        self.assertTrue(validate_pairs(records, specs)['confirmed'])
        for key, value in [('authorized_outputs', ['3']), ('public_openings', [[0, 1]]),
                           ('runtime_status', 'FAIL'), ('inputs_sha256', 'different')]:
            changed = copy.deepcopy(records)
            changed[1][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_pairs(changed, specs)

    def test_pair_completeness_and_baseline_trace_are_checked(self):
        specs, records = self.fixture()
        for changed in (records[:1], records + records[:1]):
            with self.assertRaises(ValueError):
                validate_pairs(changed, specs)
        records[0]['public_openings'][0][1] = 1.0
        # The specification is independent of the recorded observations.
        specs, _ = self.fixture()
        with self.assertRaises(ValueError):
            validate_pairs(records, specs)

    def test_opening_predictions_follow_the_authentic_loop_order(self):
        self.assertEqual(expected_openings('count_distinct', [1, 2, 2]), [[0, 1.0], [0, 1.0], [0, 0.0]])
        self.assertEqual(expected_openings('is_ascending', [1, 2, 2]), [[0, 0.0], [0, 1.0]])
        self.assertEqual(expected_openings('count_distinct', []), [])

    def test_raw_observations_survive_json_round_trip_and_reject_tampering(self):
        stdout = 'OPEN[0]=0\nOPEN[0]=1\nAUTHORIZED=2\n'
        original = {'authorized_outputs': re.findall(r'^AUTHORIZED=([^\n]+)$', stdout, re.M),
                    'public_openings': re.findall(r'^OPEN\[(\d+)\]=([^\n]+)$', stdout, re.M)}
        restored = json.loads(json.dumps(original))
        check_observations(restored, stdout)
        restored['public_openings'][0][1] = '1'
        with self.assertRaisesRegex(ValueError, 'observations'):
            check_observations(restored, stdout)
