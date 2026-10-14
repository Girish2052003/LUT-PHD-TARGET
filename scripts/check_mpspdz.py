#!/usr/bin/env python3
"""Compile representative *invoked* MP-SPDZ functions and optionally emulate them.

This runs genuine MP-SPDZ tooling. Emulation is cleartext testing, NOT an MPC
security proof or the paper's SPDZEval benchmark. All inputs are public
constants cast to secret-typed sfix; later runs should use real party inputs.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from spdz_audit.experiment import load_tasks
from spdz_audit.lowering import lower, original_callable

PIN = "78fe3d8bad4e654276eb3a11a88173195e672f44"
CASES = [
    ("absolute", -4.0),
    ("sqrt_abs", -4.0),
    ("sqrt_abs", 4.0),
    ("log_positive", -2.0),
    ("log_positive", 2.0),
    ("reciprocal", 0.0),
    ("reciprocal", 2.0),
    ("nested_signed_log", -2.0),
]
NUMBER = re.compile(r"SPDZ_AUDIT_RESULT:\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)")


def run_process(cmd: list[str], cwd: Path, timeout: int) -> dict:
    try:
        job = subprocess.run(cmd, cwd=cwd, timeout=timeout, text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        return {"returncode": job.returncode, "output": job.stdout[-16000:]}
    except subprocess.TimeoutExpired as error:
        return {"returncode": None, "output": str(error), "timed_out": True}


def check(mpspdz: Path, output: Path, emulate: bool = False, max_cases: int = 4) -> dict:
    mpspdz = mpspdz.resolve()
    if not (mpspdz / "compile.py").is_file() or not (mpspdz / "Programs" / "Source").is_dir():
        raise ValueError("Expected MP-SPDZ checkout with compile.py and Programs/Source")
    current = run_process(["git", "rev-parse", "HEAD"], mpspdz, 10)
    revision = current["output"].strip()
    if revision != PIN:
        raise ValueError("MP-SPDZ must be pinned to " + PIN + "; received " + revision)
    emulator = mpspdz / "emulate.x"
    if emulate and not emulator.is_file():
        raise ValueError("--emulate requires a built MP-SPDZ emulate.x")
    tasks = {entry["id"]: entry for entry in load_tasks(ROOT / "experiments" / "benchmark.json")}
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for index, (task_id, x) in enumerate(CASES[:max_cases]):
        task = tasks[task_id]
        expected = float(original_callable(task["source"])(x))
        for mode in ("baseline", "safe"):
            name = f"spdz_audit_{index:02d}_{mode}"
            path = mpspdz / "Programs" / "Source" / (name + ".mpc")
            if path.exists():
                raise FileExistsError("Refusing to overwrite " + str(path))
            code = (lower(task["source"], mode=mode, backend="mpspdz")
                    + "\nfrom Compiler.library import print_ln\n"
                    + f"_spdz_audit_x = sfix({x!r})\n"
                    + f"_spdz_audit_y = f(_spdz_audit_x)\n"
                    + "print_ln('SPDZ_AUDIT_RESULT: %s', _spdz_audit_y.reveal())\n")
            record = {"task": task_id, "mode": mode, "x": x, "expected": expected,
                      "secret_typed_constant": True, "actual_party_input": False,
                      "compiler": "pending", "emulation": "not_requested"}
            (output / (name + ".mpc")).write_text(code)
            try:
                path.write_text(code)
                compile_log = run_process(
                    [sys.executable, "compile.py", "-R", "64", name], mpspdz, 240)
                (output / (name + ".compile.log")).write_text(compile_log["output"])
                record["compiler"] = ("success" if compile_log["returncode"] == 0
                                      else "timeout" if compile_log.get("timed_out") else "failure")
                if emulate and record["compiler"] == "success":
                    runtime = run_process([str(emulator), name], mpspdz, 180)
                    (output / (name + ".emulate.log")).write_text(runtime["output"])
                    match = NUMBER.search(runtime["output"])
                    if runtime["returncode"] != 0:
                        record["emulation"] = "runtime_failure"
                    elif match is None:
                        record["emulation"] = "unparsed_output"
                    else:
                        observed = float(match.group(1))
                        record["observed"] = observed
                        record["emulation"] = ("pass" if math.isclose(
                            observed, expected, abs_tol=0.05, rel_tol=0.05) else "mismatch")
                elif emulate:
                    record["emulation"] = "compile_failed"
            finally:
                path.unlink(missing_ok=True)
            records.append(record)
    result = {
        "engine": "genuine_MP_SPDZ_compiler_and_optional_cleartext_emulator",
        "mpspdz_commit": revision,
        "ring_bits": 64,
        "absolute_and_relative_tolerance": 0.05,
        "not_original_spdzeval": True,
        "not_security_proof": True,
        "results": records
    }
    (output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mpspdz", type=Path, required=True)
    p.add_argument("--output", type=Path, default=ROOT / "results" / "mpspdz")
    p.add_argument("--emulate", action="store_true")
    p.add_argument("--max-cases", type=int, default=4)
    args = p.parse_args()
    if not 1 <= args.max_cases <= len(CASES):
        p.error("--max-cases must be between 1 and " + str(len(CASES)))
    result = check(args.mpspdz, args.output, emulate=args.emulate, max_cases=args.max_cases)
    print(json.dumps(result, indent=2))
    if any(r["compiler"] != "success" for r in result["results"] if r["mode"] == "safe"):
        raise SystemExit("At least one modified program failed MP-SPDZ compilation")
    if args.emulate and any(r["emulation"] != "pass" for r in result["results"] if r["mode"] == "safe"):
        raise SystemExit("At least one modified program failed MP-SPDZ cleartext emulation")


if __name__ == "__main__":
    main()
