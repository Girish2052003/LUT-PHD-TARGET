# Reproducing and extending SPDZCoder

I'm studying [SPDZCoder](https://arxiv.org/abs/2501.00363), which translates ordinary Python into privacy-preserving MP-SPDZ programs. My goal is to understand the original translation pipeline, reproduce its experiments where the source materials permit, and investigate whether a functionally correct translation can still introduce a privacy problem.

This repository is my working record for the coding assignment from Professor Prabhat Kumar at LUT University, due **31 October 2026**.

## Where the work stands

I've implemented and tested a reconstruction of the paper's refactoring, generation, self-reflection and repair workflow. I also reproduced the specific bubble-sort repair shown in Figure 4 and tested an additional privacy-validation step using the MP-SPDZ compiler and its cleartext emulator.

**The full SPDZCoder reproduction is still open.** The paper describes a 313-task dataset called SPDZEval, but I have not obtained the authors' complete implementation or those original benchmark files. The professor's email supplied the paper URL without a separate code or dataset link, and my public searches have not located a verified release. The original published pass@1 and pass@2 figures below are therefore reference points, not scores that I measured.

## What I've implemented

| Part | What it covers | Evidence |
|---|---|---|
| Paper workflow | Ten refactoring rules, AST rule selection, canonical Python, generation, self-reflection and a bounded repair loop | `src/spdz_audit/paper_reconstruction.py`, `paper_prompts.py` |
| Model interface | Optional model adapter and API-documentation comparison interface; model responses and usage can be logged | `src/spdz_audit/model_adapter.py` |
| Privacy checks | A limited AST screen for direct reveals, unapproved output, some secret-dependent branches, loop bounds and indices | `PrivacyScreen` in `paper_reconstruction.py` |
| Benchmark preparation | Validation of original SPDZEval files, including 313 tasks and the six published category totals | `src/spdz_audit/spdzeval_import.py` |
| Additional numerical study | Domain-sensitive branch lowering, a reconstructed eager baseline and a masked-argument alternative | `src/spdz_audit/lowering.py` |

The paper's original code and complete prompts have not been recovered, so the pipeline is **my implementation based on its published description**, not a checkout of the authors' software. The scripted model responses used in the tests are fixtures, not actual LLM generations. No live model API experiments have been run yet.

## Results so far

| Experiment | Measured result | What it establishes |
|---|---|---|
| Python regression tests | **44 passed** | Implementation behavior, repair control flow, import checks and selected security checks |
| Figure 4 bubble-sort formulas | **0/6** ascending outputs before repair; **6/6** after repair | The correction illustrated in the paper works on six independently chosen permutations |
| Information-flow counterexample | Both variants returned **0** for secret inputs −3 and 5; the deliberately leaky variant also printed the secret | Matching function outputs do not rule out extra public disclosures |
| DomainSafety-24 Python study | Reconstructed eager baseline **4,109/7,464**; masked-argument version **7,464/7,464** | Improvement on a deliberately targeted Python stress set |
| DomainSafety-24 MP-SPDZ emulation | Both variants passed **27/27** selected cases in each input mode, at 0.05 absolute/relative tolerance | Compiler/emulator compatibility on selected cases; **no numerical advantage demonstrated** |

I used a pinned MP-SPDZ revision (`78fe3d8bad4e654276eb3a11a88173195e672f44`) for the compiler/emulator runs. These checks use the **cleartext emulator**, not a secure multiparty deployment or a formal security proof. The Figure 4 inputs, privacy-leak example and DomainSafety-24 tasks are my independent tests; they are **not** the original SPDZEval dataset.

For comparison, the paper reports **85.94% pass@1** and **92.01% pass@2** for SPDZCoder over SPDZEval. I have **not reproduced those results**, and I do not treat deterministic input-level accuracy as pass@k.

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

I need access to the authors' SPDZCoder codebase (including its full prompts and experiment scripts), the original **313 SPDZEval tasks with their unit tests**, and their recommended setup/model configuration. Without those materials I can test examples from the paper and run my extension, but I cannot honestly compare my work against their exact experimental baseline or reproduce their split-wise pass@k results.

I am continuing to record results and difficulties as I work toward the 31 October submission.
