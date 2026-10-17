# Accepted original-modification paired smoke — E1

Independent reviewer: `diagnostic_review`, 17 October 2026. **GO for this narrow
smoke only**; full Phase E/F and assignment acceptance remain open.

Run38958484872, job117167248922, commit35adfb04c1132ae91d1b2c6e21cf791855eab768,
artifact12072157406. The 569,647-byte ZIP has SHA-256
`5803b934764c15b5ef02e0b1fc5f865e0c8a25c9281148ec6d5d64a566bd3fdc`.
All718files are preserved under `research/evidence/2026-10-16/paired-smoke/`.

The reviewer reconstructed checks without using the project's verifier: all
32pairs/64executions, original and transformed candidates, template/input bytes,
source insertion, raw streams and both party logs. All922baseline files,
36MP-SPDZ sources, official binary, unchanged evaluator and resolved packages
match their pins. Removing the two added statements from each pipeline restores
its original AST. Independently derived transformations remove exactly the
targeted reveal; removing observer wrappers restores the appropriate candidate
AST. No downloaded candidate executed on the review host.

Every execution compiled and completed at the original60-second timeout with one
attempt. Both variants share the same container and matched inputs; pair order
alternates. The two native candidate pairs are accepted before and after the
change. All56private-input observed/control executions and four synthetic
fallback executions return independently calculated expected results. Synthetic
fallback source remains byte-identical.

| Authentic candidate; private witness inputs | Authorized output | Original opening traces | Modified traces |
|---|---|---|---|
| count_distinct c1; [1,1,2] / [1,2,2] | 2 / 2 | [0,1,1] / [1,1,0] | empty / empty |
| is_ascending c0; [1,1,2] / [1,2,2] | 0 / 0 | [1,0] / [0,1] | empty / empty |

Across24observed private-input probes, **50original opening events become zero**.
Twenty original executions have nonempty traces; empty/singleton cases contribute
none. These are events, not50distinct vulnerabilities. Plain observer controls
preserve the same authorized results. The diagnostic harness has no native Pass
marker, so its author-oracle REJECT is expected and is excluded from native rates.

| Native candidate | Runtime seconds, original → modified | Global MB, original → modified | Compiler integer opens | Integer triples |
|---|---:|---:|---:|---:|
| count_distinct c1 | 28.5628 → 31.3084 | 390.364 → 429.331 | 191 → 98 | 2917 → 3010 |
| is_ascending c0 | 14.2188 → 14.2445 | 195.163 → 195.164 | 35 → 18 | 2042 → 2059 |

These are single-run descriptive costs including preprocessing; no statistical
speed claim follows. Compiler opens include protocol operations and must not be
equated with the observer's explicit candidate-opening events.

Accepted scope: a measured repair of the comparison-mask opening pattern in two
authentic archived translations under the explicit private-input/output-only
policy. Exact added pipeline finalizer statements were exercised; preceding model
stages were not regenerated. No formal confidentiality guarantee follows.
`lower_bound` remains unchanged. Complete native regression requires its own
experiment and independent acceptance.
