#!/usr/bin/env python3
"""Recalculate SPDZCoder's reported pass@1/pass@2 from ORIGINAL evaluation files.

This measures correctness flags previously produced by the authors' evaluator.
It is NOT a new compiler/emulator run, and it makes no LLM API calls.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import tarfile

ZENODO_MD5 = "3c6d7707d7aecc051d35312f81405c66"
COUNTS = {
    "array_test": 43, "loop_test": 97, "branch_test": 34,
    "math_test": 38, "numpy_operation_test": 32, "numpy_ufunc_test": 34,
    "syntax_test": 35
}
RESULT_RE = re.compile(r"^([^,\r\n]+),\s*(True|False),\s*(True|False)\s*$")


def parse_results(report_text: str, n_expected: int) -> list[tuple[str, bool, bool]]:
    """Take the first machine-readable output section; reject extra/missing tasks."""
    rows = []
    ids = set()
    for line in report_text.splitlines():
        match = RESULT_RE.match(line.strip())
        if not match:
            continue
        if len(rows) >= n_expected:
            raise ValueError("More machine-readable task rows than expected")
        name, c0, c1 = match.groups()
        name = name.strip()
        if name in ids:
            raise ValueError("Repeated task in authors' evaluation output: " + name)
        ids.add(name)
        rows.append((name, c0 == "True", c1 == "True"))
    if len(rows) != n_expected:
        raise ValueError(f"Expected {n_expected} outcomes, found {len(rows)}")
    return rows


def measure(rows: list[tuple[str, bool, bool]]) -> dict:
    n = len(rows)
    count0 = sum(v0 for _, v0, _ in rows)
    count1 = sum(v1 for _, _, v1 in rows)
    union = sum(v0 or v1 for _, v0, v1 in rows)
    return {
        "n": n, "first_correct": count0, "second_correct": count1,
        "at_least_one_correct": union,
        "pass_at_1_first_percent": round(100 * count0 / n, 5),
        "pass_at_1_second_percent": round(100 * count1 / n, 5),
        "pass_at_2_percent": round(100 * union / n, 5),
    }


def reproduce(source_tar: Path) -> dict:
    if hashlib.md5(source_tar.read_bytes()).hexdigest() != ZENODO_MD5:
        raise ValueError("Source archive differs from the Zenodo release")
    result = {"source": "https://zenodo.org/records/18152253",
              "source_archive_md5": ZENODO_MD5,
              "metric_source": "original authors' saved evaluation flags",
              "fresh_compiler_evaluation": False,
              "live_model_requests": 0,
              "per_split": {}}
    all_rows = []
    with tarfile.open(source_tar, "r:*") as tar:
        for split, expected in COUNTS.items():
            name = f"SPDZCoder/evaluation/experiment-1-stage_3_output_{split}.txt"
            source = tar.extractfile(tar.getmember(name))
            if source is None:
                raise ValueError("Unreadable original evaluation " + name)
            rows = parse_results(source.read().decode("utf-8", errors="replace"), expected)
            metrics = measure(rows)
            result["per_split"][split] = metrics
            all_rows.extend([(split, task, v0, v1) for task, v0, v1 in rows])
            print("ORIGINAL SAVED EVALUATION:", split, json.dumps(metrics))
    total = measure([(split+"/"+task,v0,v1) for split,task,v0,v1 in all_rows])
    if total["n"] != 313:
        raise AssertionError("Original task total was not 313")
    result["overall"] = total
    print("ORIGINAL SAVED EVALUATION TOTAL:", json.dumps(total))
    print("Paper reports: pass@1 85.94%; pass@2 92.01%.")
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--tar", default="results/official_artifacts/SPDZCoder.tar")
    p.add_argument("--output", default="results/official_artifacts/original_saved_evaluation_metrics.json")
    args = p.parse_args()
    result = reproduce(Path(args.tar))
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n")
    print("SAVED RESULTS:", dest)


if __name__ == "__main__":
    main()
