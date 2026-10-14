import json
import tempfile
import unittest
from pathlib import Path

from spdz_audit.experiment import run, load_tasks


class ExperimentTests(unittest.TestCase):
    def test_records_actual_exception_and_paired_fix(self):
        task = {'id': 'sqrt', 'family': 'sqrt', 'source': 'def f(x):\n    return math.sqrt(x) if x >= 0 else math.sqrt(-x)\n', 'boundaries': [-4, 0, 4]}
        with tempfile.TemporaryDirectory() as d:
            result = run([task], Path(d), seeds=[17], random_count=0)
            self.assertEqual(result['inputs'], 3)
            self.assertEqual(result['modes']['baseline']['passed_inputs'], 1)
            self.assertEqual(result['modes']['safe']['passed_inputs'], 3)
            rows = [json.loads(x) for x in (Path(d)/'observations.jsonl').read_text().splitlines()]
            self.assertEqual(len(rows), 6)
            self.assertEqual(rows[0]['status'], 'exception')
            self.assertEqual(rows[0]['exception_type'], 'ValueError')
            self.assertEqual(result['paired_tasks']['improved'], 1)

    def test_original_failure_invalidates_experiment(self):
        task = {'id': 'invalid', 'family': 'log', 'source': 'def f(x):\n    return math.log(x)\n', 'boundaries': [0]}
        with tempfile.TemporaryDirectory() as d, self.assertRaises(ValueError):
            run([task], Path(d), seeds=[17], random_count=0)

    def test_unknown_or_duplicate_ids_are_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'benchmark.json'
            task = {'id': '../bad', 'family': 'sqrt', 'source': 'def f(x):\n    return x\n', 'boundaries': [0]}
            path.write_text(json.dumps({'tasks': [task]}))
            with self.assertRaises(ValueError):
                load_tasks(path)
            task['id'] = 'fine'
            path.write_text(json.dumps({'tasks': [task, task]}))
            with self.assertRaises(ValueError):
                load_tasks(path)


if __name__ == '__main__':
    unittest.main()
