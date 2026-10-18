# Pre-specified authentic stage-2 MASCOT replay protocol

This is a practical experiment protocol, **not the professor-facing report**. It is a controlled replay of authors' **saved** stage-2 code, not fresh LLM generation and not a randomized ablation.

## Source identity and scientific question

Original release: Zenodo SPDZCoder.tar SHA-256 `a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac`. MP-SPDZ 0.3.6 sources at `6cc3fccef0904764364eb8e285519cd34028f325`; unchanged original evaluator SHA-256 `7b999498f06050ab4db54e19097f65cd56c09eb7446384ddca4b62165969f1a2`.

The authors' saved stage-2 evaluation flags are 229/313 first-candidate and 261/313 at-least-one-of-two; saved final stage-3 flags are 269/313 and 288/313. We ask whether original saved stage-2 candidate **programs**, when freshly compiled and executed by the **unchanged original MASCOT evaluator**, have native acceptance rates close to their archived values. We do not assume identical acceptance, because independent original stage-3 reruns already demonstrate run-to-run variability.

## Pre-specified input and evaluation controls

- All 313 original native task identities and original test templates, with **two saved stage-2 candidate texts per task**, 626 candidate inputs total.
- Each stage-2 source file, evaluation file and native test template must match the pinned original file hashes and the independently accepted 313-task identity/order ledger. The stage-2 ledger records the SHA-256 of **every one of the 626 saved candidate strings**.
- The original `evaluation/evaluate_experimental-mp.py` runs `insert_compile_run` unmodified; all original timeouts, retries, checks and weaknesses (including lenient stdout substring matching) are preserved and described, not corrected within the reproduction.
- Same evaluated MP-SPDZ source, official binary, 2 MASCOT parties, CPU/memory limits, non-root read-only Docker, no network, no GitHub/API secrets as the accepted original stage-3 replay.
- The only addition to the original pinned replay *build context* is a separate stage-2 harness, a generated source/hash ledger and an explicit Dockerfile COPY line. Original baseline modules, repository evaluator, templates and accepted stage-3 replay sources are unchanged.
- Native failures, missing or malformed candidates, retries, compile failures and all warnings remain in the experiment's denominator; do not filter or repair stage-2 candidates to make rates look better.

## Launch and acceptance gates

1. Run pure source-binding and failure-path tests, original provenance checks, then seven smoke cases (one authentic task in each of seven categories × two stage-2 candidate texts = **14 original native evaluations**) in the restricted MASCOT container.
2. Validate original task IDs, exact candidate/template hashes, original test stdout/err streams, compilation/source hashes, timeout retry path, resolved packages and complete outcomes using `scripts/verify_stage2_replay.py`. Do **not** require all stage-2 source programs to pass; failed native tests are valid experimental data.
3. Inspect/accept the smoke raw artifact independently before authorizing the complete [stage2-full] workflow.
4. Run a seven-way split 626-candidate native evaluation only after accepted smoke. Each category job validates raw records and releases all logs. Aggregate must reject any missing/duplicated/wrong-source record and verify 626 unique candidates, 313 exact native tasks, source/environment pins and observed original acceptance markers.
5. Recalculate first/second/union counts and all historical saved-stage-2 disagreements. Compare them with the previously accepted fresh original stage-3 B2b replay as *different runs* (not causal treatment groups). Report original oracle weaknesses and run-to-run variability; avoid statistical claims unsupported by repeat trials.

**No new live model calls, paid services, repaired candidate text, or final report writing**. Independent review must accept both the smoke and full evidence before Phase C can be promoted. Historical model availability remains blocked pending the user's decision.
