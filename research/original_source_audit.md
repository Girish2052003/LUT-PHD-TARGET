# Original-source audit and open reproduction findings

Audit date: 15 October 2026 (Europe/Helsinki). Source: the checksum-pinned
[SPDZCoder artifact](https://zenodo.org/records/18152253), licensed CC BY 4.0 in
its publisher metadata. Paths and line numbers below refer to the original TAR,
not this repository's independent reconstruction. Independent reviewer:
`original_source_audit`; primary agent cross-checked the evaluator and task joins.
These are technical research records, not the professor-facing final report.

## Archived outcome identities — verified

The exact native templates, processed inputs, final SPDZCoder candidates, GPT-4
API-documentation candidates and saved outcomes share all **313 IDs** and the
same record order. Seven physical splits contain 43/97/34/38/32/34/35 tasks.
`identity_verified_scores.json` records 313 template hashes, 28 source-file
hashes and 1,252 ordered candidate hashes. Reproduction command:

```bash
python scripts/reproduce_official_scores.py --tar /path/to/SPDZCoder.tar --output /tmp/identity_verified_scores.json
```

`evaluation/evaluate_experimental-mp.py:125–134` maps `response_0/1` to
`cr_0/1`; lines 144–150 compute first-candidate acceptance and the same-task
union. Lines 159–164 serialize the two flags in that order. Thus the archived
counts are **269 first, 265 second, 288 union, 25 neither**. They measure the
authors' saved evaluator decisions; they do not independently establish program
correctness or confidential execution.

The original evaluator SHA-256 is
`7b999498f06050ab4db54e19097f65cd56c09eb7446384ddca4b62165969f1a2`.

## Paper-to-source map

| Component | Original source location | Observed behavior |
|---|---|---|
| Input preparation | `data/process_input_data.py:15–73` | Extracts input/annotation/output blocks from native templates into JSON Lines. |
| Three-stage pipeline, two candidates | `src/pipeline-mp.py:22–68,82–98` | Calls refactoring, generation and optional repair; repetitions is hardcoded to two. |
| Refactoring ordering | `src/apply_high_rules.py:23–42` | Math, data structures/syntax, while, break/continue, branch, arrays; ORAM is disabled. |
| Math rules | `src/high_semantic_rules/hi_math_ufunc_rule.py:13–54` | Linear/nonlinear primitives; selector always returns the rule. |
| Syntax/data structure rules | `src/high_semantic_rules/hi_DS_method_Syntax_sugar_rule.py:7–61` | Two always-selected rules. |
| While rewriting | `src/high_semantic_rules/hi_while_loop_rule.py:8–65` | AST selection; unknown iteration counts may be left unchanged. |
| Break/continue | `src/high_semantic_rules/hi_ocf_break_continue_rule.py:8–120` | AST selection and flag-based examples. |
| Branch rewriting | `src/high_semantic_rules/hi_ocf_branch_rule.py:10–206` | Three rules for branch structure, comparisons and oblivious form. |
| Array rewriting | `src/high_semantic_rules/hi_array_creation_indexing_manipulation_rule.py:6–153` | Three demonstrations; selector always returns its rule. |
| Generation examples | `src/apply_low_rules.py:43–104`; `src/low_semantic_rules/lo_chain_of_thought_rule.py:603–622` | Three warmup exchanges plus selected logic/math/array/control/type/memory material. |
| Selection | `src/apply_low_rules.py:73–100`; `src/low_semantic_rules/__init__.py:42–79` | AST logical-operator selector; model yes/no math/array classifiers; substring check for public control. |
| Self-reflection | `src/apply_low_rules.py:110–141`; `src/low_semantic_rules/lo_self_reflection_rule.py:14–59` | Prompt checks of imports, APIs and constructs; stage-2 snapshots are already post-reflection. |
| Feedback/repair | `src/apply_feedback_tc.py:54–206` | Template insertion, MASCOT execution, error classification and repair attempts. |
| Error prompts | `src/feedback_rule/use_cr_error.py:33–65`; `use_functionality_message.py:15–44` | CFP, candidate and optionally traceback; reuses generation examples. |
| Parameters | `utility/utils.py:115–131`; stage entry functions | Three repairs by default; temperature 0.7 is hardcoded in stage functions. |
| Response extraction | `utility/gpt_chat_api.py:13–20,70–84` | Takes the last fenced code block. |

## Original defects and discrepancies to investigate

These originated as source findings and limitation candidates. The weak native
oracle now has independently accepted runtime counterexamples (D1); the remaining
source discrepancies are not automatically demonstrated benchmark failures.

1. **Stage-1 successful responses are discarded.** In
   `src/apply_high_rules.py:72–89`, the retry loop ends at line 79. The successful
   `if matches: break` at lines 80–81 exits the enclosing rule-instance loop
   before postprocessing/update. An unsuccessful response retains the old input.
   This control flow cannot explain the transformed archived stage-1 outputs.
   Source SHA-256: `d0c5b43b5c72b9fb3efd611917a14a6970b03ffc0e3749e44951d455a0da50de`.
2. **Repair does not carry forward code and feedback.**
   `src/apply_feedback_tc.py:126` resets the candidate to the original on every
   attempt; line 196 stores `_message` without updating `message`. On exhaustion,
   lines 203–206 return the original, whereas paper §3.2 describes the last
   rectified output. Source SHA-256:
   `249d3af10e7ea031450de7aa66954215d48b40919e5b28455202e63ed5e978a8`.
3. **Acceptance is a weak stdout check.**
   `evaluation/evaluate_experimental-mp.py:88–99` accepts `pass` anywhere in
   stdout unless stderr contains `Traceback`; it ignores returncode. D1 now
   preserves four known-wrong accepted native executions, including filename
   contamination and signed-relative errors. These are separate from the selected
   comparison-mask privacy modification.
4. **Generation prompt selection defects.**
   `src/apply_low_rules.py:94–96` appends data-type entries 8/9 while describing
   MemValue entries 10/11. The singleton logical-operation visitor is never reset
   between visits (`src/low_semantic_rules/__init__.py:79`,
   `src/apply_low_rules.py:77–80`).
5. **Demonstration issues.** Oblivious branching at
   `hi_ocf_branch_rule.py:107` uses `x < 3` where the source at line 91 says
   `x <= -3`; the error also appears in generation warmup. Break/continue
   demonstrations access `a[i+1]` across the full range. Establish affected scope
   before claiming benchmark failures from either issue.
6. **Token accounting is incomplete.** Classifier calls do not contribute to
   returned totals; retries generally count only the final response. Archived
   token totals cannot be equated with complete billed usage.

## Archived stage snapshots and their limits

All seven categories have input, stage-1, stage-2 and stage-3 records with
matching IDs. Representative actual records selected by the independent audit:

| Category / task | Record (1-based) | Saved stage-2 → stage-3 acceptance |
|---|---:|---|
| array / reverse_and_concat | 8 | (False, True) → (True, True) |
| branch / sin_or_cos | 1 | (True, True) → (True, True) |
| loop / max_adjacent_product | 4 | (True, False) → (True, True) |
| math / sigmoid | 5 | (True, False) → (True, True) |
| numpy_operation / array_from_intrinsic_linspace | 1 | (True, True) → (True, True) |
| numpy_ufunc / logsumexp | 3 | (False, False) → (True, True) |
| syntax / second_largest | 2 | (False, False) → (False, True) |

The standard prefixes are `data/input_processed_data/`,
`data/stage_1_IR_output/experiment-1-..._intermediate_representation.jsonl`,
`data/stage_2_SPDZ_output/experiment-1-...jsonl` and
`data/stage_3_output/experiment-1-...jsonl`. These snapshots omit per-rule
messages, pre-reflection programs, intermediate repairs, actual feedback and
complete call-level provenance. **Fifty branch candidates change from stage 2
to stage 3 while both recorded repair-token counts are zero.** The source and
saved fields do not explain those changes. Do not fabricate a causal trace to
fill this gap.

## Environment and execution difficulties

- Author scripts and `utility/utils.py:129` target **MP-SPDZ 0.3.6**. The
  official tag resolves to `6cc3fccef0904764364eb8e285519cd34028f325`.
  Earlier 0.3.9 runs are separately labeled compatibility experiments.
- The artifact does not pin OS/Python or the MP-SPDZ commit. Its `requirement.txt`
  conflicts with README references to `requirements.txt`; `tiktoken` is imported
  but not directly pinned there.
- The launch selects `azure-gpt4` mapped to deployment `gpt-4`, whereas saved
  records identify `gpt-4-turbo-2024-04-09`. The deployment revision is unpinned.
  Do not run the multi-model shell script: it also launches extra API workloads.
- Local nested Bubblewrap attempts failed with network-namespace/UID-map
  permission errors. No arbitrary generated candidate was executed as a result.
  The restricted CI Docker path subsequently enabled accepted B2a/B2b and D1
  execution. Keep that confinement for all downloaded candidates.
- The first local source download timed out after 120 seconds. Resuming the
  official download completed it; exact size, MD5 and SHA-256 matched before
  source inspection.

Status on 17 October: B2a/B2b and D1 are accepted narrow subphases. The original
pipeline modification has independently accepted targeted paired evidence (E1).
Broad B2 dependencies, complete source traces,
available ablations and full paired comparison remain open. Full model generation
needs separately authorized credentials and a documented decision about historical
model availability. The current machine-readable state is authoritative.
