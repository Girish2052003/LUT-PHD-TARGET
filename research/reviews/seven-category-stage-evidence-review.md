# Independent seven-category historical methodology trace acceptance

**Date:** 18 October 2026. **Scope:** original-author saved data only; **not** the professor-facing report.

## Execution and provenance

The author Zenodo release was retrieved and SHA-256 checked against the official pinned archive in [GitHub Actions run 39073490709](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39073490709), at commit `f3fe755c423e138c7dffc5d9a9924510a95f657c`. Output artifact `12115901735` is an eight-file ZIP (seven JSON traces plus manifest), ZIP SHA-256 `f6678180e7fcccf90b0f77f54dd1071c3469191239ec7520c0229d93f8200718`.

Each trace contains four real historical snapshots from original files, with exact source filename, zero-based task position, stage record hashes, original native template and final archived source hashes:

1. Native processed input (original source, instructions, annotations)
2. Saved stage-1 refactoring
3. Saved stage-2 generation/post-reflection
4. Saved stage-3 final candidate

These four *historical saved stages* are not four newly executed author pipeline stages. The full 313-task identity ledger is used to verify task order and final-code SHA-256. Neither the author LLM nor a model substitution was called.

## Independently recalculated selected results

| Authentic category and task | Candidate 0 changed from saved stage2 to stage3 | Candidate 1 changed | Authors' archived native final acceptance |
|---|---|---|---|
| array / reverse_and_concat | Yes | No | Yes / Yes |
| loop / max_adjacent_product | No | Yes | Yes / Yes |
| branch / sin_or_cos | Yes | Yes | Yes / Yes |
| math / sigmoid | No | Yes | Yes / Yes |
| NumPy operation / array_from_intrinsic_linspace | No | No | Yes / Yes |
| NumPy ufunc / logsumexp | Yes | Yes | Yes / Yes |
| syntax / second_largest | No | Yes | No / Yes |

**Total:** eight of fourteen saved candidate program texts differ between stage 2 and stage 3. Difference does **not** by itself prove that a particular repair occurred, nor that the change improved correctness. All recorded final acceptance values above are authors' *saved evaluation flags*, not newly measured outcomes from this trace job.

A material original-artifact ambiguity: in `branch_test/sin_or_cos`, both saved final candidates differ from their stage-2 counterparts although the archived final-stage prompt/completion token fields are **zero for both**. Do not fabricate missing LLM messages or reconstruct repair behavior from token zeros.

## Accepted and unaccepted requirements

**Accepted narrow milestone:** all seven physical benchmark categories have verifiably indexed and hash-checked *historical* input / stage1 / stage2 / stage3 example records; no source identity or manifest mismatches in the independently inspected ZIP.

**Still open:** Paper-to-source explanation of complete runtime control flow, unrecorded prompts/repairs, genuine original code generation under historical models, stage-wise original ablations and reproducible fresh stage-execution traces where feasible. This artifact improves Phase A, **does not close R1/R4 or Phase A globally**, and should not cause report-writing or PR merge approval.

To reproduce: use `scripts/export_original_methodology_traces.py` with a SHA-256-verified Zenodo `SPDZCoder.tar` and current `identity_verified_scores.json`; the CI workflow retrieves/pins archive and archives exact selected records. See the stored JSON receipt for identifiers and counts.
