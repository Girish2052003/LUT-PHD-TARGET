# Original evaluator replay (Level 2)

This executes the unmodified author function
`evaluation/evaluate_experimental-mp.py:insert_compile_run` on authentic archived
candidate bytes and native templates. It does not generate model responses.
The wrapper collects per-candidate evidence; it does not replace the acceptance
decision with a new oracle.

The initial smoke used `array_test/indicate_positive`, candidate 0. Full coverage
was subsequently completed: 1,252 final-stage original candidates and 626 stage-2
candidates, with independent raw-evidence review. See `HANDOFF.md` and
`research/reviews/final-readiness-review-20261021.md` for current state. Preserve
the original failures; do not repeat the completed smoke/full phases.

## Pins and disclosed differences

- Official author archive SHA-256:
  `a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac`.
- MP-SPDZ 0.3.6 compiler/scripts commit:
  `6cc3fccef0904764364eb8e285519cd34028f325`.
- Official 0.3.6 binary archive SHA-256:
  `e83efcbbe9b295fe276450f3d4aa6e822f35d4bf348c87dee4877b4fed4e5f40`.
- MASCOT, two co-located parties, default compiler/protocol parameters. Templates
  retain their original inputs, numerical precision and test predicates.
- The authors did not pin OS/Python or all transitive dependencies. This replay
  uses Python 3.11.9 and the explicit evaluator-only dependency list. The resolved
  base-image digest, installed packages, OS packages and binary hashes are saved.
- The original 60/150-second timeout starts and three retries are preserved.
  Process-group cleanup prevents orphaned protocol processes after a timeout.
  Compiler artifacts are cleared per attempt to avoid attributing stale schedules.
  Party logs and combined sources are preserved per attempt. A schedule alone
  does not establish compilation success: it is written before finalization.
  The classification requires the original runtime-launch marker as well.

## Isolation

The launcher uses a non-root, read-only Docker container with no external
network, no user credentials, no added Linux capabilities, two CPUs, 6 GiB RAM,
256 processes and bounded disposable scratch filesystems. Only the result
directory is mounted from the host. Source files are hash-checked before and
after the experiment. Fresh protocol certificates belong solely to this local
test and are not uploaded. This is containment, not a formal sandbox proof or a
distributed-deployment security evaluation.

Local nested namespace creation is unavailable in the current work environment.
The runner therefore refuses ordinary host execution; GitHub Actions supplies
the Docker runtime. The original plaintext emulator is not used here.

## Evidence

Each candidate produces exact code/template/combined-source hashes, original
oracle acceptance, separate compile/runtime classifications, process exit codes,
timeouts, durations, full stdout/stderr and party logs. Original saved flags are
comparison metadata, never reused as fresh outcomes. A successful process is not
automatically a correct program; an author-accepted result can still have a
separate execution failure because of the original oracle weakness.

The safe build context excludes author `.git`, caches and credential files.
Compiler/scripts are exported from the pinned Git object, excluding untracked
or locally changed working-tree bytes, and individually hashed. An independent
static review inspected all 313 templates and 1,252 archived candidates. It found
166 parseable GPT-4 candidates requesting party inputs and 53 using randomness
(two overlap). No replacement input files or seed values are invented; resulting
failures remain in the denominator. Static screening is not a security proof.
Original source remains attributed to the authors' CC BY 4.0 Zenodo release;
MP-SPDZ is obtained from its official repository and release.
