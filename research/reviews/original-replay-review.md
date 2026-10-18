# Original evaluator replay review — 15 October 2026

This is a practical engineering record, not the submission report. The reviewed
baseline is the official checksum-verified archive. Main at `5fbc609` preserves
the independently checked archived identity audit; the new replay branch has
not yet produced an accepted fresh execution result.

## Review and changes

Independent reviewer: `replay_safety_review`, read-only source and archive audit.
The reviewer independently matched all 922 exported source files against the
archive and inspected 313 templates plus 1,252 candidate programs. Seven syntax
failures were inspected as raw text. No filesystem, network, subprocess or
dynamic-execution calls were identified within this bounded inspection.

Three concrete findings were addressed before the first CI execution:

1. Stale schedules, party logs and combined sources could be attributed to a
   later attempt or empty candidate. Clear execution artifacts per attempt;
   capture sources before execution and archive streams/party logs per attempt.
   An empty candidate retains a null combined-source hash.
2. Copying the compiler working tree could include an untracked helper despite
   a clean tracked-file status. Export `Compiler/` and the four required scripts
   directly from the pinned Git commit, and hash every exported file. Regression
   test includes both an untracked file and a modified tracked file.
3. MP-SPDZ writes its schedule before compiler finalization. A schedule alone
   cannot mean compile PASS. Require a fresh schedule and the subsequent original
   runtime-launch marker; otherwise record UNKNOWN, FAIL or TIMEOUT as supported
   by the observed execution.

The original evaluator's insertion, oracle, command and timeout progression are
preserved. Killing the subprocess group on timeout and clearing disposable
artifacts are explicitly documented containment adaptations.

## Reproduction observations

- Original author source preparation succeeded using the verified 65,761,280-byte
  TAR; MP-SPDZ 0.3.6 source came from commit
  `6cc3fccef0904764364eb8e285519cd34028f325` and its official binary release.
- Local nested namespaces are unavailable, so no generated/author code is run
  on the host. The first execution gate uses restricted Docker in GitHub Actions.
- The container's OpenSSL CLI preflight remains an integration check for CI.
- Original templates and SPDZCoder candidates have no detected input/random
  calls. GPT-4 candidates include 166 input-requesting and 53 randomized
  parseable programs, with two overlapping. No missing party inputs are invented.
- 71 local regression tests passed after the fixes; the 17-phase handoff checker,
  source preparation, shell syntax and whitespace checks passed. These are
  harness checks, not benchmark reproduction results.

## Remaining acceptance gates

The independent recheck confirmed all three fixes, all seven focused tests and
all 36 exported MP-SPDZ files against their pinned Git objects, including script
executable permissions. No blocker remains to the inspected single-candidate
smoke. Docker construction, certificates and MASCOT execution still require CI
evidence. Inspect the real smoke's source hashes, compiler output, party logs and
original oracle outcome. Only then expand
the run. Full Level 2 replay, limitation witness, modification, paired comparison
and practical readiness remain open. Full generation has the separate historical
model/credential blocker recorded in the requirement ledger.

## Executed smoke and staged expansion

Commit `554522da16fc22fd008b3f5b4c0a5bb6c62a5d45`, run `38673372763`,
job `116221356127`, artifact `11944757660`: the genuine
`array_test/indicate_positive`, candidate 0, compiled and completed two-party
MASCOT with return code 0. The unchanged author oracle accepted the native
`Pass the test` output. Candidate wall time was 7.437576699 seconds; party-0
reported protocol time 6.94729 seconds including preprocessing. These are one
measurement, not a comparative performance estimate.

Independent reviewer `smoke_evidence_review` checked the ZIP and every archived
evidence file, all 922 original source files, all 36 compiler/script files, the
runtime binary, exact candidate/template insertion, combined-source hash,
stdout/stderr and both party logs. All matched. The narrow B2a smoke gate passed.
The entire 56,289-byte ZIP's 15 extracted files are now durable repository
evidence, with a receipt and original artifact expiry (13 January 2027).

The staged full-workflow review found no launch blocker. Additional acceptance
checks now verify each exact command, require three attempts on final timeout,
and bind source/runtime/package evidence to the reviewed smoke rather than
merely agreeing across runs. Aggregation rejects missing/duplicate candidates,
wrong hashes and malformed outcomes; it reports original acceptance separately
from process completion. Full coverage and scientific acceptance are pending.
