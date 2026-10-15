import ast
import unittest

from scripts.probe_original_limitations import observe_original_reveals, privacy_template
from scripts.probe_original_limitations import validate_diagnostics


class ObservationTests(unittest.TestCase):
    def test_observer_preserves_value_and_does_not_add_openings(self):
        # This is our small local fixture, never downloaded/generated author code.
        source = 'def example(x):\n    return x.reveal() + x.reveal()\n'
        observed, sites = observe_original_reveals(source)
        class SecretFixture:
            def __init__(self): self.opens = 0
            def reveal(self):
                self.opens += 1
                return 19
        events = []
        namespace = {'print_ln': lambda *args: events.append(args)}
        exec(compile(observed, '<local synthetic observation fixture>', 'exec'), namespace)
        value = SecretFixture()
        self.assertEqual(namespace['example'](value), 38)
        self.assertEqual(value.opens, 2)
        self.assertEqual(len(sites), 2)
        self.assertEqual(len(events), 2)
        self.assertEqual([e[-1] for e in events], [19, 19])
        calls = [n for n in ast.walk(ast.parse(observed)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'reveal']
        self.assertEqual(len(calls), 2)

    def test_private_inputs_are_not_embedded_in_diagnostic_source(self):
        source = privacy_template('count_distinct', 3)
        self.assertIn('sfix.get_input_from(0)', source)
        self.assertNotIn('[1, 1, 2]', source)
        self.assertEqual(source.count('answer.reveal()'), 1)
        self.assertNotIn('Pass the test', source)

    def test_diagnostic_gate_rejects_runtime_success_without_witness_evidence(self):
        records = [{'case_id': str(i), 'runtime_status': 'PASS',
                    'template_kind': 'diagnostic', 'task_id': 'fake'} for i in range(16)]
        with self.assertRaisesRegex(ValueError, 'hypothesis'):
            validate_diagnostics(records)
