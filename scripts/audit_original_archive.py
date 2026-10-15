#!/usr/bin/env python3
"""Audit official SPDZCoder evaluation records directly inside the original TAR.

Read-only; never imports or executes author code and never needs an API key.
Produces provenance, split counts, native-record schema and evaluation excerpts.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import tarfile

PREFIX = "SPDZCoder/"
EXPECTED_MD5 = "3c6d7707d7aecc051d35312f81405c66"
SPLITS = ("array_test", "loop_test", "branch_test", "math_test",
          "numpy_operation_test", "numpy_ufunc_test", "syntax_test")
PAPER_SPLITS = {"array_test": 43, "loop_test": 97, "branch_test": 34,
                "math_test": 38, "numpy_operation_test": 32,
                "numpy_ufunc_test": 34, "syntax_test": 35}
MAX_READ = 8_000_000


def read_member(archive: tarfile.TarFile, relative: str) -> bytes:
    member = archive.getmember(PREFIX + relative)
    if not member.isfile() or member.size > MAX_READ:
        raise ValueError("Not an allowed sized regular file: " + relative)
    fp = archive.extractfile(member)
    if fp is None:
        raise ValueError("Could not read file: " + relative)
    data = fp.read(MAX_READ + 1)
    if len(data) != member.size:
        raise ValueError("Wrong file length: " + relative)
    return data


def summary_shape(obj: object) -> dict:
    if isinstance(obj, list):
        return {"type": "list", "length": len(obj),
                "first": summary_shape(obj[0]) if obj else None}
    if isinstance(obj, dict):
        return {"type": "dict", "keys": list(obj)[:35],
                "members": {str(k): summary_shape(v) for k, v in list(obj.items())[:12]}}
    if isinstance(obj, str):
        return {"type": "str", "length": len(obj)}
    return {"type": type(obj).__name__}


def inspection_errors(report: dict) -> list[str]:
    errors = []
    if report.get("raw_mpc_task_count") != 313 or report.get("raw_mpc_categories") != PAPER_SPLITS:
        errors.append("Native benchmark counts differ from the published 313-task splits")
    for section in ("split", "stage3", "baseline"):
        for split, expected in PAPER_SPLITS.items():
            info = report.get(section, {}).get(split, {})
            count = info.get("length" if section == "split" else "records")
            if "error" in info or count != expected:
                errors.append(f"Incomplete {section}/{split}: {info.get('error', count)}")
    for path, info in report.get("script_previews", {}).items():
        if "error" in info:
            errors.append(f"Unreadable source preview {path}: {info['error']}")
    return errors


def inspect(archive_path: Path) -> dict:
    md5 = hashlib.md5(archive_path.read_bytes()).hexdigest()
    if md5 != EXPECTED_MD5:
        raise ValueError("Zenodo published MD5 checksum mismatch")
    report = {"source": "https://zenodo.org/records/18152253",
              "archive_md5": md5, "split": {}, "stage3": {},
              "baseline": {}, "evaluation": {}, "script_previews": {}}
    with tarfile.open(archive_path, "r:*") as tar:
        names = {m.name[len(PREFIX):] for m in tar
                 if m.isfile() and m.name.startswith(PREFIX)}
        input_tasks = [n for n in names if n.startswith("data/input_data/") and n.endswith(".mpc")]
        print("OFFICIAL RAW MPC TASK FILES:", len(input_tasks))
        report["raw_mpc_task_count"] = len(input_tasks)
        report["raw_mpc_categories"] = dict(Counter(n.split("/")[2] for n in input_tasks))
        for split in SPLITS:
            path = "data/input_processed_data/" + split + ".json"
            try:
                content = read_member(tar, path).decode("utf-8")
                entries = [json.loads(line) for line in content.splitlines() if line.strip()]
                info = summary_shape(entries)
                report["split"][split] = info
                print("OFFICIAL SPLIT:", split, json.dumps(info)[:1700])
            except (KeyError, ValueError) as e:
                report["split"][split] = {"error": str(e)}
                print("OFFICIAL SPLIT ERROR:", split, str(e))

            stage3 = "data/stage_3_output/experiment-1-" + split + ".jsonl"
            baseline = "data/baseline_output/gpt4-1-" + split + ".jsonl"
            for key, p in (("stage3", stage3), ("baseline", baseline)):
                try:
                    raw = read_member(tar, p).decode("utf-8", errors="replace")
                    objects = [json.loads(line) for line in raw.splitlines() if line.strip()]
                    info = {"records": len(objects),
                            "first_row_shape": summary_shape(objects[0]) if objects else None}
                    report[key][split] = info
                    print("OFFICIAL OUTPUT:", key, split, json.dumps(info)[:1900])
                except (KeyError, ValueError) as e:
                    report[key][split] = {"error": str(e)}
                    print("OFFICIAL OUTPUT ERROR:", key, split, str(e))

        for path in sorted(n for n in names
                           if n.startswith("evaluation/experiment-1-stage_3_output")
                           and n.endswith(".txt")):
            raw = read_member(tar, path).decode("utf-8", errors="replace")
            lines = raw.splitlines()
            report["evaluation"][path] = {
                "n_lines": len(lines),
                "preview": lines[:16],
                "metric_like": [line for line in lines if re.search(
                    r"pass@|accuracy|correct|success|total|error", line, re.I)][:35]
            }
            print("OFFICIAL EVALUATION:", path,
                  json.dumps(report["evaluation"][path])[:1900])

        for path in ("evaluation/evaluate_experimental-mp.py",
                     "src/pipeline-mp.py", "src/apply_feedback_tc.py",
                     "requirement.txt", "data/process_input_data.py"):
            try:
                lines = read_member(tar, path).decode("utf-8", errors="replace").splitlines()
                report["script_previews"][path] = {
                    "line_count": len(lines), "head": lines[:90]}
                print("OFFICIAL SOURCE PREVIEW:", path, json.dumps(lines[:85])[:3500])
            except (KeyError, ValueError) as e:
                report["script_previews"][path] = {"error": str(e)}
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--tar", default="results/official_artifacts/SPDZCoder.tar")
    p.add_argument("--output", default="results/official_artifacts/native_data_audit.json")
    opts = p.parse_args()
    result = inspect(Path(opts.tar))
    result["inspection_errors"] = inspection_errors(result)
    output = Path(opts.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print("NATIVE AUDIT REPORT:", output)
    if result["inspection_errors"]:
        raise SystemExit("Native inspection incomplete: " + "; ".join(result["inspection_errors"]))


if __name__ == "__main__":
    main()
