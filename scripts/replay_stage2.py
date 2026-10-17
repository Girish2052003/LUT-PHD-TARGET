#!/usr/bin/env python3
"""Run real SAVED STAGE-2 MPC candidates in the unchanged original MASCOT evaluator.

This harness runs only in the established network-none, non-root, read-only
container. It uses the same original insert_compile_run and Recorder as the
already independently accepted stage-3 replay. No language model runs here.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace

from replay_original import EVALUATOR_SHA, Recorder, digest, reset_execution_artifacts, verify_baseline


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def stage2_candidates(baseline, ledger, split, task=None):
    """Verify every candidate in the requested split, including later unselected rows."""
    category = ledger["categories"][split]
    source_path = category["candidate_source_path"]
    raw = (baseline / source_path).read_bytes()
    if sha(raw) != category["candidate_source_sha256"]:
        raise ValueError("Stage-2 author source file digest changed")
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    references = [r for r in ledger["task_records"] if r["category"] == split]
    if len(rows) != category["tasks"] or len(rows) != len(references):
        raise ValueError("Missing or extra original source rows")
    for row, expected in zip(rows, references):
        if (row.get("test_name") != expected["task_id"].split("/")[1]
                or expected["position_in_split"] >= len(rows)):
            raise ValueError("Stage-2 source row order and identity mismatch")
        for c in (0, 1):
            source = row.get(f"response_{c}")
            if not isinstance(source, str) or sha(source.encode("utf-8")) != expected["candidate_sha256"][c]:
                raise ValueError("Stage-2 candidate hash/order mismatch")
    return [(row, reference) for row, reference in zip(rows, references)
            if task is None or reference["task_id"] == f"{split}/{task}"]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--task", help="Exact original category/task for smoke")
    p.add_argument("--split", help="Entire original category for full, both candidates")
    p.add_argument("--candidate", choices=["0", "1", "both"], default="both")
    args = p.parse_args()
    if bool(args.task) == bool(args.split):
        raise ValueError("Specify exactly one of --task or --split")
    if (os.environ.get("REPLAY_CONTAINER") != "1" or os.geteuid() == 0
            or {p.name for p in Path("/sys/class/net").iterdir()} != {"lo"}):
        raise RuntimeError("Original stage-2 evaluator runs only in reviewed restricted container")
    if any(k in os.environ for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GITHUB_TOKEN",
                                      "GH_TOKEN", "AZURE_OPENAI_API_KEY")):
        raise RuntimeError("Do not supply credentials to candidate replay")
    output, baseline = Path("/results"), Path("/baseline")
    if any(output.iterdir()):
        raise ValueError("Fresh output directory required")
    identity = json.loads(Path("/harness/identity.json").read_text())
    ledger = json.loads(Path("/harness/stage2_identity.json").read_text())
    manifest = json.loads(Path("/harness/source_manifest.json").read_text())
    if (ledger["author_archive_sha256"] != manifest["author_archive_sha256"]
            or len(ledger["task_records"]) != 313 or len(identity["task_records"]) != 313
            or [r["task_id"] for r in ledger["task_records"]] !=
               [r["task_id"] for r in identity["task_records"]]):
        raise ValueError("Stage-2 source, identity and pinned original archive do not agree")
    verify_baseline(manifest)
    original_evaluator = baseline / "evaluation/evaluate_experimental-mp.py"
    if digest(original_evaluator) != EVALUATOR_SHA:
        raise ValueError("Original authors' evaluator source changed")
    os.chdir("/run")
    sys.path.insert(0, str(baseline))
    spec = importlib.util.spec_from_file_location("unchanged_original_stage2_evaluator", original_evaluator)
    evaluator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evaluator)
    setup = subprocess.run(["bash", "/mp-spdz/Scripts/setup-ssl.sh", "2"],
                           capture_output=True, text=True, timeout=60)
    (output / "ssl-setup.log").write_text(setup.stdout + setup.stderr)
    if setup.returncode:
        raise RuntimeError("Original two-party MASCOT setup failed")
    for f in ("source_manifest.json", "stage2_identity.json", "installed-packages.txt", "os-packages.txt"):
        shutil.copyfile("/harness/" + f, output / f)
    category, target = (args.task.split("/", 1) if args.task else (args.split, None))
    if category not in ledger["categories"] or (args.task and not target):
        raise ValueError("Unknown category or task")
    selected = stage2_candidates(baseline, ledger, category, target)
    if len(selected) != (1 if args.task else ledger["categories"][category]["tasks"]):
        raise ValueError("Expected original task selection is incomplete")
    environment = {
        "python": sys.version, "platform": platform.platform(),
        "research_commit": os.environ.get("RESEARCH_COMMIT"),
        "container_image_id": os.environ.get("REPLAY_IMAGE_ID"),
        "protocol": "MASCOT", "parties": 2, "network": "Docker --network none; loopback only",
        "mp_spdz_commit": manifest["mp_spdz_commit"], "mascot_binary_sha256": manifest["mascot_binary_sha256"],
        "source_archive_sha256": manifest["author_archive_sha256"],
        "source_kind": "authentic_saved_stage2_prior_to_saved_stage3",
        "model_stage_executed": False, "api_calls": 0,
        "original_evaluator_sha256": EVALUATOR_SHA,
        "limits": {"cpus": 2, "memory_bytes": 6442450944, "pids": 256},
        "note": "Fresh original native MASCOT evaluation of SAVED stage-2 code; no historical LLM generation",
    }
    (output / "environment.json").write_text(json.dumps(environment, indent=2) + "\n")
    candidates = (0, 1) if args.candidate == "both" else (int(args.candidate),)
    outcomes = []
    for stage_record, reference in selected:
        task = stage_record["test_name"]
        for candidate in candidates:
            code = stage_record[f"response_{candidate}"]
            code_hash = sha(code.encode("utf-8"))
            if code_hash != reference["candidate_sha256"][candidate]:
                raise ValueError("Stage-2 code changed before original evaluator")
            relative = Path("logs") / category / task / "spdzcoder" / str(candidate)
            recorder = Recorder(output / relative, task)
            combined = baseline / "evaluation/evaluation_storage" / (task + ".mpc")
            reset_execution_artifacts(Path("/run"), combined)
            evaluator.subprocess = SimpleNamespace(run=recorder.run,
                                                     TimeoutExpired=subprocess.TimeoutExpired)
            start = time.monotonic()
            accepted, error = False, None
            try:
                accepted = evaluator.insert_compile_run(
                    SimpleNamespace(spdz_path="/mp-spdz"), category, task, code) if code else False
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
            attempts = recorder.attempts
            last = attempts[-1] if attempts else {
                "compile_status": "NOT_RUN", "runtime_status": "NOT_RUN",
                "failure_class": "empty_candidate" if not code else "harness_error",
                "stdout_sha256": None,
            }
            result = {
                "task_id": reference["task_id"], "category": category, "system": "spdzcoder",
                "stage": "stage2", "candidate_id": candidate,
                "source_file": reference["source_file"],
                "source_file_sha256": reference["source_file_sha256"],
                "source_sha256": code_hash, "template_sha256": reference["template_sha256"],
                "compile_status": last["compile_status"],
                "combined_source_sha256": last.get("combined_source_sha256"),
                "runtime_status": last["runtime_status"], "oracle_status": "ACCEPT" if accepted else "REJECT",
                "oracle": "unmodified author insert_compile_run",
                "output_digest": last["stdout_sha256"],
                "duration_seconds": time.monotonic() - start,
                "failure_class": "harness_error" if error else (
                    last["failure_class"] or (None if accepted else "oracle_reject")),
                "log_path": relative.as_posix(), "exception": error,
                "attempts": attempts,
                "historical_author_flag": reference["historical_stage2_evaluator_flags"][candidate],
            }
            (output / relative / "outcome.json").write_text(json.dumps(result, indent=2) + "\n")
            with (output / "outcomes.jsonl").open("a") as stream:
                stream.write(json.dumps(result) + "\n")
            outcomes.append(result)
            print(json.dumps({k: result[k] for k in
                ("task_id", "candidate_id", "compile_status", "runtime_status",
                 "oracle_status", "failure_class")}), flush=True)
    verify_baseline(manifest)
    summary = {
        "fresh_original_evaluator_replay": True, "source_kind": "saved_stage2",
        "model_stage_executed": False, "live_model_calls": 0, "attempted": len(outcomes),
        "expected": len(selected) * len(candidates),
        "accepted": sum(r["oracle_status"] == "ACCEPT" for r in outcomes),
        "runtime_completed": sum(r["runtime_status"] == "PASS" for r in outcomes),
        "harness_errors": sum(r["exception"] is not None for r in outcomes),
        "baseline_source_unchanged": True,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    if summary["harness_errors"]:
        raise SystemExit("Stage-2 evaluator harness exception; preserve and inspect logs")


if __name__ == "__main__":
    main()
