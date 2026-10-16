# Independent executed diagnostic review

Reviewer: `diagnostic_review`, 16 October 2026. **GO for narrow witness
acceptance**, not for a repaired implementation or a general confidentiality claim.

Verified run 38742644019, job 116448023661, commit
`aa89eb661370480643a6637180b773d080009437`, artifact 11975569559, ZIP SHA-256
`1cec70b42babb21d12d1e430442fa31f379a5af8f75b45c8e09384eac2d809e7`.
All 133 extracted files match. All 922 author-file hashes, 36 MP-SPDZ source
hashes, evaluator hash and official runtime binary match the pins.

All 16 cases have exact source/template/insertion hashes, matching raw streams,
return code zero, and launch/completion logs for both MASCOT parties. Removing
the observer wrappers restores each original candidate's exact AST. The helper
prints existing public values and adds no opening operation.

| Authentic candidate | Private input pair | Authorized result | Observed openings |
|---|---|---:|---|
| `count_distinct` c1 | `[1,1,2]` / `[1,2,2]` | 2 / 2 | `[0,1,1]` / `[1,1,0]` |
| `lower_bound` c1, public x=4 | `[1,3,5]` / `[2,3,6]` | 1 / 1 | Differences `[3,1,-1]` / `[2,1,-2]` |

Original and observed variants preserve the authorized result. Under the stated
private-input/output-only policy, the differing public openings distinguish
inputs with equal permitted outputs. Subtracting the lower-bound differences
from public 4 reconstructs each private array.

The private-input diagnostics intentionally omit `Pass the test`, so their
original-oracle acceptance flags are false. Native acceptance of these same
archived candidates is separately established by full replay. These are authentic
candidate-level witnesses, not new model generations, historical breaches of
public benchmark constants, network packet captures, or host-compromise tests.

Four native zero-return mutations also demonstrate false acceptance. The
`pass_or_not` filename supplies the evaluator's substring despite no success
print. `median` expects 3.05/2.5 and both `second_largest` templates expect
5.4/-1.66; zero gives signed relative error -1 and satisfies the flawed checks.
They are diagnostic mutations, never counted as original model candidates.

Accepted main limitation: functionality-based acceptance can admit translated
programs that open input-dependent intermediates beyond their permitted result.
The filename and numerical-oracle weaknesses remain separate findings.
