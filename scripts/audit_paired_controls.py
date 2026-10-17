#!/usr/bin/env python3
"""Independent read-only audit of run 38989067493 raw GitHub Actions ZIP artifacts.

Example: python scripts/audit_paired_controls.py summary.zip seven-category-*.zip
No original program or generated candidate is executed.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import zipfile

SPLITS = {
    "array_test": 43, "loop_test": 97, "branch_test": 34, "math_test": 38,
    "numpy_operation_test": 32, "numpy_ufunc_test": 34, "syntax_test": 35,
}


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def audit(summary_zip, split_zips):
    with zipfile.ZipFile(summary_zip) as z:
        summary = json.loads(z.read("summary.json"))
        combined = [json.loads(line) for line in z.read("paired-records.jsonl").splitlines()]
    expected = {(r["task_id"], r["candidate_id"], r["variant"]): r for r in combined}
    if len(combined) != 1252 or len(expected) != 1252:
        raise ValueError("Expected 1,252 unique native execution records")
    records = {}
    found_splits = set()
    attempts_checked = 0
    for filename in split_zips:
        with zipfile.ZipFile(filename) as z:
            paths = [p for p in z.namelist() if re.fullmatch(
                r"paired-full/[^/]+/logs/[^/]+/(baseline|modified)/record\.json", p)]
            if not paths:
                raise ValueError(f"No records in {filename}")
            split = paths[0].split("/")[1]
            if split not in SPLITS or split in found_splits or len(paths) != 4 * SPLITS[split]:
                raise ValueError(f"Missing, repeated, or malformed category: {split}")
            found_splits.add(split)
            for path in paths:
                folder = path.removesuffix("record.json")
                row = json.loads(z.read(path))
                key = (row["task_id"], row["candidate_id"], row["variant"])
                if key not in expected or key in records or row != expected[key] or row["kind"] != "native":
                    raise ValueError(f"Unexpected, duplicated or changed aggregate record: {key}")
                if row["task_id"].split("/")[0] != split:
                    raise ValueError("Task/category identity mismatch")
                source = z.read(folder + "candidate.py.txt")
                raw = z.read(folder + "original.py.txt")
                proposed = z.read(folder + "transformed.py.txt")
                template = z.read(folder + "template.mpc")
                if any(digest(data) != row[name] for data, name in (
                    (source, "source_sha256"), (raw, "original_source_sha256"),
                    (proposed, "transformed_source_sha256"),
                    (template, "template_sha256"))):
                    raise ValueError(f"Source/template hash mismatch: {key}")
                if row["variant"] == "baseline" and source != raw:
                    raise ValueError(f"Baseline source altered: {key}")
                if row["variant"] == "modified" and source != proposed:
                    raise ValueError(f"Modified source/proposal mismatch: {key}")
                if not row["attempts"]:
                    raise ValueError(f"Empty attempts: {key}")
                final_stdout = ""
                for index, attempt in enumerate(row["attempts"]):
                    mpc = z.read(folder + f"attempt-{index}.mpc")
                    stdout = z.read(folder + f"attempt-{index}.stdout.txt")
                    stderr = z.read(folder + f"attempt-{index}.stderr.txt")
                    if any(digest(data) != attempt[name] for data, name in (
                        (mpc, "combined_source_sha256"),
                        (stdout, "stdout_sha256"), (stderr, "stderr_sha256"))):
                        raise ValueError(f"Raw attempt bytes changed: {key}/{index}")
                    final_stdout = stdout.decode("utf-8", "replace")
                    attempts_checked += 1
                compiled = re.search(r"^Hash: ([a-z0-9]+)$", final_stdout, flags=re.M)
                records[key] = {
                    "row": row, "source": source,
                    "mpc_sha256": row["attempts"][-1]["combined_source_sha256"],
                    "compiled_hash": compiled.group(1) if compiled else None,
                    "success_marker": bool(re.search(r"^Pass the test\s*$", final_stdout, flags=re.M)),
                }
    if found_splits != set(SPLITS) or set(records) != set(expected):
        raise ValueError("Incomplete native record coverage")
    tasks = {t for t, _, _ in records}
    if len(tasks) != 313 or any(sum(t.startswith(s + "/") for t in tasks) != n
                                for s, n in SPLITS.items()):
        raise ValueError("Incomplete 313-task category ledger")
    flips, changed, marker_disagreements = [], [], []
    for t in sorted(tasks):
        for candidate in (0, 1):
            before = records[t, candidate, "baseline"]
            after = records[t, candidate, "modified"]
            b, a = before["row"], after["row"]
            if (b["original_source_sha256"] != a["original_source_sha256"]
                or b["template_sha256"] != a["template_sha256"]):
                raise ValueError("Original candidate or native oracle changed")
            is_changed = before["source"] != after["source"]
            if is_changed:
                changed.append(f"{t} candidate {candidate}")
            elif (before["mpc_sha256"] != after["mpc_sha256"]
                  or before["compiled_hash"] != after["compiled_hash"]):
                raise ValueError("Byte-identical candidate has different compiled program")
            if b["oracle_status"] != a["oracle_status"]:
                flips.append({
                    "task_id": t, "candidate_id": candidate,
                    "source_changed": is_changed,
                    "baseline": b["oracle_status"], "modified": a["oracle_status"],
                    "same_mpc_sha256": before["mpc_sha256"] == after["mpc_sha256"],
                    "same_compiler_hash": before["compiled_hash"] == after["compiled_hash"],
                    "compiler_hash": before["compiled_hash"],
                })
            for variant, entry in (("baseline", before), ("modified", after)):
                if (entry["row"]["oracle_status"] == "ACCEPT") != entry["success_marker"]:
                    marker_disagreements.append([t, candidate, variant])
    # These are observations specific to this pinned run, not universal assumptions.
    if len(changed) != 2 or len(flips) != 4 or any(f["source_changed"] for f in flips):
        raise ValueError("Unexpected outcome/source change pattern; manual review required")
    outcomes = {}
    for variant in ("baseline", "modified"):
        counts = {
            "first": sum(records[t, 0, variant]["row"]["oracle_status"] == "ACCEPT" for t in tasks),
            "second": sum(records[t, 1, variant]["row"]["oracle_status"] == "ACCEPT" for t in tasks),
            "union": sum(any(records[t, c, variant]["row"]["oracle_status"] == "ACCEPT"
                             for c in (0, 1)) for t in tasks),
        }
        published = summary["variants"][variant]["overall"]
        if any(counts[k] != published[{"first": "first_accepted",
                                     "second": "second_accepted",
                                     "union": "union_accepted"}[k]] for k in counts):
            raise ValueError(f"Aggregate score mismatch: {variant}")
        outcomes[variant] = counts
    return {
        "source_run": 38989067493, "tasks": 313, "pairs": 626,
        "executions": len(records), "attempts_checked": attempts_checked,
        "changed_candidates": changed, "unchanged_source_flips": flips,
        "outcomes": outcomes, "oracle_marker_disagreements": marker_disagreements,
        "interpretation": "Identical-source flips cannot be credited to the postprocessor. "
                          "Causes of outcome variability not established. "
                          "The audit does not rerun MASCOT or prove confidentiality.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("summary", type=Path)
    p.add_argument("splits", type=Path, nargs=7)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    evidence = json.dumps(audit(args.summary, args.splits), sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(evidence)
    print(evidence)


if __name__ == "__main__":
    main()
