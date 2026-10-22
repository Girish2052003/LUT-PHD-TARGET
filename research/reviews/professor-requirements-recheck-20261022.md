# Professor assignment recheck — 22 October 2026

The primary agent reread the connected Gmail thread titled **Funded PhD enquiry —
Explainable AI security and resilient software systems**, including Professor
Prabhat Kumar's assignment of 12 October 2026, 17:38:49 UTC, and his follow-up of
14 October 2026, 05:42:31 UTC. A sender-specific search after 14 October found no
later amendment. This is a requirements reconciliation, not professor acceptance
of the work. Private message headers, signatures and unrelated correspondence
are not copied into the repository.

## Authoritative scope

The assignment asks Girish to study the paper and codebase; reproduce the
implementation and key experimental results; explain the main concepts and
methodology; identify one substantive limitation and address it through code;
compare the modified implementation experimentally with the original baseline;
document reproduction difficulties; and submit a brief report containing the
limitation, solution, relevant snippets and comparison results. The deadline is
**31 October 2026**. The follow-up supplies the ACM paper and Zenodo record
18152253, without changing these requirements.

The email does not prescribe a report page count, require universal formal
verification, specify an improvement in aggregate pass rate, or explicitly
waive unavailable historical experiments. The repository's strict internal gates
are useful evidence controls, not extra demands attributed to the professor.

## Evidence-backed assessment before finalizing the draft

| Actual requested work | Evidence and current assessment |
|---|---|
| Study paper and original code | Completed: source-to-paper map, original archive hashes, authentic saved stage examples; R1 PASS |
| Reproduce implementation | Substantial but incomplete: authentic original evaluator and native saved-candidate execution reproduced; historical GPT-4/Azure generation sequence NOT REPRODUCED; R2 IN_PROGRESS |
| Reproduce key experimental results | Substantial but incomplete: original final-stage, stage-2 and baseline results freshly executed; genuine without-refactoring corpus not recovered; R3 IN_PROGRESS |
| Explain concepts and methodology | Completed in source audit and report draft; paper/source differences explicit; R4 PASS |
| Identify a substantive limitation | Completed under the stated private-input/output-only policy: authentic candidates explicitly open intermediate comparisons; R5 PASS |
| Address it through source modifications | Completed within the narrow supported secret-integer product pattern, integrated into both original entry points; deterministic added slice tested, no regenerated model pipeline; R6 PASS |
| Compare against original baseline | Completed within scope: 626 native pairs, targeted probes, unchanged-source controls and protocol costs; no demonstrated aggregate accuracy gain; R7 PASS |
| Document reproduction difficulties | Completed: preserved failure taxonomy, original failed aggregation and separate artifact recovery, oracle defects and historical gaps; R8 PASS |
| Brief report with snippets and results | Five-page draft prepared; independent content review, rendered-document verification and integration tracked in REPORT |
| Submit by deadline | Not submitted. User review and explicit submission authorization remain; no email sent |

R9 PASS is the repository's **readiness to prepare a report with explicitly
accepted exceptions**, not a claim that the professor's entire assignment is
100% complete. Girish's 21 October drafting decision accepts disclosure of the
two historical gaps; it does not establish that the professor has accepted them
and does not turn R2/R3 into PASS.

The defensible deliverable is a transparent report of reproduced work and
evidence-backed limitations. Missing historical provenance/candidate artifacts
would have to come from the original authors or another attributable source.
Any newly generated experiment requires separate provider/model/budget approval
and must be labeled NEW EXPERIMENT. It cannot recreate unobserved history.

## Evidence links

- [Requirement ledger](../requirements/assignment_traceability.md)
- [Report scope decision](../requirements/report_authorization_user_decision-20261021.txt)
- [Final report draft](../../docs/final_report.md)
- [Evidence guide](../../docs/final_report_evidence.md)
- [Research-base acceptance](final-readiness-review-20261021.md)

This recheck precedes completion of the report's final review and integration.
It authorizes no new experiment, contact, submission or broader scientific claim.
