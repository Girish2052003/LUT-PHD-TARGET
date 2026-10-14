# Reproduction and extension of SPDZCoder — interim assignment report

**Author:** Girish Nallan Chakravathy  
**Assignment deadline:** 31 October 2026  
**Status as of:** 14 October 2026 — partial, independently validated extension; **not** a full reproduction.  
**Paper:** Dong et al., arXiv:2501.00363v2 (21 March 2025).

## 1. Original method and reproduced scope

SPDZCoder translates Python into privacy-preserving MP-SPDZ code by (a) expert-guided refactoring to Canonical Form Python, (b) LLM generation with dynamically selected examples and self-reflection, and (c) optional compiler/runtime/logic-error feedback. The paper evaluates 313 SPDZEval tasks across array, loop, branch, math, NumPy, and syntax splits. Its declared configuration is GPT-4-turbo-2024-04-09, temperature 0.7, two samples per function, and up to three repair rounds.

The published overall result is **85.94% pass@1; 92.01% pass@2** (paper Table 4). **We have not reproduced those figures.** Original source, original SPDZEval test files and runnable implementation were not supplied in the user's originally empty target repository; repeated public/author-repository searches have not identified a verifiable source download. This absence from discovery is not proof the artifacts do not exist. No LLM calls have been made.

## 2. Concrete limitation and hypothesis

Section 2.2 of the paper demonstrates oblivious selection by evaluating both sqrt(x) and sqrt(-x), then multiplying their outputs by secret-valued condition bits. Eager evaluation can give an inactive branch an invalid argument. This violates the ordinary Python function's semantics even if the final weighted sum is intended to select only one branch. In real MP-SPDZ, the symptom may be bad fixed-point values rather than a host-language exception. We **do not claim** that the actual SPDZCoder authors' unpublished implementation uses this unguarded pattern everywhere.

**Hypothesis:** With identical branch-selection logic, a branch-activation mask applied to inputs of partial functions will reduce invalid-domain failures without altering the active-branch result for supported pure scalar functions.

## 3. Independent implementation

We implemented a restricted Python AST lowering tool with two modes: **baseline** (arithmetic predication resembling the paper's example) and **safe** (our improvement). For each branch activation bit m:

    safe_arg = m * argument + (1 - m) * 1
    sqrt(safe_arg), log(safe_arg), or numerator / safe_denominator

For nested branches, activation bits are multiplied; no Python secret-valued conditional or data-dependent index is emitted. **Active invalid operations still fail**, and unsupported syntax is rejected. Finite and representable intermediates remain an explicit precondition. The same restricted frontend emits ordinary Python for the semantic experiment and MP-SPDZ for follow-up compiler checks.

Relevant code: src/spdz_audit/lowering.py, src/spdz_audit/experiment.py, scripts/check_mpspdz.py, experiments/benchmark.json, tests/*.

## 4. Independent measured comparison

**Benchmark:** DomainSafety-24, *not* SPDZEval. Twenty-four disclosed targeted functions covering arithmetic controls, square roots, logarithms, divisions, nested branches and composed operations. Per task: boundary values plus three seeded samples (seeds 17, 29, 43), 100 points per seed from a 1/16-step grid. There are 7,464 paired inputs overall, not 7,464 independent programs. Both variants receive identical inputs and use the original validated Python function as oracle, with 1e-10 absolute and relative comparison tolerances.

| Python semantic metric | Reconstructed eager baseline | Domain-safe modification |
|---|---:|---:|
| Passed inputs / 7,464 | 4,109 | **7,464** |
| Failed inputs (exception) | 3,355 | **0** |
| Passing functions / 24 | 4 | **24** |
| Input accuracy | 55.05% | **100.00%** |

All 20 task-level changes are improvements, and no regressions occurred on this test set. This is a **44.95 percentage-point improvement on a deliberately constructed stress set**, **not** a generalization claim. The original author's LLM baseline and the original 313 tasks were not run. Deterministic accuracy must not be labeled pass@1/pass@2.

**Independent verification:** GitHub Actions run 38488603949 succeeded: 22 unit tests, full rerun of the 24-task benchmark, raw row-pair consistency check, SHA-256 raw-observation provenance check, archived generated sources/observations/summary. URL: https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38488603949

## 5. MP-SPDZ validation and limitations

An additional runner targets real MP-SPDZ at commit 78fe3d8bad4e654276eb3a11a88173195e672f44 (a pinned compatibility version, **not verified as the paper authors' original environment**). It generates *invoked* sfix-typed programs rather than merely compiling unused function definitions, captures compiler logs, and can check numeric output with the official cleartext emulator. Compiler acceptance, cleartext emulator behavior, true multiparty protocol execution, and cryptographic obliviousness are distinct claims.

**Results:** GitHub Actions run [38488848728](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38488848728) compiled four programs in each mode (8/8 successful). A separate run [38489081857](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38489081857) executed those eight programs with secret-typed constants through the **official cleartext emulator**; both reconstructed baseline and modified variant passed **4/4** inputs each at an absolute/relative tolerance of 0.05. Run [38489589290](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38489589290) repeated compilation and cleartext emulation using runtime-supplied inputs via **`sfix.get_input_from(0)`**; both variants again passed **4/4** cases each. The small numerical deviations in evaluated square roots (on the order of `0.00012` for some runs) are within the loose 5% tolerance. **These results do not establish a numerical improvement of the modified lowering in MP-SPDZ**; they reveal a distinction between host Python's invalid-domain exceptions and MP-SPDZ fixed-point behavior. The strengthened [38490443262](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38490443262) run expanded validation to **27 paired cases representing all 24 targeted functions**, checking both embedded secret-typed constant inputs and player-0 runtime inputs. In each input mode, **both variants passed 27/27 numerical comparisons** (absolute and relative tolerances 0.05). This is 54 tested instances per mode type (27 per lowering variant) and 108 execution outcomes in total, not 108 independent functions. In both variants the largest observed absolute differences from the expected values remained small; e.g., in the logged runtime party-input outputs, one modified square root differed by approximately 0.00012. **No fixed-point numerical superiority was established for the new lowering even in this larger targeted emulator sample.** Neither cleartext emulation nor these examples constitute actual secure multiparty execution or a cryptographic proof.

## 6. Reproduction difficulties and future work

1. Original authors' runnable SPDZCoder and the full 313-task SPDZEval test suite were not present in the supplied repository and have not yet been found via reproducible public searches.
2. The paper's exact compiler commit/runtime environment is unspecified; our pin is an independent compatibility target.
3. The paper's original GPT-4-turbo version/model sampling and repair cycles have not been executed, so RQ1–RQ4/pass@k cannot be honestly replicated.
4. DomainSafety-24 deliberately selects domain-sensitive functions; 100% success here does not measure general code generation, arbitrary program privacy, overflowing intermediates, or unseen language constructs.
5. Small MP-SPDZ fixed-point numerical deviations were observed, and the reconstructed eager baseline matched the modified version on all 27 selected official emulator cases in each input mode. A comprehensive accuracy and overhead study, and full secure multiparty execution, remain to be done. For logged evidence consult the CI runs in section 5.

**Conclusion:** A narrow but substantive limitation in the paper's illustrative oblivious-lowering pattern can be mitigated by propagating secret activation masks into partial-operation arguments. The independent controlled Python experiment supports this claim on 24 targeted functions. **The supervisor's requirement to reproduce the original published implementation and key SPDZEval results remains open** until the original artifacts and experiment access are obtained. All measured and published results are deliberately distinguished.
