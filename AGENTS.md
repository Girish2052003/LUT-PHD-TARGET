# Research continuity

Before editing, read `HANDOFF.md`, `research/progress.json`, and
`research/requirements/assignment_traceability.yaml`. Fetch and inspect current
remote refs and open PRs; historical SHAs are not permission to overwrite work.

Continue the next unfinished phase. Do not recreate completed milestones unless
a changed dependency, missing evidence or reproducibility failure requires it;
record that reason. A PASS requires implementation, execution, preserved evidence
and independent checking. Keep original-author evidence, fresh replay, model
generation and independent reconstruction distinct.

After a phase changes, update the machine-readable records and run:

```bash
python scripts/check_handoff.py --render
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/check_handoff.py
```

Use research branches and independent review/CI before merging into `main`.
Preserve unmerged branches and historical evidence. The controlling user contract
is `research/requirements/execution_contract.md`.

No paid model calls or substitute models are authorized. Final-report writing is
locked until the practical gates are accepted and Girish explicitly authorizes
it. No email is authorized. Existing report drafts are historical, not final.
