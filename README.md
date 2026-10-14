# SPDZCoder research assignment — reproducible extension and honest reproduction status

**Researcher:** Girish Nallan Chakravathy.  
**Supervisor's deadline:** **31 October 2026**.  
**Source paper:** Dong et al., *SPDZCoder: Combining Expert Knowledge with LLMs for Generating Privacy-Computing Code*, arXiv:2501.00363v2.

**Scope:** A verified **independent extension** investigating safe evaluation of oblivious branches. **This is not a complete reproduction of the authors' SPDZCoder**, because the original implementation, 313-task SPDZEval and original LLM runs have not been obtained.

## Current measured evidence

| Test | Reconstructed eager-predication baseline | Domain-safe extension | Evidence |
|---|---:|---:|---|
| Targeted Python semantic cases passed | 4,109 / 7,464 | **7,464 / 7,464** | GitHub Actions run 38488603949 |
| Entire 24-function tasks passed | 4 / 24 | **24 / 24** | Same run; independent raw-row validator |
| MP-SPDZ invoked programs compiled at pinned commit | 4 / 4 | **4 / 4** | GitHub Actions run 38488848728 |
| MP-SPDZ emulator (secret-typed constants) | **4 / 4** | **4 / 4** | GitHub Actions run 38489081857; tolerance 5% |
| MP-SPDZ emulator (party-0 runtime input) | **4 / 4** | **4 / 4** | GitHub Actions run 38489589290; `sfix.get_input_from(0)`; tolerance 5% |
| Original published 313 SPDZEval tasks | Not run | Not run | Missing original runnable artifacts |

The 24-function stress suite was **deliberately constructed to expose this specific defect**. These results are NOT an unbiased estimate of how often the bug occurs in real code, and they are NOT pass@k scores.

The paper reports 85.94% pass@1 and 92.01% pass@2, which are **published figures only** in this project.

## Why this extension?

A simple data-oblivious branch such as (x > 0) * sqrt(x) + (x <= 0) * sqrt(-x) calculates both roots. The inactive root can receive a negative input. Our restricted AST lowering propagates a secret activation mask m into the *arguments* of partial operations:

    masked_arg = m * argument + (1 - m) * 1

Thus inactive sqrt/log/division receive safe dummy arguments. Active invalid arguments remain invalid. No secret bit is revealed by the emitted control flow. We make **no claim of full cryptographic security** or support for arbitrary Python.

## Reproduce the deterministic experiment

Requires Python 3.10+ and no paid LLM access:

    python -m pip install -e .
    python -m unittest discover -s tests -v
    python scripts/run_experiments.py --output results/semantic
    python scripts/verify_results.py --results results/semantic

The runner saves its raw JSONL observations, a gzip copy, generated Python and MP-SPDZ source, SHA-256 provenance, input-group summaries and verification result.

For genuine compiler validation, first obtain MP-SPDZ commit 78fe3d8bad4e654276eb3a11a88173195e672f44. Then run:

    python scripts/check_mpspdz.py --mpspdz /path/to/MP-SPDZ --output results/mpspdz --max-cases 4

To run the official **cleartext** emulator, build `emulate.x` in MP-SPDZ, then append `--emulate`. Add `--party-input` to create runtime input files and call `sfix.get_input_from(0)` instead of using literal constants. Both modes passed the tiny four-case emulator sample at a loose 5% tolerance; **no MP-SPDZ numerical improvement has yet been demonstrated**. Cleartext emulation is distinct from actual secure multiparty protocols.

All commands above also run or are configured in .github/workflows/research-verification.yml. Individual CI result artifacts are retained for 30 days.

## Start here

- docs/report.md — interim assignment report, measured results, limitations and code explanation.
- docs/paper_guide.md — explain SPDZCoder from first principles, including the benchmark and the exact model settings.
- docs/reproduction_log.md — pinned environment, evidence ledger and unresolved blockers.
- docs/superpowers/specs/2026-10-14-domain-safe-lowering-design.md — detailed scope and threat model.
- src/spdz_audit/lowering.py — baseline and modified restricted lowering.
- experiments/benchmark.json — all 24 independently authored test functions.
- scripts/check_mpspdz.py — invokes generated secret-typed fixed-point programs through the real compiler and optional emulator.

**Remaining blockers:** original source and full SPDZEval benchmark; actual generated model samples and paper RQ1–RQ4 runs; true secure multiparty network-protocol execution and full MPC security analysis. No invented scores, model outputs, datasets or compiler assurances should be substituted.
