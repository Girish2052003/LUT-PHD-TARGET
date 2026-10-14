# Reproducing and extending SPDZCoder

I'm studying [SPDZCoder](https://arxiv.org/abs/2501.00363), which translates ordinary Python into privacy-preserving MP-SPDZ programs. My goal is to understand the original translation pipeline, reproduce its experiments where the source materials permit, and investigate whether a functionally correct translation can still introduce a privacy problem.

This repository is my working record for the coding assignment from Professor Prabhat Kumar at LUT University, due **31 October 2026**.

## Where the work stands

I've implemented and tested a reconstruction of the paper's refactoring, generation, self-reflection and repair workflow. I also reproduced the specific bubble-sort repair shown in Figure 4 and tested an additional privacy-validation step using the MP-SPDZ compiler and its cleartext emulator.

**The original release has now been located.** On 14 October Professor Kumar supplied the [published ACM paper](https://doi.org/10.1145/3845985) and the [official Zenodo artifact](https://zenodo.org/records/18152253). I downloaded and checksum-verified the authors' 65,761,280-byte archive and identified all 313 original MPC task programs, seven processed input splits, their pipeline code and generated baseline/final-stage outputs. I also independently summed the authors' saved **first-candidate** evaluation flags: **269/313 = 85.94%**, matching the published pass@1. That is a recalculation from **archived author-evaluated outcomes**, not a fresh LLM generation or secure-protocol rerun. Pass@2 recalculation and direct evaluation are separate checks in progress.

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
| Python regression tests | **44 passed at the earlier milestone**; new provenance and score-parser tests added | Pipeline behavior, experiment checks and research provenance |
| Figure 4 bubble-sort formulas | **0/6** ascending outputs before repair; **6/6** after repair | The correction illustrated in the paper works on six independently chosen permutations |
| Information-flow counterexample | Both variants returned **0** for secret inputs −3 and 5; the deliberately leaky variant also printed the secret | Matching function outputs do not rule out extra public disclosures |
| DomainSafety-24 Python study | Reconstructed eager baseline **4,109/7,464**; masked-argument version **7,464/7,464** | Improvement on a deliberately targeted Python stress set |
| DomainSafety-24 MP-SPDZ emulation | Both variants passed **27/27** selected cases in each input mode, at 0.05 absolute/relative tolerance | Compiler/emulator compatibility on selected cases; **no numerical advantage demonstrated** |

I used a pinned MP-SPDZ revision (`78fe3d8bad4e654276eb3a11a88173195e672f44`) for the compiler/emulator runs. These checks use the **cleartext emulator**, not a secure multiparty deployment or a formal security proof. The Figure 4 inputs, privacy-leak example and DomainSafety-24 tasks are my independent tests; they are **not** the original SPDZEval dataset.

The paper reports **85.94% pass@1** and **92.01% pass@2**. I have now confirmed the **85.94% first-candidate rate from the authors' saved evaluation records** (269 of 313). I have **not** regenerated the model results or independently rerun the complete MP-SPDZ MASCOT evaluation. The task-level pass@2 union audit is in progress. Deterministic input accuracy is not pass@k.

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
- [My current research report](docs/professor_submission_interim.md) — implementation, experiments and limitations.
- [Original artifact search](docs/artifact_discovery_log.md) — what I checked and what I still need.
- [Experiment log](docs/reproduction_log.md) — environment, commit pin and links to test runs.
- [Domain-safe lowering design](docs/engineering/domain_safe_lowering.md) — supported language and constraints.

## What I still need for the original reproduction

The source and original task files are now **available from the authors' Zenodo release**. My remaining work is to reconcile the native `.json`-named JSON Lines input format, independently reproduce the saved per-task success results, run the authors' original evaluator where the environment permits, and compare the added privacy validation against their unchanged generated outputs. Regenerating historic LLM outputs additionally requires API credentials and model availability; actual MASCOT runs require a separate controlled MP-SPDZ setup.

I am continuing to record results and difficulties as I work toward the 31 October submission.
