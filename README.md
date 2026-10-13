# SPDZCoder reproduction and domain-safe oblivious lowering

Research assignment workspace for Girish Nallan Chakravathy. Target paper:
Dong et al., **SPDZCoder: Combining Expert Knowledge with LLMs for Generating
Privacy-Computing Code**, arXiv:2501.00363v2 (21 March 2025).

**Status: work in progress; the full paper reproduction is not complete.**

The repository supplied for the assignment was empty on 14 October 2026
(Europe/Helsinki). The authors' implementation and the 313-function SPDZEval
dataset have not yet been located. This repository will keep independently
implemented experiments clearly separate from the paper's reported results.
No LLM API experiments have run.

## Research direction

Oblivious selection evaluates both branch expressions. An operation in an
inactive branch can still receive an invalid argument: for example, `sqrt(x)`
and `sqrt(-x)` cannot both be real for nonzero `x`. The proposed extension
uses the branch's secret activation mask to give inactive partial operations
safe dummy arguments, without revealing the mask. We will measure semantic
correctness on a disclosed stress benchmark and compile emitted programs
using a pinned MP-SPDZ compiler. These experiments are not SPDZEval scores.

## Assignment requirements

| Requirement | Current status |
|---|---|
| Study paper and explain methodology | Paper audit in progress |
| Study original code | Blocked: original code not provided or located |
| Reproduce key experimental results | Blocked: original artifacts and LLM access missing |
| Implement substantive improvement | Domain-safe lowering under development |
| Compare baseline and modification | Controlled microbenchmark planned |
| Brief report, snippets and reproduction difficulties | In progress |

Deadline supplied by the supervisor: **31 October 2026**.
