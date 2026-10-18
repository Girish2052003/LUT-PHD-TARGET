# Historical GPT-4 Turbo access: Phase B3 decision evidence (18 October 2026)

**Research reproducibility status, not an authorization, original LLM experiment, or final professor-facing report.**

## New externally verified time constraint

OpenAI's official deprecations page (https://developers.openai.com/api/docs/deprecations, section “2026-04-22: Legacy GPT model snapshots”) schedules the **OpenAI API** shutdown of the model snapshot `gpt-4-turbo-2024-04-09` and `gpt-4-turbo` alias for **23 October 2026**. As of this record date, this is a **future** shutdown, not proof the model is already inaccessible.

Official source: https://developers.openai.com/api/docs/deprecations
Official model detail: https://developers.openai.com/api/docs/models/gpt-4-turbo
Retrieved for project gate review: **18 October 2026**.

## Why the actual original experiment is not automatically unblocked

The paper identifies the model snapshot `gpt-4-turbo-2024-04-09`, while the released original launch maps `azure-gpt4` to an Azure deployment identifier `gpt-4`; the exact historical Azure deployment's snapshot revision, region, account access and rollout/retirement status are **not pinned by the released source** (see `research/original_source_audit.md` and `research/reviews/phase-a-paper-source-crosswalk-20261018.md`). An **OpenAI API** shutdown date does **not** establish the particular authors' **Azure deployment** shutdown date, historical weight identity, or that Girish has/had access. Microsoft previously documented GA availability of `turbo-2024-04-09` on Azure, but historical general availability does not prove present account-specific deployment access:
https://techcommunity.microsoft.com/blog/azure-ai-services-blog/announcing-the-general-availability-of-gpt-4-turbo-with-vision-on-azure-openai-s/4127916

No historical model credentials/outputs or paid model invocations were used in this gate review. Even a now-accessible API snapshot would not recover the missing exact original historical prompts/transcripts, sampling, tool-side deployments, nondeterministic responses, and full chronological model history.

## User decision needed (not assumed)

- **Option A — attempt independently labeled new model generation:** First identify accessible exact 2024-04-09 snapshot and its actual provider/deployment, gain Girish's *explicit* permission for legal credentials, API usage and a defined cost limit, then run a controlled pilot. If original model/provenance cannot be identified, never describe a contemporary or different-model trial as the historical original pipeline. The professor's deadline is 31 October 2026; OpenAI API legacy snapshot shutdown is scheduled 23 October, creating a separate time constraint.
- **Option B — explicitly accept bounded irreproducibility:** Girish explicitly accepts that actual historical GPT generation cannot be reproduced under presently available pinned evidence; the paper's genuine SPDZCoder *without-refactoring* ablation corpus cannot be identified; their original published claims remain attributed to the paper, **not independently reproduced**. Preserve Level 1 saved reconstruction, complete Level 2 native replay, original-source modification, paired experiments, negative results and blockers. Do not elevate B3 to PASS or claim a complete historical generation. The accepted exception must be recorded in a separate attributable decision in the R1–R9 gate ledger before readiness is considered.

**Current action state:** PENDING_USER_DECISION. No billable API calls or exception approval inferred from a generic request to continue working. B3 BLOCKED, R2/R3/R8 IN_PROGRESS, G IN_PROGRESS, R9/REPORT BLOCKED. A successful exact-head CI or technical mergeability cannot substitute for this scientific decision.
