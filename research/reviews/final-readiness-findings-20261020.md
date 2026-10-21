# Independent final-audit findings — 20 October 2026

This is a technical acceptance record, not the professor-facing report.

Reviewer: independent `r8_final_review` assistant context, read-only inspection of
main `b8c94068e1fecfcd716c1ce2f71bf95a05a5f038` and R8 head
`ec4dd8be38c80bb3f9b45cbca0bb70ff2265890b`.

## Findings requiring repair

1. High: the prior R8 gate covered only three stage2 receipts, not substantive
   difficulties across the project. The 14 October reproduction log was stale.
2. High: missing source-hash/evaluator fields were silently bypassed. Source,
   recovery and artifact identities were not reconciled.
3. Medium: equal totals could hide changed category names, transferred failures,
   removed unclassified errors or changed disagreement identities.

The prior successful run39261150673 establishes execution of that narrow checker,
not those missing properties. No fabricated experimental result was identified.

## Executed negative regressions

Commit26ccdb0868c5344086d72e17a3e02dea2c3b9c80, run39492627095:
four old tests passed and six new mutation tests failed because the checker
did not reject the deliberately changed data.

Commitf317b56c54ec60a9c4cb136fb6f28c6bb769aec5, run39492946695:
four old tests passed; eight mutation tests failed; two new project-register
tests failed because the register-validation function did not yet exist.
These are intentionally preserved RED results, not failed native experiments.

The implementation adds exact source/run/artifact pins, category partitions,
disagreement identities and terminal-error categories; a 13-family difficulty
index links concrete causes, resolutions/blockers, runs and evidence files.
A separate raw-artifact audit rechecks original insertion, author oracle outcomes,
negative evidence, stage2 taxonomy, paired comparisons and targeted smoke
without executing any downloaded candidate or calling a model.

**21 October update:** GREEN raw-audit run39493312330 and R8 run39493312087 at45a51e6 have been inspected. Independent r8_pr13_review found no critical or important code/evidence defect at that commit. Final documentation/governance and exact PR/main integration are recorded separately in `final-readiness-review-20261021.md`.
R8 documentation may pass separately from B3/R2/R3 experimental requirements.
The latter must remain unreproduced/incomplete where evidence is missing.
