# Accepted authentic stage-2 original-MASCOT seven-category smoke

**Date:** 18 October 2026. Research evidence only, **not the final submission report**.

- Original experimental GitHub Actions run: https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39075137852
- Tested commit: `53f1f2733df010db90c13cafde7b5b2bbaa9277f`
- Raw GitHub artifact: `12116746822`, SHA-256 `6f2f6b563cb0fb6ade2eec1799dbf90a5d31b419c9be940d36209c1c6175f36b`, 134 evidence files
- Source archive: the original authors' Zenodo tar, SHA-256 `a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac`
- Source comparison: accepted historical saved stage2 snapshot artifact `12116316330`

## Independent raw audit

Using a separate read-only ZIP parser rather than the project's own stage2 verifier, I inspected the seven original task identities, native templates, 14 candidate SHA-256 values, 313-entry stage2 source ledger, installed dependency/OS packages, original evaluator SHA-256, 2-party original MASCOT runtime settings, per-attempt input MPC, stdout/stderr SHA-256 values and native author acceptance semantics. All fourteen **exact saved stage2 candidate source texts** appear in the executable MPC input file; no stage3 code or reconstructed sample substitutes for them. All seven Docker runs share the same pinned environment and source identity. There were no unresolved harness exceptions or duplicate/missing native records.

| Original task | Candidate 0 | Candidate 1 |
|---|---|---|
| array_test/reverse_and_concat | REJECT | ACCEPT |
| loop_test/max_adjacent_product | ACCEPT | REJECT |
| branch_test/sin_or_cos | ACCEPT | ACCEPT |
| math_test/sigmoid | ACCEPT | REJECT |
| numpy_operation_test/array_from_intrinsic_linspace | ACCEPT | ACCEPT |
| numpy_ufunc_test/logsumexp | REJECT | REJECT |
| syntax_test/second_largest | REJECT | REJECT |

**Observed native totals:** 14 original candidate executions, 14 recorded attempts, 7 ACCEPT and 7 REJECT; compiler PASS 8 and FAIL 6; MPC runtime PASS 8 and NOT_RUN 6. All 14 evaluations match the authors' saved stage2 Boolean flags for these selected tasks. Failed compilation or original REJECT is valid baseline data, not excluded from the denominator.

The evaluation stage is *fresh* only in the sense that the **historically saved code** was compiled and/or executed anew in the original MASCOT evaluator. There were **zero live LLM calls**. This does not freshly execute the authors' refactoring, generation, self-reflection or repair stages; those historical model stages remain unavailable without separately authorized model access. The author evaluator retains its weak stdout marker acceptance and published native test limitations.

## Narrow evidence acceptance and next run

Accept the **seven-category original stage2 14-candidate smoke** and its independent raw-source checks. This does **not** accept the full 626-candidate score reproduction, numerical equivalence, semantic correctness or a causal no-repair ablation. Full original stage2 evaluation remains a separate exact-denominator gate. Original-stage3 data and privacy modification evidence remain separately accepted within their scopes.

Proceed with the reviewed 626-candidate stage2 full run only after this receipt, maintaining the same pinned stage2 replayer, pre-registered protocol, fail-closed verification, all-candidate denominator and authentic author oracle. The full result must be independently audited before any Phase C/R3 promotion. Do not merge any PR or start writing the professor-facing report prematurely.
