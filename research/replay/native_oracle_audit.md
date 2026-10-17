# Native oracle audit — bounded source inspection

Independent reviewer `smoke_evidence_review` inspected all 313 original native
templates from the pinned archive. These findings describe the shipped tests;
they do not establish universal numerical correctness or confidentiality.

| Criterion | Templates |
|---|---:|
| Exact/property equality, including two vector `.equal` checks | 193 |
| Direct Boolean expectation | 29 |
| Absolute error | 53 |
| Absolute relative error | 33 |
| Mixed absolute and relative (`branch_test/relu`) | 1 |
| Signed relative error without absolute value | 3 |
| Missing implementation/oracle | 1 |
| Total | 313 |

Numeric thresholds use strict `<`: 0.001 occurs in seven templates, 0.005 in
nine, 0.01 in 43, 0.05 in 31 and 0.1 in one. The mixed ReLU template uses two
thresholds; memberships therefore sum to 91 across 90 numeric templates.
All 312 implemented oracles print exactly `Pass the test` on their success path
and reveal the final flag; 148 templates also contain other reveal calls. These
calls are not by themselves evidence of prohibited disclosure.

## Original weaknesses requiring runtime witnesses

- `data/input_data/numpy_operation_test/np_basic_slicing_stride.mpc` contains
  a docstring, insertion marker and TODO, with no implemented test. Keep it in
  the 313-task denominator and disclose that no native oracle exists.
- `data/input_data/branch_test/pass_or_not.mpc` is the only filename containing
  `pass`. Compiler output prints source/schedule/bytecode paths. The original
  evaluator accepts the substring `pass` anywhere in stdout unless stderr has
  `Traceback`, ignoring the return code. Thus the filename can contaminate the
  acceptance decision even when the success-path print does not occur. This
  is a source-derived prediction, not yet an executed limitation witness.
- `branch_test/median`, `loop_test/second_largest` and
  `syntax_test/second_largest` use `(output.reveal() - expected) / expected < 0.01`
  without absolute value. A sufficiently negative signed error can satisfy this
  predicate. Test a controlled original-system witness before claiming impact.

No native template contains party-input or random calls. The archived GPT-4
candidates contain 166 parseable programs requesting party input and 53 using
randomness, with two overlapping. The archive provides no `Input-P*` values for
these examples. Replay preserves their bytes and records missing-input failures;
it does not invent inputs or silently remove example code.

This audit advances phases A/C/D; it does not close them or replace real replay.
