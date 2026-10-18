# Phase A — source-to-paper methodology evidence and remaining acceptance gates

**Research verification memo, 18 October 2026. Not the professor submission report.**

## Authoritative evidence

- Original paper: *SPDZCoder: Combining Expert Knowledge with LLMs for Generating Privacy-Computing Code*, arXiv `2501.00363v2`, particularly §2.1, §3.1–3.2, Figure 2 and §5/Table 6.
- The **authors' immutable Zenodo archive** (`SPDZCoder.tar` SHA-256 `a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac`), not the independent reconstruction under `src/spdz_audit`.
- Earlier reviewer’s line-level original-code inspection: `research/original_source_audit.md`. Treat historical reviewed source-line observations as attributable, not as newly executed author stages.
- Seven checksum-verified **historical author stage snapshots**, each with original file path, task position, stage row SHA-256, template identity, and final code hash: [Actions 39073490709](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39073490709), artifact `12115901735` and `research/evidence/2026-10-18/seven-category-stage-receipt.json`.
- Complete authentic archived **stage-2 vs stage-3** evaluation logs and matching task identifiers: [Actions 39073915415](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39073915415), artifact `12116316330`, `research/evidence/2026-10-18/saved-stage2-stage3-audit-receipt.json`.
- Independent **fresh native stage-2** execution is **separate** and belongs in draft PR #9; it must not be confused with an LLM stage run. At this memo's creation, the complete native results were still pending.

## 1. Paper's problem and required security distinctions

The paper §2.1 and §3.1 emphasize a semantic gap between ordinary Python and MP-SPDZ, which uses secret types and data-oblivious execution. In the paper, **high-level differences** concern oblivious control flow and absent library functionality; **low-level differences** concern API names, types, syntax and corresponding operations. The ten high-level rule instances (paper Table 1) belong to the refactoring stage; the generation rule combines low-level demonstrations.

Do **not** equate data-oblivious control-flow structure with a general absence of intermediate public openings. The selected original-system D1 limitation is narrower: under a stated private-input/output-only observation policy, two permitted equal-output inputs can produce different **explicit intermediate comparison openings**. E1 fixes one supported source pattern, not the entire algorithmic privacy problem.

## 2. Exact paper-to-source crosswalk

| Paper claim / purpose | Released authors' source as inspected | Evidence strength and limits |
|---|---|---|
| Prepare real function inputs and tests | `data/process_input_data.py:15–73`; `data/input_processed_data/*.json` contains JSON Lines | All 313 original task IDs and 313 native templates hash-bound by C1; original saved input rows in seven trace artifacts |
| Figure 2: refactor Python into Canonical Form Python (CFP) | `src/pipeline-mp.py:22–68`; `src/apply_high_rules.py:23–42` | Saved stage-1 outputs exist and match tasks, but are **historical**; not fresh model responses |
| High-level rule families (math, syntax/structures, while, break/continue, branch, arrays) | `src/high_semantic_rules/hi_math_ufunc_rule.py`, `hi_DS_method_Syntax_sugar_rule.py`, `hi_while_loop_rule.py`, `hi_ocf_break_continue_rule.py`, `hi_ocf_branch_rule.py`, `hi_array_creation_indexing_manipulation_rule.py` | Original source examples inspected; several selector families apply unconditionally, while others inspect ASTs. Actual per-rule messages not preserved |
| Stage-1 selection and ordering | `src/apply_high_rules.py:23–89` | A source-level early-break discrepancy appears to discard a successful response before update; historical transformed stage-1 records cannot establish that this exact released control path created them |
| §3.2 stage 2: translate CFP to MP-SPDZ using generation rule and in-context examples | `src/apply_low_rules.py:43–104`, `src/low_semantic_rules/lo_chain_of_thought_rule.py:603–622` | Saved stage-2 candidate text is genuine but is already **post-self-reflection**, not the original pre-reflection model response |
| Dynamically selected low-level instructions | `src/apply_low_rules.py:73–100`; `src/low_semantic_rules/__init__.py:42–79` | AST selector, model yes/no classification, and substring-based public-control detection; selection conversation and billed classifier tokens not preserved |
| Self-reflection to check APIs/imports/concepts | `src/apply_low_rules.py:110–141`; `src/low_semantic_rules/lo_self_reflection_rule.py:14–59` | A genuine stage-2 snapshot is **not** evidence of individually replayed reflection; missing pre-reflection output must not be reconstructed |
| §3.2 stage 3: compile/test and feed failures back into repair | `src/apply_feedback_tc.py:54–206`; `src/feedback_rule/use_cr_error.py`; `use_functionality_message.py` | The released code resets original candidate on each attempt and does not carry replacement feedback forward as paper narrative implies. Saved stage-3 differences cannot be attributed to a particular repair transcript |
| Hyperparameters / response extraction | `utility/utils.py:115–131`; `utility/gpt_chat_api.py:13–20,70–84` | Temperature 0.7, up to three repair attempts, two archived candidate outputs; last fenced code block extraction. Historical model/deployment revision not pinned |
| Native evaluation and saved pass flags | `evaluation/evaluate_experimental-mp.py:88–99,125–164` | Exact original task/source joins and fresh MASCOT replay accepted at B2b; evaluator accepts `pass` substring anywhere in stdout unless a traceback, a known weak oracle, not a formal semantic-correctness oracle |

These references are from the earlier source audit of the **original tar**. This crosswalk does not assert independent reexecution of each original LLM call.

## 3. Seven real category stage examples (not imagined model conversations)

Each example has exactly four saved **state snapshots**: processed input → stage-1 refactored intermediate representation → stage-2 generated/post-reflection program → stage-3 final program. The authentic selected task IDs are:

- `array_test/reverse_and_concat`: candidate 0 changed from saved stage2 to final, candidate 1 unchanged.
- `loop_test/max_adjacent_product`: only candidate 1 changed.
- `branch_test/sin_or_cos`: **both** changed.
- `math_test/sigmoid`: only candidate 1 changed.
- `numpy_operation_test/array_from_intrinsic_linspace`: neither changed.
- `numpy_ufunc_test/logsumexp`: both changed.
- `syntax_test/second_largest`: only candidate 1 changed.

This is **8 changed program strings of 14**, NOT 8 confirmed repair conversations or 8 proven improvements. The saved stage2/3 code hashes and final author evaluation flags are independently checked. Missing per-rule prompts, pre-reflection generations, intermediate repair messages and retry sequencing are genuinely **unknown**.

Source/provenance discrepancy: `branch_test/sin_or_cos` records two changed candidate strings with zero saved stage-3 prompt/completion token counts. Earlier source audit also reported **50 branch candidate texts changed despite zero recorded repair token counts**; neither observation may be fixed by inventing exchanges or assuming token zeros mean no work. Raw saved stages alone do not establish a causal history.

## 4. Published results and truly reproduced scope

Paper Table 6 reports **without refactoring** 33.23% pass@1 and 45.37% pass@2 (paper-level result; no independent original no-refactoring model-generation reproduction accepted). The archived genuine **without repair** native flags have now been re-parsed: stage2 **229/313 (73.16%)** first and **261/313 (83.39%)** union; stage3 **269/313 (85.94%)** first and **288/313 (92.01%)** union. Across 626 saved candidate flags: **93 REJECT→ACCEPT, 1 ACCEPT→REJECT, 532 unchanged**, with exact archival regression `math_test/pi_to_the_x` candidate 0.

This stage comparison is **recomputed saved author results**, not a fresh randomized trial. Original stage3 programs were separately rerun under MASCOT at B2b, producing different native outcomes from archived flags in several cases. The stage2 fresh original MASCOT replay currently executing in PR #9 must remain a separately labeled result, with any disagreements preserved.

## 5. Explicit contradictions and reproduction blockers

1. Paper's qualitative description of sequential refactoring and feedback does not resolve the released source-level **success-break** and **noncarried feedback** behaviors; do not claim saved staged programs were generated by running the exact current code if that has not happened.
2. The authors' original model deployment string and released saved model label do not uniquely pin the historical exact model. API/version credentials and paid model regeneration remain **B3 BLOCKED**, pending verified availability and user's explicit separate permission.
3. The original file `requirement.txt` versus README `requirements.txt`, incomplete OS/Python/dependency pinning and missing intermediate model transcripts constrain exact environment reproduction.
4. Original native evaluator has known **false positives** and one native test without a working oracle; strict functional correctness, confidentiality and noninterference cannot be inferred from the author's `Pass the test` marker.
5. Full original source archive plus paper + seven saved stage examples give a credible *methodology explanation* and auditable archived task flow, but cannot certify internal historical model-call order or every retry.

## Phase A acceptance proposal (for independent reviewer, not automatic status promotion)

Accept **source-linked main-component methodology mapping and seven historical category output exemplars** after independently checking this memo against the published paper, authors' pinned original code and all seven saved ZIP traces. Mark source discrepancies and missing historical messages as explicit limitations, not glossed-over success. Any demand for actual historical model-call replay belongs to the separately blocked B3/R2 path; do not silently relabel archived outputs as fresh stage execution.

Do **not** set Phase A or R1/R4 to PASS merely because this memo exists. Require a second independent reviewer to confirm line anchors, missing-data boundaries, scope and any per-rule source inconsistencies. No branch merge or professor-facing report is authorized by this memo.
