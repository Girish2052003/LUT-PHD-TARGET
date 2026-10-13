# Domain-safe oblivious lowering: design and evidence boundaries

## Intended outcome

Produce defensible progress toward the supervisor's assignment: reproduce the
specified paper where artifacts permit, implement and evaluate one substantive
limitation, and report the evidence and remaining blockers honestly. The user
authorized implementation and pushing intermediate work. No messages are to be
sent to the supervisor, and no paid API execution or key creation is included.

## Available evidence

The supplied v2 PDF is authoritative. The supplied target repository was empty.
GitHub repository search and public web searches did not locate the authors'
implementation or SPDZEval. Absence from these searches is not proof of
nonpublication. The exact original MP-SPDZ version is unspecified in the PDF.
Our compatibility target is v0.3.9, commit
78fe3d8bad4e654276eb3a11a88173195e672f44; it is not claimed to be the authors'
version. An OpenAI credential is not configured in this environment.

## Alternatives and decision

1. **Domain-safe branch lowering (selected):** a concrete, falsifiable limitation
   directly illustrated by Section 2.2; a deterministic compiler extension can
   be evaluated without pretending to have regenerated the paper's LLM outputs.
2. General secret-flow verification: valuable, but Python aliasing, imports and
   framework semantics require a much larger analysis to justify security claims.
3. More prompting or a newer model: requires the missing dataset and model access,
   and confounds improvement with model changes.

## Supported language and algorithm

A single scalar Python function with one positional parameter, pure return
expressions, and nested if/else returns. Public numeric constants, comparisons,
arithmetic, sqrt, natural logarithm, and division are supported. Unsupported
syntax fails explicitly. Every branch has an explicit return on each path.
Predicates use total arithmetic only (no division, calls, or secret indexing).

The baseline reconstructs arithmetic predication from the paper's explanatory
example: b*f(u)+(1-b)*g(v). It is **not the authors' implementation**.
The modification propagates a path activation mask m. For sqrt and log it
evaluates the operation on m*z+(1-m)*1. For division it masks the denominator
in the same way. Values on active paths are preserved; inactive operations
receive a domain-valid argument. Nested masks use conjunction by multiplication.
No reveal, public branch on a secret, or data-dependent memory index is emitted.
This is a syntactic property of this restricted backend, not an MPC security
proof. Finite arithmetic, fixed-point representability and overflow remain
preconditions; arbitrary Python and arbitrary secret programs are out of scope.

## Components

- `src/spdz_audit/lowering.py`: validated AST frontend and two lowering modes;
  Python and MP-SPDZ emitters use the same expression transformation.
- `src/spdz_audit/metrics.py`: strict, tested pass@k estimator and paired outcomes.
- `experiments/benchmark.json`: disclosed development/evaluation tasks; separate
  generated inputs. No invented SPDZEval labels or LLM-sample claims.
- `scripts/run_experiments.py`: deterministic held-out input execution, raw rows,
  hashes, environment provenance, summaries and generated source programs.
- `scripts/check_mpspdz.py`: genuine compiler integration; availability and runtime
  execution are separate fields, with raw logs.
- `docs/report.md`: concise provisional report with evidence boundaries.
- `docs/paper_guide.md`: easy-English methodology and defense preparation.

## Experimental contract

Compare identical original functions and inputs with only lowering mode changed.
Include ordinary arithmetic controls, sqrt, logarithm, reciprocal, combined and
nested cases. Separate development cases from unseen-input evaluation. Record
exceptions, nonfinite outputs and numeric discrepancies separately. An intentionally
targeted stress set cannot estimate the prevalence of these defects in SPDZEval.
Use seeded samples and fixed boundary cases; disclose ranges and tolerances.
Report task-level and input-level counts, including every failure. For deterministic
lowering use accuracy, not pass@k. Preserve paper tables separately as published
values, and never mark full reproduction complete without actual baseline runs.

## Verification and acceptance

Tests must detect eager-domain failures, preserve active-branch errors, handle
nested masks, reject effectful/unsupported syntax and check metrics against hand
calculations. Run the entire suite and the experiments. Compiler success alone
is not runtime or cryptographic validation. If runtime dependencies are unavailable,
record that failure and provide a runnable integration command. Push reproducible
milestones to the user's repository. Deliver an interim report if original artifacts
are still missing; explicitly request the missing original-code/benchmark link.
