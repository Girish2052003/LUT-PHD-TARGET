# Phase G independent second raw audit: complete original-vs-modified pair evidence (18 October 2026)

**Read-only independent re-evaluation; not the final professor-facing report.** Downloaded directly from [native paired original author run #38989067493](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38989067493) all eight source-run ZIP artifacts (seven category archives plus full aggregate), checked their eight complete ZIP SHA-256 hashes, parsed the raw original `paired-records.jsonl`, each category variant's individual `record.json`, complete `failure_matrix.json`, and all corresponding original compiled input/outputs. See machine-readable `research/evidence/2026-10-18/phase-g-paired-secondary-recomputed.json`.

### Checks independently executed

- **313 original task identities**, **626 candidate pairs**, **1,252 baseline/modified native records** and **1,280 raw native attempt objects**. Zero missing or duplicate task/candidate/variant keys.
- **3,840 actual raw native input `.mpc`, stdout and stderr SHA-256 digests checked** against attempt records, and **5,008 source/original/transformed/template file SHA-256 digests checked** against per-variant records.
- **1,252 exact category-record to summary-JSONL matches**; **626 original/modified outcome pairs matched to independent failure matrix**, including compiler/runtime/oracle status and acceptance deltas.
- Recalculated first/second/at-least-one: **baseline 270/266/290**, **modified 271/263/290**, denominator 313. **75 compilation failures in each variant**, no exclusions.
- Exactly **two** original saved candidate source texts differ: `loop_test/count_distinct` candidate 1 and `loop_test/is_ascending` candidate 0; both retain native ACCEPT. **All four** native acceptance flips are in source-identical controls with identical compiled MPC input fingerprints: `loop_test/standard_deviation c1`, `math_test/next_perfect_square c1`, `math_test/pi_to_the_x c0/c1`. Thus the apparent overall accuracy differences cannot be causally attributed to the patch.
- Source-run ZIP digest pins and all exception count categories are recorded in the receipt; raw source-run artifacts remain retrievable during GitHub artifact retention.

### Scope and independent verification boundaries

This new second audit is **direct inspection of previously executed author-original native results**, not a fresh MASCOT run or live historical LLM generation. It agrees with `scripts/audit_paired_controls.py` and `research/reviews/paired-full-independent-control-audit.md`. It does not prove semantic correctness beyond the known weak original oracle, nor a cryptographic noninterference theorem. Supported narrow program-level intermediate opening changes and their extra computation/communication costs remain grounded in the separate original-source private-input smoke.

The result strengthens evidence integrity for previously bounded **Phase F/R7 PASS** without extending the scope, and **does not waive B3, R2/R3/R8, Phase G or REPORT blockers**.
