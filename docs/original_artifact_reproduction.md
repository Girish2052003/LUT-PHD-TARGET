# Official SPDZCoder artifacts: source and reproduction status

**Girish Nallan Chakravathy — 14 October 2026**

Professor Prabhat Kumar provided the authors' research materials in his 14 October email.

- [ACM published paper](https://doi.org/10.1145/3845985): *SPDZCoder: Combining Expert Knowledge with LLMs for Generating Privacy-Computing Code*.
- [Zenodo record 18152253](https://zenodo.org/records/18152253): *SPDZCoder Artifacts*.
- Published TAR file: `SPDZCoder.tar`; 65,761,280 bytes; **MD5** `3c6d7707d7aecc051d35312f81405c66`. Downloaded SHA-256: `a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac`. The MD5 is used for comparison with the publisher's metadata, not as a new security claim.

## What I verified directly

A reproducible GitHub runner downloaded the official archive, checked its published checksum and inspected its TAR members without executing code from the release.

- **2,157** archived regular files, including embedded Git metadata and cached bytecode.
- **313** native MPC test programs under `data/input_data`.
- On-disk task distribution: 43 array, 97 loop, 34 branch, 38 math, 32 NumPy operations, 34 NumPy universal functions, 35 syntax. This matches all six paper totals when the two NumPy groups are combined (66).
- **Seven** processed input files under `data/input_processed_data`, named `*.json` but formatted as **JSON Lines**. They cannot be parsed with a single ordinary `json.loads()` call.
- **Seven** final-stage experimental output files, with a total of **313 task records**. Each row includes `test_name`, `response_0`, `response_1`, and both candidates' prompt/completion token fields.
- Seven matching GPT-4 baseline output files and other model baseline records.
- Original implementation in `src/pipeline-mp.py`, `src/apply_high_rules.py`, `src/apply_low_rules.py` and `src/apply_feedback_tc.py`, together with evaluation scripts under `evaluation/`.

The release uses `requirement.txt` (singular), although the README's installation example refers to `requirements.txt` (plural). Its pinned dependency file contains many packages unrelated to the simplest saved-results analysis; I will avoid installing all dependencies merely to count archived results.

## Original experimental evidence recovered

The authors' saved final-stage evaluation logs report the following numbers of **correct first candidates**:

| Group | Correct / original tasks |
|---|---:|
| Array | 36 / 43 |
| Loop | 82 / 97 |
| Branch | 34 / 34 |
| Math | 36 / 38 |
| NumPy operations | 24 / 32 |
| NumPy universal functions | 31 / 34 |
| Syntax | 26 / 35 |
| **Total** | **269 / 313 = 85.94%** |

This agrees with the paper's reported first-candidate result. It is an **independent count of the authors' previously evaluated flags**, not a new invocation of the model or a rerun of their MPC protocol. Each task has two saved candidates; `scripts/reproduce_official_scores.py` recalculates pass@1 and pass@2 from those flags, including the **same-task union** for pass@2. The reported pass@2 target is 92.01%; the new independent run must succeed before I treat that value as recalculated.

## Repeat the provenance and saved-score checks

The GitHub workflow `.github/workflows/professor-artifacts.yml` downloads and checks the published archive, runs the native-data audit, and saves source/score manifests as workflow artifacts.

For an already downloaded, checksum-matching archive:

```bash
python scripts/audit_original_archive.py --tar /path/to/SPDZCoder.tar
python scripts/reproduce_official_scores.py --tar /path/to/SPDZCoder.tar
```

These commands **do not run downloaded source code, invoke an LLM, or run MASCOT**. The authors' evaluator normally inserts generated functions into task `.mpc` templates and calls MP-SPDZ `Scripts/compile-run.py -E mascot`. Repeating those computations requires its own sandboxed compiler/protocol setup and resource controls.

## Reproduction limitations still open

My `paper_reconstruction.py` and domain-safe branch-masking frontend were written before the author release was located; they are **not** a copy of the original authors' implementation. They remain useful as independent extensions and controls but must not be mistaken for an authentic baseline.

I next need to compare the official generated output with the original evaluation criteria, independently execute a controlled set of MPC tasks, document any missing dependencies, and apply the privacy screen to the **same original generated candidates**. The screen is syntactic and may report legitimate authorized reveals; its results require careful manual classification and cannot establish full noninterference.

No paid LLM calls or new secure-protocol executions were made as part of these source audits.
