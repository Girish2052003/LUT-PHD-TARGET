#!/usr/bin/env python3
"""Fail-closed independent raw ZIP replay receipt; never runs original/generated MPC."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import zipfile

EXPECTED_ZIPS = {
  'array_test': '12ac90652fdbeed1034a555dbf140a91fe298f8b860bdbcdc385e1977977e119',
  'branch_test': 'f9ea20c2ed58d0853fc0659448a8cf5759cfbdf2b4ccdfffe5669973f5d1a3bd',
  'loop_test': '9c19d30baa11c39a2368c6947406fe7d639920fa21f70a4966ac8c0464ee4cf0',
  'math_test': 'f8e452799031df3fac1d6e6cd818b80783b2479392ab33664a86a15c4a16c253',
  'numpy_operation_test': '019deb164dc0d88058fbfb97cd39948616a15e7c6fa9594ba9d705b1b72b2369',
  'numpy_ufunc_test': '52d7ca0b5a6dafc94f894bcb97138d508cc7a299d5f6090360255fcf97766480',
  'syntax_test': 'abe0ac8871153fdd8970c86435ede7e52e7341eda7f1479ea8dd31bc2304b73d'
}
RECOVERY_SHA256 = "4ba5dc8c0470c1cf02633bb4722a204558b3c3d591a863c10cb5e28c572ba12c"
EXPECTED_TOTALS = (313, 626, 644, 1932, 229, 216, 262, 445, 147, 34)
EXPECTED_DIFFERENCES = {
    ("branch_test/choice_of_the_knight", 1),
    ("math_test/pi_to_the_x", 1),
    ("math_test/spring_rocket", 1),
}


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def read_json_lines(z: zipfile.ZipFile, name: str):
    return [json.loads(line) for line in z.read(name).splitlines()]


def audit(folder: Path) -> dict:
    recovery_path = folder / "stage2-native-recovery-evidence.zip"
    if digest(recovery_path.read_bytes()) != RECOVERY_SHA256:
        raise ValueError("Recovery ZIP checksum mismatch")
    with zipfile.ZipFile(recovery_path) as zip_recovery:
        recovered_rows = read_json_lines(zip_recovery, "outcomes.jsonl")
        recovered = {(r["task_id"], r["candidate_id"]): r for r in recovered_rows}
        if len(recovered) != len(recovered_rows):
            raise ValueError("Duplicate recovered task/candidate identity")
        saved_summary = json.loads(zip_recovery.read("summary.json"))
        native_seven_zip_audit = json.loads(zip_recovery.read("independent-seven-zip-audit.json"))

    actual: dict[tuple[str, int], dict] = {}
    compile_counts, runtime_counts, oracle_counts = Counter(), Counter(), Counter()
    failure_counts, category_counts = Counter(), {}
    raw_file_checks = native_attempts = timed_out_attempts = retries = 0
    disagreements: set[tuple[str, int]] = set()

    for category, known_sha in EXPECTED_ZIPS.items():
        fp = folder / f"original-stage2-{category}.zip"
        if digest(fp.read_bytes()) != known_sha:
            raise ValueError(f"Original raw ZIP checksum mismatch: {category}")
        with zipfile.ZipFile(fp) as z:
            base = category + "/"
            names = set(z.namelist())
            rows = read_json_lines(z, base + "outcomes.jsonl")
            per_task: dict[str, dict[int, dict]] = defaultdict(dict)
            for record in rows:
                task, candidate = record["task_id"], record["candidate_id"]
                key = (task, candidate)
                if key in actual or candidate not in (0, 1):
                    raise ValueError(f"Duplicate/malformed candidate identity: {key}")
                if record["category"] != category or record["stage"] != "stage2" or record["system"] != "spdzcoder":
                    raise ValueError(f"Unexpected original source identity: {key}")
                actual[key] = record
                per_task[task][candidate] = record
                if recovered.get(key) != record:
                    raise ValueError(f"Artifact recovery changed outcome: {key}")
                item = base + record["log_path"] + "/outcome.json"
                if item not in names or json.loads(z.read(item)) != record:
                    raise ValueError(f"Per-task result mismatch: {key}")
                attempts = record["attempts"]
                if not attempts:
                    raise ValueError(f"No native attempts: {key}")
                retries += len(attempts) > 1
                final = attempts[-1]
                if record["combined_source_sha256"] != final["combined_source_sha256"]:
                    raise ValueError(f"Final MPC checksum mismatch: {key}")
                if record["output_digest"] != final["stdout_sha256"]:
                    raise ValueError(f"Final stdout digest mismatch: {key}")
                for i, attempt in enumerate(attempts):
                    native_attempts += 1
                    timed_out_attempts += bool(attempt["timed_out"])
                    prefix = base + record["log_path"] + f"/attempt-{i}"
                    for suffix, field in [
                        (".mpc", "combined_source_sha256"),
                        (".stdout.txt", "stdout_sha256"),
                        (".stderr.txt", "stderr_sha256"),
                    ]:
                        name = prefix + suffix
                        if name not in names or digest(z.read(name)) != attempt[field]:
                            raise ValueError(f"Raw execution blob SHA256 mismatch: {key}, {i}, {suffix}")
                        raw_file_checks += 1
                accepted = record["oracle_status"] == "ACCEPT"
                compile_counts[record["compile_status"]] += 1
                runtime_counts[record["runtime_status"]] += 1
                oracle_counts[record["oracle_status"]] += 1
                failure_counts[str(record["failure_class"])] += 1
                if accepted:
                    if record["compile_status"] != "PASS" or record["runtime_status"] != "PASS":
                        raise ValueError(f"Accepted without execution: {key}")
                    stdout_name = base + record["log_path"] + f"/attempt-{len(attempts)-1}.stdout.txt"
                    if "pass" not in z.read(stdout_name).decode("utf-8", "replace").lower():
                        raise ValueError(f"Native accepted but stdout lacks pass marker: {key}")
                elif record["failure_class"] not in ("compile_failure", "oracle_reject"):
                    raise ValueError(f"Unclassified native rejection: {key}")
                if record["historical_author_flag"] != accepted:
                    if not (record["historical_author_flag"] is False and accepted is True):
                        raise ValueError(f"Unexpected saved-native disagreement: {key}")
                    disagreements.add(key)
            if not all(set(pair) == {0, 1} for pair in per_task.values()):
                raise ValueError(f"Missing candidate in category: {category}")
            accepted = lambda row: row["oracle_status"] == "ACCEPT"
            metrics = {
                "tasks": len(per_task), "candidates": len(rows),
                "first": sum(accepted(pair[0]) for pair in per_task.values()),
                "second": sum(accepted(pair[1]) for pair in per_task.values()),
                "union": sum(any(accepted(v) for v in pair.values()) for pair in per_task.values()),
                "compiler_failures": sum(r["compile_status"] == "FAIL" for r in rows),
            }
            comparison = native_seven_zip_audit["categories"][category]
            if any(metrics[k] != comparison["fresh"][k] for k in ("tasks","first","second","union")):
                raise ValueError(f"Independent and archived category outcomes disagree: {category}")
            if metrics["compiler_failures"] != comparison["compile_failures"]:
                raise ValueError(f"Compiler failures differ: {category}")
            category_counts[category] = metrics

    if actual.keys() != recovered.keys():
        raise ValueError("Original/recovered candidate identity set differs")
    pairs: dict[str, dict[int, dict]] = defaultdict(dict)
    for (task, candidate), record in actual.items():
        pairs[task][candidate] = record
    if not all(set(p) == {0, 1} for p in pairs.values()):
        raise ValueError("Task missing first/second candidate")
    accepted = lambda r: r["oracle_status"] == "ACCEPT"
    first = sum(accepted(p[0]) for p in pairs.values())
    second = sum(accepted(p[1]) for p in pairs.values())
    union = sum(any(accepted(v) for v in p.values()) for p in pairs.values())
    totals = (len(pairs), len(actual), native_attempts, raw_file_checks, first, second,
              union, oracle_counts["ACCEPT"], compile_counts["FAIL"], failure_counts["oracle_reject"])
    if totals != EXPECTED_TOTALS or disagreements != EXPECTED_DIFFERENCES:
        raise ValueError(f"Original raw evidence does not match complete acceptance gate: {totals}")
    if saved_summary["fresh"] != {"tasks": len(pairs), "first": first, "second": second, "union": union}:
        raise ValueError("Recovery summary differs from raw candidate outcomes")
    if retries != 14 or timed_out_attempts != 18:
        raise ValueError("Original retry/timeouts changed")
    return {
        "source_run": 39075744038, "recovery_run": 39080161119,
        "category_metrics": category_counts, "candidate_count": len(actual),
        "task_count": len(pairs), "attempt_count": native_attempts,
        "raw_execution_files_sha256_checked": raw_file_checks,
        "first": first, "second": second, "union": union,
        "compiler_statuses": dict(compile_counts),
        "runtime_statuses": dict(runtime_counts),
        "original_oracle_statuses": dict(oracle_counts),
        "failure_classes": dict(failure_counts), "retries": retries,
        "timed_out_attempts": timed_out_attempts,
        "disagreements": [{"task_id": task, "candidate_id": candidate}
                          for task, candidate in sorted(disagreements)],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True,
                        help="Directory with the seven downloaded original-stage2-*.zip and recovery ZIP")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    results = audit(args.directory)
    serialized = json.dumps(results, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
