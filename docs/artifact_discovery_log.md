# Original SPDZCoder source and SPDZEval artifact discovery ledger

**Date:** 14 October 2026. **Scope:** publicly discoverable materials and the supervisor's actual invitation email. **Conclusion:** no verifiable complete authors' repository or 313-task test archive was recovered. **This is NOT a claim that it cannot exist.**

## Verified positive evidence

- Original arXiv v2 paper: https://arxiv.org/abs/2501.00363, dated March 21, 2025, 19-page user-supplied PDF.
- The professor's October 12 invitation specified the PDF URL only. The email itself did not include a source-code attachment, a second repo URL, or the SPDZEval dataset.
- Sections 3-5 and Appendix A publish conceptual architecture, ten rule names, examples of selected prompt conversations, limited repair examples and reported aggregate scores. Several demonstration responses in the appendix are truncated with ellipses.
- The original authors describe hand-curating 313 paired functions/tests (43/97/34/38/66/35 across six splits) but no complete set is present in the supplied PDF.
- Pinned independent MP-SPDZ compatible revision used by this repository: https://github.com/data61/MP-SPDZ/commit/78fe3d8bad4e654276eb3a11a88173195e672f44. No evidence this was the original authors' compiler pin.

## Discovery searches performed

- GitHub repository-name/description search for `SPDZCoder`, `SPDZEval`, and multiword alternatives: no verified official source release found.
- GitHub indexed file search for `SPDZCoder`, `SPDZEval`, `EliminateBreak MP-SPDZ`, `FixCompilationRuntimeError`, distinctive pipeline names: no original runnable implementation located.
- GitHub public repositories associated with account `xndong` (potential author account): no identified SPDZCoder repository. Account attribution is not guaranteed and searching one account does not exhaust authors' repositories.
- Web keyword search for SPDZCoder/SPDZEval with `GitHub`, `dataset`, `Hugging Face`, `Zenodo`, `Gitee`, author names, and code availability: results led primarily to the paper abstract, research indices and unrelated MP-SPDZ repos, not a confirmed author source archive.
- arXiv abstract HTML, supplied PDF and cited reference metadata inspected; no independent code artifact URL resolved.
- Third-party AI Security Portal labels `SPDZEval` as an external dataset text but supplies **no clickable dataset archive** in the inspected page: https://aisecurity-portal.org/en/literature-database/spdzcoder-combining-expert-knowledge-with-llms-for-generating-privacy-computing-code/ . A label is not a dataset download.

## Minimum evidence required to change status

1. **Original-code provenance:** URL or emailed archive from one of the cited authors or the supervisor, exact archive checksum or Git commit, publication/license status, and execution instructions.
2. **Original benchmark:** all 313 original Python functions, MP-SPDZ references, unit tests and six split labels; validate exact identifiers, provenance and sample-level expected outputs.
3. **Original model and experiment config:** exact rule prompt text, few-shot examples, backbone version, temperature, seeds, repetition 2, max feedback 3, runtime type choices, token-usage recording and output postprocessing.
4. **Original run:** execute baseline and full pipeline on the same tasks; report per-task/per-split candidate successes, true pass@1/pass@2, repair ablation and token costs. Distinguish compile success, cleartext emulation and secure multiparty protocol.
5. **Modification comparison:** run an added privacy validation gate on the same generated samples, count catches/false positives, and compare with original functional results. Avoid claiming that a syntactic gate formally proves noninterference.

## Research ethics boundary

All generated examples in `experiments/benchmark.json`, `scripts/run_paper_reconstruction_fixtures.py` and `scripts/check_information_flow_leak.py` are **ours**. The Figure 4 swap logic is explicitly transcribed from the paper, but its six input permutations are ours. No task should be described as an original SPDZEval test merely because it resembles the paper. No randomly generated test input can be reclassified as an independent LLM sample for pass@k. Until original artifacts arrive, submission status is **PARTIAL RECONSTRUCTION**, not **FULL REPRODUCTION**.
