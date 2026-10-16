# Original-system limitation probes

These are explicitly labeled diagnostics, excluded from every archived-candidate
pass-rate denominator. No model is called and no diagnostic function is described
as an author-generated response. The immutable baseline remains unchanged.

## Competing hypotheses

1. The native evaluator accepts known-wrong programs through a filename containing
   `pass` or a one-sided relative-error predicate. Use four zero-return mutations
   and four authentic archived controls with byte-identical native templates.
2. Two authentic, freshly accepted SPDZCoder candidates disclose intermediates
   beyond their intended returned result. Use their exact archived source on
   explicit diagnostic private inputs, with an observation wrapper as a separate
   variant. This is a candidate-level confidentiality test, not a claim that
   constants in the original native benchmark were secret from its authors.

The real baseline function remains `insert_compile_run` from the unchanged
author evaluator. Only its `__file__`-based lookup root is redirected to disposable
template copies. The recorder logs the actual diagnostic paths and commands.
Original source hashes are checked before and after execution.

## Confidentiality policy and observations

Party 0 owns a length-three fixed-point input array via `sfix.get_input_from(0)`.
Length is public. In `lower_bound`, x=4 is also public. The returned distinct count
or index is the sole authorized output. The observer is another honest-but-curious
MASCOT participant; a value deliberately opened to every party is observable even
if the program does not normally print it. Both parties run on one isolated test
host; this experiment does not model host or filesystem compromise.

| Authentic candidate | Input pair A / B | Permitted output | Predicted extra observation |
|---|---|---:|---|
| `loop_test/count_distinct`, candidate 1 | `[1,1,2]` / `[1,2,2]` | 2 / 2 | Opened pairwise inequality pattern differs. |
| `loop_test/lower_bound`, candidate 1 | `[1,3,5]` / `[2,3,6]` | 1 / 1 | Opened `4-arr[i]` differences reconstruct each private element. |

Run both the original function and an instrumented variant on each input pair.
The observer wraps the **result** of each existing `.reveal()` call, prints it
and returns it unchanged. It adds no `.reveal()` calls. The local synthetic
instrumentation test checks equal returned values and the original opening count;
no author code is executed on the host.

Acceptance requires all 16 diagnostic/control executions, correct identical
authorized outputs in both variants, exactly three/six observed openings per
private-input execution, traces agreeing with the underlying input relationships,
and different traces for inputs with equal permitted outputs. A successful
process alone cannot pass this gate. Failed hypotheses are preserved in the
summary and cause the workflow to fail.

The native zero mutations are additional oracle witnesses. They are not a repair,
an accuracy improvement, or a new model sample. Their native inputs, tolerances
and success-marker logic are unchanged. The expected rejection is a diagnostic
ground-truth statement based on their incorrect constant output.

## Status

Executed successfully in run `38742644019` at `aa89eb6`; all 16 cases and 133 raw
files independently checked. See `research/reviews/diagnostic-evidence-review.md`.
The selected main limitation is unintended intermediate openings in otherwise
functionally accepted candidates. A repaired implementation remains unaccepted.
The full native replay is separate at `769bb12`; diagnostic cases never affect
its benchmark denominators.
