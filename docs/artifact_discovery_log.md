# Tracking down the original SPDZCoder code and SPDZEval data

**14 October 2026**

I need the authors' implementation and original test data to compare my changes with their results. So far, I have not found a verifiable complete source release or the 313-task SPDZEval archive. That does not mean the files are unavailable; it means I have not been able to establish where to obtain them.

## What the materials contain

Professor Kumar's 12 October email links to [arXiv:2501.00363](https://arxiv.org/abs/2501.00363), but there is no separate repository address or code/data attachment in the message. The 19-page v2 paper explains the translation method, gives ten refactoring-rule names, examples of prompts and repaired programs, and reports aggregate benchmark results. Its appendix shows selected examples, including some shortened with ellipses. I could not recover the full 313-task source/target pairs and tests from the PDF.

I have used a public MP-SPDZ checkout pinned at [`78fe3d8`](https://github.com/data61/MP-SPDZ/commit/78fe3d8bad4e654276eb3a11a88173195e672f44). This is my reproducibility choice; I have not confirmed it was the paper authors' exact compiler version.

## Searches I have made

- GitHub repositories and indexed source files for `SPDZCoder`, `SPDZEval`, the paper's distinctive refactoring-rule names and related pipeline terms.
- Public repositories that could be associated with the authors, including the `xndong` account. I have not confirmed that this account belongs to a paper author, so I do not treat that search as exhaustive.
- Web searches for the paper and its dataset alongside GitHub, Gitee, Hugging Face and Zenodo.
- The arXiv abstract page, PDF references and appendix material for an official source-code or benchmark link.
- A third-party [research listing](https://aisecurity-portal.org/en/literature-database/spdzcoder-combining-expert-knowledge-with-llms-for-generating-privacy-computing-code/) mentioning SPDZEval, which did not provide a usable dataset archive when checked.

These searches did not establish an official download. I have kept the relevant original-paper information in [my paper analysis](deep_paper_audit.md).

## Materials required for an exact comparison

1. **Original code:** the authors' SPDZCoder source repository or archive, commit or version, complete expert-rule prompts, generation/repair scripts and permission to use the materials.
2. **Original tests:** the 313 SPDZEval Python/MP-SPDZ pairs, expected results, unit tests and six category labels (array 43, loop 97, branch 34, math 38, NumPy 66 and syntax 35).
3. **Execution setup:** the intended MP-SPDZ version and instructions, the model/version and prompt settings, two-sample evaluation configuration, repair budget and any original outputs or token-accounting scripts.
4. **Comparison protocol:** the same program inputs, test harness and generation budgets for the unmodified implementation and my added privacy checks.

Once I have these, I can measure the original baseline first and then test the modification under matching conditions.

## How I am labeling my current work

The 24 functions in `experiments/benchmark.json`, the nine scripted pipeline examples and the additional secret-reveal counterexample are my own experiments; **they are not SPDZEval**. I reproduced the Figure 4 conditional-swap logic from the paper, but used independently chosen inputs. Until I obtain the original code and test files, I will describe the project as a **paper-based reconstruction with independently tested extensions**, not a complete reproduction of the published pass@k scores.

The source/data dependency is tracked in [issue #2](https://github.com/Girish2052003/LUT-PHD-TARGET/issues/2).
