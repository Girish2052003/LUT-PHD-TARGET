# Independent scientific and metadata review — 21 October 2026

Reviewer: `/root/report_scientific_review`, separate review context.

Reviewed worktree: `/workspace/scratch/7cbc31894eab/LUT-PHD-TARGET/.worktrees/final-report`.
Research base: `c237aa4a6d98a16b141a9b178a046a121ea1e659`.

**Disposition: PASS within the review scope below. No remaining critical or important finding.**
This accepts the report's correspondence to the available evidence, not completion of the two unreproduced historical experiments, external scientific certification, visual publication approval, or permission to submit.

## Reviewed text identities

- `docs/final_report.md`: SHA-256 `2a319b87c30dee25caf1fddc91758c598789bccb4c8daa4ab5b1352f39415271`.
- `docs/final_report_evidence.md`: SHA-256 `b2dfc5e475be6a048ae30ac7246a117526cde9213a3ee11e47fcff3b6a485b12`.
- The reported finalizer remains SHA-256 `8c93f4687569c7419b573b20b1349b2d67563a39ce50dba16fda38dd197d8aa2`; the original-entrypoint patch remains `21fba36fc7df71fc3e8f3053a12a3893e29cc6a09d052f204d1d217c6cbbd328`. Both are byte-identical to the copies preserved in the executed targeted-smoke artifact.

## Findings addressed during this review

1. **Minor, corrected:** the draft described ten refactoring “categories.” Paper Table 1 and section 3.1 specify ten refactoring rule instances grouped into fewer families. The report now says “ten refactoring rules.” Verified against the actual primary paper HTML, https://arxiv.org/html/2501.00363v2, Table 1 and section 3.1.
2. **Minor, corrected:** B3's active `next_action` still requested a user exception decision after it had been recorded. The current progress record preserves BLOCKED / NOT REPRODUCED and records the accepted report-scope exception without inviting duplicate approval or unapproved model calls.
3. **Minor precision, corrected:** the original-oracle sentence now specifies a non-timed-out attempt and a case-insensitive `pass` match. This matches `scripts/summarize_original_replay.py:117`, `scripts/audit_stage2_full_zips.py:34`, and preserved behavior.
4. A transient generated-marker mismatch was observed while the author was editing concurrently. The later fresh `python scripts/check_handoff.py` passed, including 21 phases, nine requirements, and preserved evidence hashes.

## Independent numerical and source checks

The review read AGENTS.md, HANDOFF.md, the execution contract, current progress and requirement ledger, exception registry, main report, companion guide, original-source audit, relevant diagnostic/paired/stage-2 reviews and machine receipts. No original candidate or author pipeline was executed on the host.

| Report material | Direct checks and bounded result |
|---|---|
| Paper methodology and citation | Opened the actual arXiv v2 paper and publisher record. Three stages, ten refactoring rules, GPT-4-turbo-2024-04-09, temperature 0.7, two candidates, three repair retries, 313 tasks, paper date/authors, and Zenodo v2/2026 attribution agree. |
| Table 1 final-stage replay | Independently parsed all 1,252 preserved final outcomes. SPDZCoder: 626 records, 641 attempts, first/second/union 268/265/288, 75 compile failures, one final timeout. GPT-4 API-doc: 626 records, 639 attempts, 95/112/154, 312 compile failures, 70 runtime failures, two final timeouts. Total attempts 1,280. |
| Archived decisions | Checked the original identity-score record (269/265/288), saved-stage receipt (229/213/261), full-replay disagreement review (GPT-4 95/114/156, five disagreements), and the source-derived acceptance convention. The report does not present these as regenerated model results. |
| Stage 2 | Checked the full independent acceptance, secondary raw audit, difficulty receipt, and current main raw-audit logs: 626 candidates, 644 attempts, 147 compiler failures, 479 completed runtimes, 445 ACCEPT, 34 completed-runtime REJECT, 14 retrying candidates, 18 timed-out attempts, three archived/fresh disagreements; fresh first/second/union 229/216/262. |
| Full paired table | Independently parsed all 1,252 paired records in the downloaded `final-audit/paired-native/paired-records.jsonl`: baseline 270/266/290 and modified 271/263/290; 640 attempts and 75 compiler failures per variant. Exactly two source changes, both ACCEPT to ACCEPT. All four outcome flips have identical source and compiled MPC input within the pair. |
| Table 3 costs | Read the four relevant records directly from downloaded `final-audit/paired-native/reported_costs.json`. All runtime, communication, integer-triple and compiler-open values match the report, including 18.6831/20.6538 and 8.822/8.86707 seconds. These are distinguished correctly from targeted-smoke timings and explicit-opening events. |
| Original-only repeat evidence | Checked `independent-original-repeat-audit.json` and its raw-evidence review: 16 executions, four candidates times four trials; next_perfect_square candidate 1 accepted three times. The report correctly leaves the cause unresolved. |
| Targeted 32 pairs / 64 executions | Independently parsed all smoke records and checked 192 actual MPC/stdout/stderr SHA-256 digests. Parsed raw AUTHORIZED/OPEN output markers again; checked all 56 private observed/control outputs against independently computed distinct-count or strict-ascending results. No discrepancy. Baseline explicit-opening events total 50; modified total zero. Case partition 2 native + 24 observed private + 4 unobserved private controls + 2 synthetic fallback pairs agrees. |
| Concrete witness | Read preserved raw candidate texts and stdout. `[1,1,2]` and `[1,2,2]` produce authorized count 2 and original comparison traces `[0,1,1]` / `[1,1,0]`. Modified traces are empty. The diagnostic is correctly labeled new private-input evidence, not a historical breach. |
| Code snippets | Read the complete finalizer, original pipeline patch, executed patched entrypoints, original candidate strings and transformed text. Import/call, both paired expressions, and Replace visitor exactly match source. The finalizer is applied after optional feedback; only its deterministic slice was exercised. The report explicitly excludes unexecuted model-dependent prefixes and does not claim generation-quality improvement. |
| Reproduction gaps | Checked 498-file/35-group search receipt, embedded-history references, release lineage, and source-only input receipt. All 313 input/instruction pairs and six direct parse exceptions agree. UniTrans numerical collision remains a different system; historical generation and genuine no-refactoring are NOT REPRODUCED. |

## Fairness and limits

The report correctly keeps archived, fresh native, modified-source and independent reconstruction evidence separate. It does not pool private/synthetic diagnostics into benchmark rates. Full paired baseline totals are explicitly separated from the earlier replay totals. Only the two transformed sources support the scoped repair; unchanged-source flips are not attributed to improved or regressed accuracy. The original weak oracle, missing functional assertion, failed stage-2 aggregate workflow and separate artifact-only recovery are disclosed. Costs are single-run observations, and explicit candidate openings are distinguished from protocol opens. No universal equivalence, noninterference, leakage elimination, performance distribution, or general correctness gain is asserted.

## Authorization and metadata review

- Verified the decision record SHA-256: `ee6d16f86c937e6984dbab0211ce94c4ca638c2d6d5450bb6d6a6a89a24d082b`. It records the exact preceding two-gap question and the reply “yes go for it!” The current task also explicitly confirms this decision.
- The exception registry records REPORT_READINESS scope and preserves the older research-integration decision separately. R2 and R3 remain IN_PROGRESS; B3 remains BLOCKED. R9 PASS is a readiness decision with explicit exceptions, and REPORT remains IN_PROGRESS during this review. No professor waiver is claimed. This is Girish's decision to proceed with a candid draft, not a finding that the professor waived assignment requirements.
- The professor's assignment as preserved in `execution_contract.md` calls for a brief report covering methodology/reproduction, limitation, modification, code, comparison and difficulties; each is present. The parent reports separately rereading the 12 October assignment and 14 October source follow-up from Gmail. This reviewer did not independently access that mailbox and makes no mailbox-provenance claim.
- Reviewed the small diffs in `check_handoff.py`, `audit_final_evidence.py`, `verify_reproduction_difficulty_coverage.py` and related tests. The renderer now reflects authorized drafting while withholding submission. Audit output fields now state that the audit itself does not grant authorization, instead of denying an independent user decision. No scientific counts, evaluator behavior or experiment results are modified.
- Reviewed the two workflow changes: they add the report branch to the existing read-only evidence-audit and difficulty-accounting push triggers; they do not launch native candidates or model calls.
- Read `build_final_report.py`. It deterministically converts the current report's supported Markdown constructs, retains code and links, and does not invoke models. Its success is correctly separated from visual QA. This review did not create or visually inspect the DOCX/PDF; root's separate render verification remains necessary.

## Fresh verification observed

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest tests.test_handoff tests.test_original_reproduction_difficulty_coverage -v`: **30 tests, PASS**.
- `python scripts/check_handoff.py`: **PASS**, 21 phases / nine requirements / preserved evidence hashes verified.
- Independently retrieved exact research-base GitHub jobs: runs 39541724306, 39541724468, 39541724568 and 39541724665 are successful. The regression job log 119030743095 explicitly reports **189 tests, OK**; raw-evidence job 119030744230 explicitly reports **31 artifacts**, zero new native executions, zero new model calls, and exact base commit c237aa4a6d98a16b141a9b178a046a121ea1e659. This supports the report's base-snapshot statement, distinct from the report branch's later 190-test suite reported by root.

## Review boundaries

This was a read-only scientific/report/metadata review with one external note written at the explicitly permitted path. It did not rerun native experiments, download/re-audit every historical ZIP anew, reproduce historical model conversations, certify security, inspect document page images, merge changes, send email or submit anything. Final report-branch CI, final artifact-text/hash/render verification, and reviewed integration remain separate gates. Any later substantive report or code changes require a targeted recheck.

Integration note from primary agent: the review is dated 21 October UTC; it was preserved on 22 October in Europe/Helsinki. The reviewed report and guide hashes match commit `5e90d232f4d5aeadad3686c546e762b170749f00`.
