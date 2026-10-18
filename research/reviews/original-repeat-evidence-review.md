# Independent acceptance of original-source repeatability evidence (17 October 2026)

Exact experimental run: https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39043579023

Research commit: dd46d91d3f668a120e0c6cfaeb629b3e94cf6a60
Artifact ID: 12105905095. ZIP SHA-256: 74aa415f29c1ff63f21ce1d666d053abaa39eb36da7a983f0e5b9a2718987843.
Artifact inventory: 211 files.

The independent read-only audit recomputed the exact 16 outcomes for four authentic candidates, checked original candidate and native template identities against the 313-task identity ledger, verified exact source/archive pins and common MASCOT environment, compared each raw program/stdout/stderr digest with the recorded SHA-256, extracted compiler fingerprints, checked the presence of the original native Pass the test stdout marker, and compared the regenerated outcomes with the original workflow summary. No downloaded source was executed on the audit host.

| Original candidate | ACCEPT / 4 | Decisions |
|---|---:|---|
| loop_test/standard_deviation candidate 1 | 4 | A A A A |
| math_test/next_perfect_square candidate 1 | 3 | A A A R |
| math_test/pi_to_the_x candidate 0 | 0 | R R R R |
| math_test/pi_to_the_x candidate 1 | 0 | R R R R |

Each run compiled and executed successfully and produced one original-evaluator attempt. For next_perfect_square candidate 1, the identical MPC source and compiler fingerprint yielded both accepted and rejected native results in isolated fresh original-only MASCOT runs. The accepted runs printed the original success marker; the rejected run did not.

Conclusion: ACCEPT this **narrow evidence of original-evaluator run-to-run acceptance variability**. Do not infer a numerical cause, secret-input privacy breach, universal nondeterminism, or a general second-execution effect. The previously observed four within-pair flips favoring second-run acceptance have no established causal mechanism; isolated original-only repeats do not demonstrate that pattern universally.

The privacy finalizer changed two authentic generated candidate sources in the full 626-pair replay and both retained their native acceptance. The apparent aggregate correctness change is confounded by unchanged-source variability; it is not an attributable correctness improvement. The targeted private-input smoke observation (50 intermediate candidate opening events to zero) and its documented computation/communication cost tradeoff remain separate.

Phase F: independent native-evidence consistency and reproducibility-variability subchecks are accepted in the stated scope. The main PR #6, the paper's final requirements and the report-writing gate remain open. Outstanding practical tasks: seven-category authentic methodology traces, available ablations/oracle checks, final requirement evidence reconciliation, user decision about historical LLM generation, and final independent acceptance.

To reproduce this audit, obtain the GitHub Actions artifact and verify the per-trial outcomes, environment.json, source_manifest.json, attempts and the verified summary. Do not assume a successful CI badge alone proves any confidentiality property.
