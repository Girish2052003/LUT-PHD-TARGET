# Assignment requirements and evidence

Generated from `assignment_traceability.yaml` by `scripts/check_handoff.py --render`.
These are practical acceptance gates. Historical milestones do not replace original-system evidence.

| ID | Requirement | Status | Phases |
|---|---|---|---|
| R1 | Study original paper | **IN_PROGRESS** | A |
| R2 | Reproduce original implementation | **IN_PROGRESS** | A, B2, B3 |
| R3 | Reproduce key results | **IN_PROGRESS** | B1, B2, C, C1, B2a |
| R4 | Explain actual methodology | **IN_PROGRESS** | A |
| R5 | Demonstrate substantive limitation | **IN_PROGRESS** | D |
| R6 | Implement original-source modification | **NOT_STARTED** | E |
| R7 | Compare original and modified | **NOT_STARTED** | F |
| R8 | Document reproduction difficulties | **IN_PROGRESS** | A, B2, B3, G |
| R9 | Final report readiness | **BLOCKED** | REPORT |

## R1 — Study original paper

> Please study the provided paper and its codebase, reproduce the implementation and key experimental results, and explain the paper’s main concepts and methodology.

- **Scientific interpretation:** Map all major paper claims to original code or a documented absence.
- **Implementation obligation:** Read complete paper, appendix and original source.
- **Experimental obligation:** Trace representative authentic tasks through all stages.
- **Expected outputs:** Paper-to-code map and seven task traces.
- **Acceptance criteria:** Every major component traced with exact source paths.
- **Known limitations:** Paper audit exists; source mapping incomplete.
- **Verification reviewer:** Pending requirement acceptance; historical audit reviewed by code_review agent
- **Evidence:** `docs/deep_paper_audit.md`, `research/original_source_audit.md`
- **Evidence commit:** 8d9cf2e5125fbcb8255e30c1e5b8841324223461
- **Workflow identifiers:** https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557115103, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557128629, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557114938

## R2 — Reproduce original implementation

> Please study the provided paper and its codebase, reproduce the implementation and key experimental results, and explain the paper’s main concepts and methodology.

- **Scientific interpretation:** Execute author entry points in a pinned environment.
- **Implementation obligation:** Keep immutable original and separate modified source.
- **Experimental obligation:** Smoke then execute intended stages; disclose historical dependency blockers.
- **Expected outputs:** Source manifest, environment pins and run logs.
- **Acceptance criteria:** Original execution evidenced; substitutions cannot count as PASS.
- **Known limitations:** Archive retrieved; full generation needs credentials/model availability.
- **Verification reviewer:** Pending requirement acceptance; historical audit reviewed by code_review agent
- **Evidence:** `research/evidence/2026-10-14/source_provenance.json`, `research/original_source_audit.md`, `research/evidence/2026-10-15/original-smoke/receipt.json`, `research/reviews/original-replay-review.md`
- **Evidence commit:** 554522da16fc22fd008b3f5b4c0a5bb6c62a5d45
- **Workflow identifiers:** https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557115103, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557128629, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557114938, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38673372763

## R3 — Reproduce key results

> Please study the provided paper and its codebase, reproduce the implementation and key experimental results, and explain the paper’s main concepts and methodology.

- **Scientific interpretation:** Fresh original evaluation, plus archived reconstruction as separate evidence.
- **Implementation obligation:** Use exact IDs, authentic candidates and original oracle.
- **Experimental obligation:** Attempt all 313 tasks, comparative baselines and available ablations.
- **Expected outputs:** Task-level outcomes, category metrics and logs.
- **Acceptance criteria:** Independent compile/runtime/oracle evidence; archived flags alone insufficient.
- **Known limitations:** Smoke is not full replay. One native template has no oracle; historical generation requires separately authorized model access.
- **Verification reviewer:** Pending requirement acceptance; historical audit reviewed by code_review agent
- **Evidence:** `research/evidence/2026-10-14/original_saved_evaluation_metrics.json`, `research/original_source_audit.md`, `research/evidence/2026-10-14/identity_verified_scores.json`, `research/evidence/2026-10-15/original-smoke/receipt.json`, `research/reviews/original-replay-review.md`
- **Evidence commit:** 554522da16fc22fd008b3f5b4c0a5bb6c62a5d45
- **Workflow identifiers:** https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557115103, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557128629, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557114938, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38673372763

## R4 — Explain actual methodology

> Please study the provided paper and its codebase, reproduce the implementation and key experimental results, and explain the paper’s main concepts and methodology.

- **Scientific interpretation:** Explain stage relationships using real implementation traces.
- **Implementation obligation:** Map input/refactor/generate/reflect/repair/evaluate entry points.
- **Experimental obligation:** Capture seven category traces without fabricated responses.
- **Expected outputs:** Source map and authentic intermediate representations.
- **Acceptance criteria:** Each explanation linked to reproducible original-source traces.
- **Known limitations:** Conceptual notes exist; original-source traces incomplete.
- **Verification reviewer:** Pending requirement acceptance; historical audit reviewed by code_review agent
- **Evidence:** `docs/paper_guide.md`, `research/original_source_audit.md`
- **Evidence commit:** 8d9cf2e5125fbcb8255e30c1e5b8841324223461
- **Workflow identifiers:** Pending

## R5 — Demonstrate substantive limitation

> Then identify one substantive limitation and address it through your own code modifications.

- **Scientific interpretation:** A reproducible defect belonging to the original system.
- **Implementation obligation:** Investigate candidate failure classes and root causes.
- **Experimental obligation:** Minimal witness, alternatives, affected scope and impact.
- **Expected outputs:** Limitation dossier and failing original case.
- **Acceptance criteria:** Authentic original-system witness executes and is independently checked.
- **Known limitations:** Source-grounded oracle/repair candidates; runtime witness and selection still pending.
- **Verification reviewer:** Pending requirement acceptance; historical audit reviewed by code_review agent
- **Evidence:** `research/replay/native_oracle_audit.md`, `research/original_source_audit.md`, `research/limitation_candidates.md`, `research/replay/diagnostic_protocol.md`, `research/reviews/diagnostic-review.md`
- **Evidence commit:** Pending
- **Workflow identifiers:** Pending

## R6 — Implement original-source modification

> Then identify one substantive limitation and address it through your own code modifications.

- **Scientific interpretation:** Modify authentic source or reproducibly apply a patch.
- **Implementation obligation:** Pin baseline and preserve licensed attribution.
- **Experimental obligation:** Meaningful before/after regression and scope tests.
- **Expected outputs:** Patch, source hashes, tests and run logs.
- **Acceptance criteria:** Modification addresses demonstrated failure without hidden oracle/input changes.
- **Known limitations:** No qualifying original-source patch accepted yet.
- **Verification reviewer:** Pending requirement acceptance; historical audit reviewed by code_review agent
- **Evidence:** Pending
- **Evidence commit:** Pending
- **Workflow identifiers:** Pending

## R7 — Compare original and modified

> Please submit a brief report describing the limitation, your proposed solution, relevant code snippets, and experimental results comparing your modified implementation with the original baseline.

- **Scientific interpretation:** Fair matched experiments isolate the change.
- **Implementation obligation:** Build task-level paired comparison and failure accounting.
- **Experimental obligation:** Same candidates/input/oracle/protocol; ablation, regressions and uncertainty.
- **Expected outputs:** Raw paired results, metrics and complete failure matrix.
- **Acceptance criteria:** Measured baseline and modified results independently reproducible under equal conditions.
- **Known limitations:** Independent DomainSafety results do not satisfy this requirement.
- **Verification reviewer:** Pending requirement acceptance; historical audit reviewed by code_review agent
- **Evidence:** Pending
- **Evidence commit:** Pending
- **Workflow identifiers:** Pending

## R8 — Document reproduction difficulties

> Please also document any difficulties encountered during reproduction.

- **Scientific interpretation:** Retain negative results and precise blockers.
- **Implementation obligation:** Maintain run manifests and difficulty log.
- **Experimental obligation:** Track environment, dependency, model, data, compiler and oracle failures.
- **Expected outputs:** Difficulty register tied to commands, logs and resolutions.
- **Acceptance criteria:** Every attempted run or failure has an inspectable cause/status.
- **Known limitations:** Initial failures documented; execution and full failure inventory ongoing.
- **Verification reviewer:** Pending requirement acceptance; historical audit reviewed by code_review agent
- **Evidence:** `docs/reproduction_log.md`, `research/reviews/pr5-independent-review.md`, `research/original_source_audit.md`, `research/evidence/2026-10-15/original-smoke/receipt.json`, `research/reviews/original-replay-review.md`, `research/evidence/2026-10-15/original-full/attempt-1.json`
- **Evidence commit:** 554522da16fc22fd008b3f5b4c0a5bb6c62a5d45
- **Workflow identifiers:** https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557115103, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557128629, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557114938, https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38673372763

## R9 — Final report readiness

> Please submit a brief report describing the limitation, your proposed solution, relevant code snippets, and experimental results comparing your modified implementation with the original baseline.

- **Scientific interpretation:** Practical readiness only; report is explicitly deferred by user.
- **Implementation obligation:** Check R1–R8 evidence or explicit accepted exceptions.
- **Experimental obligation:** Independent final review of every practical acceptance gate.
- **Expected outputs:** Gate summary and user authorization record, then eventual report.
- **Acceptance criteria:** R1–R8 defensibly complete or exceptions accepted; user permission before drafting.
- **Known limitations:** No accepted practical exceptions and no report authorization.
- **Verification reviewer:** Pending requirement acceptance; historical audit reviewed by code_review agent
- **Evidence:** `HANDOFF.md`, `research/requirements/execution_contract.md`
- **Evidence commit:** Pending
- **Workflow identifiers:** Pending
