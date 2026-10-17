# Original SPDZCoder: saved stage-2 versus final stage-3 results

**Practical reproduction evidence only. Not the final submission report.**

## Source and reproducibility

Run [39073915415](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39073915415) at commit `b17fc7c57f331e604bf675c745a1eb6c8a1a5e9a` independently retrieved and checked the complete, SHA-256-pinned original authors' release. Result artifact: `12116316330` (ZIP SHA-256 `5ae5d2312a54617797168a67ff4f1fcc49da8dc12506a30ad5a8090c6a2098c4`). The archived native evaluation flags for *all seven physical groups* were parsed using the original task ID/order ledger and the preexisting strict flag parser. No model inference, no substituted prompts, no MP-SPDZ execution, and no candidate generation was performed for this saved-stage analysis.

Actual source paths: `evaluation/experiment-1-stage_2_SPDZ_output_<category>.txt` and `evaluation/experiment-1-stage_3_output_<category>.txt` in the original Zenodo archive. The existing original saved stage-3 values are cross-checked against the previously validated 313-task ledger. Original stage-2 source-code snapshots are separately preserved for seven representative categories via `scripts/export_original_methodology_traces.py`.

## Original author archived outcomes — all 313 tasks

| Category | N | Stage 2 first / union | Stage 3 first / union |
|---|---:|---:|---:|
| Array | 43 | 32 / 39 | 36 / 40 |
| Loop | 97 | 70 / 82 | 82 / 90 |
| Branch | 34 | 29 / 29 | 34 / 34 |
| Math | 38 | 30 / 35 | 36 / 37 |
| NumPy operations | 32 | 21 / 24 | 24 / 25 |
| NumPy ufuncs | 34 | 26 / 28 | 31 / 32 |
| Syntax | 35 | 21 / 24 | 26 / 30 |
| **Total** | **313** | **229 / 261** | **269 / 288** |

Stage-2 first candidate: **229/313 = 73.16%**, and at least one of two: **261/313 = 83.39%**. These reproduce the paper's archived *without repair* headline values. Original stage-3: **269/313 = 85.94%** first and **288/313 = 92.01%** two-candidate union; these reproduce the archived full-stage values. The second-candidate saved acceptance count is 213 at stage 2 and 265 at stage 3.

## Include the negative results

Across the **626** matched candidate outcomes, 93 change from REJECT to ACCEPT, **one changes from ACCEPT to REJECT**, and 532 preserve their decision. The exact regression is `math_test/pi_to_the_x`, candidate 0: stage 2 ACCEPT, stage 3 REJECT. This is an original-authors' **archived** regression, not a regression introduced by Girish's security modification.

Every category is present and every original task ID is matched. The numerical gains are paired historical observations, **not a new controlled experiment that independently disables repair**. Original model traffic, input token accountability, unrecorded intermediate repairs and all low-level prompts are not preserved by the stage outcome logs; missing provenance may make causal attribution unsafe. Differences between saved stage2/3 candidate programs do not prove they were caused specifically by model repair. All 313 denominator entries and failures are retained.

## Narrow phase disposition

Accept the archived stage-level score recalculation and category/candidate accounting as a **new reproducibility submilestone for Phase C/R3**, supported by the original saved logs and a checksum-pinned source. Full Phase C remains open: independently replaying stage-2 candidate outputs and available ablations under the unchanged native evaluator is a different, not yet accepted task. Phase A remains open beyond the seven genuine *saved* stage examples. The historical model-generation blocker still requires user authorization. No professor-facing report writing is authorized.
