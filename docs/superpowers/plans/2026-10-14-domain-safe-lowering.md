# Domain-safe oblivious lowering implementation plan

> For agentic workers: use superpowers:executing-plans to implement this plan task by task.

**Goal:** implement and measure domain-safe arithmetic predication while preserving
the boundary between partial reproduction and the unavailable full experiment.

**Architecture:** a restricted AST frontend produces baseline and masked expressions.
Two backends share the transformation. A deterministic experiment runner keeps raw
measurements and generates MP-SPDZ programs for separate compiler verification.

**Tech stack:** Python 3.10+ standard library, MP-SPDZ v0.3.9 compiler; reportlab
only for the optional PDF report.

**Spec:** ../specs/2026-10-14-domain-safe-lowering-design.md

## Global constraints

- No invented author outputs, benchmark records, model samples, or measured scores.
- Fail explicitly on unsupported syntax; no execution of arbitrary uploaded code.
- No API key creation, live LLM calls, or messages to third parties.
- Pin MP-SPDZ at 78fe3d8bad4e654276eb3a11a88173195e672f44.
- Deterministic lowering uses accuracy; pass@k is reserved for independent samples.

## Review focus

1. An active invalid operation must still fail rather than silently be repaired.
2. Nested inactive branches must mask inner partial operations and remain oblivious.
3. Unsupported effectful calls and expression syntax must fail explicitly.
4. Fixed-point compiler acceptance must not be reported as execution correctness.
5. Repeated inputs or deterministic variants must not inflate sample-based metrics.

## Task 1: restricted lowering and regression tests

Files: src/spdz_audit/lowering.py, tests/test_lowering.py.
Interface: lower(source: str, mode: str='safe', backend: str='python') -> str.

- [ ] Write failing tests for sqrt(x)/sqrt(-x), log, reciprocal and nested branches;
      active-domain failures, invalid predicates and rejected arbitrary calls.
- [ ] Run `python -m unittest discover -s tests -v`; confirm missing module failure.
- [ ] Implement AST validation and mask propagation; emit Python and MP-SPDZ code.
- [ ] Run all tests; inspect emitted source and commit.

## Task 2: experiment and metrics

Files: src/spdz_audit/metrics.py, tests/test_metrics.py, experiments/benchmark.json,
scripts/run_experiments.py.
Interfaces: pass_at_k(n: int,c: int,k: int) -> float; run via documented CLI.

- [ ] Test exact metric values and invalid sizes before implementing metrics.
- [ ] Implement explicit, non-executing schema validation and deterministic experiment
      recording; compare against the original function only after AST validation.
- [ ] Run all tests and experiments; retain raw rows, source hashes and summaries.
- [ ] Compare controls and domain-sensitive cases separately; commit results.

## Task 3: compiler integration and report

Files: scripts/check_mpspdz.py, docs/report.md, docs/paper_guide.md,
docs/reproduction_log.md, configs/paper_v2.json, README.md.

- [ ] Verify generated source with the pinned real compiler and save each log.
- [ ] Attempt runtime setup without substituting host simulation for MPC execution.
- [ ] Generate report from measured JSON; label unexecuted requirements explicitly.
- [ ] Fresh-context code/evidence review; fix important findings with regression tests.
- [ ] Run complete verification, commit and push the branch; provide result links.
