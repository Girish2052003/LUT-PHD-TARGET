# Scoped original-pipeline comparison-mask modification

Status: narrow E1 paired smoke independently accepted; complete native regression pending.
This is a technical experiment record, not the professor-facing report.

## Defect and supported correction

An authentic `count_distinct` translation opens each pairwise inequality while
accumulating a secret distinctness flag. Under the explicit private-input,
output-only policy, inputs `[1,1,2]` and `[1,2,2]` have the same authorized count
but reveal different comparison patterns. Accepted D1 evidence is retained in
`research/evidence/2026-10-15/original-diagnostics/`.

The postprocessor removes a `.reveal()` only when its comparison bit (or `1-bit`)
is multiplied into an accumulator with a supported secret-integer invariant.
The comparison and its operands are unchanged. Using a secret bit instead of its
public opening preserves the integer product under standard MP-SPDZ semantics
and avoids that explicit opening. This reasoning has a narrow domain; no formal
proof or universal confidentiality claim is made.

All stores to the accumulator are checked. Unsupported binding/control forms,
dynamic calls, malformed programs, ambiguous functions and mixed opened-operand
comparisons fall back unchanged. Code with no selected rewrite is byte-identical;
a changed module is formatted by `ast.unparse`. Inputs must use standard MP-SPDZ
numeric primitives/arrays and valid ranges. Custom operators, reflection, dynamic
rebinding, secret public control and overflow behavior are outside the contract.

Static original-data coverage is two changes out of 626 candidates:
`loop_test/count_distinct` candidate 1 and `loop_test/is_ascending` candidate 0.
`lower_bound` is an accepted disclosure witness but remains unfixed. This is a
postprocessor for a demonstrated class, not a general leakage detector.

## Integration into the original source

`scripts/apply_original_postprocess.py` verifies every prepared baseline file and
the exact original hashes of `src/pipeline.py` and `src/pipeline-mp.py`. It copies
the original tree into a separate modified tree, adds one import and a finalizer
after feedback and before writing final output, and records a unified patch plus
original/modified hashes. The unmodified baseline stays intact. Original source
is from the SPDZCoder authors' Zenodo artifact, CC BY 4.0; additions are explicitly
marked Girish project modifications.

Both entry points call the same postprocessor. The experiment executes the exact
added assignment extracted from each patched entry point and requires their
outputs to agree. Only this deterministic finalizer slice is executed: earlier
model-dependent stages are neither run nor simulated. Historical generation
remains separately blocked. Model prompts, samples, token accounting, original
evaluator, templates, tolerances and compiler settings are not experiment variables.

## Pre-specified paired smoke

There are 32 pairs / 64 executions, with both variants in the same restricted image
and job. Pair order alternates. Every attempt starts with fresh compiled artifacts,
party logs and explicit party inputs; original timeout/retry behavior is retained.

- Two authentic changed candidates use their byte-identical native templates.
- Each candidate has 12 observed private-input cases: ten fixed-point arrays and
  two integer arrays. These cover empty/singleton arrays, equal-output witness
  pairs, duplicates, negative/zero values, ascending/descending order, exact binary
  fractions, moderate fixed-point magnitudes and large representable integers.
- The two equal-output witness arrays per task also run without instrumentation,
  giving four unobserved control pairs.
- Two locally authored public-return regressions exercise arithmetic zero folding
  and `match` rebinding. They must remain byte-identical and keep public-print
  behavior; they are never represented as model responses.

Party 0 owns each probe array. Length and type are public. The returned count/bit
is the only authorized value. The observer prints and returns only the result of
an existing reveal; it performs no new reveal. Baseline opening values must match
the original loop's comparisons, modified traces must be empty, and both variants
must return the independently computed reference output. Matching output alone is
insufficient. Native outcomes and these new diagnostics are never pooled into a
benchmark rate. The synthetic fixtures are not privacy witnesses.

`scripts/verify_paired_replay.py` regenerates case specifications, candidate
transformations, observers, templates and input bytes; reconstructs the original
source insertion; checks raw hashes, commands, retries, classifications, two-party
logs and author decisions; and recalculates the semantic diagnostic validation.
All failures remain in the artifact. Local tests run only owned fixtures; downloaded
candidates execute only in the read-only, non-root, network-none MASCOT container.

The smoke workflow records CPU/kernel/runner information and both variants' raw
cost output. Timing is descriptive; no speed advantage is asserted from one run.
Complete native paired coverage and its bounded analysis were subsequently accepted
in Phase F; see the full comparison checkpoint below.

## Accepted E1 result

Run38958484872 at35adfb04c1132ae91d1b2c6e21cf791855eab768 completed all64executions.
Both native candidate pairs pass before and after; all private/control and
synthetic expected outputs are preserved. Across24observed private probes,
50original intermediate opening events become zero. Both equal-output witness
pairs lose their distinguishing explicit opening traces. All718artifact files
are preserved and independently audited; see
`research/reviews/paired-smoke-evidence-review.md`.

The measured tradeoff is extra secret multiplication:93additional integer triples
for native count_distinct and17for is_ascending. Timing/communication measurements
are retained as single-run descriptive observations, not performance guarantees.
Compiler opens include internal protocol operations; zero observed intermediate
openings does not mean zero cryptographic protocol openings.

The full launch gate binds the exact accepted modification manifest and ten
critical harness/source files to this receipt. A later code change cannot reuse
the old smoke approval. Full coverage uses626candidate pairs, reports all failures
and original-oracle decisions, separates changed versus byte-identical sources,
and includes exploratory task-level paired uncertainty with explicit limitations.

## Reproduction commands

```bash
python scripts/prepare_original_replay.py
python scripts/apply_original_postprocess.py --build-dir tmp/original-replay-build
docker build -t modified-original-paired tmp/original-replay-build
REPLAY_HARNESS=replay_modified.py bash scripts/run_original_replay_container.sh \
  modified-original-paired results/paired-smoke
python scripts/verify_paired_replay.py --root results/paired-smoke \
  --baseline tmp/original-replay-build/baseline
```

Run only the reviewed Docker workflow. Never import/execute downloaded candidate
source on a host containing user credentials or sensitive files.

## Accepted full comparison — current checkpoint, 21 October 2026

Phase F completed in run **38989067493** at
`b5846f5be000e6f511ed319011549ed4aaa8472c`: **313 tasks, 626 matched candidate
pairs, 1,252 executions and 1,280 attempts**. Baseline first/second/union acceptance
is **270/266/290**; modified acceptance is **271/263/290**. Exactly two candidate
sources change (`count_distinct` candidate 1 and `is_ascending` candidate 0), both
ACCEPT to ACCEPT. Four acceptance flips occur among the 624 byte-identical source
controls; no causal aggregate accuracy gain is established.

The targeted smoke's native runtime measurements are count_distinct
**28.5628 to 31.3084 seconds** and is_ascending **14.2188 to 14.2445 seconds**.
The separate full-paired run measured **18.6831 to 20.6538 seconds** and
**8.822 to 8.86707 seconds**, respectively. Keep these single-run measurements
attached to their own run; neither proves general speed or precision behavior.

The patch is exercised as its exact added deterministic finalization step on
authentic saved candidates. The preceding model-dependent original pipeline was
not rerun. Mixed opened-operand `lower_bound` remains unchanged. See
`research/reviews/phase-f-bounded-native-interpretation-20261018.md`,
`research/reviews/paired-full-independent-control-audit.md` and
`research/evidence/2026-10-21/final-readiness/raw-audit-acceptance.json`.
Do not rerun accepted native experiments merely because an older dated note says
Phase F is pending.
