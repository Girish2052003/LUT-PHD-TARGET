# Phase F: independent experiment interpretation and bounded acceptance record

**Technical evidence review — not the final professor-facing report.**

## Evidence provenance

- Authentic, pinned original-system full native paired run: [GitHub Actions #38989067493](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38989067493), commit `b5846f5be000e6f511ed319011549ed4aaa8472c`.
- All **eight** evidence ZIPs (seven raw category archives plus aggregated outcome data) independently audited in `research/reviews/paired-full-independent-control-audit.md`. Original program strings, compiler input, stdout/stderr and source/attempt SHA-256 identities were verified for **1,252 execution records and 1,280 attempts**.
- Accepted D1 original intermediate-opening witness: [run 38742644019](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38742644019), with explicitly stated private-input / authorized-output-only policy.
- E1 original-source finalizer targeted smoke: [run 38958484872](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38958484872), **32 paired cases / 64 executions**. Real transformed candidates and outputs are independently recorded; **50 observed explicit intermediate comparison openings became zero** in selected private-input probes.
- Independent original-only repeated MASCOT evidence: [run 39043579023](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39043579023), four identical authentic candidates × four runs each. `math_test/next_perfect_square` c1 had **ACCEPT on 3/4 and REJECT on 1/4** with unchanged compilation fingerprint.

## Explicit measured benchmark estimand

Let (t) denote an original published task, (c\in\{0,1\}) its **historically saved** candidate index and (v\in\{B,M\}) the original baseline or proposed original-source finalizer. (Y(t,c,v)) is the outcome of the **unchanged authors' MASCOT evaluator**, not the proposition of semantic correctness for all possible inputs. Outcomes are reproduced on all 626 candidate pairs with the same native templates and pinned evaluator.

Only **two** original candidate source texts actually change:
`loop_test/count_distinct` candidate 1 and `loop_test/is_ascending` candidate 0. Both remain **ACCEPT→ACCEPT**. All other **624** candidates are source-identical controls. There were **four** acceptance flips among these unchanged controls; all four had the same source, combined MPC program and compiler fingerprint, yet outcomes varied between executions. The 16-trial original-only follow-up independently demonstrates original-native run-to-run acceptance variability for at least one unchanged candidate. It does **not** identify a universal mechanism or justify post-hoc filtering.

### Full 313-task summary (native author evaluator)

| Metric | Baseline (B) | Modified (M) |
|---|---:|---:|
| First candidate accepted | 270/313 | 271/313 |
| Second candidate accepted | 266/313 | 263/313 |
| At least one accepted for task | 290/313 | 290/313 |
| Compile failures | 75/626 | 75/626 |
| Source texts truly modified | N/A | **2/626** |

The **+1 first-candidate and −3 second-candidate differences are not attributable to the source finalizer**, because every acceptance change occurs on unchanged-source controls. The union count is unchanged in this run but does **not** prove general equivalence. Do **not** assign a statistically significant quality improvement or regression to the patch on these aggregate rates. Source-unchanged control variability is recorded, not erased.

## Precisely bounded privacy-related estimand

Under the explicitly stated D1 policy, input *length/type* and the final returned count/bit are public; individual values and intermediate comparison bits are private. A successful witness consists of two private inputs with identical permitted outputs but distinguishable **explicit public intermediate comparison openings** in the original candidate. This is a concrete *output-only declassification* counterexample for that candidate, not a proven historical deployment exploit. The E1 instrumentation observes whether the specific program-level intermediate `.reveal()` values appear; it does not observe/forbid internal cryptographic protocol openings.

The corrected source finalizer changes only a supported comparison-bit product in a strongly constrained secret-`sint` accumulator; it is not a general semantic transformation of arbitrary expressions. In targeted private-input probes it retains independently computed authorized outputs and eliminates the **50 observed explicit candidate-level opening events**. The mixed opened-operand `lower_bound` witness and unsupported value/control patterns are deliberately **unchanged**.

A conditional algebraic rationale explains the narrow operation: for supported 0/1 secret bits (b_i) and valid secret-integer multiplication, replacing the public opening `b_i.reveal()` with (b_i) in a secret-product accumulator preserves the mathematical product value, assuming compatible MP-SPDZ value/type behavior. The source review explicitly rejects unsupported cases where Python zero folding, rebindings, nonlinear casts, overflow, custom operators or other type semantics invalidate this premise. Therefore this is **not a formal noninterference theorem for all programs**, nor a cryptographic proof that all leakage is removed.

## Reproducibly measured computational tradeoffs (single runs)

| Authentic changed candidate | Compiler opens, B→M | Multiplication triples, B→M | Global communication B→M | Runtime B→M |
|---|---|---|---|---|
| count_distinct c1 | 191→98 | 2917→3010 | 390.364→429.331 MB | 18.6831→20.6538 s |
| is_ascending c0 | 35→18 | 2042→2059 | 195.163→195.164 MB | 8.822→8.86707 s |

The compiler-reported opens are protocol/compiler operations; they are not the same event count as explicit candidate-level `.reveal()` instrumentation. The extra secret multiplications and increased communication must be disclosed; isolated runtime measures do not establish an expected performance distribution or speed advantage.

## Preconditions for honest Phase F status

**Technical results accepted within experimental scope:** all 626 source-paired native inputs and outputs, two actual code transformations, unchanged-source negative controls, E1 targeted explicit-opening removal with authorized-output preservation, measured costs and native evaluator instability.

**Broader Phase F/R7 closure still subject to governance:** final independent review of exact source-version equivalence and CI evidence, updated original-workflow ledger/dependencies and PR review/merge sequence; source-to-paper Phase A, remaining Phase C oracle/ablation inventory and Phase G evidence acceptance cannot be treated as complete simply because this results review exists. The historical LLM source is unavailable without separately authorized credentials; no hidden model stage was performed. No user authorization to draft the final report exists.

**Scientific conclusion:** the substantive improvement evidenced by this modification is **elimination of specific observable intermediate comparison openings on two authentic supported original translations while preserving tested final outputs**; it is *not* demonstrated general benchmark correctness improvement, zero total cryptographic opens, comprehensive source confidentiality, or proof of all-program equivalence.
