"""Tests of the disclosed RECONSTRUCTION, not tests of the authors' code."""
import unittest

from spdz_audit.paper_reconstruction import (
    RULES, Attempt, Evaluation, PaperPipeline, PrivacyScreen, ReplayModel,
    extract_code, match_rules, check_refactor_pattern_removed
)


def step(stage, response):
    return {"stage": stage, "response": response}


class PaperPipelineTests(unittest.TestCase):
    def test_table_one_has_ten_distinct_refactoring_rules(self):
        self.assertEqual(len(RULES), 10)
        self.assertEqual(len(set(x[0] for x in RULES)), 10)

    def test_ast_selection_only_relevant_rules(self):
        self.assertEqual(match_rules("def f(x):\n    return x + 1\n"), [])
        src = ("def f(x):\n    if -1 < x < 2:\n"
               "        return x\n    else:\n        return -x\n")
        self.assertEqual(match_rules(src), [
            "NestedIf_MultipleReturn", "ChainedComparison", "ObliviousForm"
        ])
        src2 = ("def f(a):\n    while len(a) > 3:\n"
                "        if a[0] > 2:\n            break\n"
                "        continue\n    return a\n")
        self.assertIn("RewriteWhileLoop", match_rules(src2))
        self.assertIn("EliminateBreak", match_rules(src2))
        self.assertIn("EliminateContinue", match_rules(src2))

    def test_extract_code_fenced_or_plain_and_syntax_failure(self):
        self.assertIn("return x", extract_code("def f(x):\n return x"))
        self.assertIn("return x", extract_code(
            "\x60\x60\x60python\ndef f(x):\n return x\n\x60\x60\x60"))
        with self.assertRaises(SyntaxError):
            extract_code("return ?")

    def test_replay_is_not_a_real_sampling_backend(self):
        replay = ReplayModel([step("generate", "def f(x):\n return x")])
        with self.assertRaises(ValueError):
            replay.complete("reflect", [], 0.7)
        self.assertEqual(len(replay.remaining), 0)

    def test_real_pipeline_sequence_matches_paper_stages(self):
        source = ("def f(x):\n    if x > 0:\n"
                  "        return x\n    else:\n        return -x\n")
        responses = [
            step("refactor:NestedIf_MultipleReturn", source),
            step("refactor:ObliviousForm", source),
            step("generate", "def f(x):\n    return (x > 0).if_else(x, -x)"),
            step("reflect", "def f(x):\n    return (x > 0).if_else(x, -x)")
        ]
        p = PaperPipeline(ReplayModel(responses), lambda code: Evaluation(True))
        result = p.run(source)
        self.assertEqual(result.repairs, 0)
        self.assertTrue(result.result.passed)
        self.assertEqual(result.stages, [
            "refactor:NestedIf_MultipleReturn", "refactor:ObliviousForm",
            "generate", "reflect"
        ])
        self.assertEqual(len(p.events), 4)
        self.assertEqual(p.events[0]["messages"][0]["role"], "system")

    def test_invalid_refactor_signature_fails(self):
        model = ReplayModel([step("refactor:ObliviousForm",
                                  "def changed(x):\n return x\n")])
        source = "def f(x):\n return x if x > 0 else -x\n"
        # SyntaxSugar rule is first for ternary, so use if/else to target.
        source = "def f(x):\n if x > 0:\n  return x\n"
        with self.assertRaisesRegex(ValueError, "signature"):
            PaperPipeline(model, lambda _: Evaluation(True)).run(source)

    def test_fail_closed_on_unremoved_structural_rules(self):
        with self.assertRaisesRegex(ValueError, "EliminateBreak"):
            check_refactor_pattern_removed(
                "EliminateBreak", "def f(x):\n for i in range(2):\n  break\n return x")
        with self.assertRaisesRegex(ValueError, "RewriteWhileLoop"):
            check_refactor_pattern_removed(
                "RewriteWhileLoop", "def f(x):\n while x > 0:\n  x -= 1\n return x")
        check_refactor_pattern_removed(
            "EliminateBreak", "def f(x):\n return x")

    def test_reveal_aliases_and_qualified_print_are_rejected(self):
        gate = PrivacyScreen()
        self.assertIn("explicit-secret-reveal",
            gate.check("def f(x):\n    r = x.reveal\n    r()\n    return x"))
        self.assertIn("unauthorized-output-or-dynamic-call",
            gate.check("def f(x):\n    logger.print_ln('%s', x)\n    return x"))

    def test_privacy_gate_sees_reveals_and_public_secret_branches(self):
        gate = PrivacyScreen()
        self.assertIn("explicit-secret-reveal",
            gate.check("def f(x):\n    x.reveal()\n    return x + 1"))
        self.assertIn("secret-dependent-public-branch",
            gate.check("def f(x):\n    if x > 0:\n        return x\n    return -x"))
        self.assertIn("secret-dependent-loop-bound",
            gate.check("def f(x):\n    for i in range(x):\n        pass\n    return x"))
        self.assertIn("possibly-secret-index",
            gate.check("def f(i, a):\n    return a[i]"))
        self.assertEqual(gate.check(
            "def f(x):\n    return (x > 0).if_else(x, -x)"), [])

    def test_functional_baseline_accepts_hidden_reveal_extension_repairs(self):
        source = "def f(x):\n    return x + 1\n"
        insecure = "def f(x):\n    unused = x.reveal()\n    return x + 1\n"
        secure = "def f(x):\n    return x + 1\n"
        # The evaluator is an intentionally functional-only fixture: it does
        # not claim to run MP-SPDZ and deliberately does not test leakage.
        checker = lambda _: Evaluation(True)
        baseline = PaperPipeline(ReplayModel([
            step("generate", insecure), step("reflect", insecure)
        ]), checker, privacy_extension=False).run(source)
        modified = PaperPipeline(ReplayModel([
            step("generate", insecure), step("reflect", insecure),
            step("repair:1", secure)
        ]), checker, privacy_extension=True).run(source)
        self.assertTrue(baseline.result.passed)
        self.assertIn("reveal", baseline.final)
        self.assertTrue(modified.result.passed)
        self.assertNotIn("reveal", modified.final)
        self.assertEqual(modified.repairs, 1)

    def test_feedback_is_bounded_and_failure_preserved(self):
        source = "def f(x):\n    return x\n"
        wrong = "def f(x):\n    return -x\n"
        model = ReplayModel([step("generate", wrong), step("reflect", wrong),
                             step("repair:1", wrong), step("repair:2", wrong)])
        p = PaperPipeline(model, lambda _: Evaluation(
            False, "functionality", "mismatch"), max_feedback=2)
        outcome = p.run(source)
        self.assertFalse(outcome.result.passed)
        self.assertEqual(outcome.repairs, 2)
        self.assertEqual(len(p.events), 4)

    def test_compilation_feedback_reaches_repair_message(self):
        source = "def f(x):\n return x\n"
        initial = "def f(x):\n return unavailable_fn(x)"
        repaired = "def f(x):\n return x"
        model = ReplayModel([step("generate", initial), step("reflect", initial),
                             step("repair:1", repaired)])
        def evaluator(code):
            return Evaluation(not ("unavailable" in code), "compile_runtime",
                              "unknown compiler symbol")
        p = PaperPipeline(model, evaluator)
        result = p.run(source)
        self.assertTrue(result.result.passed)
        self.assertIn("unknown compiler symbol", p.events[-1]["messages"][1]["content"])

    def test_temperature_and_feedback_input_validation(self):
        model = ReplayModel([])
        for bad in (-1, 1.4):
            with self.assertRaises(ValueError):
                PaperPipeline(model, lambda _: Evaluation(True), max_feedback=bad if bad == -1 else 3,
                              temperature=0.7 if bad == -1 else 3)


if __name__ == "__main__":
    unittest.main()
