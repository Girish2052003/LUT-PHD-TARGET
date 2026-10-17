#!/usr/bin/env python3
"""Independently audit real original stage-2 MASCOT smoke ZIPs as passive data.

Inputs are GitHub Actions artifact ZIPs, not source code to import or execute.
This verifier deliberately uses a separate parsing path from the experiment's
harness-side scripts. The authors' original stdout acceptance semantics are
preserved; they are not proof of true functional correctness.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import zipfile

CATEGORIES = (
    "array_test", "loop_test", "branch_test", "math_test",
    "numpy_operation_test", "numpy_ufunc_test", "syntax_test",
)
SOURCE_SHA = "a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac"
EVALUATOR_SHA = "7b999498f06050ab4db54e19097f65cd56c09eb7446384ddca4b62165969f1a2"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def original_oracle(attempt):
    if attempt["timed_out"]:
        return False
    return "pass" in attempt["stdout"].lower() and "Traceback" not in attempt["stderr"].strip()


def audit(smoke_zip, saved_traces_zip):
    smoke_path = Path(smoke_zip)
    with zipfile.ZipFile(smoke_path) as evidence, zipfile.ZipFile(saved_traces_zip) as prior:
        if evidence.testzip() is not None or prior.testzip() is not None:
            raise ValueError("ZIP file CRC mismatch")
        names = set(evidence.namelist())
        pins = defaultdict(set)
        rows = []
        for category in CATEGORIES:
            trace = json.loads(prior.read(category + ".json"))
            task_id = trace["task_id"]
            if task_id.split("/")[0] != category:
                raise ValueError("Archived category and selected task disagree")
            folder = f"stage2-smoke/{task_id}/"
            ledger_raw = evidence.read(folder + "stage2_identity.json")
            source_raw = evidence.read(folder + "source_manifest.json")
            ledger = json.loads(ledger_raw)
            manifest = json.loads(source_raw)
            env = json.loads(evidence.read(folder + "environment.json"))
            if (env["source_kind"] != "authentic_saved_stage2_prior_to_saved_stage3"
                    or env["original_evaluator_sha256"] != EVALUATOR_SHA
                    or env["protocol"] != "MASCOT" or env["parties"] != 2 or env["api_calls"] != 0
                    or env["source_archive_sha256"] != SOURCE_SHA
                    or manifest["author_archive_sha256"] != SOURCE_SHA):
                raise ValueError("Original evaluator, archive or security conditions changed")
            pins["stage2_ledger"].add(sha(ledger_raw))
            pins["source_manifest"].add(sha(source_raw))
            pins["image"].add(env["container_image_id"])
            pins["installed_packages"].add(sha(evidence.read(folder + "installed-packages.txt")))
            pins["os_packages"].add(sha(evidence.read(folder + "os-packages.txt")))
            if len(ledger["task_records"]) != 313:
                raise ValueError("Original stage-2 candidate ledger incomplete")
            authentic = next((r for r in ledger["task_records"] if r["task_id"] == task_id), None)
            if authentic is None:
                raise ValueError("Original stage-2 task absent")
            template = trace["native_template"]["content"]
            if sha(template.encode()) != authentic["template_sha256"]:
                raise ValueError("Native author template differs")
            candidate_texts = trace["stages"]["stage_2_generate_reflect"]["fields"]
            output_rows = [json.loads(line) for line in evidence.read(folder + "outcomes.jsonl").splitlines() if line.strip()]
            summary = json.loads(evidence.read(folder + "summary.json"))
            if (len(output_rows) != 2 or summary["attempted"] != 2 or summary["expected"] != 2
                    or summary["harness_errors"] != 0 or summary["live_model_calls"] != 0):
                raise ValueError("Original two-candidate MASCOT result incomplete")
            for c, row in enumerate(output_rows):
                if (row["task_id"] != task_id or type(row["candidate_id"]) is not int
                        or row["candidate_id"] != c or row.get("stage") != "stage2"
                        or row["oracle"] != "unmodified author insert_compile_run"
                        or row["exception"] is not None):
                    raise ValueError("Candidate identity or original evaluator mismatch")
                code = candidate_texts.get(f"response_{c}")
                if (not isinstance(code, str)
                        or sha(code.encode()) != row["source_sha256"]
                        or row["source_sha256"] != authentic["candidate_sha256"][c]
                        or row["template_sha256"] != authentic["template_sha256"]
                        or row["historical_author_flag"] is not authentic["historical_stage2_evaluator_flags"][c]):
                    raise ValueError("Saved original stage-2 candidate text/flag differs")
                log = folder + row["log_path"] + "/"
                if row != json.loads(evidence.read(log + "outcome.json")):
                    raise ValueError("Per-candidate record differs from run table")
                attempts = row["attempts"]
                if not attempts or len(attempts) > 3:
                    raise ValueError("Missing or excessive original evaluator attempts")
                accepted = False
                for i, attempt in enumerate(attempts):
                    raw_mpc = evidence.read(log + f"attempt-{i}.mpc")
                    stdout = evidence.read(log + f"attempt-{i}.stdout.txt")
                    stderr = evidence.read(log + f"attempt-{i}.stderr.txt")
                    if any(sha(raw) != attempt[key] for raw, key in (
                            (raw_mpc, "combined_source_sha256"),
                            (stdout, "stdout_sha256"), (stderr, "stderr_sha256"))):
                        raise ValueError("Executed native MPC program or logs differ from metadata")
                    if code.encode() not in raw_mpc:
                        raise ValueError("Authentic saved stage-2 candidate was not inserted into the MPC program")
                    command = ("/mp-spdz/Scripts/compile-run.py -E mascot "
                               "/baseline/evaluation/evaluation_storage/" + task_id.split("/")[1] + ".mpc")
                    if (attempt["command"] != command
                            or attempt["timeout_seconds"] !=
                            (150 if "math" in category or "ufunc" in category else 60) + 30 * i):
                        raise ValueError("Original command or timeout progression differs")
                    accepted = original_oracle({
                        "timed_out": attempt["timed_out"],
                        "stdout": stdout.decode("utf-8", "replace"),
                        "stderr": stderr.decode("utf-8", "replace"),
                    })
                if accepted != (row["oracle_status"] == "ACCEPT"):
                    raise ValueError("Original saved evaluator decision differs from raw stdout")
                rows.append({
                    "task_id": task_id, "candidate_id": c, "oracle_status": row["oracle_status"],
                    "archived_author_accepted": row["historical_author_flag"],
                    "compile_status": row["compile_status"], "runtime_status": row["runtime_status"],
                    "raw_attempts": len(attempts), "source_sha256": row["source_sha256"],
                })
        if len(rows) != 14 or len({(r["task_id"], r["candidate_id"]) for r in rows}) != 14:
            raise ValueError("Seven-category original stage-2 smoke is incomplete")
        if any(len(values) != 1 for values in pins.values()):
            raise ValueError("Source, packages, or image drift between stage-2 smoke categories")
        return {
            "smoke_artifact_sha256": sha(smoke_path.read_bytes()),
            "smoke_task_count": 7, "native_candidate_count": 14,
            "raw_attempt_count": sum(row["raw_attempts"] for row in rows),
            "native_accept": sum(row["oracle_status"] == "ACCEPT" for row in rows),
            "native_reject": sum(row["oracle_status"] == "REJECT" for row in rows),
            "archived_acceptance_disagreements": sum(
                (row["oracle_status"] == "ACCEPT") != row["archived_author_accepted"] for row in rows),
            "compile_status": dict(Counter(row["compile_status"] for row in rows)),
            "runtime_status": dict(Counter(row["runtime_status"] for row in rows)),
            "pins": {k: next(iter(v)) for k, v in pins.items()},
            "outcomes": rows,
            "scope": "Independent ZIP hash/data verification, not MPC execution or new model generation",
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-zip", type=Path, required=True)
    parser.add_argument("--historical-traces-zip", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    result = json.dumps(audit(options.smoke_zip, options.historical_traces_zip), indent=2) + "\n"
    if options.output:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(result)
    print(result)


if __name__ == "__main__":
    main()
