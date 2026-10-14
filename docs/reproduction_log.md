# Experiment log

## 14 October 2026, Europe/Helsinki

- I started with an empty assignment repository, confirmed through GitHub and a local checkout.
- I reviewed the arXiv v2 paper. Main model: gpt-4-turbo-2024-04-09, temperature 0.7,
  two samples per task, maximum three repair iterations.
- Public searches for SPDZCoder/SPDZEval and the repository search returned no
  identified author code or dataset. The PDF's hyperlink annotations contain no
  author artifact URL. This records our discovery result, not a claim of absence.
- Cloned real MP-SPDZ v0.3.9 at 78fe3d8bad4e654276eb3a11a88173195e672f44.
  The paper does not identify an exact compiler commit. Our pin is a compatibility
  target and must not be called the paper's original environment.
- Python 3.12.14, 9 visible CPUs, no GPU tool, no configured OPENAI_API_KEY.
- I started with testable, independent implementation and experiments
  while I looked for the missing code and data. This cannot replace
  the original-code/313-task reproduction requirement.
- I have not reproduced the authors' original LLM generations or full SPDZEval results.

### Experimental milestones (independent of SPDZEval)

- GitHub Actions [38488603949](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38488603949): 22/22 tests; 24 functions, 7,464 identical input pairs; reconstructed host-Python baseline 4,109 passes (3,355 exceptions), domain-safe extension 7,464 passes. Independent raw observation/manifest and SHA-256 verification passed.
- GitHub Actions [38488848728](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38488848728): genuine pinned MP-SPDZ compiler accepted eight invoked fixed-point test programs (4 each mode), all using secret-typed literal inputs.
- GitHub Actions [38489081857](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38489081857): official MP-SPDZ cleartext emulator numerically passed all four cases in both modes at 0.05 absolute/relative tolerance; inputs were compile-time constants cast to secret types.
- GitHub Actions [38489589290](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38489589290): official emulator compiled and numerically passed four cases in both modes with runtime `sfix.get_input_from(0)` and party-0 input files. Neither method outperformed the other at the measured numerical tolerance.
- GitHub Actions [38490443262](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38490443262) widened fixed-point emulation to 27 paired cases spanning each of the 24 stress tasks. Both modes passed 27/27 using secret-typed embedded constants, and both passed 27/27 using actual party-0 runtime input instructions; no numerical superiority for the modified lowering observed. Four selected cases in prior runs remain valid but superseded by this broader experiment. All three workflow jobs finished successfully. The reported 0.05 absolute/relative tolerance is loose.
- Cleartext emulator results do not establish the behavior or security of a genuine multiparty network protocol. Tests use a targeted and non-representative runtime sample. Original source/benchmark remains unresolved; see [issue #2](https://github.com/Girish2052003/LUT-PHD-TARGET/issues/2).

### Paper-based reconstruction and Figure 4

- [GitHub Actions run 38494328178](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38494328178): 44 Python regression tests, pinned compiler, complete cleartext-emulator workflow and Figure 4 experiment passed. The published faulty swap logic passed 0/6 ascending sorts; the published repair passed 6/6, using my six chosen inputs.
- In [run 38492518496](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38492518496), I compiled and executed a deliberately constructed unauthorized-reveal example. Both candidate programs returned zero for secret inputs −3 and 5, but the leaking candidate also printed the respective secret. My added privacy check rejected the extra output.
- I also ran nine scripted (non-LLM) pipeline cases to verify privacy-screen feedback and repair. These are fixtures, not model pass@k measurements. I have not used the original SPDZEval tests or historic model samples.
