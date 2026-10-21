# Independent evidence and difficulty reconciliation — 21 October 2026

Technical acceptance record for PR #13, not the professor-facing report.
Authoritative prior main: `b8c94068e1fecfcd716c1ce2f71bf95a05a5f038`.
Audited implementation: `45a51e612453bab03c34e66bd9fe8977e2290e75`.

## Assignment scope and current acceptance

The professor's 12 October email in the thread “Funded PhD enquiry — Explainable
AI security and resilient software systems” requests paper/code study, implementation
and key-result reproduction, methodology explanation, one substantive limitation
with own code changes, baseline comparisons, a brief report with snippets/results,
and reproduction difficulties. The 14 October follow-up supplies ACM and Zenodo.
The deadline is **31 October 2026**. These messages were read on 20 October;
private email content is not copied into the public repository. The assignment
wording in `research/requirements/execution_contract.md` remains authoritative.

| Gate | Decision and boundary |
|---|---|
| R1 | PASS: original paper/source map, with discrepancies explicitly identified. |
| R2 | IN_PROGRESS: original native evaluator and saved-source execution reproduced; historical model generation NOT REPRODUCED. |
| R3 | IN_PROGRESS: archived metrics and full native final/stage-2 comparisons reproduced; historical generation and genuine without-refactoring ablation NOT REPRODUCED. |
| R4 | PASS: methodology and seven authentic saved-stage examples; missing dialogue is not fabricated. |
| R5 | PASS: authentic intermediate-opening witnesses under the declared private-input/output policy. |
| R6 | PASS: bounded original-entrypoint patch, deterministic finalizer execution and targeted tests. |
| R7 | PASS: full matched original/modified native comparison with unchanged-source fluctuations and costs disclosed. |
| R8 | PASS for documentation: 13 substantive difficulty families, source-linked failures/recoveries, raw-data rechecks and reviewed limitations. Documentation does not require the blocked experiments to become successful. |
| R9 | BLOCKED: the preserved user quote permits conditional research integration, not explicit report-readiness exceptions. Report writing remains separately unauthorized. |

All existing PASS phases retain their narrow scopes: M1–M6, A, B1, B2a, B2b,
B2, C1, C, D1, D, E, E1, F and G. B3 remains BLOCKED; REPORT remains BLOCKED.
G's historical PASS is the prior verified original-source integration, not a claim
that this new PR has already merged. PR #13 still requires its own review and
exact-head CI, followed by checking the actual merged main.

## Independent checks and preserved evidence

Raw-evidence [run 39493312330](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39493312330)
completed on 20 October at the audited commit. Artifact **12296548051**, 583,101 bytes,
SHA-256 `912dd08ff6d57ba9c8607217ec189be6a6279ec284ec0f0f26be695f77202e17`,
was retrieved and independently inspected on 21 October. It expires on
18 January 2027; the individual original artifact expiries are in the receipt.
Selected output files are preserved with byte hashes in
`research/evidence/2026-10-21/final-readiness/receipt.json`.

The workflow checked **31 pinned raw/summary ZIPs**. Original final-stage code
and native template insertion were reconstructed for **1,252 records / 1,280
attempts**, closing the earlier automated insertion-check gap. Stage 2 was checked
by three existing independent auditors, including source-TAR identity and raw
stdout/stderr. Paired evidence was recalculated by the original verifier plus
an independent control auditor; targeted source/input/output/opening checks were
also repeated. No original/generated candidate executed and no model was called.

| Evidence family | Independently recomputed result |
|---|---|
| Final-stage original MASCOT, run 38703569637 attempt 2 | SPDZCoder first/second/union **268/265/288**; GPT-4 API-doc **95/112/154**, each out of 313. 1,252 records, 1,280 attempts. This is saved-source native execution, not model regeneration. |
| Stage-2 original MASCOT, source 39075744038 / recovery 39080161119 | **626 candidates / 644 attempts; 147 compile failures, 34 completed-runtime oracle rejections, 445 acceptances**. Fresh first/second/union **229/216/262**, saved **229/213/261**. Preserve three disagreement identities, two unclassified compiler errors and 18 timed-out attempts. |
| Full paired run 38989067493 | **626 pairs / 1,252 executions / 1,280 attempts**; original **270/266/290**, modified **271/263/290**. Two source changes, both ACCEPT to ACCEPT. Four acceptance flips on unchanged-source controls: no causal pass-rate improvement. |
| Targeted run 38958484872 | **64 executions / 32 pairs** verified. 24 observed private-input pairs show **50 to 0 explicit intermediate-opening events**, with authorized outputs preserved; four private control pairs, two native pairs and two synthetic fallback pairs remain separate. |

Original stage-2 aggregation **39075744038 remains failure**; artifact-only recovery
**39080161119 remains success**. The raw audit checks both historical workflow states.
No unsuccessful native run was relabeled. The final-stage initial download failure
and recovery also remain explicitly documented.

## Review findings and repairs

The independent `r8_final_review` context found the old R8 checker too narrow and
fail-open on missing provenance fields. Counts alone admitted altered categories,
disagreement identities and removal of unclassified errors. Intentional negative
regressions were executed in runs **39492627095** and **39492946695** before repair.
At `45a51e6`, **14 R8 tests** and the R8 accounting workflow **39493312087** pass.

A separate `r8_pr13_review` assistant context inspected the new implementation,
delegated raw verifiers and actual receipt; independently ran all 14 R8 tests;
and found **no critical or important defect at 45a51e6**. Its nonblocking concern
was incomplete workflow path triggers. The workflow now watches verifier/source
preparation and difficulty-register changes and also validates relevant main pushes.
This is an independent assistant review, not external scientific certification.

The 21 October documentation extends `docs/reproduction_log.md`, updates the
modification checkpoint and marks both 14 October reports as historical. A dated
correction distinguishes smoke runtime costs from full-paired runtime costs.
All underlying archived measurements and original code are preserved.

## Permission scope correction

The exact 18 October quote and SHA-256 remain unchanged in
`research/requirements/conditional_merge_user_decision-20261018.txt` and the
exception registry. It says to attempt recovery and then merge if unsuccessful,
while retaining NOT REPRODUCED labels. It does **not** establish report-scope
acceptance or authorize drafting. Existing accepted decisions therefore retain
`authorization_scope: RESEARCH_INTEGRATION`; R9 returns to BLOCKED.

Two new tests demonstrate that the previous checker accepted merge-only or missing
scope for report readiness. Both failed before repair and pass after repair;
`permission-scope-red.log` and `permission-scope-green.log` preserve that sequence.
The corrected checker requires an explicit known authorization scope and uses
only REPORT_READINESS decisions for incomplete R2/R3 at R9. The checker validates
records, not human authorship; independent review of the actual instruction remains
necessary. R8 no longer depends on successfully executing B3 or on its exception.

## Historical experiment recovery and remaining steps

The published TAR, 35 saved groups, 498 relevant source files, embedded Git
history and release/remote audits identify no attributable original without-
refactoring corpus. All 313 input/instruction pairs are recovered, with six direct
Python parse exceptions preserved. The matching UniTrans counts are not the
required experiment. The original Azure deployment/version and complete dialogue
remain unverified. Neither gap is proved impossible forever; authors could supply
missing provenance/artifacts. Paid model access is unauthorized. A newly generated
run would require provider/model/cost approval and a NEW EXPERIMENT label.

Before report writing: finish PR #13 independent documentation/governance review,
require all applicable CI at its exact head, merge, then check actual main. After
that, present the remaining two gaps to Girish for an explicit report-scope decision
and writing authorization. Only after that decision prepare the brief report and
editable/PDF deliverables for his review. Sending or submitting requires a separate
instruction. The repository must never claim all professor requirements are complete
while reproduction gaps and the final report remain outstanding.

## Final local review before commit

The independent `r8_pr13_review` context accepted the documentation and governance
changes for commit/CI on 21 October, with no critical or important findings. It
ran all **15 handoff tests**, checked the 21-phase/9-requirement ledger, verified
the copied audit receipt hashes and compared the acceptance JSON byte-for-byte
with the downloaded artifact. The primary checkout's complete **189-test** suite,
R8 verifier and rendered handoff checks passed. A final minor trigger improvement
uses `scripts/**` and source/evidence paths to cover transitive audit dependencies.
The working README's stale PR6/R8 paragraph and original replay README were also
corrected. Exact-head remote CI and actual merged-main checks remain required;
local review does not assert those future results.
