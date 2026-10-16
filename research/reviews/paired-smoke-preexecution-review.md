# Paired-smoke pre-execution review — bounded GO

Reviewer: `replay_safety_review`, 16 October 2026.

The reviewer independently confirmed the fixed inventory of 32 pairs / 64
executions: two native, 24 observed private-input, four private controls and two
synthetic fallback pairs. Candidate/template identity, matched inputs, alternating
order, unchanged evaluator and container restrictions were checked. Both pipeline
patches regenerate from pinned originals, and manifests/packages are anchored to
accepted baseline evidence.

One blocker was found: JSON converts regex tuples into lists, so the evidence
checker's direct comparison would falsely reject every nonempty opening trace.
A JSON-round-trip test reproduced the failure; list normalization fixed it while
preserving tampering rejection. The reviewer independently ran all six focused
pairing/patch tests successfully. The primary agent ran all 99 repository tests.

Decision: **GO for this restricted smoke only**. There is no runtime, full paired
regression, full-generation, general confidentiality, or merge acceptance yet.
Inspect and preserve all execution failures; do not weaken the pre-specified
policy to make the smoke green. No downloaded candidate executed on the host.

Reviewed launch files (SHA-256):

```json
{
  "scripts/apply_original_postprocess.py": "24173f44cdcdd316f9ca331e9a0b398f57ac7894323279829e46125ed52a03c7",
  "scripts/replay_modified.py": "58de75c99504738d32551cec3abcf246b5cdc8d2cc5a0a7efdf0576262ed85f1",
  "scripts/verify_paired_replay.py": "f1452c8cf2d0e29cc03545e8973e60f06757c27c89ed31c546a6e5eb21891881",
  "research/modifications/secret_arithmetic.py": "8c93f4687569c7419b573b20b1349b2d67563a39ce50dba16fda38dd197d8aa2",
  "research/modifications/Dockerfile": "0bf5a65bee49c23449f028fbec5f02522b1466709483528b5d0baf90b00ecaad",
  "scripts/run_original_replay_container.sh": "e72a2a5449b7b90608a6baaf4699fc203e3a5dad8e793b02bc07a39c04894e07",
  ".github/workflows/modified-original-comparison.yml": "1d98dff0858241878143c52ffab03b030c48e61b167dc861f0cca8ffbb068da3"
}
```
