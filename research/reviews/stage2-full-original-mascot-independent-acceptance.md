# Independent acceptance: complete authentic original-stage-2 MASCOT replay

**18 October 2026 — practical research evidence, NOT final submission report.**

## Accepted exact scope

The original author Zenodo SPDZCoder stage-2 **historically saved candidate source strings** have been compiled/executed with the unchanged original `insert_compile_run` evaluator and original 2-party MASCOT via pinned MP-SPDZ 0.3.6. The first complete [run 39075744038](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39075744038), research commit `1e3c95d5357cd8b913a11916e562b6de7d633ccb`, had **7/7 category jobs PASS** and produced **626 native candidate records / 313 distinct tasks / 644 native attempts**. Its *aggregate* job failed due to the pre-reviewed extra `stage2-full/` pathname in the artifact-only download; the failure remains visible rather than edited away.

The independent [artifact-only recovery run 39080161119](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39080161119) at `58197ee4b93c70a04cc19f4c15a319eba3b4f4d8` succeeded using **exactly the seven already completed original native category artifacts**, with **zero rerun native candidates**. Recovery output ZIP artifact `12118194181` has SHA-256 `4ba5dc8c0470c1cf02633bb4722a204558b3c3d591a863c10cb5e28c572ba12c`; it includes the unmodified original-run aggregated results, a separately recomputed all-seven raw ZIP audit, and a separate source-to-MPC audit against the genuine pinned `SPDZCoder.tar`. The original TAR SHA-256 is `a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac`.

I independently downloaded the seven source-run category ZIPs and the recovery summary. Direct raw-byte checks reconstructed all recorded candidate source, stdout/stderr and combined MPC hashes, original native acceptances, 313 distinct identities, all retries and source/environment fingerprints. The artifact-only CI additionally read the **original authors' TAR** anew, independently checked the precise 313 original test templates and 626 source strings, and verified all **626 actual compiled native `.mpc` input files contain their authentic saved stage-2 candidate source**. Both independent checkers exactly agree with the unchanged author's oracle decisions and totals.

## Native results, without exclusion or smoothing

| Metric | Original saved author stage-2 flags | Fresh unchanged-author MASCOT |
|---|---:|---:|
| First-candidate ACCEPT | **229/313** | **229/313** |
| Second-candidate ACCEPT | **213/313** | **216/313** |
| At least one candidate ACCEPT | **261/313** | **262/313** |
| Candidate records ACCEPT | **442/626** | **445/626** |

Of 626 original stage-2 candidate executions: **479 completed compilation and runtime**, 147 had **compiler failures** (no native runtime), 34 executed and failed the unchanged original oracle, and **445 were ACCEPT**. None were silently removed. All 644 raw attempt records, including retries and timeouts, remain attached to their source-run artifacts.

The three exact archived/fresh differences (each **archived REJECT → fresh ACCEPT**) are `branch_test/choice_of_the_knight` candidate 1, `math_test/pi_to_the_x` candidate 1, and `math_test/spring_rocket` candidate 1. For the branch task, the original 60-second attempt timed out; its 90-second retry ran the **same compiled program** successfully and printed the original pass marker. The two math tasks printed the pass marker in their fresh run; the precise cause of historical disagreement is **not established**. Original stage-3 native reruns have also shown outcome variability. Do **not** interpret the three differences as source edits or improved correctness from the new privacy finalizer.

## Causal and confidentiality boundaries

This **accepts real original-stage-2 native evaluator reproduction** and a complete task/candidate failure matrix, including the native-stage differences from saved author flags. It does *not* reproduce the authors' historical LLM refactoring, model generation or reflection conversations. There were no API calls, historical model replacements, changed original oracle thresholds or extra synthetic benchmark candidates.

The paper's *without repair* numbers, 229/313 and 261/313, are exactly reproduced as **archived saved flags** and closely, but not perfectly, as fresh original native results. The independent no-refactoring artifact search in PR #8 found no explicitly named genuine no-refactoring experiment; one seven-category saved group **numerically identical** to Table 6's no-refactoring 104/313 and 142/313 is actually labeled `UniTrans/GPT-4 baseline`, a **different system**, and cannot be substituted. Any claims that code transformation improved pass@k must be separated from original evaluator runtime variability and model-stage differences.

Original native test cases include known oracle weaknesses, including a missing functional oracle, signed-relative errors and the original evaluator's permissive `pass` substring check. An accepted candidate is **accepted under these published tests**, not an independent universal semantic-correctness or confidentiality proof.

## Acceptance recommendation and remaining gate

**Accept** the complete native stage-2 Level-2 reproducibility submilestone: exact authentic author texts, same native templates/oracle, seven category coverage, all failures and independent TAR-to-executed-source evidence. Preserve original red aggregate workflow plus separate green evidence recovery; do not call that a clean single-run CI completion.

**Do not automatically declare all of Phase C or R3 PASS.** Its broader obligations include residual source-level oracle interpretation, any demonstrably available other ablations, original paper-to-pipeline source review and the separately blocked historical model regeneration. Source-to-paper methodology crosswalk/available ablation inventory are in PR #8; full F source-modification evidence and control variability in PR #7, all ultimately subject to independent PR and exact requirement-ledger acceptance. The final professor-facing report stays locked until the user gives explicit authorization.

**Reproduction:** `scripts/verify_stage2_replay.py`, `scripts/audit_stage2_full_zips.py`, `scripts/check_native_stage2_mpc_against_tar.py`, the pinned native source artifacts in the machine-readable receipt, and the artifact-only GHA workflow `.github/workflows/stage2-artifact-aggregation.yml`.
