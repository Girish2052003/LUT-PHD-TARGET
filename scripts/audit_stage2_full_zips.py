#!/usr/bin/env python3
"""Passively audit SEVEN genuine original stage-2 MASCOT category evidence ZIPs.

No code from the archive is imported/executed; all data are read directly from
GitHub Actions artifact ZIPs. Historical model stages were NOT replayed.
The unmodified author's intentionally weak stdout oracle remains the metric.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import zipfile

COUNTS = {
    "array_test": 43, "loop_test": 97, "branch_test": 34, "math_test": 38,
    "numpy_operation_test": 32, "numpy_ufunc_test": 34, "syntax_test": 35,
}
ARCHIVE = "a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac"
EVALUATOR = "7b999498f06050ab4db54e19097f65cd56c09eb7446384ddca4b62165969f1a2"
MP_COMMIT = "6cc3fccef0904764364eb8e285519cd34028f325"
MASCOT_BINARY = "2a592fec9a9f9d0e7e8148bdf9ee7a67811dd6781c333981b386f3d1b7c8a5b3"
RUN_COMMIT = "1e3c95d5357cd8b913a11916e562b6de7d633ccb"
EMPTY_SHA = hashlib.sha256(b"").hexdigest()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def original_oracle(stdout, stderr, timed_out):
    # The released evaluator checks lowercase "pass" anywhere in stdout.
    return not timed_out and "pass" in stdout.lower() and "Traceback" not in stderr.strip()


def check_attempt(row, evidence, folder, attempt, index):
    name = row["task_id"].split("/", 1)[1]
    command = ("/mp-spdz/Scripts/compile-run.py -E mascot "
               + "/baseline/evaluation/evaluation_storage/" + name + ".mpc")
    if attempt["command"] != command:
        raise ValueError("Original MASCOT command/task changed")
    expected_timeout = (150 if any(x in row["category"] for x in ("math", "ufunc"))
                        else 60) + 30 * index
    if attempt["timeout_seconds"] != expected_timeout:
        raise ValueError("Original retry timeout changed")
    inputs = []
    for extension, field in (("mpc", "combined_source_sha256"),
                             ("stdout.txt", "stdout_sha256"),
                             ("stderr.txt", "stderr_sha256")):
        raw = evidence.read(folder + f"attempt-{index}." + extension)
        if sha(raw) != attempt[field]:
            raise ValueError("Raw MPC input/output digest differs: " + row["task_id"])
        inputs.append(raw)
    mpc, out, err = inputs
    stderr, stdout = err.decode("utf-8", "replace"), out.decode("utf-8", "replace")
    if attempt["runtime_launch_marker"] != ("mascot-party.x" in stderr and "Running " in stderr):
        raise ValueError("MASCOT runtime launch marker differs")
    compiled = attempt["schedule_present"] and attempt["runtime_launch_marker"]
    compile_status = ("PASS" if compiled else
                      "TIMEOUT" if attempt["timed_out"] else
                      "UNKNOWN" if attempt["schedule_present"] else "FAIL")
    runtime_status = ("NOT_RUN" if not attempt["runtime_launch_marker"] else
                      "TIMEOUT" if attempt["timed_out"] else
                      "PASS" if attempt["returncode"] == 0 else "FAIL")
    if (attempt["compile_status"], attempt["runtime_status"]) != (compile_status, runtime_status):
        raise ValueError("Original compiler/native execution classification differs")
    return original_oracle(stdout, stderr, attempt["timed_out"])


def category_records(z, category):
    prefix = category + "/"
    def load(name):
        return json.loads(z.read(prefix + name))
    manifest = load("source_manifest.json")
    ledger = load("stage2_identity.json")
    env = load("environment.json")
    files = {r["path"]: r["sha256"] for r in manifest["baseline_files"]}
    source_path = f"data/stage_2_SPDZ_output/experiment-1-{category}.jsonl"
    flags_path = f"evaluation/experiment-1-stage_2_SPDZ_output_{category}.txt"
    if (manifest["author_archive_sha256"] != ARCHIVE
            or env["source_archive_sha256"] != ARCHIVE
            or env["research_commit"] != RUN_COMMIT
            or env["source_kind"] != "authentic_saved_stage2_prior_to_saved_stage3"
            or env["original_evaluator_sha256"] != EVALUATOR
            or env["protocol"] != "MASCOT" or env["parties"] != 2 or env["api_calls"] != 0
            or env["mp_spdz_commit"] != MP_COMMIT
            or env["mascot_binary_sha256"] != MASCOT_BINARY
            or files.get("evaluation/evaluate_experimental-mp.py") != EVALUATOR):
        raise ValueError("Original source, evaluator, or MASCOT execution pin differs")
    if (ledger["author_archive_sha256"] != ARCHIVE
            or len(ledger["task_records"]) != 313
            or len({r["task_id"] for r in ledger["task_records"]}) != 313):
        raise ValueError("Pinned original stage-2 identity ledger incomplete")
    expected_source = ledger["categories"][category]
    if (expected_source["candidate_source_sha256"] != files.get(source_path)
            or expected_source["historical_evaluation_sha256"] != files.get(flags_path)
            or expected_source["tasks"] != COUNTS[category]):
        raise ValueError("Original stage-2 code or saved evaluation file changed")
    img = env["container_image_id"]
    if not isinstance(img, str) or not re.fullmatch(r"sha256:[a-f0-9]{64}", img):
        raise ValueError("Invalid per-runner Docker image fingerprint")
    source_pins = (
        sha(z.read(prefix + "source_manifest.json")),
        sha(z.read(prefix + "stage2_identity.json")),
        sha(z.read(prefix + "installed-packages.txt")),
        sha(z.read(prefix + "os-packages.txt")),
    )
    references = {r["task_id"]: r for r in ledger["task_records"]}
    raw_rows = z.read(prefix + "outcomes.jsonl").splitlines()
    if len(raw_rows) != 2 * COUNTS[category]:
        raise ValueError("Incomplete native candidate outcome table")
    summary = load("summary.json")
    if (summary["attempted"] != len(raw_rows) or summary["expected"] != len(raw_rows)
            or summary["harness_errors"] or not summary["baseline_source_unchanged"]
            or summary["live_model_calls"] != 0 or summary["model_stage_executed"]):
        raise ValueError("Native run summary incomplete or wrong source")
    rows, seen = [], set()
    for line in raw_rows:
        row = json.loads(line)
        task, candidate = row["task_id"], row["candidate_id"]
        key = (task, candidate)
        if (key in seen or not task.startswith(prefix) or type(candidate) is not int
                or candidate not in (0, 1) or row["category"] != category
                or row["system"] != "spdzcoder" or row["stage"] != "stage2"
                or row["oracle"] != "unmodified author insert_compile_run"
                or row["exception"] is not None):
            raise ValueError("Duplicate or non-original native stage-2 record")
        seen.add(key)
        ref = references.get(task)
        if (ref is None or row["source_sha256"] != ref["candidate_sha256"][candidate]
                or row["template_sha256"] != ref["template_sha256"]
                or row["source_file_sha256"] != expected_source["candidate_source_sha256"]
                or row["source_file"] != source_path
                or row["historical_author_flag"] is not
                    ref["historical_stage2_evaluator_flags"][candidate]):
            raise ValueError("Stage-2 candidate, original template or saved flag differs")
        folder = prefix + row["log_path"] + "/"
        if row["log_path"] != f"logs/{category}/{task.split('/', 1)[1]}/spdzcoder/{candidate}":
            raise ValueError("Candidate log path does not match original task identity")
        if json.loads(z.read(folder + "outcome.json")) != row:
            raise ValueError("Saved per-candidate record differs from run table")
        attempts = row["attempts"]
        if len(attempts) > 3 or (not attempts and row["source_sha256"] != EMPTY_SHA):
            raise ValueError("Original retry budget or recorded nonempty-source execution differs")
        result = False
        for i, attempt in enumerate(attempts):
            result = check_attempt(row, z, folder, attempt, i)
            if i < len(attempts) - 1 and not attempt["timed_out"]:
                raise ValueError("Original evaluator retry occurred without timeout")
        if attempts and row["combined_source_sha256"] != attempts[-1]["combined_source_sha256"]:
            raise ValueError("Final combined native source hash differs")
        if result != (row["oracle_status"] == "ACCEPT"):
            raise ValueError("Native saved decision and actual stdout differ")
        rows.append(row)
    if (len(seen) != 2 * COUNTS[category]
            or summary["accepted"] != sum(r["oracle_status"] == "ACCEPT" for r in rows)
            or summary["runtime_completed"] != sum(r["runtime_status"] == "PASS" for r in rows)):
        raise ValueError("Category denominator or measured native summary differs")
    return rows, source_pins, img


def measure(task_ids, rows, historical=False):
    accepted = {(r["task_id"], r["candidate_id"]):
                bool(r["historical_author_flag"]) if historical else r["oracle_status"] == "ACCEPT"
                for r in rows}
    return {"tasks": len(task_ids), "first": sum(accepted[t, 0] for t in task_ids),
            "second": sum(accepted[t, 1] for t in task_ids),
            "union": sum(accepted[t, 0] or accepted[t, 1] for t in task_ids)}


def audit(paths):
    if len(paths) != 7:
        raise ValueError("Exactly seven original native category ZIPs required")
    seen_categories, all_rows, pinsets, image_ids, category_metrics = set(), [], set(), {}, {}
    for path in paths:
        with zipfile.ZipFile(path) as z:
            if z.testzip() is not None:
                raise ValueError("Corrupt raw category ZIP")
            categories = {n.split("/", 1)[0] for n in z.namelist()}
            if len(categories) != 1:
                raise ValueError("Unexpected multiple category prefixes")
            category = next(iter(categories))
            if category not in COUNTS or category in seen_categories:
                raise ValueError("Unknown or repeated original category")
            seen_categories.add(category)
            rows, pins, img = category_records(z, category)
            pinsets.add(pins)
            image_ids[category] = img
            ids = {r["task_id"] for r in rows}
            if len(ids) != COUNTS[category]:
                raise ValueError("Original native test category denominator differs")
            category_metrics[category] = {
                "fresh": measure(ids, rows), "historical": measure(ids, rows, True),
                "compile_failures": sum(r["compile_status"] != "PASS" for r in rows),
                "archived_disagreements": sum((r["oracle_status"] == "ACCEPT") !=
                                             r["historical_author_flag"] for r in rows),
            }
            all_rows.extend(rows)
    if seen_categories != set(COUNTS) or len(pinsets) != 1 or len(all_rows) != 626:
        raise ValueError("Original 313 tasks / seven categories / shared source pins incomplete")
    ids = {r["task_id"] for r in all_rows}
    if len(ids) != 313:
        raise ValueError("Original task identity coverage incomplete")
    return {
        "scope": "Independent read-only ZIP audit of seven fresh original-MASCOT stage-2 candidate runs",
        "source_run_id": 39075744038, "source_research_commit": RUN_COMMIT,
        "source_archive_sha256": ARCHIVE, "candidate_count": 626, "task_count": 313,
        "categories": category_metrics, "fresh": measure(ids, all_rows),
        "historical": measure(ids, all_rows, True),
        "saved_to_fresh_disagreements": [
            {"task_id": r["task_id"], "candidate_id": r["candidate_id"],
             "saved": r["historical_author_flag"], "fresh": r["oracle_status"] == "ACCEPT"}
            for r in all_rows
            if (r["oracle_status"] == "ACCEPT") != r["historical_author_flag"]],
        "native_compile_statuses": dict(Counter(r["compile_status"] for r in all_rows)),
        "native_runtime_statuses": dict(Counter(r["runtime_status"] for r in all_rows)),
        "independently_built_category_image_ids": image_ids,
        "common_source_ledger_and_dependency_digests": list(next(iter(pinsets))),
        "live_model_calls": 0, "original_evaluator_unchanged": True,
        "limitations": "Authentic saved candidate replay only. Original weak stdout oracle retained; "
                       "not proof of semantic equivalence, security, or model regeneration.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("category_zips", type=Path, nargs=7)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = json.dumps(audit(args.category_zips), indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result)
    print(result)


if __name__ == "__main__":
    main()
