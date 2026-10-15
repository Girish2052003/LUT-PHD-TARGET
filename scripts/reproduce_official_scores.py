#!/usr/bin/env python3
"""Recalculate SPDZCoder's reported pass@1/pass@2 from ORIGINAL evaluation files.

This measures correctness flags previously produced by the authors' evaluator.
It is NOT a new compiler/emulator run, and it makes no LLM API calls.
"""
from __future__ import annotations

import argparse
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
        # Authors place human-readable repeats after this separator.
        if line.strip().startswith("********"):
            break
        match = RESULT_RE.match(line.strip())
        if not match:
            if line.strip():
                raise ValueError("Malformed machine-readable outcome row: " + line)
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


def validate_task_ids(native: set[str], ordered_groups: dict[str, list[str]]) -> None:
    """Reject equal-sized but different datasets, duplicates and reordered pairs."""
    expected_order = ordered_groups["processed"]
    for source, names in ordered_groups.items():
        if any(not isinstance(name, str) or not name for name in names):
            raise ValueError(f"Invalid task ID in {source}")
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicate task IDs in {source}")
        if set(names) != native:
            raise ValueError(f"Task IDs differ from native templates in {source}")
        if names != expected_order:
            raise ValueError(f"Task order differs from processed inputs in {source}")


def read_regular(tar: tarfile.TarFile, path: str) -> bytes:
    member = tar.getmember("SPDZCoder/" + path)
    if not member.isfile() or member.size > 8_000_000:
        raise ValueError("Not a bounded regular source file: " + path)
    handle = tar.extractfile(member)
    if handle is None:
        raise ValueError("Unreadable source: " + path)
    raw = handle.read(8_000_001)
    if len(raw) != member.size:
        raise ValueError("Wrong source length: " + path)
    return raw


def records(raw: bytes, expected: int) -> list[dict]:
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != expected or any(not isinstance(r, dict) or "test_name" not in r for r in rows):
        raise ValueError("Malformed records or incorrect split denominator")
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
              "saved_flag_meaning": "Author-evaluator acceptance; not independently established correctness",
              "task_identity_verified": True,
              "candidate_order_verified": True,
              "source_files": {}, "task_records": [], "per_split": {}}
    all_rows = []
    with tarfile.open(source_tar, "r:*") as tar:
        members = tar.getmembers()
        if len(members) != len({m.name for m in members}):
            raise ValueError("Duplicate archive member paths")
        for split, expected in COUNTS.items():
            paths = {
                "processed": f"data/input_processed_data/{split}.json",
                "generated": f"data/stage_3_output/experiment-1-{split}.jsonl",
                "baseline": f"data/baseline_output/gpt4-1-{split}.jsonl",
                "outcomes": f"evaluation/experiment-1-stage_3_output_{split}.txt",
            }
            raw = {kind: read_regular(tar, path) for kind, path in paths.items()}
            for kind, path in paths.items():
                result["source_files"][path] = hashlib.sha256(raw[kind]).hexdigest()
            data = {kind: records(raw[kind], expected) for kind in ("processed", "generated", "baseline")}
            rows = parse_results(raw["outcomes"].decode("utf-8"), expected)
            prefix = f"SPDZCoder/data/input_data/{split}/"
            native = {m.name[len(prefix):-4] for m in members
                      if m.isfile() and m.name.startswith(prefix) and m.name.endswith(".mpc")}
            if len(native) != expected or any("/" in name for name in native):
                raise ValueError("Native template count/paths differ for " + split)
            ids = {kind: [r["test_name"] for r in records_] for kind, records_ in data.items()}
            ids["outcomes"] = [r[0] for r in rows]
            validate_task_ids(native, ids)
            for position, (task, first, second) in enumerate(rows):
                template = f"data/input_data/{split}/{task}.mpc"
                template_sha = hashlib.sha256(read_regular(tar, template)).hexdigest()
                item = {"task_id": split + "/" + task, "position_in_split": position,
                        "template_path": template, "template_sha256": template_sha,
                        "archived_acceptance": [first, second], "candidate_sha256": {}}
                for system, kind in (("spdzcoder", "generated"), ("gpt4_api_docs", "baseline")):
                    sources = [data[kind][position].get(f"response_{i}") for i in (0, 1)]
                    if any(not isinstance(code, str) for code in sources):
                        raise ValueError("Malformed candidate source for " + item["task_id"])
                    item["candidate_sha256"][system] = [hashlib.sha256(code.encode("utf-8")).hexdigest() for code in sources]
                result["task_records"].append(item)
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
