# Final report evidence guide

Companion to [the brief report](final_report.md), revised 22 October 2026. This guide
keeps reproducibility details outside the five-page report. All counts below are
bounded observations, not proofs of general correctness or confidentiality.

## Scope and immutable evidence snapshot

The report uses research snapshot
`c237aa4a6d98a16b141a9b178a046a121ea1e659` ([browse](https://github.com/Girish2052003/LUT-PHD-TARGET/tree/c237aa4a6d98a16b141a9b178a046a121ea1e659)).
This is the already verified research base; the report package has later commits.
Earlier paper-inspired fixtures and cleartext-emulator results are excluded from
the report's original-system benchmark tables. No model APIs were called for this
report. No native candidates were rerun to prepare it.

| Report claim | Preserved evidence / method |
|---|---|
| Paper stages, configuration and source differences | [Original source audit](../research/original_source_audit.md), [paper guide](paper_guide.md), [paper v2](https://arxiv.org/abs/2501.00363v2) |
| Archived SPDZCoder 269/265/288, stage 2 229/213/261 and GPT-4 API-doc 95/114/156 | Original archive; `scripts/reproduce_official_scores.py`; [stage-2 acceptance](../research/evidence/2026-10-18/stage2-original-full-independent-acceptance.json) |
| Fresh final SPDZCoder 268/265/288 and GPT-4 API-doc 95/112/154 | [Final summary](../research/evidence/2026-10-21/final-readiness/final-native-summary.json), [raw audit](../research/evidence/2026-10-21/final-readiness/raw-audit-acceptance.json) |
| Stage 2: 626 candidates, 644 attempts, 147 compile failures, 445 acceptances, 34 runtime-completed rejections | [Independent stage-2 acceptance](../research/evidence/2026-10-18/stage2-original-full-independent-acceptance.json), [secondary raw audit](../research/evidence/2026-10-18/phase-g-stage2-raw-secondary-independent-audit.json) |
| Distinguishable intermediate-opening traces with equal final outputs | [Diagnostic review](../research/reviews/diagnostic-evidence-review.md), [raw receipt](../research/evidence/2026-10-15/original-diagnostics/receipt.json) |
| 32 targeted pairs, 64 executions, 50 to 0 observed explicit opening events | [Targeted comparison review](../research/reviews/paired-smoke-evidence-review.md), [718-file receipt](../research/evidence/2026-10-16/paired-smoke/receipt.json) |
| 626 full pairs, 2 changed sources, 4 flips on unchanged controls | [Paired summary](../research/evidence/2026-10-21/final-readiness/paired-native-summary.json), [independent raw audit](../research/reviews/paired-full-independent-control-audit.md) |
| Full-paired native costs and bounded interpretation | [Phase F review](../research/reviews/phase-f-bounded-native-interpretation-20261018.md) |
| Reproduction difficulties, failed aggregation and artifact-only recovery | [Difficulty register](../research/reproduction_difficulties.json), [reproduction log](reproduction_log.md) |
| Missing genuine without-refactoring outputs despite recovering all inputs | [Final input receipt](../research/evidence/2026-10-19/no-refactor-input-final-receipt.json), [source/archive search](../research/evidence/2026-10-18/final-attempt-original-no-refactoring-content-audit.json) |

First/second counts refer to saved candidate indices 0/1. Either/union counts a
task once when at least one saved candidate is accepted. They are distinct from
a fresh model sampling experiment. The original evaluator's stdout/stderr rule
is preserved even where it gives a false positive; runtime status is separate.

## Source and environment pins

| Component | Exact identity |
|---|---|
| Author artifact | [Zenodo record 18152253, v2](https://zenodo.org/records/18152253), `SPDZCoder.tar`, 65,761,280 bytes, CC BY 4.0 |
| Author TAR SHA-256 | `a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac` |
| Author TAR published MD5 | `3c6d7707d7aecc051d35312f81405c66` |
| MP-SPDZ compiler/scripts | Version 0.3.6, commit `6cc3fccef0904764364eb8e285519cd34028f325` |
| MP-SPDZ release archive SHA-256 | `e83efcbbe9b295fe276450f3d4aa6e822f35d4bf348c87dee4877b4fed4e5f40` |
| MASCOT binary SHA-256 | `2a592fec9a9f9d0e7e8148bdf9ee7a67811dd6781c333981b386f3d1b7c8a5b3` |
| Original evaluator SHA-256 | `7b999498f06050ab4db54e19097f65cd56c09eb7446384ddca4b62165969f1a2` |
| Python 3.11.9 image digest | `sha256:8fb099199b9f2d70342674bd9dbccd3ed03a258f26bbd1d556822c6dfc60c317` |
| Modification module SHA-256 | `8c93f4687569c7419b573b20b1349b2d67563a39ce50dba16fda38dd197d8aa2` |

Two MASCOT parties ran on one runner. Container limits were two CPUs, 6 GiB RAM
and 256 processes, non-root, read-only and network-disabled during evaluation.
Dependency lists, runner details and compiled-source hashes are retained in raw
artifacts. These choices are disclosed reconstruction choices. They are not the
authors' recovered historical hardware. See [replay protocol](../research/replay/README.md).

## Experiment and workflow identities

| Purpose | Run | Research commit | Interpretation |
|---|---|---|---|
| Full final-stage replay | [38703569637](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38703569637), attempt 2 | `769bb12ce342b814590061ef04fdffbbe19c9990` | 1,252 candidates across SPDZCoder and GPT-4 API-doc; 1,280 attempts |
| Original stage-2 native jobs | [39075744038](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39075744038) | `1e3c95d5357cd8b913a11916e562b6de7d633ccb` | **FAILED workflow**: seven native jobs succeeded; aggregation path was wrong |
| Stage-2 artifact-only recovery | [39080161119](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39080161119) | `58197ee4b93c70a04cc19f4c15a319eba3b4f4d8` | Successful recovery of the same evidence; zero native reruns |
| Original privacy diagnostics | [38742644019](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38742644019) | `aa89eb661370480643a6637180b773d080009437` | 16 native/diagnostic cases; new explicit-policy tests |
| Targeted paired modification | [38958484872](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38958484872) | `35adfb04c1132ae91d1b2c6e21cf791855eab768` | 32 pairs / 64 executions |
| Full native paired modification | [38989067493](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38989067493) | `b5846f5be000e6f511ed319011549ed4aaa8472c` | 626 pairs / 1,252 executions / 1,280 attempts |
| Original-only repeat controls | [39043579023](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39043579023) | See run's immutable `head_sha` and preserved control review | 4 candidates × 4 repetitions; one has 3/4 acceptance |
| Source-only no-refactoring input audit | [39253932391](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39253932391) | `1eadb23c6d74477530a77eae374aee6c49c98ac6` | 313 input/instruction pairs; 307 direct Python parses, 6 preserved NumPy exceptions |
| Verified base main raw-evidence audit | [39541724665](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39541724665) | `c237aa4a6d98a16b141a9b178a046a121ea1e659` | Re-audits 31 artifacts; zero new model/native executions |

The earlier [final-readiness receipt](../research/evidence/2026-10-21/final-readiness/receipt.json)
preserves audit run 39493312330 at its own source commit. Its JSON summaries are
the report's checked-in snapshot. The later main audit above independently
rechecked the same source artifacts; these are distinct audit receipts.

## Exact modification and report snippets

The [original pipeline patch](../research/modifications/original-pipeline.patch)
adds the import and finalizer call to both original entry points. The actual
implementation is [secret_arithmetic.py](../research/modifications/secret_arithmetic.py).
The model-dependent prefixes were not executed. The native comparison exercised
the exact added finalizer assignment on saved candidates.

The original snippets come from
`data/stage_3_output/experiment-1-loop_test.jsonl` in the pinned author TAR.
Original and transformed text copies can be inspected without executing them:

- [count_distinct original](../research/evidence/2026-10-16/paired-smoke/paired-smoke/logs/loop_test--count_distinct--c1--native/baseline/original.py.txt)
  and [transformed](../research/evidence/2026-10-16/paired-smoke/paired-smoke/logs/loop_test--count_distinct--c1--native/modified/transformed.py.txt).
- [is_ascending original](../research/evidence/2026-10-16/paired-smoke/paired-smoke/logs/loop_test--is_ascending--c0--native/baseline/original.py.txt)
  and [transformed](../research/evidence/2026-10-16/paired-smoke/paired-smoke/logs/loop_test--is_ascending--c0--native/modified/transformed.py.txt).

The supported comparison must be a valid 0/1 bit (or its complement), and all
bindings of the product accumulator must retain the supported secret-integer
invariant. All unsupported cases fall back unchanged. `lower_bound` is an
unfixed witness. Internal protocol openings and explicit candidate disclosures
are different measures. No all-program correctness or confidentiality theorem
is claimed.

## Rechecking and reproducing

Run from the repository root with Python 3.10+ for the owned regression suite:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python scripts/check_handoff.py
python scripts/verify_reproduction_difficulty_coverage.py \
  --output results/report-r8-check/acceptance.json
```

The [final evidence audit workflow](../.github/workflows/final-evidence-audit.yml)
uses a GitHub Actions read-only token to retrieve the exact 31 ZIPs listed in
[`research/final_audit_artifacts.json`](../research/final_audit_artifacts.json).
It checks artifact/run/commit identities and ZIP hashes, verifies exact original
source insertion, recalculates outcomes and preserves the failed workflow plus
separate recovery. It reads original candidates as data and runs no candidate or
model. Its command is:

```bash
python scripts/audit_final_evidence.py \
  --cache tmp/report-evidence-check --output results/report-evidence-check
```

Use new cache/output directories. The workflow supplies `GH_TOKEN` with
`contents: read` and `actions: read`; no token belongs in source or a report.
GitHub artifacts have retention limits. Exact IDs and hashes in the manifest
identify the evidence; if a raw ZIP expires, obtain the archived bytes from the
repository owner instead of treating a summary as a fresh raw audit.

Native rerun recipes are preserved in these reviewed workflows:
[final-stage](../.github/workflows/original-evaluator-replay.yml),
[stage 2](../.github/workflows/original-stage2-mascot.yml),
[targeted pairs](../.github/workflows/modified-original-comparison.yml), and
[full pairs](../.github/workflows/modified-original-full.yml).
The [modification README](../research/modifications/README.md#reproduction-commands)
gives local preparation and confined Docker commands. Original candidate code
must run only in the reviewed containment environment. The completed native
experiments do not need to be repeated to review this report.

## Status against the assignment

| Requirement | Current evidence | Remaining boundary |
|---|---|---|
| R1 Study paper | PASS | Paper/source discrepancies disclosed |
| R2 Reproduce implementation | IN_PROGRESS | Original saved-candidate native replay reproduced; historical model generation not reproduced |
| R3 Reproduce key results | IN_PROGRESS | Available original native results reproduced; historical generation and genuine without-refactoring remain missing |
| R4 Explain methodology | PASS | Paper stages and actual source behavior distinguished |
| R5 Identify limitation | PASS | Defined private-input, final-output-only policy |
| R6 Modify original source | PASS | Narrow finalizer in both original entry points; only deterministic slice exercised |
| R7 Experimental comparison | PASS | 626 pairs plus targeted probes, variability and costs disclosed |
| R8 Document difficulties | PASS | Documentation does not imply every difficulty was solved |
| R9 Report readiness | PASS with user-accepted historical exceptions | Report draft completion is separately tracked in REPORT; no submission authorized |

Girish accepted the two historical gaps for report scope and authorized drafting
on 21 October; the [decision record](../research/requirements/report_authorization_user_decision-20261021.txt)
and [exception registry](../research/requirements/exception_decisions.json) preserve
that scope. The original authors could supply missing deployment/call provenance
or an attributable without-refactoring corpus. A new authorized model run would
be a **NEW EXPERIMENT**, never a recovered historical run.

The active phase and next action remain in [HANDOFF.md](../HANDOFF.md) and
[research/progress.json](../research/progress.json). The final Word/PDF drafts
require Girish's review before submission by 31 October 2026.
