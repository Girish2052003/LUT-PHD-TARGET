"""Regression tests use hand-computed answers, not the compiler as an oracle."""
import ast
import math
import unittest

from spdz_audit.lowering import UnsupportedSyntax, lower, original_callable, lowered_callable


ROOT = '''def f(x):
    if x > 0:
        return math.sqrt(x)
    else:
        return math.sqrt(-x)
'''


class LoweringTests(unittest.TestCase):
    def test_paper_example_baseline_exposes_eager_domain_error(self):
        # Removing eager evaluation would make this fail: it characterizes the baseline.
        with self.assertRaises(ValueError):
            lowered_callable(ROOT, mode="baseline")(4)

    def test_sqrt_repair_selects_valid_inactive_argument(self):
        f = lowered_callable(ROOT)
        for x, expected in [(-9, 3), (-4, 2), (0, 0), (4, 2), (9, 3)]:
            with self.subTest(x=x):
                self.assertEqual(f(x), expected)

    def test_log_inactive_zero_and_negative(self):
        source = 'def f(x):\n    if x > 0:\n        return math.log(x)\n    else:\n        return 0\n'
        f = lowered_callable(source)
        self.assertEqual(f(-2), 0)
        self.assertEqual(f(0), 0)
        self.assertAlmostEqual(f(math.e), 1)

    def test_inactive_zero_denominator_is_masked(self):
        source = 'def f(x):\n    if x != 0:\n        return 1 / x\n    else:\n        return 7\n'
        f = lowered_callable(source)
        self.assertEqual(f(0), 7)
        self.assertEqual(f(-2), -.5)

    def test_active_invalid_operation_is_not_silently_fixed(self):
        for expr, error in [('math.sqrt(x)', ValueError), ('math.log(x)', ValueError), ('1 / x', ZeroDivisionError)]:
            source = f'def f(x):\n    if x <= 0:\n        return {expr}\n    else:\n        return 0\n'
            with self.subTest(expr=expr), self.assertRaises(error):
                lowered_callable(source)(0 if '/' in expr else -1)

    def test_nested_inactive_branch_masks_inner_operations(self):
        source = '''def f(x):
    if x > 0:
        if x > 1:
            return math.log(x - 1)
        else:
            return math.sqrt(1 - x)
    else:
        return 1 / (x - 1)
'''
        f = lowered_callable(source)
        for x, expected in [(-1, -.5), (0, -1), (1, 0), (2, 0), (3, math.log(2))]:
            with self.subTest(x=x):
                self.assertAlmostEqual(f(x), expected)

    def test_partial_operation_inside_partial_argument_is_masked_recursively(self):
        source = 'def f(x):\n    if x > 0:\n        return math.log(math.sqrt(x))\n    else:\n        return 3\n'
        self.assertEqual(lowered_callable(source)(-4), 3)
        self.assertAlmostEqual(lowered_callable(source)(4), math.log(2))

    def test_if_expression_is_supported(self):
        self.assertEqual(lowered_callable('def f(x):\n    return 1 / x if x != 0 else 5\n')(0), 5)

    def test_total_controls_and_chained_comparison(self):
        source = 'def f(x):\n    if -2 < x <= 3:\n        return x * x + 1\n    else:\n        return -x\n'
        for x in [-3, -2, 0, 3, 4]:
            self.assertEqual(lowered_callable(source)(x), original_callable(source)(x))

    def test_boolean_predicates_have_boolean_not_operand_semantics(self):
        source = 'def f(x):\n    if (x > 0 and x < 2) or x == -1:\n        return 5\n    else:\n        return 8\n'
        for x in [-2, -1, 0, 1, 2]:
            self.assertEqual(lowered_callable(source)(x), original_callable(source)(x))

    def test_disallows_nonboolean_predicate(self):
        with self.assertRaises(UnsupportedSyntax):
            lower('def f(x):\n    if x:\n        return 1\n    else:\n        return 2\n')

    def test_rejects_partial_predicate(self):
        with self.assertRaises(UnsupportedSyntax):
            lower('def f(x):\n    if 1 / x > 0:\n        return 1\n    else:\n        return 2\n')

    def test_unsupported_language_fails_closed(self):
        sources = [
            'def f(x):\n    return __import__("os")\n',
            'def f(x):\n    return x.reveal()\n',
            'def f(x):\n    return math.sin(x)\n',
            'def f(x):\n    return x[0]\n',
            'def f(x):\n    while x > 0:\n        return x\n',
            'def f(x):\n    if x > 0:\n        return x\n',
            'def f(x=1):\n    return x\n',
            'def f(math):\n    return math\n',
            '@print\ndef f(x):\n    return x\n',
            'def f(x):\n    return True\n',
            'def f(x):\n    return 1e999\n',
            'def f(x):\n    return x ** 2\n',
        ]
        for source in sources:
            with self.subTest(source=source), self.assertRaises(UnsupportedSyntax):
                lower(source)

    def test_generated_body_has_no_secret_control_flow_or_reveal(self):
        for backend in ['python', 'mpspdz']:
            source = lower(ROOT, backend=backend)
            tree = ast.parse(source)
            self.assertFalse(any(isinstance(n, (ast.If, ast.IfExp, ast.While, ast.For, ast.Subscript)) for n in ast.walk(tree)))
            self.assertNotIn('reveal', source)

    def test_backend_and_mode_are_validated(self):
        with self.assertRaises(ValueError):
            lower(ROOT, mode='typo')
        with self.assertRaises(ValueError):
            lower(ROOT, backend='typo')


if __name__ == '__main__':
    unittest.main()
