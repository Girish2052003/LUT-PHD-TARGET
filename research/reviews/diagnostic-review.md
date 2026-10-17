# Diagnostic pre-execution review

Independent reviewer: `diagnostic_review`, 15 October 2026. Read-only review of
the new limitation runner, restricted launcher, build context and workflow.

The reviewer verified original candidate hashes for `count_distinct` and
`lower_bound`, and their prior fresh native MASCOT acceptance. MP-SPDZ 0.3.6's
`sint.reveal` emits a public opening; `sfix.reveal` delegates to it. Printing the
returned clear value makes that party-visible observation inspectable without
adding another opening. This is conditional on the stated private-input and
output-only policy; it is not a historical data-breach claim.

The first review found that process completion alone could let an unconfirmed
hypothesis produce green CI. The runner now additionally checks 16 unique cases,
the native marker/acceptance predictions, original/instrumented authorized-output
agreement, exact predicted observation counts/values and differing observations
for equal permitted outputs. An independent hand-built fixture passed, and a
wrong authorized output was rejected. Three focused tests passed.

The final review found no blocker to restricted execution. Both input pairs for
`count_distinct` return 2, with predicted opened patterns `[0,1,1]` versus
`[1,1,0]`. Both `lower_bound` pairs return index 1, with opened differences
`[3,1,-1]` versus `[2,1,-2]`; public x=4 reconstructs the private values.

No author/generated program ran on the host. No witness or improvement is
accepted until actual CI execution and raw-evidence review are complete.
