# Independent original/modified native-control audit — 17 October 2026

**Scope:** Evidence-quality review, not the professor-facing submission report.
**Original run:** [38989067493](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38989067493), exact research commit `b5846f5be000e6f511ed319011549ed4aaa8472c`. Primary PR: [#6](https://github.com/Girish2052003/LUT-PHD-TARGET/pull/6) (draft).

## Why an independent check was necessary

The native pair summary showed a first-candidate acceptance change of 270→271 and a second-candidate change of 266→263. That does **not** measure a correctness benefit or regression caused by the secret-arithmetic finalizer: only two of 626 generated candidate sources were modified, while the four acceptance flips were on unchanged source.

A separate read-only audit parsed all eight GitHub Actions ZIP artifacts (seven categories and one summary) directly, rather than trusting the repository's own report. The audit code is `scripts/audit_paired_controls.py`; the output is `research/evidence/2026-10-17/independent-paired-control-audit.json`. It does not execute archive code.

### Reproduction inputs

| Artifact | ID |
|---|---:|
| Combined summary | 12087032937 |
| Array | 12085202183 |
| Loop | 12086621899 |
| Branch | 12086301260 |
| Math | 12087042728 |
| NumPy operations | 12085025605 |
| NumPy universal functions | 12086986769 |
| Syntax | 12084594130 |

Download and provide the eight GitHub Actions ZIPs to the script (summary first, seven split files in arbitrary order). Its result is derived from the ZIPs; it refuses missing, duplicated or mismatched native data.

## Independently verified observations

- Exactly **313 task identities**, **626 candidate pairs** and **1,252 executions** across native category counts 43/97/34/38/32/34/35.
- **1,280 raw attempts**, including retries; hashes for candidate source, unmodified proposed source, MPC template, compiled input `.mpc`, stdout and stderr match the case records.
- All per-case JSON records exactly match the combined JSONL (not merely the aggregate counts).
- Baseline native first/second/union: **270/266/290** of 313.
- Modified native first/second/union: **271/263/290**.
- Only `loop_test/count_distinct` candidate 1 and `loop_test/is_ascending` candidate 0 change. Both remain ACCEPT under their original native oracles.

### Four acceptance flips on unchanged code

| Original task, candidate | Baseline | Modified-label rerun | Exact combined MPC / compiler hash |
|---|---|---|---|
| `loop_test/standard_deviation`, 1 | ACCEPT | REJECT | Both identical |
| `math_test/next_perfect_square`, 1 | ACCEPT | REJECT | Both identical |
| `math_test/pi_to_the_x`, 0 | REJECT | ACCEPT | Both identical |
| `math_test/pi_to_the_x`, 1 | ACCEPT | REJECT | Both identical |

All four programs compiled successfully. The final stdout success marker appears only for the accepting execution; raw input MPC and compiler hash are identical across each pair. **All four accepted outcomes occurred on execution-order 1, while all four rejected outcomes occurred on execution-order 0; this holds regardless of the baseline/modified label.** This is an order-associated observation, not proof of warm-up effects or any particular root cause. The original oracle criteria are sensitive to approximate arithmetic in some cases, but the specific cause of each flip is **not proven**. Do not assert a numerical or cryptographic mechanism without controlled repeated-run evidence.

A single native evaluation can report a different acceptance marker even for unchanged code. Neither the apparent +1 first-candidate gain nor -3 second-candidate loss is attributable to the finalizer. The 290→290 task-union result is an observed outcome, **not proof of semantic equivalence**.

## Targeted privacy observation remains separate

The accepted smoke run [38958484872](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38958484872) shows 50 observed intermediate-opening events reduced to zero across targeted private-input probes, with expected authorized results preserved in those tests. Compiler opens, triples, communication and time are separate performance measurements. For `count_distinct`, opens 191→98, triples 2917→3010 and global communication 390.364→429.331 MB in one run. No speed, universal confidentiality or general numerical improvement is claimed.

## Limitations and follow-up acceptance gates

1. This verifies **artifact consistency and the confounding unchanged-source outcome variability**, not original-sample historical regeneration, model repair stage execution, formal confidentiality, or independently re-running all MASCOT programs.
2. The four unchanged-source flips all favor the second execution, so any causal claim requires independently controlled, repeated same-source MASCOT trials with randomized order, alongside numerical-oracle values, RNG inputs and runtime configuration. Do not weaken original test thresholds.
3. Finish seven-category original-source methodology traces, available ablations, oracle inventory, interpretation of the paired failure matrix and source-linked limitations.
4. Have the primary research team reconcile `research/progress.json`, `HANDOFF.md` and the requirement ledger; this audit is offered as a review checkpoint, **not an automatic phase-status change**.
5. Maintain PR #6 as draft until broader verification and user authorization. Do not begin final report writing.

All inputs remain traceable to GitHub's pinned workflow artifacts; archival retention and rerun instructions should stay with the primary handoff.


## Independent cross-run original replay comparison

This section compares the separately accepted original-only 626 SPDZCoder candidate replays in [run 38703569637](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38703569637) with the 626 baseline-label executions in [paired run 38989067493](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38989067493). Task/candidate joins used exact case-sensitive identifier ordering and retained both failed and accepted cases. The earlier original-only acceptance count was 533/626 (268 first + 265 second); the later paired original-label count was 536/626 (270 + 266).

**Three candidate decisions differ between the two independently executed original baselines:**

| Authentic candidate | Earlier original-only replay | Paired original baseline |
|---|---|---|
| `loop_test/choppy_array` candidate 0 | REJECT | ACCEPT |
| `math_test/pi_to_the_x` candidate 1 | REJECT | ACCEPT |
| `math_test/spring_rocket` candidate 0 | REJECT | ACCEPT |

A separate comparison of the earlier original-only replay with the paired **modified-label** outputs has five differences: the common `choppy_array` and `spring_rocket` changes, plus `standard_deviation` candidate 1 (ACCEPT→REJECT), `next_perfect_square` candidate 1 (ACCEPT→REJECT), and `pi_to_the_x` candidate 0 (REJECT→ACCEPT). These additional three are **unchanged-source controls**, not caused by the postprocessor. The two actually changed candidates remain ACCEPT in the full paired run.

This is independent cross-run original-evaluator acceptance evidence, not evidence of new model generation or true correctness improvement. Do not collapse it into a single deterministic pass@k claim. Source hashes for the paired dataset are checked by the raw artifact verifier; historical original-only candidate identity was validated in its accepted replay evidence.

A targeted follow-up to test the repeatability hypothesis is [workflow `unchanged-control-repeats.yml`](../../.github/workflows/unchanged-control-repeats.yml), launched at commit `dd46d91d3f668a120e0c6cfaeb629b3e94cf6a60`: four unchanged authentic candidate identifiers, four isolated original-only MASCOT runs each, no replacement oracle or extra model calls. Its results must be independently checked before attributing a cause.
