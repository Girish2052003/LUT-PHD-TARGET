#!/usr/bin/env python3
"""Instrument the unmodified author evaluator inside the restricted replay container.

No model API is invoked. Candidate bytes and original oracle stay unchanged.
Process-group cleanup on timeout is an explicit containment adaptation.
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
import signal
import subprocess
import sys
import time
from types import SimpleNamespace

EVALUATOR_SHA = "7b999498f06050ab4db54e19097f65cd56c09eb7446384ddca4b62165969f1a2"


def classify_attempt(returncode, timed_out, schedule_present, runtime_started):
    # A schedule is written before compiler finalization. Only the subsequent
    # original runtime launch establishes that compile_file() returned normally.
    compiled = schedule_present and runtime_started
    compile_status = "PASS" if compiled else ("TIMEOUT" if timed_out else "UNKNOWN" if schedule_present else "FAIL")
    runtime_status = "NOT_RUN" if not runtime_started else ("TIMEOUT" if timed_out else ("PASS" if returncode == 0 else "FAIL"))
    failure = ("timeout" if timed_out else "incomplete_compilation_evidence" if compile_status == "UNKNOWN" else "compile_failure" if not compiled else
               "runtime_failure" if runtime_status != "PASS" else None)
    return {"compile_status": compile_status, "runtime_status": runtime_status, "failure_class": failure}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reset_execution_artifacts(work_dir: Path, combined_path: Path | None = None):
    """A later attempt must never inherit compiled schedules or prior party logs."""
    for folder in ("Programs", "logs"):
        shutil.rmtree(work_dir / folder, ignore_errors=True)
    if combined_path is not None:
        combined_path.unlink(missing_ok=True)


def verify_baseline(manifest):
    for item in manifest["baseline_files"]:
        path = Path("/baseline") / item["path"]
        if digest(path) != item["sha256"]:
            raise ValueError("Original baseline source changed: " + item["path"])
    for item in manifest["mp_source_files"]:
        if digest(Path("/mp-spdz") / item["path"]) != item["sha256"]:
            raise ValueError("Pinned MP-SPDZ source changed: " + item["path"])
    if digest(Path("/mp-spdz/mascot-party.x")) != manifest["mascot_binary_sha256"]:
        raise ValueError("Pinned MASCOT binary changed")


class Recorder:
    def __init__(self, folder: Path, task: str):
        self.folder, self.task, self.attempts = folder, task, []
        folder.mkdir(parents=True)

    def run(self, command, *, shell, text, capture_output, timeout):
        # The author function supplies these same subprocess options and timeout.
        if not (shell and text and capture_output):
            raise ValueError("Unexpected original subprocess contract")
        reset_execution_artifacts(Path("/run"))
        index = len(self.attempts)
        combined = Path("/baseline/evaluation/evaluation_storage") / (self.task + ".mpc")
        combined_hash = digest(combined)
        shutil.copyfile(combined, self.folder / f"attempt-{index}.mpc")
        started = time.monotonic()
        process = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        timed_out = False
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = process.communicate()
        (self.folder / f"attempt-{index}.stdout.txt").write_text(stdout)
        (self.folder / f"attempt-{index}.stderr.txt").write_text(stderr)
        for party_log in Path("/run/logs").glob(self.task + "-*"):
            if party_log.is_file():
                shutil.copyfile(party_log, self.folder / f"attempt-{index}-party-{party_log.name}.log")
        schedule_present = Path(f"/run/Programs/Schedules/{self.task}.sch").is_file()
        runtime_started = "mascot-party.x" in stderr and "Running " in stderr
        status = classify_attempt(process.returncode, timed_out, schedule_present, runtime_started)
        self.attempts.append({"command": command, "timeout_seconds": timeout,
                              "returncode": process.returncode, "timed_out": timed_out,
                              "schedule_present": schedule_present, "runtime_launch_marker": runtime_started,
                              "duration_seconds": time.monotonic() - started,
                              "combined_source_sha256": combined_hash,
                              "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
                              "stderr_sha256": hashlib.sha256(stderr.encode()).hexdigest(), **status})
        if timed_out:
            raise subprocess.TimeoutExpired(command, timeout, output=stdout, stderr=stderr)
        return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--results", default="/results")
    p.add_argument("--task", default="array_test/indicate_positive")
    p.add_argument("--split", help="Replay every task in one original split; overrides --task")
    p.add_argument("--system", choices=("spdzcoder", "gpt4_api_docs"), default="spdzcoder")
    p.add_argument("--candidate", choices=("0", "1", "both"), default="0")
    args = p.parse_args()
    if os.environ.get("REPLAY_CONTAINER") != "1" or os.geteuid() == 0:
        raise RuntimeError("Use the restricted non-root Docker launcher; host execution is disabled")
    if set(p.name for p in Path("/sys/class/net").iterdir()) != {"lo"}:
        raise RuntimeError("Replay requires Docker --network none")
    if any(name in os.environ for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GITHUB_TOKEN", "GH_TOKEN", "AZURE_OPENAI_API_KEY")):
        raise RuntimeError("Credentials must not enter the replay container")
    output = Path(args.results)
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Use an empty result directory; refusing stale output reuse")
    identity = json.loads(Path("/harness/identity.json").read_text())
    manifest = json.loads(Path("/harness/source_manifest.json").read_text())
    verify_baseline(manifest)
    path = Path("/baseline/evaluation/evaluate_experimental-mp.py")
    if digest(path) != EVALUATOR_SHA:
        raise ValueError("Original evaluator differs from the reviewed source")
    os.chdir("/run")
    sys.path.insert(0, "/baseline")
    spec = importlib.util.spec_from_file_location("original_evaluator", path)
    evaluator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evaluator)
    # Fresh local certificates are test-only protocol keys, never user credentials.
    setup = subprocess.run(["bash", "/mp-spdz/Scripts/setup-ssl.sh", "2"], capture_output=True, text=True, timeout=60)
    (output / "ssl-setup.log").write_text(setup.stdout + setup.stderr)
    if setup.returncode:
        raise RuntimeError("MASCOT certificate setup failed")
    environment = {"python": sys.version, "platform": platform.platform(), "protocol": "MASCOT",
                   "parties": 2, "mp_spdz_commit": manifest["mp_spdz_commit"],
                   "mp_spdz_version": "0.3.6", "source_archive_sha256": manifest["author_archive_sha256"],
                   "mascot_binary_sha256": manifest["mascot_binary_sha256"],
                   "research_commit": os.environ.get("RESEARCH_COMMIT"),
                   "container_image_id": os.environ.get("REPLAY_IMAGE_ID"),
                   "limits": {"cpus": 2, "memory_bytes": 6442450944, "pids": 256},
                   "network": "loopback only; Docker network none", "api_calls": 0,
                   "randomness": "Original templates and protocol defaults; no undocumented seed substitution",
                   "adaptations": ["Evaluator-only dependencies; author OS/Python unpinned",
                                   "Kill subprocess group on timeout to prevent orphaned parties",
                                   "Fresh Programs and party logs for each attempt; no stale execution artifacts",
                                   "Non-root read-only container; compiler writes only disposable scratch"]}
    (output / "environment.json").write_text(json.dumps(environment, indent=2) + "\n")
    shutil.copyfile("/harness/installed-packages.txt", output / "installed-packages.txt")
    shutil.copyfile("/harness/os-packages.txt", output / "os-packages.txt")
    shutil.copyfile("/harness/source_manifest.json", output / "source_manifest.json")
    selected = [x for x in identity["task_records"] if (x["task_id"].split("/")[0] == args.split if args.split else x["task_id"] == args.task)]
    if not selected:
        raise ValueError("Unknown original task/split")
    candidate_ids = [0, 1] if args.candidate == "both" else [int(args.candidate)]
    results = []
    for item in selected:
        split, task = item["task_id"].split("/")
        source_path = (f"data/stage_3_output/experiment-1-{split}.jsonl" if args.system == "spdzcoder" else
                       f"data/baseline_output/gpt4-1-{split}.jsonl")
        rows = [json.loads(s) for s in (Path("/baseline") / source_path).read_text().splitlines() if s.strip()]
        record = rows[item["position_in_split"]]
        if record["test_name"] != task:
            raise ValueError("Candidate-task pairing changed")
        for candidate in candidate_ids:
            code = record[f"response_{candidate}"]
            code_sha = hashlib.sha256(code.encode()).hexdigest()
            if code_sha != item["candidate_sha256"][args.system][candidate]:
                raise ValueError("Candidate source differs from identity evidence")
            relative = Path("logs") / split / task / args.system / str(candidate)
            recorder = Recorder(output / relative, task)
            combined = Path("/baseline/evaluation/evaluation_storage") / (task + ".mpc")
            reset_execution_artifacts(Path("/run"), combined)
            evaluator.subprocess = SimpleNamespace(run=recorder.run, TimeoutExpired=subprocess.TimeoutExpired)
            started = time.monotonic()
            accepted, error = False, None
            try:
                accepted = evaluator.insert_compile_run(SimpleNamespace(spdz_path="/mp-spdz"), split, task, code) if code else False
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
            attempts = recorder.attempts
            last = attempts[-1] if attempts else {"compile_status": "NOT_RUN", "runtime_status": "NOT_RUN", "failure_class": "empty_candidate" if not code else "harness_error", "stdout_sha256": None}
            outcome = {"task_id": item["task_id"], "category": split, "system": args.system,
                       "candidate_id": candidate, "source_sha256": code_sha,
                       "template_sha256": item["template_sha256"], "compile_status": last["compile_status"],
                       "combined_source_sha256": last.get("combined_source_sha256"),
                       "runtime_status": last["runtime_status"], "oracle_status": "ACCEPT" if accepted else "REJECT",
                       "oracle": "unmodified author insert_compile_run", "output_digest": last["stdout_sha256"],
                       "duration_seconds": time.monotonic() - started,
                       "failure_class": "harness_error" if error else (last["failure_class"] or (None if accepted else "oracle_reject")),
                       "log_path": relative.as_posix(), "exception": error, "attempts": attempts,
                       "historical_author_flag": item["archived_acceptance"][candidate] if args.system == "spdzcoder" else None}
            (output / relative / "outcome.json").write_text(json.dumps(outcome, indent=2) + "\n")
            with (output / "outcomes.jsonl").open("a") as fp:
                fp.write(json.dumps(outcome) + "\n")
            results.append(outcome)
            print(json.dumps({k: outcome[k] for k in ("task_id", "system", "candidate_id", "compile_status", "runtime_status", "oracle_status", "failure_class")}), flush=True)
    verify_baseline(manifest)
    summary = {"fresh_original_evaluator_replay": True, "live_model_calls": 0, "attempted": len(results),
               "expected": len(selected) * len(candidate_ids), "accepted": sum(r["oracle_status"] == "ACCEPT" for r in results),
               "runtime_completed": sum(r["runtime_status"] == "PASS" for r in results),
               "harness_errors": sum(r["exception"] is not None for r in results), "baseline_source_unchanged": True}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    if summary["harness_errors"] or not summary["runtime_completed"]:
        raise SystemExit("Replay did not establish a healthy execution environment; inspect preserved evidence")


if __name__ == "__main__":
    main()
