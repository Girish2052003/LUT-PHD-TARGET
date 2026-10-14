# My notes on SPDZCoder

**Reference:** Dong, Xin, Li and Xu, *SPDZCoder: Combining Expert Knowledge with LLMs for Generating Privacy-Computing Code*, arXiv:2501.00363v2, 21 March 2025. Page references are to the 19-page arXiv v2 PDF.

## 1. Why I chose to study this problem

Ordinary Python can reveal information through the branches it takes or the addresses it accesses. Multi-party computation (MPC) aims to compute a function over different people's private inputs without exposing those inputs. MP-SPDZ provides secret types (such as sint and sfix) and MPC-specific operations. Simply copying Python into MP-SPDZ is not enough.

**Data-oblivious** means that for equal-size secret inputs, the visible instruction sequence and memory-access pattern do not change with the input (paper, pages 2–3). A secret-dependent Python if statement therefore needs a careful transformation.

## 2. How the proposed pipeline works

SPDZCoder uses expert-written transformation knowledge **plus a large language model**. It is not a newly trained neural network. The three stages are (paper pages 2–6):

1. **Refactor** ordinary Python into Canonical Form Python (CFP): replace advanced functions and constructs, rewrite secret-dependent branches and loops, and choose oblivious algorithms. Ten refactoring rules address high-level semantic differences.
2. **Generate** MP-SPDZ from CFP: a prompt dynamically selects low-level demonstrations, such as Python float becoming an MP-SPDZ sfix and Python math functions being replaced by the appropriate MPC APIs. A self-reflection prompt checks for invented APIs.
3. **Repair** with compile, runtime, and functional error feedback: when unit tests are available, fix the code up to a fixed retry limit.

The paper also uses AST or LLM pattern matching to avoid applying irrelevant rules.

## 3. The original experiment I need to reproduce

Paper section 4.2 (page 5): GPT-4-turbo, version 2024-04-09; temperature 0.7; two generated samples per task; maximum three repair feedback rounds. The target evaluation is **SPDZEval**, manually constructed with 313 pairs of Python and MP-SPDZ functions and test cases.

| SPDZEval split | Number |
|---|---:|
| Array (AR) | 43 |
| Loop (LO) | 97 |
| Branch (BR) | 34 |
| Math (MA) | 38 |
| NumPy (NP) | 66 |
| Syntax (SX) | 35 |
| **Total** | **313** |

Metric: pass@1 and pass@2 across **generated candidate programs**; repeated inputs to one deterministic program do not create independent candidates.

From the published Table 4 (page 7): SPDZCoder obtains overall **85.94% pass@1** and **92.01% pass@2**. These are **author-reported**, not outcomes reproduced in this project.

**Table transcription caution:** The prose/abstract calls 63.58% the best baseline pass@1, but the same published Table 4 lists 64.21% for OpenAI-o3-mini under API documentation. The 76.36% pass@2 highest baseline is listed for OpenAI-o1. A separate table cell for DeepSeek-V2.5 has a suspicious pass@2 lower than pass@1 (array split); consult the original typeset table instead of silently correcting it.

## 4. The numerical limitation I first investigated

Paper section 2.2 (page 3) gives a branch-free expression combining sqrt(x) and sqrt(-x). Both square roots are evaluated in this expression even though only one should contribute to the result. For many x, the inactive expression has an invalid real-valued input. In Python, that immediately raises a domain exception. In MP-SPDZ, invalid-domain arithmetic may instead return an unreliable fixed-point result. This is a **plausible limitation in the illustrative arithmetic-predication pattern**, not proof that the authors' actual private compiler has this bug.

### My branch-mask modification

Let m be the secret-valued activation bit for a branch: m=1 means active, m=0 means inactive. For a partial operation, feed it the masked argument

    safe_arg = m * original_arg + (1 - m) * 1

When m=1, the real argument is unchanged. When m=0, the operation receives 1, valid for square root, natural log, and a divisor. The result is still selected by the original secret bit, without a secret-dependent Python branch. Nested branches multiply their activation bits.

This is an independent, restricted AST compiler extension: one scalar parameter, pure returns, comparisons, arithmetic, square root, log and nested if/else. It deliberately rejects unsupported syntax. I have separately implemented a paper-based refactor–generate–repair pipeline, but I do not have the authors' complete code, prompts or original benchmark.

## 5. What I actually measured

A deliberately targeted 24-function stress suite was compared against a **reconstructed eager-predication baseline**, with exactly the same 7,464 input pairs for both implementations. The baseline passed 4,109 and raised 3,355 domain exceptions; the modified compiler passed 7,464. At that milestone, 22 regression tests and an independent raw-result consistency validator passed in [GitHub Actions run 38488603949](https://github.com/Girish2052003/LUT-PHD-TARGET/actions/runs/38488603949). The expanded project now has 44 passing Python tests. I have kept the original experiment logs rather than replacing them with a single aggregate claim.

**These particular accuracy figures come from Python execution, not from the original SPDZEval.** They are not the paper's SPDZEval pass@k, a representative estimate of real-world defects, a proof of MPC security, or proof of fixed-point correctness. The compiler and runtime results are reported independently.

## 6. Questions I want to be ready to explain

**Why not just use a normal if statement?** The condition may be secret. Choosing a Python branch using it can expose secret-dependent control flow.

**Does computing both sides always fix the problem?** No. Both sides must be safe to evaluate; inactive divisions and logarithms can be invalid. I use a branch-activation mask before these operations.

**Is your baseline the original SPDZCoder implementation?** No. It reconstructs an arithmetic-predication example from the paper. I cannot claim a measured improvement to the authors' actual system without their original source and benchmark.

**Is 100% accuracy a general achievement?** No. It is 100% only on a disclosed, deliberately targeted Python stress set. Fixed-point numeric error, overflow, source language coverage, actual party inputs, privacy guarantees and the paper's broader benchmark need separate verification.

**What is still missing?** The authors' complete SPDZCoder source, the 313 SPDZEval tasks and tests, the original model/experiment setup, and real multiparty protocol evaluation. I have compiled and run selected programs in the MP-SPDZ cleartext emulator, which is not the same as a secure multiparty run.


For the broader implementation and the actual Figure 4 example I reproduced, see [my research report](professor_submission_interim.md). I keep those experiments separate from the numerical branch-masking study above.
