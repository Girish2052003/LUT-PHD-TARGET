# SPDZCoder: reproduction progress and privacy-aware validation

> **Historical 14 October draft — not the final submission.** The statements below
> describe that earlier evidence scope. Original MASCOT replay, the original-source
> privacy patch and paired experiments were subsequently completed within their
> documented limits. Use the [current difficulty log](reproduction_log.md),
> [requirement ledger](../research/requirements/assignment_traceability.md) and
> [handoff](../HANDOFF.md) for current status. Girish authorized the final draft on
> 21 October; see [final_report.md](final_report.md). This earlier text is preserved
> as a dated interim record and must not be used as the current report.

**14 October update:** Professor Kumar has since provided the [original source and benchmark on Zenodo](https://zenodo.org/records/18152253) and the [ACM version](https://doi.org/10.1145/3845985). The historical limitations in this interim report describe the state *before receiving those links*. The original package has now been checksum-verified; its 313 task programs and saved outputs were inventoried, and 269/313 first-candidate successes were independently counted from the archived evaluation records. I have **not yet** run the original secure-protocol evaluator or regenerated historic model outputs. See [original artifact reproduction](original_artifact_reproduction.md).

**Girish Nallan Chakravathy** · Research progress as of 14 October 2026  
**Paper:** Dong et al., *SPDZCoder: Combining Expert Knowledge with LLMs for Generating Privacy-Computing Code*, [arXiv:2501.00363v2](https://arxiv.org/abs/2501.00363)  
**Assignment deadline:** 31 October 2026

## 1. Understanding the paper

SPDZCoder translates Python into MP-SPDZ code by combining ten expert-derived refactoring rules with language-model generation and feedback. The first stage converts Python into Canonical Form Python (CFP), including changes for secret-dependent control flow and unsupported language constructs. The second uses relevant MP-SPDZ examples and a self-reflection pass to generate code. The third uses compilation, execution and functional errors to repair unsuccessful outputs, up to three feedback rounds.

The authors evaluate 313 SPDZEval tasks across six categories. They report **85.94% pass@1 and 92.01% pass@2** for the complete pipeline. Those numbers are the **paper's published results, not my reproduced results**.

## 2. Implementation and current reproduction

I have built a paper-based version of the refactor–generate–reflect–repair workflow, including AST rule selection, ten rule categories, bounded repair, an optional model adapter and test logging. The source is in `src/spdz_audit/paper_reconstruction.py`, `paper_prompts.py` and `model_adapter.py`.

I also reproduced the **before-and-after conditional-swap logic from Figure 4**. Using the pinned MP-SPDZ compiler and cleartext emulator, I tested the six permutations of three distinct integers. The faulty algorithm produced **0/6 correct ascending sorts**; the repaired algorithm produced **6/6**. These are my test inputs applied to an algorithm shown in the paper, not the authors' original model outputs or SPDZEval tests. The [full run and logs](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38494328178) are available.

## 3. Limitation and proposed improvement

A key limitation I am investigating is that **correct returned values do not necessarily mean the generated program preserves the intended privacy policy**. A function may compute the required output and still add an unauthorized secret reveal or secret-dependent public operation.

My proposed addition is a privacy screen between code generation/reflection and functional evaluation. It checks for explicit reveals, unapproved output calls, and selected secret-dependent branches, loop bounds and array indices. Findings are passed to the existing repair loop as concrete feedback. I have also added limited structural checks for refactoring rules that should remove particular AST constructs.

The screen is a heuristic safeguard; it does not establish full noninterference or cryptographic security.

A simplified MP-SPDZ counterexample shows the issue:

```python
# Deliberately leaking candidate: correct return value, extra public disclosure
def f(x):
    print_ln('UNAUTHORIZED_SECRET:%s', x.reveal())
    return sfix(0)

# Candidate after removing the unauthorized disclosure
def f(x):
    return sfix(0)
```

## 4. Experimental comparison

| Test | Baseline | Modified | Interpretation |
|---|---|---|---|
| Function-output check, secret input −3 | Returns 0 **and prints −3** | Returns 0, no extra print | The extra output leaks a secret despite correct return value |
| Function-output check, secret input 5 | Returns 0 **and prints 5** | Returns 0, no extra print | Same failure on a second input |
| Nine scripted pipeline cases | Functional-only fixture accepts 7 deliberately unsafe candidates | Privacy check flags and scripted repair removes all 7; two safe controls remain accepted | Tests the checker and repair interface; not a model-quality benchmark |
| Figure 4 sorting example | 0/6 ascending sorts before repair | 6/6 after repair | Reproduces the paper's illustrated correction |

The secret-output programs were **independently constructed**, compiled and run in the **official MP-SPDZ cleartext emulator** using party-0 runtime inputs. The outcome is reproducible in [GitHub Actions](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38492518496). It does **not** show that the authors' actual system generated the leaking candidate. The nine-case comparison uses scripted responses and a synthetic functional-only evaluator; no live LLM calls were made.

Separately, I tested domain-safe branch lowering on 24 targeted functions and 7,464 Python inputs. The reconstructed eager baseline passed 4,109 inputs and the modified lowering passed 7,464. However, **both variants passed all 27 selected MP-SPDZ emulator cases in each input mode** at a 0.05 absolute/relative tolerance. I therefore do not claim a measured MP-SPDZ numerical advantage from that experiment.

## 5. Difficulties and outstanding reproduction work

The professor's email supplied the paper URL but no separate code repository or dataset. I checked the paper, its supplementary prompt examples and public repository/dataset searches, but have not found a verified complete release of the authors' implementation or the 313 SPDZEval tasks and tests. The appendix contains selected examples, not all original prompts and run scripts. The paper also does not pin the exact MP-SPDZ revision used in its experiments.

As a result, I **cannot yet reproduce the complete original system, its pass@k results, refactoring/repair ablations or token accounting**. The historic model version and exact execution setup also need confirmation. The work above is a tested reconstruction and a direct reproduction of one published algorithm; it must not be confused with the original 313-task comparison.

## 6. Next experiments

Once the original code and SPDZEval materials are available, I will run the unmodified authors' baseline first, retain task-level outputs and failure logs, and then add the privacy check without changing the model, task split, repair budget or test inputs. I will compare functional pass rates, detected privacy violations, false positives and additional time/token cost. Until then, my experiments remain explicitly separate from the published SPDZEval results.

**Repository and evidence:** [LUT-PHD-TARGET](https://github.com/Girish2052003/LUT-PHD-TARGET) · [Paper analysis](deep_paper_audit.md) · [Artifact search](artifact_discovery_log.md) · [Reproduction log](reproduction_log.md)
