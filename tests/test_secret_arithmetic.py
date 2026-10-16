import ast
import unittest

from research.modifications.secret_arithmetic import preserve_secret_arithmetic


class SecretArithmeticTests(unittest.TestCase):
    def rewrite(self, body):
        # Locally authored syntax fixtures; no downloaded candidate is executed.
        source = 'def example(arr, x):\n' + ''.join('    ' + line + '\n' for line in body.splitlines())
        return source, preserve_secret_arithmetic(source, 'example')

    def test_comparison_opening_in_secret_product_is_removed(self):
        source, (changed, events) = self.rewrite('acc = sint(1)\nfor i in range(len(arr)):\n    acc *= (arr[i] != x).reveal()\nreturn acc')
        self.assertEqual(len(events), 1)
        self.assertNotIn('.reveal()', changed)
        self.assertIn('acc *= arr[i] != x', changed)
        self.assertEqual(events[0]['rule'], 'secret_product')

    def test_comparison_alias_inside_one_minus_mask_is_removed(self):
        _, (changed, events) = self.rewrite('acc = sint(1)\nfor i in range(len(arr)):\n    bit = arr[i] >= x\n    acc = acc * (1 - bit.reveal())\nreturn acc')
        self.assertEqual(len(events), 1)
        self.assertNotIn('.reveal()', changed)

    def test_mixed_comparison_rewrite_is_deferred_without_type_and_range_proof(self):
        source, result = self.rewrite('best = sint(2**31 - 1)\nret = sint(-1)\nfor i in range(len(arr)):\n    eligible = arr[i] <= x\n    nearer = (x - arr[i]).reveal() < best.reveal()\n    choose = eligible * nearer\n    ret = choose.if_else(sint(i), ret)\n    best = choose.if_else(x - arr[i], best)\nreturn ret')
        self.assertEqual(result, (source, []))

    def test_authorized_return_and_public_control_are_unchanged(self):
        bodies = [
            'acc = sint(1)\nreturn acc.reveal()',
            'acc = sint(1)\nfor i in range(x.reveal()):\n    acc *= arr[i]\nreturn acc',
            'acc = sint(1)\nacc *= arr[x.reveal()]\nreturn acc',
            'acc = sint(1)\nacc *= helper(x.reveal())\nreturn acc',
            'best = sint(100)\nnearer = x.reveal() < best.reveal()\nif nearer:\n    return x\nreturn best',
        ]
        for body in bodies:
            with self.subTest(body=body):
                source, (changed, events) = self.rewrite(body)
                self.assertEqual(changed, source)
                self.assertEqual(events, [])

    def test_malformed_or_ambiguous_source_is_unchanged(self):
        for source in ('def broken(:', 'def example(x):\n    return x\ndef example(x):\n    return 0\n'):
            self.assertEqual(preserve_secret_arithmetic(source, 'example'), (source, []))

    def test_candidate_without_supported_rewrite_is_byte_identical(self):
        source = '# preserve comments and formatting\ndef example(arr):\n  return arr[0]\n'
        self.assertEqual(preserve_secret_arithmetic(source, 'example'), (source, []))

    def test_shadowed_constructor_and_reassigned_comparison_are_unchanged(self):
        for body in (
            'sint = arbitrary\nacc = sint(1)\nacc *= (arr[0] != x).reveal()\nreturn acc',
            'acc = sint(1)\nbit = arr[0] != x\nbit = arbitrary\nacc *= bit.reveal()\nreturn acc',
        ):
            source, (changed, events) = self.rewrite(body)
            self.assertEqual((changed, events), (source, []))

    def test_arithmetic_zero_simplification_cannot_reuse_secret_fact(self):
        # MP-SPDZ _number.__mul__ returns Python zero for multiplication by zero.
        source, result = self.rewrite('acc = sint(1)\nacc *= 0\nacc += 1\nacc *= (arr[0] != x).reveal()\nreturn acc')
        self.assertEqual(result, (source, []))

    def test_all_store_forms_invalidate_secret_accumulator_assumption(self):
        for assignment in ('acc = other = cint(1)', 'acc, other = cint(1), 0',
                           'acc: object = cint(1)', 'acc = cint(1)'):
            with self.subTest(assignment=assignment):
                source, result = self.rewrite('acc = sint(1)\n' + assignment + '\nacc *= (arr[0] != x).reveal()\nreturn acc')
                self.assertEqual(result, (source, []))

    def test_loop_carried_type_change_and_unsupported_loops_are_unchanged(self):
        for loop in ('for i in range(2):\n    acc *= (arr[0] != x).reveal()\n    acc = cint(1)',
                     'for acc in [cint(1)]:\n    pass\nacc *= (arr[0] != x).reveal()'):
            with self.subTest(loop=loop):
                source, result = self.rewrite('acc = sint(1)\n' + loop + '\nreturn acc')
                self.assertEqual(result, (source, []))

    def test_match_capture_cannot_rebind_an_accumulator(self):
        source, result = self.rewrite('acc = sint(1)\nmatch cint(1):\n    case acc:\n        pass\nacc *= (arr[0] != x).reveal()\nreturn acc')
        self.assertEqual(result, (source, []))

    def test_module_match_capture_cannot_shadow_constructor(self):
        source, _ = self.rewrite('acc = sint(1)\nacc *= (arr[0] != x).reveal()\nreturn acc')
        source = 'match cint:\n    case sint:\n        pass\n' + source
        self.assertEqual(preserve_secret_arithmetic(source, 'example'), (source, []))

    def test_dynamic_calls_and_module_side_effects_are_outside_scope(self):
        for statement in ('unknown(arr)', 'exec("sint = cint")'):
            source, result = self.rewrite(statement + '\nacc = sint(1)\nacc *= (arr[0] != x).reveal()\nreturn acc')
            self.assertEqual(result, (source, []))
        source, _ = self.rewrite('acc = sint(1)\nacc *= (arr[0] != x).reveal()\nreturn acc')
        source = 'mutate_globals()\n' + source
        self.assertEqual(preserve_secret_arithmetic(source, 'example'), (source, []))

