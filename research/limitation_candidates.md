# Limitation candidates and initial failure investigation

This working dossier compares original-system candidates before choosing a
modification. Source-only predictions, freshly observed failures and diagnostic
witnesses are distinct. No final report or universal security claim is made.

## Candidate comparison

| Candidate class | Original evidence | Feasibility and current limitation |
|---|---|---|
| Unsupported APIs and types | Most of the 25 double-failure tasks below fail compilation with concrete original MP-SPDZ errors. | Deterministic repairs may help specific constructs; broad repair claims would require extensive semantics/edge cases. |
| Secret-dependent bounds/indexing | `last_partial_sum`, `move_to_end`, `get_subarr_by_indices`; eager array accesses in `array_subtract_2`. | Real failures; earlier independent DomainSafety experiments are not original-system evidence. |
| Arithmetic and restricted domains | `pi_to_the_x`, `entropy`, `soft_max`; native `log_and_cube` has a zero-reference division. | Distinguish unsupported APIs, numeric-domain problems and oracle defects before selecting a fix. |
| Refactoring/repair control flow | Stage 1 discards successful changes; repair resets code/feedback as documented in `original_source_audit.md`. | Real source discrepancies; generation-stage improvement needs unavailable authorized historical model calls. Offline control-flow tests cannot substitute for generation results. |
| Unintended public openings | Authentic final `count_distinct` candidate 1 opens equality-pattern bits; `lower_bound` candidate 1 opens `x-arr[i]` and distance. Both pass fresh native MASCOT replay. | Strong confidentiality candidates under an explicit output-only policy. Private-input, equal-output witnesses must execute before declaring a breach. |
| Evaluation integrity | `pass_or_not` path contaminates substring acceptance; three tests omit absolute value; one oracle is absent. | Cheap deterministic witnesses and repair comparison are possible. Correcting an evaluator is not evidence of better generated code. |
| Conflicting benchmark semantics | `multiply_first_five` reference multiplies six values; `traverse_and_sum` source uses zip while expected values use a Cartesian product. | Do not classify these solely as generator failures or silently rewrite expected outputs. |

## The 25 archived double-failure tasks

All 50 candidates were read as source. The table records the first available
fresh failures at run `38703569637`, commit `769bb12`; the two math candidates
await the failed-download retry. Raw per-attempt traces are in the matching
`original-full-spdzcoder-<split>-<commit>` artifact. Candidate numbers are 0/1.

| Task | Fresh candidate 0 / 1 evidence or pending status |
|---|---|
| array/array_and | Both return Python lists where the native template calls `.reveal()`. |
| array/array_or | Both have the same list/native-array interface mismatch. |
| array/last_partial_sum | Both use a secret `sint` in Python `range`. |
| loop/multiply_first_five | Missing argument / runtime completes but native reference multiplies six elements. |
| loop/soft_max | Secret-to-clear fixed-point conversion / nonexistent `Compiler.math` import. |
| loop/count_reverse_pair_with_break | Both define the wrong function name (`without_break`). |
| loop/choppy_array | Timeout / Python Boolean has no `.bit_and`. Timeout alone does not establish the root cause. |
| loop/impatient_merchant | Both complete but fail the native predicate; state updates require semantic diagnosis. |
| loop/array_subtract | Python Boolean `.if_else` / `.bit_and` errors; eager indexing also needs checking. |
| loop/clip | Incompatible `cint`/float comparison / undefined `upperBound`. |
| math/pi_to_the_x | Source reviewed; fresh math run initially blocked by a truncated archive download. |
| numpy_operation/cost_matrix | Missing `.dim` / calling a tuple as `.sizes()`. |
| numpy_operation/np_basic_slicing_stride | Both run but no native oracle exists (`#TODO`). |
| numpy_operation/QR_decomposition | Missing matrix `.qr` / undefined placeholder `qr_decompose`. |
| numpy_operation/find_nearest_index | Missing secret-integer `.sqrt` / wrong `Compiler.sint` import. |
| numpy_operation/max_pooling | Missing `.s_rows` / missing `.dim` APIs. |
| numpy_operation/np_diagonal | Wrong function signature / unsupported assignment (`NotImplementedError`). |
| numpy_operation/np_arange | `regint` plus float / float-to-integer conversion error. |
| numpy_ufunc/entropy | Both import nonexistent `Compiler.library.count`; later secret-index/domain issues are not reached. |
| numpy_ufunc/toy_layer | Native predicate rejects / missing array `.dot`; additional name typo is not reached. |
| syntax/move_to_end | Both require runtime/secret-register truth values during compilation. |
| syntax/traverse_and_sum | Wrong import / zip-source versus Cartesian-reference contradiction. |
| syntax/array_round | Missing `.floor` / `.round` APIs. |
| syntax/array_subtract_2 | Eager out-of-range index / Python Boolean `.if_else`. |
| syntax/get_subarr_by_indices | Secret index needs cleartext / wrong array element type. |

Task shorthand uses the original `<category>_test` directory names; exact IDs,
candidate hashes and log paths remain in machine-readable replay records.
Compilation stops at its first error, so later source concerns are hypotheses.

Static reveal counts are not privacy findings: a public-regint reveal or an
unused helper is not an executed secret disclosure. The two specific candidates
above are being tested with declared secret inputs and permitted outputs in
`research/replay/diagnostic_protocol.md` before any modification is selected.
