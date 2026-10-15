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
4. Work on a research branch. Reuse PR #5 while its official-artifact audit is
   unfinished. Require independent review and CI before merging. Preserve all
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

Audit PR #5 against the checksum-pinned original source. Exact task-ID joins now pass for templates, processed inputs, both authentic
candidate sets and saved outcomes (313 tasks and 1,252 candidate hashes). The evaluator boolean semantics are documented in `research/original_source_audit.md`;
finish controlled execution setup before running generated programs. Fix the provenance-helper issues in
`research/reviews/pr5-independent-review.md`, then obtain review and CI evidence.

After that, map the paper to real source paths, capture seven real stage traces,
and perform Level 2 replay with the original evaluator in a restricted environment.
Do not run archived generated Python with credentials or unrestricted host access.
Check actual MASCOT commands and oracle behavior; the earlier cleartext emulator
is a separate experiment.

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

The active worktree is `LUT-official-review` on local branch
`research/phase-ledger-20261014`, initially based on the PR #5 head. The older
`LUT-PHD-TARGET` worktree has preserved independent compiler work at `1b54aad`.
Do not copy its stale tree over newer official-artifact work. Local paths are
conveniences; the remote repository and evidence hashes are the durable state.
