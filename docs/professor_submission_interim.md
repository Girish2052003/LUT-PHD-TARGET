# Reproducing selected SPDZCoder mechanisms and adding privacy-aware validation
**Interim research report — not a complete original-code or SPDZEval reproduction**

**Candidate:** Girish Nallan Chakravathy  
**Research group:** Professor Prabhat Kumar, LUT University  
**Target paper:** Xiaoning Dong, Peilin Xin, Jia Li, Wei Xu, "SPDZCoder: Combining Expert Knowledge with LLMs for Generating Privacy-Computing Code", arXiv:2501.00363v2, March 21, 2025.  
**Assignment deadline:** October 31, 2026.

## 1. Objective and original architecture

The original SPDZCoder synthesizes privacy-preserving MP-SPDZ code from Python without model fine-tuning. It addresses discrepancies between Python and secure multiparty computation (MPC), chiefly unavailable APIs, fixed-point/secret data types, and data-oblivious control flow. The paper combines MPC expert knowledge with LLM inference through:

1. **Refactoring:** ten transformation-rule categories (Table 1) progressively turn Python into Canonical Form Python (CFP); pattern matching selects only applicable rules.
2. **Generation:** dynamically selected low-level in-context examples map CFP types, functions and syntax into MP-SPDZ, followed by API-oriented self-reflection.
3. **Repair:** compile/run candidates and use compile/runtime or functional errors to inform up to three repair prompts (Section 3 and Appendix A).

The authors' configuration (Section 4) is GPT-4-turbo-2024-04-09, temperature 0.7, two generated candidates per problem and at most three repairs. SPDZEval contains 313 functions distributed across array 43, loop 97, branch 34, math 38, NumPy 66 and syntax 35. Published scores are 85.94% pass@1 and 92.01% pass@2 (Table 4); these are **not** our measured scores.

## 2. Reproduction method and missing artifacts

The professor supplied the arXiv link but not a code repository or a benchmark attachment. Searches for SPDZCoder, SPDZEval, the authors' public repos and unique code strings have not produced a verified original runnable release. Consequently:

- We built an **independent, explicitly labeled paper-based reconstruction** of rule selection, CFP, LLM-model interface, generation, reflection, repair and audit logs.
- It contains deterministic response-replay tests and an optional real API adapter recording actual prompt/completion usage. **No actual LLM API calls have run.**
- A strict importer rejects any dataset presented as the complete original SPDZEval unless it has all 313 source/target pairs, tests, split counts and provenance. We have **not** created surrogate cases pretending to be SPDZEval.
- All genuine MP-SPDZ execution uses the publicly available compiler pinned to commit 78fe3d8bad4e654276eb3a11a88173195e672f44; this is an independent compatibility environment, not established as the authors' exact environment.

The reconstruction is valuable for understanding and evaluating the architecture but cannot substitute for the original dataset, code or stochastic model generations.

## 3. Substantive limitation and proposed modification

**Identified limitation:** functional correctness does not entail privacy correctness. A translator can emit the expected authorized output and also reveal secrets via an extra logging call, secret-dependent public branch or secret-dependent access. Section 5.3 of the paper itself notes that some refactorings rarely violate obliviousness. A traditional output-only unit test cannot necessarily detect additional unauthorized disclosures.

**Proposed extension:** insert a conservative AST-based privacy check after generation/reflection and after each repair attempt, converting detected violations into actionable repair feedback. The checker catches direct/aliased ".reveal" attributes, unapproved print/output calls and selected input-tainted Python branches, loops and indices. It also adds structural checks that selected refactoring rules actually removed their target AST patterns. It is deliberately **not** a proof of noninterference, nor a sound-and-complete taint analysis.

For a function with declared public output F, the application-level security obligation is:

For all secret inputs x and y with the same public inputs and F(x)=F(y), their *unauthorized public application-level traces* must agree.

The counterexample uses F(x)=0. Baseline code returns zero but additionally prints x.reveal(); modified code returns zero without the disclosure. Thus the baseline produces distinguishable extra application output for distinct secrets despite identical authorized answers.

**Core code fragment** (simplified from the checked MP-SPDZ programs):

    # Deliberately injected extra leak (not author-produced)
    def f(x):
        print_ln('UNAUTHORIZED_SECRET:%s', x.reveal())
        return sfix(0)

    # Modified program
    def f(x):
        return sfix(0)

The experimental commands compile and execute actual MP-SPDZ programs with input read at runtime through sfix.get_input_from(0). They do not merely run an ordinary Python simulation. However, the executor is MP-SPDZ's **official cleartext emulator**, not an actual multiparty protocol.

## 4. Experiments and results

### 4.1 Architecture and security-screen unit tests

A GitHub Actions run executes 44 independently written regression tests at the research branch. These test rule-name coverage, AST matching, signature and structural checks, stage order, bounded repair, injected model responses, code extraction, leak detection, opt-in model adapter behavior, token-usage logging and strict SPDZEval import. The nine-case **fully disclosed, replay-only** ablation deliberately uses a synthetic functional-only evaluator which always accepts outputs (not the original MP-SPDZ test harness):

- Seven unsafe candidates accepted by that functional-only fixture.
- All seven flagged/repaired by the additional privacy check with manually scripted revised responses; two safe controls were accepted.
- No actual GPT-4/LLM samples, token savings, benchmark pass@1 or pass@2 can be inferred from this replay experiment.

### 4.2 Genuine MP-SPDZ secret-output counterexample

A separate pinned-compiler/emulator job executes both program variants with runtime party-0 secret inputs -3 and 5:

| Variant | Secret input | Authorized returned output | Unauthorized public output |
|---|---:|---:|---|
| Deliberately leaky baseline | -3 | 0 | -3 |
| Deliberately leaky baseline | 5 | 0 | 5 |
| Privacy-checked modification | -3 | 0 | none |
| Privacy-checked modification | 5 | 0 | none |

**Observed:** both code variants compile and correctly return zero. The baseline emits additional public secret data; the modified program does not. This experimentally demonstrates the defined *application-output* information-flow vulnerability on a hand-constructed witness. The experiment does **not** establish that the original SPDZCoder ever produced this code, nor prove MPC protocol privacy.

### 4.3 Reproduction of the paper's Figure 4 repair algorithm

The two explicit swap formulas printed in Figure 4 (paper page 8) were transcribed into invoked MP-SPDZ sint programs, using runtime party-0 inputs. We independently tested all six permutations of three distinct values. The broken formula leaves pairs in place on greater-or-equal and swaps otherwise (reverse-sorting), whereas the repair swaps on greater-or-equal (ascending-sorting). Thus on this corpus the observed outcome was **0 of 6 correctly sorted for the original faulty formula and 6 of 6 for the repaired formula**. This is an **algorithm-level reproduction of a paper example**, not reproduction of the authors' original LLM generation and repair process or SPDZEval task test cases.

### 4.4 Earlier independent domain-safety extension

A separate intentionally targeted 24-function stress suite tested arithmetic predication against the original Python function: reconstructed eager baseline 4,109/7,464 passing paired Python inputs, modified domain-masked lowering 7,464/7,464. In real MP-SPDZ cleartext emulation, both versions passed all 27 selected numerical cases in each of the two input modes at the specified tolerances, so **no numerical accuracy advantage was established in MP-SPDZ**. These results are separate from this report's information-flow extension and must not be presented as published SPDZEval scores.

## 5. Reproduction difficulties and limitations

The public paper contains representative but incomplete appendix prompts; exact full rule text, real original model responses, benchmark/test fixtures, authentic prompt token counts and compiler version are unavailable. The historic GPT-4-turbo model/API access has not been established. The authors' Table 4 also has apparent reporting anomalies: the prose calls 63.58% the strongest baseline pass@1, whereas OpenAI-o3-mini's API-documentation row lists 64.21%; one DeepSeek-V2.5 array pass@2 cell is smaller than its pass@1 cell. We report those inconsistencies rather than changing the source.

The syntax-based privacy screen can miss leaks through aliasing, external functions, indirect flows, subtle storage and timing effects and the protocol layer. It can also reject some permitted outputs absent a more precise declassification specification. The controlled examples were designed by us, not sampled from the authors' 313 tasks. Cleartext emulation does not certify cryptographic MPC security.

## 6. Completion requirements before an original-reproduction claim

Obtain the authors' SPDZCoder repository or archive and full original SPDZEval files, together with exact prompts, runtime scripts and split-wise tests. If the historical model cannot be accessed, document that and use a transparently different model only as an approximation. Execute the true original pipeline, direct API-documentation baseline, refactor/repair ablations and the modified pipeline with identical models, task lists, generation budgets and test harness. Preserve generated source, raw outputs, failures, token usage, hardware/compiler revision, pass@1/pass@2 and paired security metrics. Finally submit an evidence-supported final brief report to the supervisor by October 31, 2026.

**Research code:** https://github.com/Girish2052003/LUT-PHD-TARGET (PR #3)  
**Concrete privacy witness:** https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38492518496  
**Missing-artifact tracker:** https://github.com/Girish2052003/LUT-PHD-TARGET/issues/2
