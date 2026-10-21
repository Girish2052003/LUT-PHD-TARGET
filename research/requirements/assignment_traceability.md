# Assignment requirements and evidence

Generated from `assignment_traceability.yaml` by `scripts/check_handoff.py --render`.
These are practical acceptance gates. Historical milestones do not replace original-system evidence.

| ID | Requirement | Status | Phases |
|---|---|---|---|
| R1 | Study original paper | **PASS** | A |
| R2 | Reproduce original implementation | **IN_PROGRESS** | A, B2, B3 |
| R3 | Reproduce key results | **IN_PROGRESS** | B1, B2, C, C1, B2a, B2b |
| R4 | Explain actual methodology | **PASS** | A |
| R5 | Demonstrate substantive limitation | **PASS** | D, D1 |
| R6 | Implement original-source modification | **PASS** | E, E1 |
| R7 | Compare original and modified | **PASS** | F |
| R8 | Document reproduction difficulties | **PASS** | A, B2, G |
| R9 | Final report readiness | **PASS** | G |

## R1 — Study original paper

> Please study the provided paper and its codebase, reproduce the implementation and key experimental results, and explain the paper’s main concepts and methodology.

- **Scientific interpretation:** Map all major paper claims to original code or a documented absence.
- **Implementation obligation:** Read complete paper, appendix and original source.
- **Experimental obligation:** Trace representative authentic tasks through all stages.
- **Expected outputs:** Paper-to-code map and seven task traces.
- **Acceptance criteria:** Every major component traced with exact source paths.
- **Known limitations:** Source-linked paper/implementation mapping and seven authentic archived stage snapshots accepted within the reviewed original-source scope. The exact historical LLM call sequence, pre-reflection outputs and full rule-by-rule transcripts cannot be recovered; original code contradicts idealized paper control-flow details. B3 remains blocked; the genuine no-refactoring ablation is unverified.
- **Verification reviewer:** Secondary assistant independent audit of source, published paper and raw native/original ZIPs; not an external third-party certification
- **Evidence:** `docs/deep_paper_audit.md`, `research/original_source_audit.md`, `research/reviews/integrated-independent-practical-acceptance-20261018.md`, `research/reviews/phase-a-paper-source-crosswalk-20261018.md`, `research/evidence/2026-10-18/seven-category-stage-receipt.json`
- **Evidence commit:** 990bd9f9ce0c539a949df44fbca5843fefd12e8c
- **Workflow identifiers:** https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557115103, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557128629, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557114938, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39073490709

## R2 — Reproduce original implementation

> Please study the provided paper and its codebase, reproduce the implementation and key experimental results, and explain the paper’s main concepts and methodology.

- **Scientific interpretation:** Execute author entry points in a pinned environment.
- **Implementation obligation:** Keep immutable original and separate modified source.
- **Experimental obligation:** Smoke then execute intended stages; disclose historical dependency blockers.
- **Expected outputs:** Source manifest, environment pins and run logs.
- **Acceptance criteria:** Original execution evidenced; substitutions cannot count as PASS.
- **Known limitations:** R2 remains IN_PROGRESS: original native evaluation is reproduced, but exact historical GPT-4/Azure generation is NOT REPRODUCED. The paper names gpt-4-turbo-2024-04-09; the released Azure deployment name is not a verified revision pin, and full call history is unavailable. Girish accepted this disclosed historical gap for report scope and authorized drafting on 21 October. B3 remains BLOCKED. No new model access, expenditure or substitute model is authorized.
- **Verification reviewer:** Native evaluation evidence and source/hashes reviewed in existing independent evidence records; B3 not executed or externally certified.
- **Evidence:** `research/evidence/2026-10-14/source_provenance.json`, `research/original_source_audit.md`, `research/evidence/2026-10-15/original-smoke/receipt.json`, `research/reviews/original-replay-review.md`, `research/evidence/2026-10-15/original-full/receipt.json`, `research/reviews/full-replay-evidence-review.md`, `research/reviews/integrated-independent-practical-acceptance-20261018.md`, `research/evidence/2026-10-18/stage2-original-full-independent-acceptance.json`, `research/reviews/stage2-full-original-mascot-independent-acceptance.md`, `research/evidence/2026-10-18/stage2-native-reproduction-difficulties.json`, `research/evidence/2026-10-18/phase-g-stage2-raw-secondary-independent-audit.json`, `research/reviews/phase-g-stage2-secondary-raw-audit-20261018.md`, `scripts/audit_stage2_phase_g_secondary.py`, `research/reviews/historical-gpt4-availability-and-exception-20261018.md`, `research/evidence/2026-10-18/final-attempt-original-no-refactoring-content-audit.json`, `research/reviews/phase-g-final-recovery-and-conditional-exception-review-20261018.md`, `research/evidence/2026-10-18/original-author-git-history-independent-audit.json`, `research/reviews/phase-g-original-hidden-history-independent-review-20261018.md`, `research/reviews/final-readiness-review-20261021.md`, `research/evidence/2026-10-21/final-readiness/raw-audit-acceptance.json`
- **Evidence commit:** 990bd9f9ce0c539a949df44fbca5843fefd12e8c
- **Workflow identifiers:** https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557115103, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557128629, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557114938, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38673372763, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38703569637, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39075744038, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39080161119, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39136184598, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39136978957

## R3 — Reproduce key results

> Please study the provided paper and its codebase, reproduce the implementation and key experimental results, and explain the paper’s main concepts and methodology.

- **Scientific interpretation:** Fresh original evaluation, plus archived reconstruction as separate evidence.
- **Implementation obligation:** Use exact IDs, authentic candidates and original oracle.
- **Experimental obligation:** Attempt all 313 tasks, comparative baselines and available ablations.
- **Expected outputs:** Task-level outcomes, category metrics and logs.
- **Acceptance criteria:** Independent compile/runtime/oracle evidence; archived flags alone insufficient.
- **Known limitations:** R3 remains IN_PROGRESS: historical LLM generation and the genuine SPDZCoder without-refactoring ablation are NOT REPRODUCED. The matching UniTrans/GPT-4 group is a different baseline. Original-oracle false positives, one missing native functional test and archived/fresh disagreements remain disclosed. Girish accepted both historical gaps for report scope on 21 October; the decision does not reproduce missing experiments or prove general correctness/security.
- **Verification reviewer:** Original native saved-source evaluation and archived flag evidence independently reviewed within the original oracle scope; no original historical model generation and no genuine original no-refactoring ablation certified.
- **Evidence:** `research/evidence/2026-10-14/original_saved_evaluation_metrics.json`, `research/original_source_audit.md`, `research/evidence/2026-10-14/identity_verified_scores.json`, `research/evidence/2026-10-15/original-smoke/receipt.json`, `research/reviews/original-replay-review.md`, `research/evidence/2026-10-15/original-full/receipt.json`, `research/reviews/full-replay-evidence-review.md`, `research/reviews/integrated-independent-practical-acceptance-20261018.md`, `research/evidence/2026-10-18/stage2-original-full-independent-acceptance.json`, `research/evidence/2026-10-18/saved-stage2-stage3-audit-receipt.json`, `research/evidence/2026-10-18/stage2-native-reproduction-difficulties.json`, `research/reviews/stage2-full-original-mascot-independent-acceptance.md`, `research/reviews/archived-stage2-stage3-evaluation-review.md`, `research/evidence/2026-10-18/authors-no-refactoring-inventory-review.json`, `research/evidence/2026-10-18/phase-g-stage2-raw-secondary-independent-audit.json`, `research/reviews/phase-g-stage2-secondary-raw-audit-20261018.md`, `scripts/audit_stage2_phase_g_secondary.py`, `research/reviews/historical-gpt4-availability-and-exception-20261018.md`, `research/evidence/2026-10-18/final-attempt-original-no-refactoring-content-audit.json`, `research/reviews/phase-g-final-recovery-and-conditional-exception-review-20261018.md`, `research/evidence/2026-10-18/original-author-git-history-independent-audit.json`, `research/reviews/phase-g-original-hidden-history-independent-review-20261018.md`, `research/reviews/final-readiness-review-20261021.md`, `research/evidence/2026-10-21/final-readiness/raw-audit-acceptance.json`
- **Evidence commit:** 990bd9f9ce0c539a949df44fbca5843fefd12e8c
- **Workflow identifiers:** https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557115103, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557128629, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557114938, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38673372763, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38703569637, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39073915415, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39075744038, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39080161119, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39136184598, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39136978957

## R4 — Explain actual methodology

> Please study the provided paper and its codebase, reproduce the implementation and key experimental results, and explain the paper’s main concepts and methodology.

- **Scientific interpretation:** Explain stage relationships using real implementation traces.
- **Implementation obligation:** Map input/refactor/generate/reflect/repair/evaluate entry points.
- **Experimental obligation:** Capture seven category traces without fabricated responses.
- **Expected outputs:** Source map and authentic intermediate representations.
- **Acceptance criteria:** Each explanation linked to reproducible original-source traces.
- **Known limitations:** Seven authentic saved intermediate stage snapshots and original source routes are mapped, but missing historical pre-reflection and repair conversations prevent reconstructing exact model chronology. Stage-1 early break and feedback reset discrepancies are retained. No fresh historical LLM stage claimed.
- **Verification reviewer:** Secondary assistant independent audit of source, published paper and raw native/original ZIPs; not an external third-party certification
- **Evidence:** `docs/paper_guide.md`, `research/original_source_audit.md`, `research/reviews/integrated-independent-practical-acceptance-20261018.md`, `research/reviews/phase-a-paper-source-crosswalk-20261018.md`, `research/evidence/2026-10-18/seven-category-stage-receipt.json`
- **Evidence commit:** 990bd9f9ce0c539a949df44fbca5843fefd12e8c
- **Workflow identifiers:** https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39073490709

## R5 — Demonstrate substantive limitation

> Then identify one substantive limitation and address it through your own code modifications.

- **Scientific interpretation:** A reproducible defect belonging to the original system.
- **Implementation obligation:** Investigate candidate failure classes and root causes.
- **Experimental obligation:** Minimal witness, alternatives, affected scope and impact.
- **Expected outputs:** Limitation dossier and failing original case.
- **Acceptance criteria:** Authentic original-system witness executes and is independently checked.
- **Known limitations:** Two authentic private-input/output-only disclosure witnesses under the defined observation policy; this is not proof of a deployed historical exploit, universal noninterference or disclosure for all generated code. The mixed-operand lower_bound case remains unsupported by the selected patch.
- **Verification reviewer:** Secondary assistant independent audit of source, published paper and raw native/original ZIPs; not an external third-party certification
- **Evidence:** `research/replay/native_oracle_audit.md`, `research/original_source_audit.md`, `research/limitation_candidates.md`, `research/replay/diagnostic_protocol.md`, `research/reviews/diagnostic-review.md`, `research/evidence/2026-10-15/original-diagnostics/receipt.json`, `research/reviews/diagnostic-evidence-review.md`, `research/reviews/integrated-independent-practical-acceptance-20261018.md`, `research/evidence/2026-10-15/original-diagnostics/limitation-probes/diagnostic-summary.json`
- **Evidence commit:** 990bd9f9ce0c539a949df44fbca5843fefd12e8c
- **Workflow identifiers:** https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38742644019

## R6 — Implement original-source modification

> Then identify one substantive limitation and address it through your own code modifications.

- **Scientific interpretation:** Modify authentic source or reproducibly apply a patch.
- **Implementation obligation:** Pin baseline and preserve licensed attribution.
- **Experimental obligation:** Meaningful before/after regression and scope tests.
- **Expected outputs:** Patch, source hashes, tests and run logs.
- **Acceptance criteria:** Modification addresses demonstrated failure without hidden oracle/input changes.
- **Known limitations:** Only comparison-bit products with a supported secret-integer invariant. Mixed opened-operand comparisons including lower_bound are unchanged. Full model-dependent pipeline not executed. Accepted ONLY within stated original-source/raw-native scope. Historical model regeneration and true no-refactoring original output remain unresolved; no universal correctness or security proof.
- **Verification reviewer:** Secondary assistant independent audit of source, published paper and raw native/original ZIPs; not an external third-party certification
- **Evidence:** `research/modifications/README.md`, `research/modifications/secret_arithmetic.py`, `research/modifications/original-pipeline.patch`, `research/modifications/pinned-patch-manifest.json`, `scripts/apply_original_postprocess.py`, `research/reviews/secret-arithmetic-review-findings.md`, `research/reviews/paired-smoke-preexecution-review.md`, `research/evidence/2026-10-16/paired-smoke/receipt.json`, `research/evidence/2026-10-16/paired-smoke/measurements.json`, `research/reviews/paired-smoke-evidence-review.md`, `research/reviews/integrated-independent-practical-acceptance-20261018.md`
- **Evidence commit:** 990bd9f9ce0c539a949df44fbca5843fefd12e8c
- **Workflow identifiers:** https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38958484872

## R7 — Compare original and modified

> Please submit a brief report describing the limitation, your proposed solution, relevant code snippets, and experimental results comparing your modified implementation with the original baseline.

- **Scientific interpretation:** Fair matched experiments isolate the change.
- **Implementation obligation:** Build task-level paired comparison and failure accounting.
- **Experimental obligation:** Same candidates/input/oracle/protocol; ablation, regressions and uncertainty.
- **Expected outputs:** Raw paired results, metrics and complete failure matrix.
- **Acceptance criteria:** Measured baseline and modified results independently reproducible under equal conditions.
- **Known limitations:** Full 626-pair/1,252-execution original vs patched comparison and repeatability follow-up accepted only under the original native-oracle and narrow privacy observation model. Only two candidate source programs changed, both ACCEPT→ACCEPT. Four unchanged-source controls changed native acceptance; no causal general accuracy improvement. Costs increase for measured candidates. B3 model generation unavailable.
- **Verification reviewer:** Secondary assistant independent audit of source, published paper and raw native/original ZIPs; not an external third-party certification
- **Evidence:** `scripts/replay_modified.py`, `scripts/verify_paired_replay.py`, `research/modifications/README.md`, `research/reviews/paired-smoke-preexecution-review.md`, `research/evidence/2026-10-16/paired-smoke/receipt.json`, `research/evidence/2026-10-16/paired-smoke/measurements.json`, `research/reviews/paired-smoke-evidence-review.md`, `research/reviews/integrated-independent-practical-acceptance-20261018.md`, `research/reviews/paired-full-independent-control-audit.md`, `research/reviews/phase-f-bounded-native-interpretation-20261018.md`, `research/evidence/2026-10-18/phase-g-paired-secondary-recomputed.json`, `research/reviews/phase-g-paired-secondary-recomputed-20261018.md`
- **Evidence commit:** 990bd9f9ce0c539a949df44fbca5843fefd12e8c
- **Workflow identifiers:** https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38958484872, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38989067493, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39043579023

## R8 — Document reproduction difficulties

> Please also document any difficulties encountered during reproduction.

- **Scientific interpretation:** Retain negative results and precise blockers.
- **Implementation obligation:** Maintain run manifests and difficulty log.
- **Experimental obligation:** Track environment, dependency, model, data, compiler and oracle failures.
- **Expected outputs:** Difficulty register tied to commands, logs and resolutions.
- **Acceptance criteria:** Every attempted run or failure has an inspectable cause/status.
- **Known limitations:** Documentation acceptance is independent of whether each difficulty is solved. B3 remains BLOCKED; R2/R3 remain IN_PROGRESS. Historical generation and genuine without-refactoring remain NOT REPRODUCED. Numerical variability causes and two compiler stderr classifications remain unknown. Register checks validate schema/path hashes; independent review supplies scientific assessment. Report-scope exceptions and drafting were separately accepted by Girish on 21 October.
- **Verification reviewer:** Independent r8_pr13_review assistant context checked audit code,31-artifact receipt and14R8tests at45a51e6; final documentation/governance reviewed separately in final-readiness-review-20261021.md. Not external certification.
- **Evidence:** `docs/reproduction_log.md`, `research/reviews/pr5-independent-review.md`, `research/original_source_audit.md`, `research/evidence/2026-10-15/original-smoke/receipt.json`, `research/reviews/original-replay-review.md`, `research/evidence/2026-10-15/original-full/attempt-1.json`, `research/evidence/2026-10-15/original-full/receipt.json`, `research/reviews/full-replay-evidence-review.md`, `research/reviews/integrated-independent-practical-acceptance-20261018.md`, `research/evidence/2026-10-18/stage2-original-full-independent-acceptance.json`, `research/evidence/2026-10-18/stage2-native-reproduction-difficulties.json`, `research/reviews/stage2-full-original-mascot-independent-acceptance.md`, `research/evidence/2026-10-18/phase-g-stage2-raw-secondary-independent-audit.json`, `research/reviews/phase-g-stage2-secondary-raw-audit-20261018.md`, `scripts/audit_stage2_phase_g_secondary.py`, `research/evidence/2026-10-18/final-attempt-original-no-refactoring-content-audit.json`, `research/reviews/phase-g-final-recovery-and-conditional-exception-review-20261018.md`, `research/evidence/2026-10-18/original-author-git-history-independent-audit.json`, `research/reviews/phase-g-original-hidden-history-independent-review-20261018.md`, `research/reproduction_difficulties.json`, `scripts/verify_reproduction_difficulty_coverage.py`, `scripts/audit_final_evidence.py`, `research/final_audit_artifacts.json`, `research/reviews/final-readiness-review-20261021.md`, `research/evidence/2026-10-21/final-readiness/receipt.json`, `research/evidence/2026-10-21/final-readiness/raw-audit-acceptance.json`
- **Evidence commit:** 45a51e612453bab03c34e66bd9fe8977e2290e75
- **Workflow identifiers:** https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557115103, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557128629, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557114938, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38673372763, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38703569637, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39075744038, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39080161119, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39136184598, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39136978957, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39493312087, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39493312330

## R9 — Final report readiness

> Please submit a brief report describing the limitation, your proposed solution, relevant code snippets, and experimental results comparing your modified implementation with the original baseline.

- **Scientific interpretation:** Practical report readiness with explicitly accepted historical exceptions; deliverable completion is tracked in REPORT.
- **Implementation obligation:** Check R1–R8 evidence or explicit accepted exceptions.
- **Experimental obligation:** Independent final review of every practical acceptance gate.
- **Expected outputs:** Gate summary and user authorization record, then eventual report.
- **Acceptance criteria:** R1–R8 defensibly complete or exceptions accepted; user permission before drafting.
- **Known limitations:** R9 PASS means readiness for the authorized report, not completion of missing historical experiments or approval to submit. REPORT draft/deliverable validation is in progress; no email or external submission is authorized.
- **Verification reviewer:** Prior independent code/evidence review, exact-main workflow inspection and explicit Girish response on 21 October; the report requires separate content/render review.
- **Evidence:** `HANDOFF.md`, `research/requirements/execution_contract.md`, `research/reviews/phase-g-merged-main-practical-acceptance-20261018.md`, `research/requirements/exception_decisions.json`, `research/requirements/conditional_merge_user_decision-20261018.txt`, `research/evidence/2026-10-18/final-attempt-original-no-refactoring-content-audit.json`, `research/evidence/2026-10-18/original-author-git-history-independent-audit.json`, `research/reviews/final-readiness-review-20261021.md`, `research/evidence/2026-10-21/final-readiness/permission-scope-red.log`, `research/evidence/2026-10-21/final-readiness/permission-scope-green.log`, `research/requirements/report_authorization_user_decision-20261021.txt`
- **Evidence commit:** c237aa4a6d98a16b141a9b178a046a121ea1e659
- **Workflow identifiers:** https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39137690936, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39137690949, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39541724306, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39541724468, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39541724568, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/39541724665
