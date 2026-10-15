#!/usr/bin/env python3
"""Static, read-only screening of original SPDZCoder vs original GPT-4 outputs.

This deliberately records potentially interesting constructs for *manual review*.
A .reveal() or print_ln() call is not inherently an unauthorized declassification.
No downloaded source code is executed, and this is not a noninterference proof.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import tarfile

SPLITS = (
    "array_test", "loop_test", "branch_test", "math_test",
    "numpy_operation_test", "numpy_ufunc_test", "syntax_test",
)
EXPECTED = (43, 97, 34, 38, 32, 34, 35)
MD5 = "3c6d7707d7aecc051d35312f81405c66"

OUTPUT_NAMES = {"print", "print_ln", "print_str", "print_float"}
REVEAL_NAMES = {"reveal", "reveal_list"}


def screen(source: str) -> dict:
    """A small, defensible *syntactic* inventory; no secret-flow assumptions."""
    if not isinstance(source, str):
        raise TypeError("Generated code must be a string")
    clean = source.strip()
    if clean.startswith("```"):
        clean = re.sub(r"^\`{3}(?:python|mpc)?[ \t]*\r?\n?", "", clean)
        clean = re.sub(r"\r?\n?\`{3}[ \t]*$", "", clean)
    flags: Counter[str] = Counter()
    try:
        tree = ast.parse(clean)
    except (SyntaxError, ValueError) as exc:
        return {"parse_ok": False, "parse_error": type(exc).__name__,
                "flags": {}, "sha256": hashlib.sha256(source.encode()).hexdigest()}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if isinstance(fn, ast.Attribute) and fn.attr in REVEAL_NAMES:
            flags["reveal_call"] += 1
        elif isinstance(fn, ast.Name) and fn.id in REVEAL_NAMES:
            flags["reveal_call"] += 1
        if ((isinstance(fn, ast.Name) and fn.id in OUTPUT_NAMES)
                or (isinstance(fn, ast.Attribute) and fn.attr in OUTPUT_NAMES)):
            flags["public_output_call"] += 1
    return {"parse_ok": True, "flags": dict(flags),
            "sha256": hashlib.sha256(source.encode()).hexdigest()}


def load_jsonlines(tar: tarfile.TarFile, filename: str, expected: int) -> dict[str, dict]:
    member = tar.getmember("SPDZCoder/" + filename)
    if not member.isfile() or member.size > 15_000_000:
        raise ValueError("Unexpected file kind/size " + filename)
    fp = tar.extractfile(member)
    if fp is None:
        raise ValueError("Unreadable file " + filename)
    rows = [json.loads(line) for line in fp.read().decode("utf-8").splitlines() if line.strip()]
    if len(rows) != expected:
        raise ValueError(f"Expected {expected} rows in {filename}, got {len(rows)}")
    result = {}
    for row in rows:
        name = row.get("test_name")
        if not isinstance(name, str) or name in result or not name:
            raise ValueError("Missing or duplicate original task name in " + filename)
        for candidate in (0, 1):
            if not isinstance(row.get(f"response_{candidate}"), str):
                raise ValueError("Missing original candidate in " + filename)
        result[name] = row
    return result


def audit(path: Path) -> dict:
    if hashlib.md5(path.read_bytes()).hexdigest() != MD5:
        raise ValueError("Source archive differs from published Zenodo checksum")
    output = {
        "provenance": "https://zenodo.org/records/18152253",
        "authors_archive_md5": MD5,
        "candidate_generation": "original saved outputs, not new generations",
        "analysis": "static indicator inventory, not actual confirmed leaks",
        "groups": {}, "totals": {},
    }
    counts = {name: Counter() for name in ("spdzcoder", "gpt4_api_doc")}
    with tarfile.open(path, "r:*") as tar:
        for partition, n in zip(SPLITS, EXPECTED):
            final = load_jsonlines(tar,
                "data/stage_3_output/experiment-1-" + partition + ".jsonl", n)
            original_baseline = load_jsonlines(tar,
                "data/baseline_output/gpt4-1-" + partition + ".jsonl", n)
            if final.keys() != original_baseline.keys():
                raise ValueError("Task identifiers differ across original model variants: " + partition)
            output["groups"][partition] = {
                "task_count": n, "candidate_count_per_system": 2*n,
                "per_task": [],
            }
            for task in sorted(final):
                taskrow = {"id": task}
                for label, rows in (("spdzcoder", final), ("gpt4_api_doc", original_baseline)):
                    checked = [screen(rows[task][f"response_{i}"]) for i in (0, 1)]
                    taskrow[label] = checked
                    for candidate in checked:
                        counts[label]["candidate_total"] += 1
                        if not candidate["parse_ok"]:
                            counts[label]["parse_failures"] += 1
                        for flag in candidate["flags"]:
                            counts[label]["candidates_with_"+flag] += 1
                            counts[label]["occurrences_"+flag] += candidate["flags"][flag]
                output["groups"][partition]["per_task"].append(taskrow)
    output["totals"] = {label: dict(count) for label,count in counts.items()}
    for label,count in counts.items():
        if count["candidate_total"] != 626:
            raise AssertionError("Missing original generated candidates: " + label)
        print("AUTHORS GENERATED CANDIDATE STATIC REVIEW:", label, json.dumps(dict(count)))
    return output


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--tar", default="results/official_artifacts/SPDZCoder.tar")
    p.add_argument("--output", default="results/official_artifacts/original_privacy_indicator_audit.json")
    args = p.parse_args()
    report = audit(Path(args.tar))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    print("SAVED ORIGINAL CANDIDATE AUDIT:", out)


if __name__ == "__main__":
    main()
