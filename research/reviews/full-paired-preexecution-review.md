# Full paired comparison launch review — conditional GO

Reviewer: `replay_safety_review`, 16–17 October 2026. This review covers launch
and aggregation; it does not accept any not-yet-run full result.

The aggregate requires 313 task IDs from the accepted ledger, two candidates and
two variants: 626 pairs / 1,252 executions. Duplicates, missing outcomes and
nonnative diagnostics are rejected. Failures and native-oracle false positives
remain in the denominator. Changed sources are separated from byte-identical
controls, whose disagreements must not be attributed to the modification.

The reviewer checked first/second/union task grouping, the exact two-sided
McNemar calculation, fixed-seed task bootstrap and the explicit uncertainty/timing
limitations. Cost parsing reproduced all six metrics from the accepted original
smoke. The two-root artifact upload and aggregate download paths agree.

Review found an initial launch-gate gap: a current modification manifest and an
old PASS receipt did not bind the full run to tested code. The corrected gate
requires the accepted smoke's exact preserved modification-manifest digest and
all ten critical launch-source digests. Tests independently confirm rejection of
changed prepared manifests, changed harness bytes, incomplete pins and unaccepted
smoke receipts. It executes before Docker build/run.

**GO is conditional on independently accepted 32-pair smoke evidence.** Full
launch still requires `[paired-full]` or explicit workflow dispatch. No full
generation, runtime result, regression acceptance or merge readiness is implied.

Reviewed SHA-256:

- Gate: `e26d626312be2de83a8443df30721359ab1bb131f59e4a995a56f209ad791526`
- Gate tests: `7dc79c5db63602db90af1251f7bd559f408539d9e3545d3b37803180f8a7f485`
- Workflow: `42fb35890c9ff60a2caef9f4bd52b6590446cc2a6cf7cae73043cc6d55839cab`
