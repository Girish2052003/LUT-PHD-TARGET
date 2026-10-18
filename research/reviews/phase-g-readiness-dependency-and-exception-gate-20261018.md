# Phase G: formal report-readiness dependency and irreproducibility exception gate

**18 October 2026 — practical verification record, NOT final report, and no implicit exception acceptance.**

### Real defect found

The machine-readable R9 ledger previously listed `phase_ids=["REPORT"]`. However R9 represents readiness to *start* the professor-facing report and user authorization explicitly comes **after** readiness. The old gate created a dependency cycle: R9 PASS required REPORT PASS while REPORT PASS was locked pending R9 PASS and user's explicit permission.

Fix: R9 now lists `phase_ids=["G"]`. `REPORT` remains BLOCKED until a later separate user instruction. No practical phase is silently promoted.

### Explicit scientific exceptions (not authorizations)

New `research/requirements/exception_decisions.json` enumerates two PENDING items: `HISTORICAL_LLM` (R2,R3,R8) and `NO_REFACTORING` (R3). R2/R3/R8 remain IN_PROGRESS. OpenAI API historical model retirement and original Azure pinning are documented; authentic SPDZCoder no-refactoring results are unavailable, and differently named numerical matches are not substituted.

A separate check in `scripts/check_handoff.py` requires any future ACCEPTED item to provide a repository-local, explicit user decision record, exact SHA-256 and quote. A decision's scope must cover its associated requirement; R3 needs both exceptional scopes, while other unfinished R1/R4/R5/R6/R7 cannot be waived by these two items. Tests assert missing/changed quote, missing artifact, incomplete coverage, and forbidden report-claim states are rejected. A checked-in quote is not cryptographic authentication of Girish's consent; human review must check the original conversation and decision.

### Completion gate still genuinely open

All practical research results A–F retain accepted bounded status. Neither an exception approval nor a professor-facing report has been created. G requires final reviewed integration and exact-main verification. R9 stays BLOCKED, B3 stays BLOCKED, and R2/R3/R8 stay IN_PROGRESS until user and actual evidence change these decisions.
