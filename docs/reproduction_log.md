# Reproduction ledger

## 14 October 2026, Europe/Helsinki

- User's target repository was empty (GitHub API and git clone both confirmed).
- Read supplied arXiv v2 PDF. Main model: gpt-4-turbo-2024-04-09, temperature 0.7,
  two samples per task, maximum three repair iterations.
- Public searches for SPDZCoder/SPDZEval and the repository search returned no
  identified author code or dataset. The PDF's hyperlink annotations contain no
  author artifact URL. This records our discovery result, not a claim of absence.
- Cloned real MP-SPDZ v0.3.9 at 78fe3d8bad4e654276eb3a11a88173195e672f44.
  The paper does not identify an exact compiler commit. Our pin is a compatibility
  target and must not be called the paper's original environment.
- Python 3.12.14, 9 visible CPUs, no GPU tool, no configured OPENAI_API_KEY.
- Design decision: complete useful independent implementation and experiments
  before requesting missing artifacts or API provisioning. This cannot replace
  the original-code/313-task reproduction requirement.
- No original baseline generations or full SPDZEval results have been reproduced.
