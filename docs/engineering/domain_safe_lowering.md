# Domain-safe oblivious lowering: design notes

I investigated the arithmetic-selection pattern illustrated in Section 2.2 of the SPDZCoder paper. It removes secret-dependent Python branches by evaluating both alternatives and using secret selection bits. That creates a possible problem for partial operations: an inactive square root, logarithm or division can receive an invalid argument even when its result is not selected.

## Implementation boundary

My implementation supports a deliberately small part of Python: pure scalar functions, one positional argument, numeric constants, comparisons, arithmetic, square roots, natural logarithms, division, and nested `if`/`else` returns. Unsupported syntax is rejected rather than silently guessed. Predicates are restricted to total arithmetic; functions with side effects, arrays, unbounded loops and arbitrary Python constructs are outside this lowering.

For a branch activation bit `m`, the modification substitutes a valid dummy argument in inactive paths:

```text
safe_arg = m * arg + (1 - m) * 1
```

When `m = 1`, the operation receives its normal argument. When `m = 0`, the operation receives `1`. For division, this is applied to the denominator. Nested branch activations are multiplied. The implementation preserves active-path domain failures and avoids generating a Python `if` that branches publicly on a secret.

This construction does **not** establish noninterference, numerical stability for arbitrary inputs or freedom from fixed-point overflow. The baseline in this repository is my reconstruction of the paper's illustrative eager-predication pattern, **not the authors' original translator**.

## Files and measurements

- `src/spdz_audit/lowering.py`: validated AST frontend, two lowering modes and Python/MP-SPDZ emission.
- `experiments/benchmark.json`: 24 disclosed functions spanning control cases and domain-sensitive arithmetic.
- `src/spdz_audit/experiment.py`: deterministic inputs, observable outcomes and source provenance.
- `src/spdz_audit/metrics.py`: passing-function and pass@k utilities; deterministic input accuracy must not be called pass@k.
- `scripts/run_experiments.py` and `scripts/verify_results.py`: raw observations, paired counts and SHA-256 validation.
- `scripts/check_mpspdz.py`: official MP-SPDZ compiler and cleartext-emulator checks.

The targeted Python test set contains 7,464 input pairs. The eager baseline passed 4,109, while the masked version passed 7,464. In the subsequent MP-SPDZ cleartext-emulator comparisons, **both versions passed 27 selected numerical cases per input mode**, using an absolute and relative tolerance of 0.05. I therefore cannot claim a demonstrated MP-SPDZ numerical improvement.

## How I assess changes

I preserve all boundary inputs, active-invalid-operation tests, nested activation checks and control functions. A new change must run the Python regression suite and the fixed-point compiler/emulator jobs without weakening the original assertions. I record the exact revision and logs for every run and keep the 24-function stress set separate from the unavailable original 313-task SPDZEval.

My next step for this line of work is broader fixed-point error and cost testing on new inputs, rather than treating the host-Python success rate as a universal result.
