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

    def test_opened_comparison_used_only_by_secret_mask_is_removed(self):
        _, (changed, events) = self.rewrite('best = sint(100)\nret = sint(-1)\nfor i in range(len(arr)):\n    eligible = arr[i] <= x\n    nearer = (x - arr[i]).reveal() < best.reveal()\n    choose = eligible * nearer\n    ret = choose.if_else(sint(i), ret)\n    best = choose.if_else(x - arr[i], best)\nreturn ret')
        self.assertEqual(len(events), 2)
        self.assertTrue(all(e['rule'] == 'secret_selector' for e in events))
        self.assertNotIn('.reveal()', changed)

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

