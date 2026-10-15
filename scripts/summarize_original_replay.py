#!/usr/bin/env python3
"""Verify original replay artifacts and aggregate complete, identity-bound outcomes."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.replay_original import classify_attempt
from scripts.prepare_original_replay import AUTHOR_SHA, MP_COMMIT


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def aggregate(records, identity, systems):
    tasks = {x["task_id"]: x for x in identity["task_records"]}
    if len(tasks) != len(identity["task_records"]) or len(set(systems)) != len(systems):
        raise ValueError("Duplicate identity or system")
    expected = {(task, system, candidate) for task in tasks for system in systems for candidate in (0, 1)}
    seen = {}
    for row in records:
        task, system, candidate = row["task_id"], row["system"], row["candidate_id"]
        key = (task, system, candidate)
        if type(candidate) is not int or key not in expected or key in seen:
            raise ValueError("Unexpected or duplicate candidate: " + repr(key))
        reference = tasks[task]
        if row["category"] != task.split("/")[0]:
            raise ValueError("Category/task mismatch: " + task)
        if row["source_sha256"] != reference["candidate_sha256"][system][candidate] or row["template_sha256"] != reference["template_sha256"]:
            raise ValueError("Original identity/hash mismatch: " + task)
        allowed = {"oracle_status": {"ACCEPT", "REJECT"}, "runtime_status": {"PASS", "FAIL", "TIMEOUT", "NOT_RUN"},
                   "compile_status": {"PASS", "FAIL", "TIMEOUT", "NOT_RUN", "UNKNOWN"}}
        if any(row[k] not in choices for k, choices in allowed.items()):
            raise ValueError("Malformed execution status: " + task)
        if not isinstance(row["duration_seconds"], (int, float)) or not math.isfinite(row["duration_seconds"]) or row["duration_seconds"] < 0:
            raise ValueError("Invalid duration")
        if row["exception"] is not None:
            raise ValueError("Unresolved harness error: " + task)
        seen[key] = row
    if set(seen) != expected:
        raise ValueError(f"Incomplete replay: expected {len(expected)}, observed {len(seen)}")

    def metrics(ids, system):
        first = sum(seen[(t, system, 0)]["oracle_status"] == "ACCEPT" for t in ids)
        second = sum(seen[(t, system, 1)]["oracle_status"] == "ACCEPT" for t in ids)
        union = sum(any(seen[(t, system, c)]["oracle_status"] == "ACCEPT" for c in (0, 1)) for t in ids)
        return {"tasks": len(ids), "first_accepted": first, "second_accepted": second, "union_accepted": union,
                "first_percent": 100 * first / len(ids), "second_percent": 100 * second / len(ids), "union_percent": 100 * union / len(ids)}

    summary = {"scope": "Fresh unchanged-author-evaluator acceptance; not independent proof of correctness or fresh model generation",
               "candidate_records": len(records), "task_count": len(tasks), "live_model_calls": 0, "systems": {}}
    categories = sorted({t.split('/')[0] for t in tasks})
    for system in systems:
        rows = [r for r in records if r["system"] == system]
        summary["systems"][system] = {
            "overall": metrics(tasks, system),
            "categories": {c: metrics([t for t in tasks if t.split('/')[0] == c], system) for c in categories},
            "compile_statuses": dict(sorted(Counter(r["compile_status"] for r in rows).items())),
            "runtime_statuses": dict(sorted(Counter(r["runtime_status"] for r in rows).items())),
            "failure_classes": dict(sorted(Counter(r["failure_class"] or "none" for r in rows).items())),
            "accepted_without_completed_runtime": sum(r["oracle_status"] == "ACCEPT" and r["runtime_status"] != "PASS" for r in rows),
            "total_candidate_wall_seconds": sum(r["duration_seconds"] for r in rows),
            "historical_disagreements": sum((r["oracle_status"] == "ACCEPT") != tasks[r["task_id"]]["archived_acceptance"][r["candidate_id"]] for r in rows) if system == "spdzcoder" else None,
        }
    return summary


def checked_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_dir():
        raise ValueError("Unsafe or missing log path")
    return path


def verify_run(root):
    """Recompute classifications, digests and author decisions from raw streams."""
    rows = [json.loads(line) for line in (root / "outcomes.jsonl").read_text().splitlines() if line.strip()]
    summary = json.loads((root / "summary.json").read_text())
    if summary["attempted"] != summary["expected"] or summary["attempted"] != len(rows) or summary["harness_errors"] or summary["baseline_source_unchanged"] is not True or summary["live_model_calls"] != 0:
        raise ValueError("Incomplete or unhealthy run: " + str(root))
    for row in rows:
        folder = checked_path(root, row["log_path"])
        if json.loads((folder / "outcome.json").read_text()) != row:
            raise ValueError("Per-candidate outcome differs from run table")
        attempts = row["attempts"]
        if len(attempts) > 3:
            raise ValueError("Original retry budget exceeded")
        if attempts and attempts[-1]["timed_out"] and len(attempts) != 3:
            raise ValueError("Original retry exhaustion requires exactly three timed-out attempts")
        accepted = False
        for index, attempt in enumerate(attempts):
            task_name = row["task_id"].split('/')[1]
            expected_command = f"/mp-spdz/Scripts/compile-run.py -E mascot /baseline/evaluation/evaluation_storage/{task_name}.mpc"
            if attempt["command"] != expected_command:
                raise ValueError("Original command/task/protocol changed")
            out, err = folder / f"attempt-{index}.stdout.txt", folder / f"attempt-{index}.stderr.txt"
            source = folder / f"attempt-{index}.mpc"
            if sha(out) != attempt["stdout_sha256"] or sha(err) != attempt["stderr_sha256"] or sha(source) != attempt["combined_source_sha256"]:
                raise ValueError("Raw attempt digest mismatch")
            stdout, stderr = out.read_text(), err.read_text()
            runtime_marker = "mascot-party.x" in stderr and "Running " in stderr
            if runtime_marker != attempt["runtime_launch_marker"]:
                raise ValueError("Runtime marker mismatch")
            status = classify_attempt(attempt["returncode"], attempt["timed_out"], attempt["schedule_present"], runtime_marker)
            if any(attempt[k] != v for k, v in status.items()):
                raise ValueError("Attempt classification mismatch")
            expected_timeout = (150 if any(s in row["category"] for s in ("math", "ufunc")) else 60) + 30 * index
            if attempt["timeout_seconds"] != expected_timeout or (index < len(attempts) - 1 and not attempt["timed_out"]):
                raise ValueError("Original retry progression changed")
            accepted = not attempt["timed_out"] and "pass" in stdout.lower() and "Traceback" not in stderr.strip()
        if (row["oracle_status"] == "ACCEPT") != accepted:
            raise ValueError("Author oracle differs from raw streams")
        if attempts:
            last = attempts[-1]
            if row["combined_source_sha256"] != last["combined_source_sha256"] or row["output_digest"] != last["stdout_sha256"] or any(row[k] != last[k] for k in ("compile_status", "runtime_status")):
                raise ValueError("Last-attempt outcome mismatch")
        elif row["combined_source_sha256"] is not None or row["source_sha256"] != hashlib.sha256(b"").hexdigest():
            raise ValueError("Nonempty candidate lacks execution evidence")
    if summary["accepted"] != sum(r["oracle_status"] == "ACCEPT" for r in rows) or summary["runtime_completed"] != sum(r["runtime_status"] == "PASS" for r in rows):
        raise ValueError("Run totals differ from candidate outcomes")
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True, help="Only full-run artifacts, excluding smoke/probe duplicates")
    p.add_argument("--identity", default="research/evidence/2026-10-14/identity_verified_scores.json")
    p.add_argument("--systems", nargs="+", default=["spdzcoder", "gpt4_api_docs"])
    p.add_argument("--output", required=True)
    args = p.parse_args()
    records, environments, pins = [], [], set()
    reference = Path(__file__).resolve().parents[1] / 'research/evidence/2026-10-15/original-smoke/smoke'
    for file in sorted(Path(args.root).rglob("outcomes.jsonl")):
        root = file.parent
        records.extend(verify_run(root))
        env = json.loads((root / "environment.json").read_text())
        if env["api_calls"] != 0 or env["protocol"] != "MASCOT" or env["parties"] != 2:
            raise ValueError("Unexpected replay configuration")
        if env["source_archive_sha256"] != AUTHOR_SHA or env["mp_spdz_commit"] != MP_COMMIT or env["mascot_binary_sha256"] != '2a592fec9a9f9d0e7e8148bdf9ee7a67811dd6781c333981b386f3d1b7c8a5b3':
            raise ValueError("Replay differs from the reviewed original source/runtime pins")
        for name in ('source_manifest.json', 'installed-packages.txt', 'os-packages.txt'):
            if sha(root / name) != sha(reference / name):
                raise ValueError("Replay environment differs from reviewed smoke: " + name)
        pins.add((env["research_commit"], env["mp_spdz_commit"], env["source_archive_sha256"], env["mascot_binary_sha256"],
                  sha(root / "source_manifest.json"), sha(root / "installed-packages.txt"), sha(root / "os-packages.txt")))
        environments.append(env)
    if len(pins) != 1:
        raise ValueError("Mixed or absent source/environment pins")
    result = aggregate(records, json.loads(Path(args.identity).read_text()), args.systems)
    result["research_commit"] = environments[0]["research_commit"]
    result["run_count"] = len(environments)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    (output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    (output / "outcomes.jsonl").write_text(''.join(json.dumps(r) + '\n' for r in sorted(records, key=lambda x: (x["system"], x["task_id"], x["candidate_id"]))))
    (output / "failure_matrix.json").write_text(json.dumps([{k: r[k] for k in ("task_id", "system", "candidate_id", "compile_status", "runtime_status", "oracle_status", "failure_class", "log_path")} for r in records], indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
