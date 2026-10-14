# MANDATORY RESEARCH EXECUTION CONTRACT — LUT PhD Coding Assignment

## Mission

Act as my principal research engineer, reproducibility scientist, secure multiparty computation (MPC) researcher, experimental evaluator, and GitHub maintainer.

I am Girish Nallan Chakravathy. This project is my coding assignment from Professor Prabhat Kumar at LUT University, due **31 October 2026**.

**Your task is to complete every practical requirement of the professor's assignment through actual implementation, experiments, testing, reproducible evidence, and independent verification.**

Do not merely design a plan, prepare a report, summarize papers, or produce reassuring progress messages. Perform the engineering work, commit it to my repository, and verify the results.

### Professor's exact assignment

> Please study the provided paper and its codebase, reproduce the implementation and key experimental results, and explain the paper’s main concepts and methodology. Then identify one substantive limitation and address it through your own code modifications.
>
> Please submit a brief report describing the limitation, your proposed solution, relevant code snippets, and experimental results comparing your modified implementation with the original baseline. Please also document any difficulties encountered during reproduction.
>
> You will have until October 31st 2026, to explore the paper and codebase, conduct your experiments, and submit your report.

**Important sequencing instruction from me:**

We must complete **ALL PRACTICAL WORK FIRST**. Do not write, polish, generate, or finalize the professor-facing submission report until the original reproduction, real code modification, baseline comparisons, regression testing, and practical evidence have passed their acceptance gates.

You may maintain raw experiment logs, technical notes, methodology documentation, traceability matrices, run manifests, issue records, and an evidence index. Those are necessary practical research records, not the final report.

When all practical gates are genuinely complete, STOP and present the evidence and gate status to me. Wait for my authorization before writing the final submission report or emailing the professor.

Never mark something complete based only on its implementation existing.

---

## 1. Authoritative sources

Use these sources in priority order.

**Professor's assignment:** The exact text reproduced above defines scope and acceptance.

**Original paper:**
- arXiv: https://arxiv.org/pdf/2501.00363
- ACM publication: https://doi.org/10.1145/3845985

**Authors' official research artifacts:**
- https://zenodo.org/records/18152253
- Archive: `SPDZCoder.tar`
- Published archive size: 65,761,280 bytes
- Published MD5: `3c6d7707d7aecc051d35312f81405c66`

**My research repository:**
- https://github.com/Girish2052003/LUT-PHD-TARGET

**Known GitHub state, verified 14 October 2026:**
- `main`: `0ae96a968022325f3f678b19db1fcd69de483b70`
- Research branch: `research/authors-artifacts-20261014`
- Research head: `5ca3809f15e8e326ff2d0a9b2e23993704be3dda`
- Open PR #5: https://github.com/Girish2052003/LUT-PHD-TARGET/pull/5

Both the original-artifact workflow and the existing research-verification workflow passed at this research head.

Recheck the current remote state before any changes. These commit IDs are historical starting anchors, not permission to overwrite newer work.

### Source integrity requirements

1. Read the actual paper, appendix, official README, relevant source, original datasets, model prompts, output logs, and evaluation scripts.
2. Treat the original authors' implementation as the actual baseline.
3. Keep my independent reconstruction separate.
4. Never silently replace missing author functionality with invented code.
5. Do not equate archived-result recalculation with a fresh reproduction of the original pipeline.
6. Preserve an immutable, checksum-verified reference copy of the original implementation.
7. Do not modify official baseline code when measuring baseline performance.
8. Clearly label original-author evidence, independently regenerated evidence, and new experimental evidence.

---

## 2. Prior milestones — do not unnecessarily repeat existing work

The previous research effort already completed the following.

### M1 — Independent paper reconstruction

Existing implementation includes:

- Refactoring workflow using ten paper-inspired rule categories
- Canonical-form Python transformations
- Code generation and self-reflection interfaces
- Bounded feedback/repair loop
- Optional LLM API adapter
- Syntactic privacy checking
- Unit tests and CI

Relevant files include:

- `src/spdz_audit/paper_reconstruction.py`
- `src/spdz_audit/paper_prompts.py`
- `src/spdz_audit/model_adapter.py`
- `src/spdz_audit/spdzeval_import.py`
- `src/spdz_audit/lowering.py`

**Limitation:** This is my independent reconstruction, NOT the authors' original implementation.

### M2 — Earlier independent experiments

- Figure 4 bubble-sort correction: 0/6 cases before repair and 6/6 after repair.
- Deliberately constructed privacy-disclosure example: equivalent intended function results while one version additionally discloses a secret.
- DomainSafety-24 Python study: independently reconstructed eager baseline 4,109/7,464 cases; proposed masked version 7,464/7,464.
- MP-SPDZ cleartext-emulator numerical experiment: both variants passed 27/27 selected cases at tolerance 0.05.

**Critical limitation:** Those experiments are not sufficient evidence of improvement over the original SPDZCoder system. No numerical advantage was demonstrated in the cited MP-SPDZ emulator comparison.

Preserve these experiments, but never present them as results measured against the original authors' pipeline.

### M3 — Official artifact discovery and validation

Professor Kumar supplied the ACM and Zenodo links on 14 October.

The original archive has been downloaded and verified through GitHub Actions.

The archive contains:

- The original pipeline code
- Prompt-related material
- Benchmark inputs and test programs
- Stage outputs
- Original model/baseline outputs
- Evaluation code and saved evaluation logs
- 313 original `.mpc` test programs

Seven physical benchmark categories exist in the archive:

| Category | Original tasks |
|---|---:|
| Array | 43 |
| Loop | 97 |
| Branch | 34 |
| Math | 38 |
| NumPy operations | 32 |
| NumPy universal functions | 34 |
| Syntax | 35 |
| Total | 313 |

The paper combines the two NumPy categories (32 + 34 = 66) into one category, giving six published groups.

The processed `*.json` input files are actually JSON Lines. Preserve their original record format and identifiers.

The archive has a `requirement.txt` file, whereas its README refers to `requirements.txt`. Investigate and document this discrepancy rather than silently changing baseline dependencies.

### M4 — Original archived results reproduced

The previous work independently parsed the authors' saved evaluation flags and calculated:

- First candidate correct: 269/313 = **85.94%**
- Second candidate correct: 265/313
- At least one of the two candidates correct: 288/313 = **92.01%**
- Neither candidate correct: 25/313

Both headline percentages match the paper.

**What this proves:** A correct recalculation of the published metrics from authors' previously evaluated outcomes.

**What it does not prove:** Fresh execution of the original pipeline, new model generation, or independent secure MPC protocol results.

Relevant scripts:

- `scripts/inspect_provided_artifacts.py`
- `scripts/audit_original_archive.py`
- `scripts/reproduce_official_scores.py`
- `scripts/audit_original_privacy_indicators.py`

The latest relevant GitHub Actions run is:

https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38557115103

### M5 — Preliminary original-output privacy indicators

The earlier static audit compared two authentic generated candidates per task:

- 626 original SPDZCoder candidates
- 626 original GPT-4 baseline candidates

Syntactic results:

- SPDZCoder: 11/626 candidates contain detected reveal calls.
- GPT-4 API-documentation baseline: 182/626 candidates contain detected reveal calls.
- Parse failures: 1 SPDZCoder candidate and 6 GPT-4 baseline candidates.

**These are NOT confirmed privacy leaks.**

Some secret revelation is legitimate and necessary to obtain authorized outputs. Do not count these indicators as vulnerabilities without establishing an explicit intended-output policy and a demonstrated violation.

### M6 — Verified CI

At the latest research head, the original-artifact workflow passed and the existing research verification passed. The regression suite reported 53 passing tests.

Do not confuse these passing tests with completion of the professor's reproduction and improvement requirements.

---

## 3. First actions — mandatory repository handoff

Before creating additional implementation code:

1. Inspect all branches, pull requests, commits, files, CI configurations, workflow artifacts, and documented experiments.
2. Read PR #5 fully, not merely its title or green check.
3. Validate whether all PR #5 results are consistent with raw archived evidence.
4. Locate contradictory, outdated, or exaggerated README claims.
5. Confirm exactly which official author files are present or retrievable.
6. Verify that no original datasets, generated programs, or benchmark identifiers have been fabricated or silently modified.
7. Inspect license and redistribution conditions.
8. Create an immutable baseline provenance record with source URL, archive hash, relevant source revisions, and file manifests.
9. Compare the original authors' pipeline with my independent reconstruction at the architectural and algorithmic levels.
10. Produce a machine-checkable requirements-to-evidence ledger.

PR #5 is currently open and has passed CI. Review it carefully and merge it if valid, rather than recreating the same work. If defects exist, repair and reverify before merging.

Keep `main` as the official validated branch. Conduct risky changes on short-lived branches with PR review and CI. Use squash or merge appropriately, preserve commit history, and safely delete only genuinely merged branch refs after independent confirmation.

**Do not delete an unmerged branch or overwrite newer commits.**

---

## 4. Formal requirement traceability

Create a repository-maintained traceability ledger, preferably at:

`research/requirements/assignment_traceability.yaml`

and a readable counterpart.

Map every professor requirement to:

- Requirement ID
- Exact source sentence
- Scientific interpretation
- Concrete implementation obligation
- Concrete experimental obligation
- Expected outputs
- Acceptance criteria
- Evidence paths
- Exact commit SHA
- Test and workflow identifiers
- Measured results
- Known limitations
- Verification reviewer/independent check
- Status: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, or `PASS`

**No requirement may be marked PASS without rerunnable, inspectable evidence.**

Use at least these requirement IDs.

### R1 — Study and understand the original paper

Study all substantive components, equations, algorithms, figures, assumptions, threat model, refactoring rules, prompting procedures, repair strategy, datasets, evaluation metrics, ablations, comparative baselines and limitations.

Trace claims to exact paper sections and original source-code locations.

Explain relationships among the stages, not merely paraphrase the abstract.

**PASS:** Every major claimed component has been mapped to the authors' implementation or explicitly identified as undocumented/unavailable.

### R2 — Reproduce the original implementation

Obtain and inspect the authors' unmodified code.

Reconstruct the documented original environment and execute its actual entry points.

The original implementation must be distinguishable from my independent reconstruction at every stage.

**PASS:** The original code executes through its intended stages, or any unavailable historical dependency is explicitly recorded as a reproducibility blocker. An unsupported substitution does not count as a complete PASS.

### R3 — Reproduce key experimental results

Reproduce the original evaluation metrics and as many key experiments as reasonably possible using the official artifacts and evaluation implementation.

Archived-score recalculation is already achieved; build on it.

**PASS:** Independent evaluation using the original programs and defined correctness oracle has actually been executed, with relevant main-paper comparisons, category breakdowns, and complete logs. Do not mark the full requirement passed on archived flags alone.

### R4 — Explain the actual methodology

Demonstrate and explain the original input→refactoring→generation→reflection→repair→evaluation flow with real task examples and intermediate representations.

**PASS:** Explanations are tied to actual implementation and reproducible traces, not merely conceptual descriptions.

### R5 — Demonstrate one substantive original-system limitation

Choose a reproducible limitation in the original authors' implementation or results.

Establish its cause, affected task class, inputs, failure behavior, scope, and realistic impact.

**PASS:** There is a failing original-system case, a reproducible minimal witness, and evidence that the weakness belongs to the original system rather than my reconstructed baseline.

### R6 — Implement an original-system modification

Implement a substantive, well-scoped fix or improvement in the original authors' pipeline or a reproducible patch applied to its original source.

**PASS:** The modified implementation runs, addresses the demonstrated limitation, passes targeted tests, and preserves the original intended functionality and security assumptions within the tested scope.

### R7 — Compare original versus modified

Evaluate both systems under equivalent conditions with actual measurements.

**PASS:** The repository contains baseline and modified raw results, identical task/input configurations, comparative metrics, regressions, uncertainty/limitations, and independently reproducible comparison scripts.

### R8 — Reproduction difficulties

Record every genuine environment, dataset, dependency, model, compiler, protocol, implementation, and evaluation issue, including the resolution or remaining blocker.

**PASS:** All experiment runs and failures are traceable to their causes without hiding negative results.

### R9 — Final report readiness

Do NOT draft the final report here.

**PASS for practical readiness:** R1–R8 have reached defensible completion, or irreducible blockers have been explicitly disclosed and accepted by me as exceptions.

Only then request my authorization to write the final report.

---

## 5. Phase A — Deep source-to-paper audit

Read the complete original source and map:

- Data preparation
- Expert refactoring rules
- Selection and ordering of rules
- Canonical-form Python
- MP-SPDZ code generation
- Retrieved examples and reference prompts
- Self-reflection
- Error detection
- Feedback and repair
- Feedback-round limits
- Evaluation harness
- Test oracle
- Pass@k computation
- Token accounting
- Baseline methods
- Published ablations

Identify every important entry point and how execution propagates through files.

Check that the code implements what the paper claims. Document discrepancies as factual observations, not assumptions.

Create a runnable per-stage trace for representative tasks from all seven archive categories.

For each stage, record:

- Original input
- Intermediate output
- Model/prompt identity where available
- Actual transformation performed
- Generated MP-SPDZ source
- Compilation outcome
- Runtime outcome
- Error/repair behavior
- Final correctness judgment

No placeholder traces are acceptable.

---

## 6. Phase B — Reconstruct and execute the unmodified official baseline

Create a clean, pinned, reproducible experiment environment.

Capture:

- Operating system and runner version
- Python version
- Exact Python dependencies
- Original author artifact hashes
- MP-SPDZ commit/version
- Compiler configuration
- MPC protocol and runtime parameters
- CPU and memory resources where relevant
- Environment variables without secret values
- RNG seeds and nondeterministic settings
- Model names, versions, temperatures, sampling and API configurations if generation is used
- Timeouts and output tolerances

Inspect all downloaded code before execution. The original TAR contains embedded `.git` internals; never execute or publish that history blindly.

Use a controlled sandbox with restricted network access, memory and CPU limits. No arbitrary generated source may execute with access to credentials or sensitive files.

Run the **unmodified authors' implementation**, starting with a small, verified smoke test and progressively expanding to the full available benchmark.

### Three distinct reproduction levels

Measure and label separately:

**Level 1 — Archived-result reconstruction:** Recalculate results from saved flags and outputs. Already achieved for main pass@k metrics.

**Level 2 — Independent evaluator replay:** Feed the original archived generated programs into the original evaluation procedure, rerun compilation/execution, and independently decide correctness.

**Level 3 — Full original generation reproduction:** Execute the original source pipeline, including actual model invocations where available and authorized, and evaluate the newly generated outputs.

Do not call Level 1 a Level 2 or Level 3 success.

Historical model availability, paid credentials, or service changes might prevent exact Level 3 replication. If that happens, record the precise blocker, reproduce Level 2 exhaustively, and ask me before making any paid API calls or accepting a substitute model.

Never fabricate a replacement model response or pretend it is historical.

### Coverage targets

Attempt the whole 313-task benchmark, all seven original physical categories, with the same candidate semantics and official evaluation criteria.

Document every task attempted, skipped, failed, timed out, or not runnable.

Reproduce important main-paper comparisons, including original SPDZCoder, genuine original baselines, and ablations where supplied data and code permit.

Investigate correctness at each stage rather than merely reporting one aggregate percentage.

---

## 7. Phase C — Make the original evaluation independently auditable

Inspect the exact evaluator and test templates.

Determine precisely:

- How generated code is inserted into original `.mpc` programs
- Which compiler and runner the authors use
- How inputs enter the MPC computation
- Which outputs are revealed
- How reference outputs are compared
- What numerical tolerance or equality criterion is applied
- How compiler failures are classified
- How runtime exceptions are classified
- How timeouts are classified
- How malformed generated responses are handled
- How generated candidates are paired to tasks
- How first and second attempts are evaluated
- How incomplete results affect denominators
- How per-category scores are aggregated

The original evaluator uses an MP-SPDZ MASCOT execution path. Verify the exact command and environment from source rather than assuming our previous cleartext-emulator configuration is equivalent.

Validate whether all 313 original task programs can be executed under this environment.

Record outcomes as task-level machine-readable records:

`task_id, category, system, candidate_id, source_sha256, compile_status, runtime_status, oracle_status, output_digest, duration, failure_class, log_path`

Do not use a shared result without identifying which exact generated program produced it.

### Pass@k requirements

Recalculate:

- First-candidate pass rate
- Second-candidate pass rate
- At-least-one-candidate success for k=2
- Category-level metrics
- Overall metrics
- Numerators and denominators

Use the same pass@k meaning that the original paper/evaluator uses; distinguish simple two-candidate success union from a statistical pass@k estimator if relevant.

The known archived totals are 269/313 and 288/313. Independently check the underlying task-level identities and outcomes.

Reject missing, duplicate, malformed, misordered or mismatched task records instead of silently skipping them.

---

## 8. Phase D — Identify and justify the strongest substantive limitation

Do not choose a limitation merely because our earlier code already includes a proposed fix.

Investigate at least these candidate classes:

1. Repeated failures in the 25 original tasks where both archived candidates failed.
2. Incorrect secret-dependent branching, indexing or loop bounds.
3. Unsupported Python constructs and insufficient refactoring.
4. Incorrect or unsafe arithmetic lowering, including domain restrictions.
5. Feedback/repair stages that preserve or introduce incorrect behavior.
6. Genuine unintended public disclosure or incorrect declassification.
7. Evaluation weaknesses that permit functionally correct but confidentiality-violating generated programs.

For each proposed limitation:

- Show the exact original source path responsible.
- Provide a minimal reproducible original-system failure.
- Classify root cause.
- Estimate affected benchmark cases.
- Explain why the failure matters.
- List alternative explanations and test them.
- Compare feasibility and scientific value.

Choose **one main limitation** that is substantive, demonstrable, solvable within the assignment, and measurable against the original baseline.

A second improvement is optional and must not distract from completing the principal requirement.

### Special rule for privacy-related limitations

A detected `.reveal()` or output call is not automatically a privacy leak.

Before declaring a breach:

- Define secret and public inputs.
- Define authorized outputs.
- Define the intended declassification policy.
- Define the relevant attacker observations.
- Distinguish public branching from secret-dependent branching.
- Distinguish permitted and forbidden output.
- Check implicit control-flow and exceptional behavior.
- Test whether observable behavior can disclose more than the allowed output.
- Record false positives and false negatives.
- Provide reproducible witnesses under the stated scope.

Static AST detection alone is not proof of noninterference and may reject correct MPC code.

If no authentic privacy violation can be established, do not invent one. Select a different demonstrated limitation from the original implementation.

---

## 9. Phase E — Implement the improvement in the real original system

Start with an unmodified, pinned baseline.

Create a narrowly scoped modification to the actual original pipeline, not only `src/spdz_audit/paper_reconstruction.py`.

If redistributing original code is permitted, preserve source provenance and license requirements.

If it is not permitted, store a reproducible patch and a script that applies it to the verified original Zenodo source.

Document:

- The original code path and defect
- The exact patch
- Why it fixes the defect
- Why it should preserve other semantics
- Explicit supported and unsupported cases
- Any newly introduced assumptions
- Failure behavior
- Performance/complexity cost

Create tests before and after the modification.

Add a regression test that fails on the original implementation and passes on the modified implementation whenever that is a meaningful expected behavior.

Do not silently change benchmark inputs, evaluator tolerances, prompts, environment versions or expected outputs to obtain a higher score.

---

## 10. Phase F — Paired original-versus-modified experiments

This is the most important practical acceptance gate.

Run the original baseline and the modified original implementation with matched conditions.

### Mandatory fairness rules

Hold constant wherever applicable:

- Dataset and task IDs
- Input examples
- Authorized-output policy
- Reference outputs
- Model and checkpoint
- Prompts except the explicitly modified component
- Sampling parameters
- Number of candidates
- Random seeds where controllable
- Compiler version
- Execution protocol
- Numerical precision
- Resource budgets
- Timeout rules
- Failure classifications
- Success criteria

If the improvement necessarily changes prompts, generation or repair behavior, identify that as the experimental variable and keep other variables controlled.

Use archived candidates when testing deterministic validation or post-processing improvements. Use new model generations only when the change specifically requires generation-stage reruns and access is authorized.

Do not compare a modified pipeline using one model against a baseline using a different model and call the difference an architectural improvement.

### Mandatory measured outcomes

Measure the outcomes relevant to the selected limitation, including:

- Baseline correctness
- Modified correctness
- Corrected original failures
- New regressions
- Compiler failures
- Runtime failures
- Timeouts
- Candidate success
- pass@1 and pass@2 where valid
- Category-level results
- End-to-end performance or execution cost
- Relevant token usage and API cost, where generation is involved
- False positives/false negatives for security checks, if applicable
- Authorized-output preservation
- Original/modified behavioral disagreement

Include full failure matrices, not only positive examples.

Compute paired task-level differences; distinguish exploratory improvements from confirmed generalization. Where sample size permits, include an appropriate uncertainty estimate and paired statistical comparison. Do not manufacture statistical significance.

Perform an ablation isolating the new modification from unrelated changes.

### Essential edge cases

Consider the cases that apply to the modification:

- Empty arrays
- Single-element arrays
- Boundary indices
- Secret-dependent indices
- Duplicate values
- Negative and zero inputs
- Extreme values and numerical precision
- Division by zero
- Restricted-domain math functions
- Secret versus public values
- Nested branches and loops
- Bounded versus unbounded iteration
- Unexpected data types
- Unsupported syntax
- Malformed model output
- Output leakage
- Authorized reveals
- Unintended additional outputs
- Hidden side effects
- Runtime exceptions
- Compilation failures
- Resource exhaustion and timeouts
- Nondeterministic model outputs
- Multiple repair iterations
- False positives introduced by validation
- Cases fixed by the modified system but already correct under the baseline
- Cases passing under cleartext emulation but failing under the intended secure protocol

Do not claim universal correctness from a finite benchmark.

---

## 11. Phase G — Strong automated verification

Extend the current CI, preserving all working checks.

Build a staged workflow:

1. Source integrity and archive verification
2. Schema and dataset checks
3. Original baseline environment validation
4. Original baseline smoke tests
5. Original baseline full evaluation
6. Modified implementation unit tests
7. Modified implementation full evaluation
8. Paired comparison
9. Ablation and regression tests
10. Research artifact verification
11. Cross-check of every claimed result against raw evidence

Every measurable result must be reproducible from clean checkout and explicit source dependencies.

Required invariants:

- No invented task IDs
- No dropped failures
- No silent schema coercion
- No altered baseline source
- No altered original evaluation oracle
- No mixed historical and newly generated samples
- No duplicate count inflation
- No reuse of stale outputs as new results
- No leaked API credentials
- No invented model calls
- No incorrect denominators
- No untracked experimental parameters
- No report statement unsupported by an exact evidence artifact

If you use formal methods, define the actual properties and scope proved. Unit tests and static screening are not mathematical proof.

Do not write “formally verified” unless an identifiable theorem, model check, or other formal verification artifact supports that specific statement.

---

## 12. Repository evidence structure

Reuse the existing structure wherever sensible; avoid breaking old paths.

Create and maintain a practical experiment index with paths to:

- Original-source manifest
- Exact archive checksums
- Paper-to-code mapping
- Environment lock/pins
- Original baseline scripts
- Modification patch or code
- Complete test manifests
- Original evaluation results
- Modified evaluation results
- Per-task paired comparisons
- Ablation results
- Failure classifications
- Security-policy specifications if applicable
- Statistical analysis
- Runtime and cost measurements
- CI run IDs and logs
- Known limitations and reproduction difficulties
- Requirement traceability ledger

Prefer machine-readable JSON/JSONL/CSV as appropriate, with checksums and clear schema validation.

Preserve raw outputs and logs in GitHub Actions artifacts or another documented artifact store. GitHub Actions artifacts expire; repository evidence must provide their identifiers, checksums, retention details and a reproducible way to regenerate them.

Do not add a 65 MB source TAR, embedded `.git` history, secret files, unsafe binaries or unnecessary generated bulk data directly to the repository.

Make `README.md` accurate and current.

Do not write the final submission report in this phase.

---

## 13. Repository and communication policies

- The official repository is `Girish2052003/LUT-PHD-TARGET`.
- Do not create another competing project or reset existing history.
- Use a controlled research branch, commits, PRs and CI.
- Reuse and finish PR #5 where appropriate.
- Review before merging.
- Merge only after relevant tests pass and evidence is inspected.
- Keep `main` as the official validated state.
- Safely remove only merged, verified temporary branches.
- Preserve provenance, rollback commits and PR history.
- Do not send emails or other external messages to Professor Kumar without my separate instruction.
- Do not make paid API calls, purchase compute, or use billable services without my authorization.
- Do not expose credentials in code, logs or PRs.
- Do not execute arbitrary downloaded/generated code outside the controlled research environment.
- Preserve my earlier work instead of replacing it with a superficially cleaner rewrite.

If a requirement genuinely cannot be fulfilled because of unavailable historical models, credentials, execution infrastructure, ambiguous original data, license restrictions or irreducible scientific uncertainty, document the exact blocker, the best completed alternative, and the evidence still missing. Ask me for a decision instead of silently weakening the requirement.

---

## 14. Formal completion gate — no report until this passes

Define for each requirement \(R_i\):

\[
\operatorname{Complete}(R_i)
=
\operatorname{Implemented}(R_i)
\land
\operatorname{Executed}(R_i)
\land
\operatorname{EvidencePreserved}(R_i)
\land
\operatorname{IndependentlyChecked}(R_i)
\]

Apply this only to requirements where those predicates have a concrete, testable meaning. For explanatory requirements, replace the implementation predicate with complete source-grounded coverage.

**No task is complete merely because the code compiles, CI is green, or a script prints an expected number.**

The practical work may be declared ready for final-report drafting only when:

- The actual original implementation has been inspected and executed as required by the assigned experimental scope.
- Key original results have been independently evaluated, not merely copied.
- One substantial limitation has been reproduced on the original system.
- My own modification exists in the original-system workflow.
- The same tests have compared original versus modified behavior.
- Relevant regressions, limitations and failures are documented.
- All claimed experimental numbers have raw evidence.
- The independent audit has no unresolved critical defects.
- The requirements ledger contains no falsely closed requirements.
- Outstanding irreducible blockers, if any, have been explicitly presented to me for decision.

Even then, do not begin final report writing automatically.

### Required progress outputs

At each substantial checkpoint, tell me:

1. What you actually changed or executed
2. Exact GitHub commit/PR and CI links
3. Which professor requirements moved forward
4. What evidence proves the progress
5. What did not work
6. What remains blocked or incomplete
7. The next experiment you are actively doing

Never provide a completion percentage without a clearly defined basis.

**START NOW.** First audit PR #5 and the current repository, then move directly into execution of the genuine original pipeline and baseline evaluator. Do not stop after planning, rediscovering the paper, or repeating previously completed metadata checks.

Your ultimate deliverable for this phase is a **fully implemented, experimentally tested, independently auditable repository**, not a report or an assurance that the assignment is done.