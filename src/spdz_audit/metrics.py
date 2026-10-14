"""Metrics for genuine candidate samples; deterministic experiments use counts."""
from math import prod


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased HumanEval-style estimator: 1 - C(n-c,k) / C(n,k).

    Callers must supply actual independent sampled candidates. This function
    cannot turn hand-written variants, retries or repeated inputs into samples.
    """
    if any(type(v) is not int for v in (n, c, k)) or not (n >= 1 and 0 <= c <= n and 1 <= k <= n):
        raise ValueError('Require integer n>=1, 0<=c<=n, and 1<=k<=n')
    if n - c < k:
        return 1.0
    return 1.0 - prod((n - c - i) / (n - i) for i in range(k))


def paired_counts(baseline: list[bool], modified: list[bool]) -> dict[str, int]:
    """Count paired improvements AND regressions without dropping observations."""
    if len(baseline) != len(modified) or any(type(x) is not bool for x in baseline + modified):
        raise ValueError('Supply equally sized lists of boolean outcomes')
    counts = dict(both_pass=0, improved=0, regressed=0, both_fail=0)
    for old, new in zip(baseline, modified):
        counts['both_pass' if old and new else 'regressed' if old else 'improved' if new else 'both_fail'] += 1
    return counts
