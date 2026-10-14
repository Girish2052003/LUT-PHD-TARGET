# My paper analysis: SPDZCoder research questions and reproduction gaps
**Reference:** Dong et al., arXiv:2501.00363v2, 21 March 2025, 19-page arXiv v2 paper.
**Purpose:** I use these notes to keep the published results, my measured experiments and my own hypotheses separate. I have not recovered the authors' full implementation.

## Provenance and central problem

- On 12 October 2026 Professor Kumar asked me to study the paper and its codebase, reproducing key implementation/experimental results, proposing a substantive fix, comparing against baseline, and documenting difficulties. Deadline: 31 October.
- His email supplied only https://arxiv.org/pdf/2501.00363. The 12 October message contains **no code attachment or separate source/baseline repository link**.
- I searched public code and repositories for SPDZCoder, SPDZEval and distinctive names on 14 October but did not find a verified authors' release. This is a *bounded discovery statement* and NOT proof no artifact exists.
- The 19-page v2 PDF appendix gives representative prompt templates (Tables 9-12), with ellipses in multiple LLM examples and only one high-level rule shown in detail. Hence exact prompts, test cases, model outputs and complete runtime cannot be recovered simply by parsing this PDF.
- I built DomainSafety-24 independently, not an original SPDZEval split. so its Python improvement over eager arithmetic predication is not a comparison against the authors' actual baseline.

## Original methodological architecture (Sections 3 and 4)

1. Identify semantic-expressing discrepancies by combining four MPC experts' knowledge; derive **10 refactoring rules** to rewrite complex plaintext Python into Canonical Form Python (CFP). Table 1 specifies: Linear_NonLinear, DataStructure, SyntaxSugar, RewriteWhileLoop, EliminateAdvancedArrayOperations, EliminateBreak, EliminateContinue, NestedIf_MultipleReturn, ChainedComparison, ObliviousForm.
2. Select relevant rules by AST-based/LLM pattern matching and apply them successively. CFP must both execute equivalently and become structurally easy to translate; Python functional correctness alone cannot prove compliance with rules (Section 5.3).
3. Select low-level demonstrations using pattern matching and generate MP-SPDZ code from CFP with the LLM. The appendix shows **representative, not exhaustive**, few-shot prompts. Self-reflection corrects false APIs, imports and syntax.
4. If tests exist, compile and execute code, detect compiler/runtime problems versus functional mismatches, feed errors back to the LLM, stop at success or max_feedback retries.
5. The paper uses GPT-4-turbo (2024-04-09), temperature=0.7, repetition=2, max_feedback=3 (Section 4.2). It does not provide a uniquely pinned MP-SPDZ revision in the PDF.

## Published RQ1 — effectiveness on SPDZEval (Section 5.1 and Table 4)

SPDZEval: 313 source/target function pairs and tests (43 array, 97 loop, 34 branch, 38 math, 66 numpy, 35 syntax). Correctness is pass@1 and pass@2 across generated candidate programs that pass tests.
- **Paper-reported SPDZCoder/GPT-4:** overall pass@1 85.94%, pass@2 92.01%.
- **Paper-reported OpenAI-o1 API Doc:** pass@1 63.58%, pass@2 76.36%.
- **Paper-reported OpenAI-o3-mini API Doc:** pass@1 **64.21%**, pass@2 74.44%.
- The prose asserts the "best-performing baseline" pass@1 is 63.58%, while the very same table lists 64.21% for o3-mini. These exact published entries conflict. Do not silently "correct" the original.
- Another table anomaly: the DeepSeek-V2.5 API Doc array pass@2 cell is printed **1.4** despite array pass@1 **79.07**; this violates monotonicity expected when k increases under the same sample procedure. It may be a typo or a different estimation/reporting issue; flag instead of guessing.
**My status: original 313-task reproduction is still pending.** I have not obtained the 313 original function/test pairs or authentic GPT-4-turbo-2024-04-09 samples.

## Published RQ2 — contribution of refactor/repair (Section 5.2, Table 6)

| Setting | pass@1 | pass@2 |
|---|---:|---:|
| Full SPDZCoder | 85.94 | 92.01 |
| Without refactoring | 33.23 | 45.37 |
| Without repair | 73.16 | 83.39 |

Published ablations support the importance of refactoring and feedback. My PaperPipeline implementation exposes separate stages and bounded repair but uses *explicit replay fixtures* unless a real external model is wired in. A replay run is useful to test software control flow; it is not a repeat of these scores.

## Published RQ3 — CFP refactoring accuracy (Section 5.3, Table 7)

Refactoring-only paper-reported pass@1/pass@2: GPT-4 91.24/95.26, GLM-4 85.77/93.43, DeepSeek-V2.5 90.88/91.61, DeepSeek-V3 91.24/95.26. The paper says GPT-4-turbo generated **five test cases per original function** to assess CFP. Functional tests alone did not detect violations of the intended refactoring rules. This observation motivates checking more than functional correctness.

## Published RQ4 — token consumption (Section 5.4, Figure 5 and Table 8)

SPDZCoder: **10,343 average prompt tokens** and **1,824 completion tokens** with repair; prompt tokens without repair **6,377**. Pattern matching saves **4,355 -> 1,567** prompt tokens in the refactor stage and **8,973 -> 4,810** in generation. These are author-reported, NOT token measurements from this project.

## The privacy limitation I am testing

**Threat:** a generated MP-SPDZ program can compute the correct declared output and still expose more secret information through an extra reveal or secret-dependent public branch. The article evaluates test-based functional correctness, rather than a formally checked full noninterference property. It acknowledges occasional violations of obliviousness in Section 5.3.

Consider the declared function F(s)=0. Two secret inputs s=-3 and s=5 have exactly the same authorized public result. An unauthorized candidate prints s.reveal() before returning zero. Both candidates pass a primary-result-only checker, but its public trace reveals two different private inputs. The safe candidate emits only the authorized zero output.

I added a syntactic privacy screen **after reflection and before evaluation**, re-used after every repair. It rejects direct reveals, unauthorized prints, some secret-dependent public branches/loop bounds, and secret-dependent indices. Rejected candidates feed actionable diagnostics into the paper-style repair stage. This screen is conservative, incomplete and **not** a formal proof of noninterference or MPC protocol security.

Formal target under a chosen declassification contract:

    forall x,y:
       (PublicInputs(x)=PublicInputs(y) AND F(x)=F(y))
          => PublicTrace(P,x)=PublicTrace(P,y).

When F(x)=0, the baseline witness violates the implication because extra log output depends on x. For the modified fixture, all emitted **application-level print lines** are identical over the checked inputs, but internal protocol traces and arbitrary program security remain unproven.

## How I interpret my experiment results

1. **Existing DomainSafety-24:** reconstructed host-Python eager-predication baseline vs arithmetic mask; 4,109/7,464 vs 7,464/7,464. Targeted, not SPDZEval.
2. **Existing pinned MP-SPDZ emulation:** 27 selected cases spanning all 24 tasks with embedded sfix constants and player-0 runtime inputs. Both variants 27/27 per input mode at absolute/relative 0.05; no numerical improvement shown.
3. **My nine-case replay-only pipeline fixture:** tests an independently reconstructed three-stage workflow and a privacy screen. No actual model calls; its synthetic "functional evaluator" always accepts candidate outputs by construction, to isolate the missing privacy check. Do **not** call these baseline GPT-4 samples.
4. **My MP-SPDZ cleartext-emulator counterexample:** source F(s)=0; malicious candidate prints s publicly, corrects nothing else; safe candidate returns zero without revealing s. Two distinct party inputs demonstrate unauthorized side output in the malicious candidate. Both return the correct authorized zero. This is a controlled attack example, not evidence of how often the original SPDZCoder makes this mistake.

## What I need to complete the original reproduction

- Get exact original SPDZCoder repository/commit, including all complete expert prompts and translation pipeline code.
- Get actual SPDZEval (313 tasks, tests, six split labels), configuration and licensed model access to replay GPT-4-turbo-2024-04-09; if the historic model is gone, record this and run an explicitly labeled nearest-available approximation only with authorization.
- Run original pipeline and real baseline on *identical* test entries, model settings and budgets, compare pass@1/pass@2, repair/refactoring ablations, and original token accounting (RQ1–RQ4).
- Apply improvement to the exact same original code and preserve model outputs/test traces and proof obligations. Report functional, security and computational-cost deltas separately, including failures and regression cases.
- Execute full MP-SPDZ secure computation as a separate security validation if resources permit. A cleartext emulator is not multiparty MPC.


For a concise account of my implementation and experiments, see [my interim report](professor_submission_interim.md).
