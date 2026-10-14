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

### Independent verification milestones (not SPDZEval)

- GitHub Actions [38488603949](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38488603949): 22/22 tests; 24 functions, 7,464 identical input pairs; reconstructed host-Python baseline 4,109 passes (3,355 exceptions), domain-safe extension 7,464 passes. Independent raw observation/manifest and SHA-256 verification passed.
- GitHub Actions [38488848728](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38488848728): genuine pinned MP-SPDZ compiler accepted eight invoked fixed-point test programs (4 each mode), all using secret-typed literal inputs.
- GitHub Actions [38489081857](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38489081857): official MP-SPDZ cleartext emulator numerically passed all four cases in both modes at 0.05 absolute/relative tolerance; inputs were compile-time constants cast to secret types.
- GitHub Actions [38489589290](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38489589290): official emulator compiled and numerically passed four cases in both modes with runtime `sfix.get_input_from(0)` and party-0 input files. Neither method outperformed the other at the measured numerical tolerance.
- GitHub Actions [38490443262](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38490443262) widened fixed-point emulation to 27 paired cases spanning each of the 24 stress tasks. Both modes passed 27/27 using secret-typed embedded constants, and both passed 27/27 using actual party-0 runtime input instructions; no numerical superiority for the modified lowering observed. Four selected cases in prior runs remain valid but superseded by this broader experiment. All three workflow jobs finished successfully. The reported 0.05 absolute/relative tolerance is loose.
- Cleartext emulator results do not establish the behavior or security of a genuine multiparty network protocol. Tests use a targeted and non-representative runtime sample. Original source/benchmark remains unresolved; see [issue #2](https://github.com/Girish2052003/LUT-PHD-TARGET/issues/2).
