# Start here — research handoff

**Read this file, `research/progress.json`, and the requirement ledger before
doing work. Do not restart completed milestones.** The assignment is due
31 October 2026. The final report is locked pending practical evidence and
Girish's explicit authorization.

## Resume safely

1. Fetch remote refs, read open PRs and check `git status`. Recorded SHAs are
   historical anchors, never permission to replace newer commits.
2. Run `python scripts/check_handoff.py`. If evidence is missing or changed,
   investigate that discrepancy; do not silently reset a completed phase.
3. Read each phase's `next_action`, evidence and completion scope in
   `research/progress.json`. Continue the earliest unfinished dependency.
4. Work on a research branch. PR #5 is complete; use the active original-evaluator research branch for new work. Require independent review and CI before merging. Preserve all
   unmerged branches.
5. Update the phase record and requirement evidence after each meaningful run.
   Use `python scripts/check_handoff.py --render` to refresh the README table and
   readable requirement ledger. Commit/push the evidence with the marker.

## Completed work to preserve

- **M1:** independent implementation of the paper-inspired pipeline and tests.
- **M2:** independent Figure 4, disclosure witness and DomainSafety experiments.
- **M3:** official Zenodo archive discovery, metadata and published checksum.
- **M4 / B1:** saved author outcomes sum to **269/313 first-candidate success**
  and **288/313 two-candidate union**. This is archived-score reconstruction.
- **M5:** static indicators on 626 author SPDZCoder and 626 GPT-4 candidates.
- **M6:** 53 tests and successful historical CI at `5ca3809`.

These are deliberately narrow completion claims. None means that fresh original
MASCOT evaluation, an authentic limitation, or a modified-original comparison
has passed. The paper's two NumPy groups combine to 66 tasks; all seven archive
groups total 313. Files named `.json` under processed inputs contain JSON Lines.

## Current practical work

PR #5 is merged as `5fbc6095eb4e5a37b8818be7d1ec7596753445cd` after
independent review and successful original-artifact/research CI at
`8d9cf2e5125fbcb8255e30c1e5b8841324223461`. **Do not redo the archived
provenance phase.** Exact joins and evaluator flag semantics are complete (C1).

Resume E/F on branch `research/original-evaluator-replay-20261015`, PR #6.
**B2a is complete:** the first authentic archived candidate ran through the
unchanged original evaluator and two-party MASCOT. Run `38673372763` at
`554522da16fc22fd008b3f5b4c0a5bb6c62a5d45` passed; all 15 raw artifact files
are preserved under `research/evidence/2026-10-15/original-smoke/` and independently
hash-checked. Do not redo that smoke solely to rediscover its result.

The historical workflow validated both candidates in seven representative categories,
then attempted all 1,252 SPDZCoder/GPT-4 candidates. The full run is requested only
by a commit with `[full-replay]` in its message or explicit workflow dispatch.
Inspect run/commit before launching another full run. A green smoke or an
implemented aggregator is not full reproduction.

**B2b is complete:** full run `38703569637` at
`769bb12ce342b814590061ef04fdffbbe19c9990` has all 1,252 candidate outcomes,
independently audited. SPDZCoder first/second/union: **268/265/288 of 313**;
GPT-4 API-doc: **95/112/154 of 313**. The initial source-download failure was
recovered by retrying only failed jobs. Five archived/fresh disagreements remain
explicit; see `research/reviews/full-replay-evidence-review.md`. Do not rerun this
baseline merely to rediscover its results. Raw artifact retention ends January 2027.

**D1 is complete:** run `38742644019` at `aa89eb6` establishes two authentic
private-input/output-only disclosure witnesses and four separate native-oracle
false positives, across 16 cases. All 133 diagnostic files are preserved and
independently checked. The selected main limitation is unnecessary intermediate
openings in otherwise functionally accepted translations. The policy is explicit;
this is not a historical breach or a universal confidentiality proof.

**E1 is complete; current work is full F:** the narrowed secret-arithmetic postprocessor
has independently accepted targeted runtime evidence. Exactly two of 626
archived candidates change; 624 remain byte-identical. The mixed fixed/integer
`lower_bound` comparison is deferred. Review and correction history is in
`research/reviews/secret-arithmetic-review-findings.md`.

Both original pipeline entry points now have a reproducible, hash-pinned finalizer
patch. The pre-specified paired smoke has 32 pairs / 64 executions: two native,
28 private-input observed/control, and two locally authored fallback pairs.
Read `research/modifications/README.md`. Run38958484872 at35adfb0 completed all64
executions; all718artifact files are preserved and independently checked.
Both native candidates pass and all private/control outputs are preserved;
50observed original opening events become zero. Only the exact added
finalizer slice is exercised on archived candidates; model stages are not simulated.
This accepts the narrow comparison-mask repair, with recorded extra multiplication
costs. Full626-candidate paired comparison remains separate. Launch it with the
reviewed gate and `[paired-full]`, preserving all failure and uncertainty results.

Four practical milestones remain: complete full paired comparison; complete
seven-category source/methodology traces; finish available
ablations and oracle checks; independently audit/consolidate evidence and validated
main. Historical generation still needs Girish's explicit blocker decision, followed
by separate report authorization. This sequence is not a guarantee against new
experimental failures; preserve and investigate every one.

A, C, broader B2/D, E/F/G and report readiness remain open. Preserve the accepted
narrow subphases; never reset or promote their scope without evidence.

Preserve the missing native oracle in `numpy_operation_test/np_basic_slicing_stride`
as a benchmark limitation; do not invent tests or missing GPT-4 party inputs.
Source-grounded oracle defects (`pass_or_not` filename contamination and three
signed-relative comparisons) now have accepted D1 runtime witnesses. They remain
separate from the selected privacy modification. See `research/replay/native_oracle_audit.md`.

Read `research/original_source_audit.md` for original stage-1/repair discrepancies
and oracle weaknesses. They are candidates for investigation, not accepted fixes.
Keep seven-category stage traces tied to authentic source and actual outcomes.

## Sources and evidence

- Baseline: <https://zenodo.org/records/18152253>, `SPDZCoder.tar`, 65,761,280 bytes.
- MD5: `3c6d7707d7aecc051d35312f81405c66`.
- SHA-256: `a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac`.
- Original artifact metadata declares CC BY 4.0; preserve attribution and mark
  modifications when redistributing permitted source.
- PR: <https://github.com/Girish2052003/LUT-PHD-TARGET/pull/5>.
- Historical reviewed head: `5ca3809f15e8e326ff2d0a9b2e23993704be3dda`.
- Historical main: `0ae96a968022325f3f678b19db1fcd69de483b70`.
- Durable evidence index: `research/evidence/2026-10-14/receipt.json`.
- Requirement ledger: `research/requirements/assignment_traceability.yaml`
  (JSON syntax, which is valid YAML 1.2), with a generated Markdown counterpart.
- User's controlling instructions: `research/requirements/execution_contract.md`.

The original evidence artifact expires 13 November 2026. Small measured results
are therefore checked into this repository. Reconstruct large source archives
from the pinned public release; never commit embedded `.git`, credentials,
unreviewed binaries, or generated confidential material.

## Active restrictions and blockers

No paid API calls, substitute model, or invented model responses are authorized.
Historical full generation (Level 3) needs authorized credentials and verification
of model availability. Record that blocker separately from Level 2 replay.

Existing `docs/report.md` and `docs/professor_submission_interim.md` are historical
drafts, not accepted final submissions. Do not expand, polish or submit them.
Only after R1–R8 pass, or Girish accepts explicit irreducible exceptions, present
the practical gates and ask for report authorization. No email is authorized.

## Local continuity notes

The active worktree is `LUT-replay` on branch
`research/original-evaluator-replay-20261015`, based on merged main `5fbc609`.
The older `LUT-official-review` worktree is preserved and may contain stale local
state; use the committed remote checkpoints instead of copying it forward. The older
`LUT-PHD-TARGET` worktree has preserved independent compiler work at `1b54aad`.
Do not copy its stale tree over newer official-artifact work. Local paths are
conveniences; the remote repository and evidence hashes are the durable state.

## New independent Phase C stage-2 evaluator checkpoint — 18 October 2026

Draft [PR #9](https://github.com/Girish2052003/LUT-PHD-TARGET/pull/9) targets the accepted-in-scope seven-category methodology [PR #8](https://github.com/Girish2052003/LUT-PHD-TARGET/pull/8), which itself targets the primary draft original-source [PR #6](https://github.com/Girish2052003/LUT-PHD-TARGET/pull/6). Do not overwrite these separate review branches or mistake unmerged code for `main`.

**Stage2 native smoke EVIDENCE ACCEPTED (narrow):** GitHub run [39075137852](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39075137852), experimental commit `53f1f2733df010db90c13cafde7b5b2bbaa9277f`, artifact `12116746822`, SHA-256 `6f2f6b563cb0fb6ade2eec1799dbf90a5d31b419c9be940d36209c1c6175f36b`. Separate ZIP review cross-referenced the original-author saved-stage snapshots: **7 authentic native tasks × 2 saved-stage2 candidates = 14 fresh MASCOT executions**, with **7 accepted, 7 rejected, 8 compiler passes, 6 compiler failures, no archived-stage2 flag disagreement in these 14**. Source texts are present byte-for-byte in the executed MPC inputs, and all identities/raw evidence match. See `research/evidence/2026-10-18/stage2-mascot-smoke-receipt.json`, `research/reviews/stage2-smoke-independent-review.md` and the rerunnable `scripts/audit_stage2_smoke_zip.py`. No language model was regenerated.

**Full stage2 native comparison RUNNING / NOT YET ACCEPTED:** [GitHub Actions run 39075744038](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39075744038), pinned original evaluator, original MASCOT and exact authors' source, 313 tasks / 626 stage2 candidates over seven splits. The same-revision smoke passed before the matrix launched. Download and independently inspect all category artifacts, recompute raw outcomes and historical saved-score disagreement before changing any milestone to PASS. Retain every failure and native weak-oracle qualification. The new stage2 experiment is **not** a historically regenerated LLM pipeline or a controlled causal repair ablation.

**Remaining practical milestone count remains four:** F full paired evidence acceptance, A complete source-methodology mapping, C stage2 native/oracle/ablation acceptance, and G final independent requirement audit/validated main. Historical live-model availability and any paid API permission remain separately blocked. The professor-facing final report stays locked until Girish explicitly authorizes it.
