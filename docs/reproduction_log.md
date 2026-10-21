# Experiment log

## Superseding difficulty reconciliation — 21 October 2026

This technical log supersedes the current-status wording in the dated 14 October
entries below. Those entries remain historical evidence. Original author artifacts
were subsequently supplied and original saved programs were executed under MASCOT;
the historical model calls have **not** been reproduced.

The project-wide [difficulty register](../research/reproduction_difficulties.json)
links 13 substantive difficulty families to exact evidence and source runs. Its
checker validates the declared inventory and file hashes; it cannot establish
that every prose explanation is true or infer the cause of numerical variability.
Independent review and raw-artifact audits provide the additional checks.

| Difficulty | Evidence and resolution or remaining limitation |
|---|---|
| Original source discovery and dependency mismatch | Professor's 14 October follow-up supplied ACM/Zenodo. The published TAR SHA-256 is `a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac`. Preserve `requirement.txt` versus README `requirements.txt`, original source and all stage records. See `research/original_source_audit.md`. |
| Environment and execution confinement | Original native replay pins MP-SPDZ 0.3.6 commit `6cc3fccef0904764364eb8e285519cd34028f325`, original evaluator and binary hashes, and a Python 3.11.9 base image. Generated candidates execute only in the reviewed non-root, read-only, network-disabled two-party MASCOT container with resource limits. The earlier independent compiler/emulator uses a different pin and is not the author-native experiment. See `research/replay/README.md` and source manifests. |
| Full final-stage download failure | Run **38703569637 attempt 1** lost the SPDZCoder math data after a truncated source download (`curl` exit 18); aggregation correctly rejected 1,176/1,252 records. Attempt 2 retried failed jobs and completed the dataset. Preserve `original-full/attempt-1.json` separately from the successful receipt. |
| Final-stage native failures | Fresh final-stage replay: SPDZCoder 75 compile failures and one final timeout; GPT-4 API-doc baseline 312 compile failures, 70 runtime failures (66 missing inputs, four requests for nonexistent player 2), and two final timeouts. Retain all 1,252 candidates and 1,280 attempts. Five archived/fresh acceptance disagreements remain; one GPT-4 runtime failure is accepted by the original filename-sensitive stdout oracle. Acceptance is not proof of correct execution. |
| Stage-2 failures and retries | Source run **39075744038**: 626 candidates, 644 attempts; 147 compile failures, 479 completed runtimes, 445 original-oracle acceptances and 34 completed-runtime rejections. Fourteen candidates retried; 18 timed-out attempts remain in the logs. Compiler error types: AttributeError 56, ImportError 28, TypeError 22, CompilerError 18, NameError 17, IndexError 2, SyntaxError 1, ValueError 1, and **two unclassified terminal stderr**. Three saved/fresh disagreements retain exact task/candidate identities. |
| Stage-2 aggregation failure and recovery | All seven native category jobs succeeded, but **39075744038 remains FAILURE** because aggregation used an extra `stage2-full` path prefix. Separate **39080161119 SUCCESS** reassembled the same seven ZIPs without native reruns. A workflow-path fix and layout regressions prevent that packaging error; they do not improve scientific outcomes. |
| Weak original correctness oracle | Original substring `pass` criterion does not require runtime success. Signed-relative tests accept known-wrong outputs; one template lacks a functional assertion. Diagnostic run **38742644019** preserves four counterexamples and controls. Keep the original benchmark oracle unchanged and interpret its scores narrowly. |
| Source, paper and saved-trace disagreement | Released stage-1 early break, repair resets and feedback handling differ from the idealized method. Missing intermediate messages cannot be reconstructed; 50 branch source changes have zero saved repair tokens. Seven-category saved-stage run **39073490709** demonstrates actual archived states, not a regenerated conversation. |
| Patch scope and costs | Narrow secret-integer mask-product rewriting was restricted after zero-folding/rebinding/type review. The mixed-operand `lower_bound` witness remains unsupported. Targeted run **38958484872** verifies 64 executions, authorized outputs and **50 to 0 explicit observed intermediate-opening events**. This is not a general confidentiality proof. Selected modified candidates require more secret multiplications and communication. |
| Unchanged-source outcome variability | Full paired run **38989067493** has 626 pairs, only two source changes (both ACCEPT to ACCEPT), and four acceptance flips on byte-identical controls. Original-only follow-up **39043579023** executed 16 repetitions; one candidate accepted in 3/4 trials. Cause remains unproven; aggregate fluctuations cannot be attributed to the patch. |
| Historical GPT-4/Azure generation | **NOT REPRODUCED.** Released Azure `gpt-4` deployment is not an identified historical snapshot; exact responses/repair history are absent and paid calls are not authorized. Authors' provenance/transcripts could recover more history. A newly authorized model run would be a **NEW EXPERIMENT**. OpenAI's public model schedule does not establish Azure deployment availability. |
| Genuine without-refactoring ablation | **NOT REPRODUCED.** Audits covered 498 relevant source files, 35 saved evaluation groups, embedded Git objects and release lineage. The 104/313 and 142/313 match belongs to UniTrans/GPT-4, not the required SPDZCoder ablation. Source preflight **39253932391** recovered all 313 original input/instruction pairs; 307 inputs parse directly and six NumPy-operation inputs do not. None was silently replaced or excluded. Authors' authentic corpus or a fully specified new experiment would be required. |
| Difficulty/readiness checker defects | The old R8 checker covered only stage-2 receipts and bypassed missing provenance assertions. Mutation-test runs **39492627095** and **39492946695** deliberately failed. Repaired checks at **45a51e6** passed; raw-audit run **39493312330** independently rechecked 31 pinned ZIPs, final-stage source insertion, stage-2 raw taxonomy, paired controls and targeted outputs. Two further permission-scope tests failed before the 21 October fix and pass after it. Conditional merge permission is no longer treated as report-readiness exception acceptance. |

The 20 October audit receipt and recomputed summaries are preserved in
[`research/evidence/2026-10-21/final-readiness/`](../research/evidence/2026-10-21/final-readiness/).
The retrieval date is 21 October; the underlying experiments remain dated by their
original runs. **No native program or model was rerun during this final audit.**
Run IDs resolve under `https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/`;
exact artifact IDs, hashes and expiry timestamps are in the receipts. Artifact
retention is finite; archived receipts are not replacements for the raw ZIPs.

R8 documents these failures and limits independently of whether they are solved.
It must not convert R2/R3/B3 into experimental PASS. The 18 October user quote
permits conditional research integration; report-scope exception acceptance and
final writing authorization remain separate decisions under the execution contract.

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
