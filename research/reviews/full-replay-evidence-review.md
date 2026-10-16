# Independent full replay evidence review

Reviewer: `full_replay_review`, 16 October 2026. **GO for the narrow two-system
Level 2 replay**, at `769bb12ce342b814590061ef04fdffbbe19c9990`, workflow
38703569637, attempt 2. This does not close full generation, stage traces,
available ablations, all assignment requirements, or report readiness.

The reviewer used an independent parser, without importing the repository
summarizer or executing author/generated code. The audit verified all 14 raw ZIP
hashes and lengths and every byte of their 6,976 extracted files; 922 author files,
36 MP-SPDZ Git objects, the official MASCOT binary, 28 identity-source hashes,
313 native templates and 1,252 candidate hashes. No missing/duplicate record or
harness exception was found. Every combined program matches exact original
candidate insertion into the original template.

All 1,280 attempts were checked for original commands, timeout progression,
stream hashes, classifications and oracle decisions. All 893 runtime launches
have two MASCOT party logs (1,786 logs). Fourteen environments match in software,
source pins and resource limits; container image IDs differ. The recorded compiler
defaults are bit length 64 and security parameter 40. CPU model and runner version
were not captured, so wall totals are not comparative performance evidence.

| System | First / 313 | Second / 313 | Either / 313 |
|---|---:|---:|---:|
| SPDZCoder | 268 (85.62%) | 265 (84.66%) | 288 (92.01%) |
| GPT-4 API documentation | 95 (30.35%) | 112 (35.78%) | 154 (49.20%) |

These are original-evaluator acceptance counts, using the same-task candidate
union, not a statistical pass@k estimator or an independent correctness proof.

SPDZCoder: 551 compilation passes, 75 compilation failures; 550 completed
runtimes, 75 not run, one timeout. GPT-4: 314 compilation passes, 312 failures;
242 completed runtimes, 312 not run, 70 runtime failures and two timeouts.
The 70 GPT-4 runtime failures comprise 66 missing-input failures and four
nonexistent-player-2 requests. No missing inputs were invented.

| Candidate | Archived → fresh | Observed evidence |
|---|---|---|
| SPDZCoder `math_test/spring_rocket` c0 | Accept → reject | Runtime completes; no success marker. |
| GPT-4 `branch_test/pass_or_not` c0 | Reject → accept | Exit 1, missing input, no success marker; filename contaminates substring oracle. |
| GPT-4 `branch_test/elu` c0 | Accept → reject | Three exhausted timeouts. |
| GPT-4 `numpy_ufunc_test/np_ufunc_exp2` c1 | Accept → reject | Runtime completes; no success marker. |
| GPT-4 `syntax_test/array_greater_than_scalar` c1 | Accept → reject | Runtime completes; no success marker. |

Archived GPT-4 totals are 95/114/156. The baseline summary leaves GPT-4 historical
disagreements null; the independently checked comparison above supplements it.
Numeric outputs for the three completed-but-rejected disagreements were not
printed, so their precise causes remain unproven. Do not substitute a later
successful repeat into the primary run.

The missing native oracle in `np_basic_slicing_stride` remains in the denominator:
all four candidates compile and complete, but all reject. Final timeouts are
SPDZCoder `choppy_array` c0 and GPT-4 `elu` c0 / `sum_unique` c0, each exhausting
60/90/120 seconds. Twenty candidates required retries overall.

The CI and local outcome/failure-matrix files are byte-identical. Summary values
differ only by about 1.1e-11 seconds in a floating-point sum. The reviewer also
checked expected candidate/template composition, which the current automated
verifier does not itself reconstruct; that is a verifier-coverage gap to close.

Raw evidence identifiers, hashes, retention and regeneration instructions are in
`research/evidence/2026-10-15/original-full/receipt.json`.
