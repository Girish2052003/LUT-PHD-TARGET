import unittest
from scripts.audit_original_privacy_indicators import screen

class PrivacyIndicatorTests(unittest.TestCase):
    def test_potential_disclosure_is_indicator_only(self):
        result = screen("def f(x):\n    print_ln('%s', x.reveal())\n    return 0\n")
        self.assertTrue(result["parse_ok"])
        self.assertEqual(result["flags"]["reveal_call"], 1)
        self.assertEqual(result["flags"]["public_output_call"], 1)

    def test_authorized_or_incomplete_code_not_called_a_leak(self):
        self.assertEqual(screen("def f(x):\n    return x + 1")["flags"], {})
        failed = screen("def f(")
        self.assertFalse(failed["parse_ok"])
        self.assertEqual(failed["flags"], {})

if __name__ == "__main__":
    unittest.main()
