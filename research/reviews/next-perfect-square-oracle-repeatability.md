# Native-oracle investigation: next_perfect_square repeatability (17 October 2026)

This is a practical research evidence note, **not** the final professor-facing report.

## Grounded artifacts

- Authenticated original SPDZCoder/MP-SPDZ experiment: https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39043579023
- Tested research commit: dd46d91d3f668a120e0c6cfaeb629b3e94cf6a60.
- Exact archived original task: math_test/next_perfect_square, candidate 1.
- Provenance-preserving saved execution: ZIP artifact 12105905095, digest SHA-256 74aa415f29c1ff63f21ce1d666d053abaa39eb36da7a983f0e5b9a2718987843.
- Original native template SHA-256: bc8569a164a2c89325fa7b42780049c3ee6658c70aba4b5d9071b007bd9cf2c4.
- Archived original candidate SHA-256: 11a45b3812a3c6347cd7707f6247778c1bacad3c19688251fd95016dba97b4df.
- Combined exact MPC input SHA-256: 2f4943aab62ecbdea679fdc72126c5b66875db99f929cd5a0a3f87021d5a3e35.
- Original MP-SPDZ reported compiled hash: 86cde692a9aeb0dfeb98eed8c87ad59704dbcfb1b4cf9a23dc5e99ce407e0553.

## Actual source and original oracle

The authentic generated candidate uses MP-SPDZ fixed-point square root and floor, returning the square of the next integer. Its relevant source transformation is:

```python
sqrt_x = mpc_math.sqrt(sfix(x))
int_sqrt_x = mpc_math.floor_fx(sqrt_x) + 1
next_perfect_square = int_sqrt_x * int_sqrt_x
return next_perfect_square
```

The unchanged original test evaluates secret-integer inputs 1, 10, 16 and 37 and requires the exact results 4, 16, 25 and 49. It joins four equality predicates by bitwise AND, reveals the final flag, then prints the exact marker `Pass the test` only if all four checks pass. It does **not** expose which individual equality check failed. In particular, x=16 is an exact-square boundary where a floor after an approximate square root could matter, but this remains a **hypothesis**, not a demonstrated explanation of the variance.

## Independently checked observed evidence

| Isolated native MASCOT execution | Compilation | Protocol return | Original oracle |
|---|---|---|---|
| 0 | PASS | 0 | ACCEPT |
| 1 | PASS | 0 | ACCEPT |
| 2 | PASS | 0 | ACCEPT |
| 3 | PASS | 0 | REJECT |

All four runs use identical source, input template and compiler fingerprint. Each has precisely one native attempt. Accepted stdout contains the original success marker, while the rejected stdout lacks it. All statuses and bytes are preserved and independently hash checked.

This establishes **observed repeatability failure of the exact original evaluator outcome** on a single authentic candidate. It does not establish numeric root cause, how often it occurs in the population, or a general property of MASCOT.

## Consequences for the professor assignment

- This is evidence of a baseline-evaluation reproducibility limitation, separate from the chosen intermediate-opening privacy limitation.
- Never claim baseline acceptance percentages are invariant across runs or that apparent +1/-3 pass changes were caused by our two source modifications; they occur on unchanged code.
- No new numerical instrumentation was added to this original-only run. If scientific attribution of the exact failure mechanism is essential, use a separate clearly labeled diagnostic that records the four intermediate equality outcomes, without altering the native benchmark or folding diagnostics into published pass rates.
- Keep the full 626-pair comparison and original 313-task denominator unchanged.
- The main selected improvement remains the narrow secret-comparison opening removal under an explicit private-input/output-only observation policy, with its measured multiplication and communication tradeoff.
