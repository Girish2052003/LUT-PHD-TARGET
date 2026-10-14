#!/usr/bin/env python3
"""Recompute result counts from raw observations; never trust summary alone."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


def verify(folder: Path):
    summary = json.loads((folder / "summary.json").read_text())
    provenance = json.loads((folder / "provenance.json").read_text())
    raw = (folder / "observations.jsonl").read_bytes()
    if hashlib.sha256(raw).hexdigest() != provenance["observations_sha256"]:
        raise ValueError("Observation SHA-256 differs from provenance")
    pairs = defaultdict(dict)
    counts = defaultdict(Counter)
    tasks = defaultdict(lambda: defaultdict(list))
    for line in raw.splitlines():
        row = json.loads(line)
        mode = row["mode"]
        if mode not in ("baseline", "safe"):
            raise ValueError("Unexpected mode")
        if row["status"] not in ("pass", "mismatch", "nonfinite", "exception"):
            raise ValueError("Unexpected status")
        key = (row["task"], row["input_id"])
        if mode in pairs[key]:
            raise ValueError("Duplicate paired observation")
        pairs[key][mode] = row
        counts[mode][row["status"]] += 1
        tasks[row["task"]][mode].append(row["status"] == "pass")
    if not pairs or len(pairs) != summary["inputs"] or len(tasks) != summary["tasks"]:
        raise ValueError("Input or task count mismatch")
    task_summary = {t["task"]: t for t in summary["task_results"]}
    if set(task_summary) != set(tasks):
        raise ValueError("Task list mismatch")
    paired = Counter()
    for key, pair in pairs.items():
        if set(pair) != {"baseline", "safe"}:
            raise ValueError("Missing paired mode")
        if pair["baseline"]["x"] != pair["safe"]["x"] or pair["baseline"]["expected"] != pair["safe"]["expected"]:
            raise ValueError("Paired inputs differ")
    for task, modes in tasks.items():
        item = task_summary[task]
        for mode in ("baseline", "safe"):
            if len(modes[mode]) != item["inputs"] or sum(modes[mode]) != item["passed_inputs"][mode]:
                raise ValueError("Incorrect per-task input counts")
            if all(modes[mode]) != item["passed"][mode]:
                raise ValueError("Incorrect task pass flag")
        a, b = item["passed"]["baseline"], item["passed"]["safe"]
        paired["both_pass" if a and b else "regressed" if a else "improved" if b else "both_fail"] += 1
    for mode in ("baseline", "safe"):
        if counts[mode]["pass"] != summary["modes"][mode]["passed_inputs"]:
            raise ValueError("Incorrect total pass count")
        if dict(counts[mode]) != summary["modes"][mode]["outcomes"]:
            raise ValueError("Incorrect outcome counts")
        if sum(all(value[mode]) for value in tasks.values()) != summary["modes"][mode]["passed_tasks"]:
            raise ValueError("Incorrect task pass total")
    for key in ("both_pass", "improved", "regressed", "both_fail"):
        if paired[key] != summary["paired_tasks"][key]:
            raise ValueError("Incorrect paired task comparison")
    if len(json.loads((folder / "source_manifest.json").read_text())) != len(tasks):
        raise ValueError("Incomplete source manifest")
    result = dict(verified_tasks=len(tasks), verified_pairs=len(pairs),
                  baseline_passes=counts["baseline"]["pass"], safe_passes=counts["safe"]["pass"],
                  baseline_failures=len(pairs) - counts["baseline"]["pass"],
                  safe_failures=len(pairs) - counts["safe"]["pass"],
                  dataset="independent_domain_safety_stress_set_NOT_SPDZEval")
    (folder / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=Path("results/semantic"))
    print(json.dumps(verify(parser.parse_args().results), indent=2))
