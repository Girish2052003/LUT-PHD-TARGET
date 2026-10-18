# Reproducing and extending SPDZCoder

<!-- PHASE_STATUS:BEGIN -->

Read [HANDOFF.md](HANDOFF.md) before continuing. **PASS is limited to the scope shown**;
it does not mean the whole assignment is finished.

| Phase | Status | Completion scope |
|---|---|---|
| M1 — Independent paper reconstruction | **PASS** | Existing paper-inspired implementation and fixture tests only; not the original authors pipeline. |
| M2 — Independent experiments | **PASS** | Recorded Figure 4, disclosure witness and DomainSafety experiments only; no improvement over authentic original established. |
| M3 — Official artifact discovery | **PASS** | Official archive metadata and checksum validated in the historical CI run. |
| M4 — Archived score reconstruction | **PASS** | Saved author booleans: first 269/313, second 265/313, union 288/313, neither 25. Exact identity gate is tracked separately in C. |
| M5 — Static original-output indicators | **PASS** | Syntactic screen only: 11/626 vs 182/626 reveal indicators; not confirmed leaks. |
| M6 — Historical regression and CI checks | **PASS** | 53 passing tests and successful historical workflows at 5ca3809 only. |
| A — Original source-to-paper audit | **PASS** | Original paper-to-source map and seven authentic saved stage examples independently accepted WITH disclosed paper/source discrepancies. No historical model calls reconstructed; B3 remains blocked. |
| B1 — Level 1: archived results | **PASS** | Archived flags only, same narrow completion as M4. |
| B2a — Original evaluator and two-party MASCOT smoke | **PASS** | One authentic archived candidate compiled, executed and accepted by unchanged author oracle; no full-benchmark claim. |
| B2b — Complete two-system archived-candidate replay | **PASS** | All1252 authentic final-stage SPDZCoder/GPT-4 candidates replayed; original acceptance counts268/265/288 and95/112/154. No new model generation or universal correctness claim. |
| B2 — Level 2: original evaluator replay | **PASS** | Level-2 authentic original evaluator reproduction accepted for 1252 final-stage SPDZCoder/GPT4 baseline candidates and 626 saved stage2 SPDZCoder candidates, all raw native MASCOT outputs checked. B3 model generation separate. |
| B3 — Level 3: original model generation | **BLOCKED** | Requires authorized credentials and verified historical model availability; no paid calls or substitute model authorized. |
| C1 — Exact archived task identity and outcome semantics | **PASS** | 313 IDs and order,1252 candidate hashes,313 template hashes and28 source-file hashes independently checked; saved-flag meaning verified. No fresh execution claimed. |
| C — Exact task identities and evaluator semantics | **PASS** | 313 original identities, all available stage2/stage3 archived scores, independent 626-candidate fresh stage2 original MASCOT replay, original oracle limitations and available ablation search accepted WITH explicit unavailable no-refactoring group. |
| D1 — Accepted authentic privacy witnesses | **PASS** | Two archived candidates distinguish private inputs with identical permitted outputs;16native/diagnostic controls independently checked under explicit policy. |
| D — Demonstrated original-system limitation | **PASS** | One authentic original-system substantive limitation accepted: candidate-level explicit intermediate comparison opening under defined private-input/output-only policy, with two runtime witnesses. Other classes not universally solved. |
| E — Patch actual original system | **PASS** | Hash-pinned patch to both authors' original pipeline entrypoints accepted within narrow supported sint mask-product transformation; target 64 executions plus full paired source-level replay, bounded fallback and original evaluator retained. |
| E1 — Accepted original-modification paired smoke | **PASS** | 32pairs/64executions;2authentictranslations preserve tested outputs and remove50observed openingevents. No full-regression or general privacy guarantee. |
| F — Paired baseline and modification comparison | **PASS** | Full fair 626-pair original-vs-patched original-native MASCOT comparison accepted WITH bounded interpretation: only 2 source changes, 4 source-identical control acceptance flips, no attributable overall correctness gain; targeted opening removal and extra protocol costs. |
| G — Practical evidence acceptance | **IN_PROGRESS** | Independent review, CI and durable evidence for every completed practical requirement. |
| REPORT — Final report readiness (writing locked) | **BLOCKED** | Practical R1–R8 accepted; report writing still requires separate explicit user authorization. |

Machine-readable state: [research/progress.json](research/progress.json).
Requirement gates: [R1–R9 ledger](research/requirements/assignment_traceability.md).
Final report writing remains locked until practical acceptance and explicit authorization.

<!-- PHASE_STATUS:END -->

I'm studying [SPDZCoder](https://arxiv.org/abs/2501.00363), which translates ordinary Python into privacy-preserving MP-SPDZ programs. My goal is to understand the original translation pipeline, reproduce its experiments where the source materials permit, and investigate whether a functionally correct translation can still introduce a privacy problem.

This repository is my working record for the coding assignment from Professor Prabhat Kumar at LUT University, due **31 October 2026**.

## Where the work stands

I've implemented and tested a reconstruction of the paper's refactoring, generation, self-reflection and repair workflow. I also reproduced the specific bubble-sort repair shown in Figure 4 and tested an additional privacy-validation step using the MP-SPDZ compiler and its cleartext emulator.

**The original release has now been located.** On 14 October Professor Kumar supplied the [published ACM paper](https://doi.org/10.1145/3845985) and the [official Zenodo artifact](https://zenodo.org/records/18152253). I downloaded and checksum-verified the authors' 65,761,280-byte archive and identified all 313 original MPC task programs, seven processed input splits, their pipeline code and generated baseline/final-stage outputs. I also independently summed the authors' saved **first-candidate** evaluation flags: **269/313 = 85.94%**, matching the published pass@1. That is a recalculation from **archived author-evaluated outcomes**, not a fresh LLM generation or secure-protocol rerun. The saved same-task union is **288/313 = 92.01%**. Exact task-identity reconciliation and fresh evaluator replay are separate gates.

## Official-source reproduction track

I keep the source-provenance and task-count evidence in [my original-artifact report](docs/original_artifact_reproduction.md). The GitHub workflow [inspects the exact published Zenodo TAR](.github/workflows/professor-artifacts.yml), checks its published MD5, and records the native benchmark/evaluation metadata. The original code is downloaded at run time and is **not silently substituted for the independently implemented code here**.

## What I've implemented

| Part | What it covers | Evidence |
|---|---|---|
| Paper workflow | Ten refactoring rules, AST rule selection, canonical Python, generation, self-reflection and a bounded repair loop | `src/spdz_audit/paper_reconstruction.py`, `paper_prompts.py` |
| Model interface | Optional model adapter and API-documentation comparison interface; model responses and usage can be logged | `src/spdz_audit/model_adapter.py` |
| Privacy checks | A limited AST screen for direct reveals, unapproved output, some secret-dependent branches, loop bounds and indices | `PrivacyScreen` in `paper_reconstruction.py` |
| Benchmark preparation | Validation of original SPDZEval files, including 313 tasks and the six published category totals | `src/spdz_audit/spdzeval_import.py` |
| Additional numerical study | Domain-sensitive branch lowering, a reconstructed eager baseline and a masked-argument alternative | `src/spdz_audit/lowering.py` |

The authors' code, dataset and prompt examples are now accessible through Zenodo, but the files under `src/spdz_audit/` remain **my independent reconstruction**, not modified copies of the authors' code. My earlier scripted responses are fixtures, not original model samples. I have not made live model API calls. I am preparing direct comparison against the authentic archived programs and test harness.

## Results so far

| Experiment | Measured result | What it establishes |
|---|---|---|
| Python regression tests | **53 passed at the reviewed `5ca3809` milestone**; subsequent checks are recorded by commit | Pipeline behavior, experiment checks and research provenance |
| Figure 4 bubble-sort formulas | **0/6** ascending outputs before repair; **6/6** after repair | The correction illustrated in the paper works on six independently chosen permutations |
| Information-flow counterexample | Both variants returned **0** for secret inputs −3 and 5; the deliberately leaky variant also printed the secret | Matching function outputs do not rule out extra public disclosures |
| DomainSafety-24 Python study | Reconstructed eager baseline **4,109/7,464**; masked-argument version **7,464/7,464** | Improvement on a deliberately targeted Python stress set |
| DomainSafety-24 MP-SPDZ emulation | Both variants passed **27/27** selected cases in each input mode, at 0.05 absolute/relative tolerance | Compiler/emulator compatibility on selected cases; **no numerical advantage demonstrated** |

I used a pinned MP-SPDZ revision (`78fe3d8bad4e654276eb3a11a88173195e672f44`) for the compiler/emulator runs. These checks use the **cleartext emulator**, not a secure multiparty deployment or a formal security proof. The Figure 4 inputs, privacy-leak example and DomainSafety-24 tasks are my independent tests; they are **not** the original SPDZEval dataset.

The paper reports **85.94% pass@1** and **92.01% pass@2**. I have now confirmed the **85.94% first-candidate rate from the authors' saved evaluation records** (269 of 313). I have **not** regenerated the model results or independently rerun the complete MP-SPDZ MASCOT evaluation. The archived same-task union is **288/313 = 92.01%**; the independent task-identity and evaluator-semantic audit is still in progress. Deterministic input accuracy is not pass@k.

## Reproduce the tests

Python 3.10+ is required.

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python scripts/run_experiments.py --output results/semantic
python scripts/verify_results.py --results results/semantic
python scripts/run_paper_reconstruction_fixtures.py --output results/paper-reconstruction-fixture.json
```

The final command uses **nine scripted examples and a deliberately simplified functional checker**. It is useful for testing the privacy-check/repair workflow, not for estimating model quality.

The MP-SPDZ tests run in [GitHub Actions](https://github.com/Girish2052003/LUT-PHD-TARGET/actions) and save the generated programs, logs and summaries. The reproducible [Figure 4 and privacy experiments](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38494328178) were successful, including compilation, cleartext execution and the runtime-input checks.

## Reading the repository

- [Paper and methodology notes](docs/paper_guide.md) — what each SPDZCoder stage does.
- [Detailed paper analysis](docs/deep_paper_audit.md) — the four research questions and reported results.
- [Historical interim draft](docs/professor_submission_interim.md) — preserved for history; not an accepted final report. Final-report work is locked by the current execution contract.
- [Original artifact search](docs/artifact_discovery_log.md) — what I checked and what I still need.
- [Experiment log](docs/reproduction_log.md) — environment, commit pin and links to test runs.
- [Domain-safe lowering design](docs/engineering/domain_safe_lowering.md) — supported language and constraints.

## What I still need for the original reproduction

The source and original task files are now **available from the authors' Zenodo release**. The native `.json`-named JSON Lines format and archived score totals are understood. Remaining work includes exact task-identity reconciliation, independent execution of the original evaluator, a demonstrated original-system limitation, and a matched comparison of a modification to the authentic baseline. Regenerating historic LLM outputs additionally requires API credentials and model availability; actual MASCOT runs require a separate controlled MP-SPDZ setup.

I am continuing to record results and difficulties as I work toward the 31 October submission.
