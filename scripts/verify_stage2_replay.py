#!/usr/bin/env python3
"""Independently verify raw *fresh* stage-2 native runs and full coverage.

The original evaluator's loose stdout acceptance check is intentionally
preserved. This checks its results, not universal semantic correctness.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.summarize_original_replay import verify_run, sha
from scripts.prepare_original_replay import AUTHOR_SHA, MP_COMMIT
from scripts.replay_original import EVALUATOR_SHA
from scripts.reproduce_official_scores import COUNTS


def validate_stage2_run(run_dir):
    root = Path(run_dir)
    records = verify_run(root)
    ledger = json.loads((root / "stage2_identity.json").read_text())
    manifest = json.loads((root / "source_manifest.json").read_text())
    environment = json.loads((root / "environment.json").read_text())
    accepted = ROOT / "research/evidence/2026-10-15/original-smoke/smoke"
    for name in ("source_manifest.json", "installed-packages.txt", "os-packages.txt"):
        if sha(root / name) != sha(accepted / name):
            raise ValueError("Stage-2 evaluator environment/source differs from accepted original smoke")
    if (environment["source_kind"] != "authentic_saved_stage2_prior_to_saved_stage3"
            or environment["model_stage_executed"] is not False
            or environment["original_evaluator_sha256"] != EVALUATOR_SHA
            or environment["api_calls"] != 0
            or environment["protocol"] != "MASCOT" or environment["parties"] != 2
            or environment["mp_spdz_commit"] != MP_COMMIT
            or environment["source_archive_sha256"] != AUTHOR_SHA
            or environment["mascot_binary_sha256"] != manifest["mascot_binary_sha256"]):
        raise ValueError("Stage-2 run evaluator/protocol provenance changed")
    if ledger["author_archive_sha256"] != AUTHOR_SHA:
        raise ValueError("Stage-2 candidate author archive pin differs")
    indexed = {r["task_id"]: r for r in ledger["task_records"]}
    original = json.loads((ROOT / "research/evidence/2026-10-14/identity_verified_scores.json").read_text())
    orig_index = {r["task_id"]: r for r in original["task_records"]}
    if len(indexed) != 313 or set(indexed) != set(orig_index) or len(ledger["task_records"]) != 313:
        raise ValueError("Original stage-2 task inventory differs from authentic 313-task ledger")
    source_files = {m["path"]: m["sha256"] for m in manifest["baseline_files"]}
    for row in ledger["task_records"]:
        if (row["template_sha256"] != orig_index[row["task_id"]]["template_sha256"]
                or row["position_in_split"] != orig_index[row["task_id"]]["position_in_split"]
                or source_files.get(row["source_file"]) != row["source_file_sha256"]):
            raise ValueError("Historical stage-2 row hash/identity differs from original")
    seen = set()
    for r in records:
        key = (r["task_id"], r["candidate_id"])
        if key in seen or r.get("stage") != "stage2" or r.get("system") != "spdzcoder":
            raise ValueError("Unexpected/duplicated stage-2 task")
        seen.add(key)
        source = indexed.get(r["task_id"])
        c = r["candidate_id"]
        if (source is None or type(c) is not int or c not in (0, 1)
                or r["category"] != source["category"]
                or r["source_sha256"] != source["candidate_sha256"][c]
                or r["source_file_sha256"] != source["source_file_sha256"]
                or r["source_file"] != source["source_file"]
                or r["template_sha256"] != source["template_sha256"]
                or r["historical_author_flag"] is not source["historical_stage2_evaluator_flags"][c]):
            raise ValueError("Original saved stage-2 candidate source/flag identity differs")
    return records, ledger


def summarize_full(records, ledger):
    tasks = {r["task_id"]: r for r in ledger["task_records"]}
    expected = {(t, candidate) for t in tasks for candidate in (0, 1)}
    indexed = {}
    for r in records:
        key = (r["task_id"], r["candidate_id"])
        if key not in expected or key in indexed:
            raise ValueError("Unexpected duplicate/foreign stage-2 candidate")
        indexed[key] = r
    if set(indexed) != expected:
        raise ValueError(f"Full original stage-2 replay incomplete: {len(indexed)}/626")
    def metrics(ids, field):
        decisions = {(t, c): ((indexed[(t, c)]["oracle_status"] == "ACCEPT")
                               if field == "fresh" else tasks[t]["historical_stage2_evaluator_flags"][c])
                     for t in ids for c in (0, 1)}
        return {
            "tasks": len(ids),
            "first": sum(decisions[t, 0] for t in ids),
            "second": sum(decisions[t, 1] for t in ids),
            "union": sum(decisions[t, 0] or decisions[t, 1] for t in ids),
        }
    categories = {}
    for category, n in ledger["categories"].items():
        ids = [task for task in tasks if task.startswith(category + "/")]
        if len(ids) != n["tasks"]:
            raise ValueError("Stage-2 native category denominator changed")
        categories[category] = {"fresh": metrics(ids, "fresh"), "historical": metrics(ids, "historical")}
    disagreement = [
        {"task_id": t, "candidate_id": c,
         "saved_flag": tasks[t]["historical_stage2_evaluator_flags"][c],
         "fresh_accept": indexed[t, c]["oracle_status"] == "ACCEPT"}
        for t, c in sorted(expected)
        if tasks[t]["historical_stage2_evaluator_flags"][c] != (indexed[t, c]["oracle_status"] == "ACCEPT")
    ]
    return {
        "scope": "Fresh MASCOT replay of authentic SAVED stage-2 candidates through unmodified original evaluator; no model generation",
        "source_kind": "historical_saved_stage2", "original_evaluator_unchanged": True,
        "live_model_calls": 0, "tasks": len(tasks), "candidate_records": len(records),
        "fresh": metrics(tasks, "fresh"), "historical": metrics(tasks, "historical"),
        "categories": categories, "saved_to_fresh_disagreements": disagreement,
        "compile_statuses": dict(Counter(r["compile_status"] for r in records)),
        "runtime_statuses": dict(Counter(r["runtime_status"] for r in records)),
        "failure_classes": dict(Counter(r["failure_class"] or "none" for r in records)),
        "accepted_without_completed_runtime": sum(r["oracle_status"] == "ACCEPT" and
                                                    r["runtime_status"] != "PASS" for r in records),
        "limitations": "Original author's weak stdout oracle retained; saved-stage2-to-stage3 differences do not establish a randomized or causal no-repair ablation; original LLM stages not reexecuted.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()
    roots = sorted(f.parent for f in args.root.rglob("outcomes.jsonl"))
    if not roots:
        raise ValueError("No stage-2 results discovered")
    records, ledgers, pins, image_ids = [], [], set(), {}
    for root in roots:
        rows, ledger = validate_stage2_run(root)
        records.extend(rows)
        ledgers.append(ledger)
        env = json.loads((root / "environment.json").read_text())
        image_id = env.get("container_image_id")
        # Each category is built in a separate runner: image-layer timestamps may
        # change the image identifier even when every pinned source and installed
        # package byte remains identical. Record ALL IDs, never equate them.
        import re
        if not isinstance(image_id, str) or not re.fullmatch(r"sha256:[a-f0-9]{64}", image_id):
            raise ValueError("Missing or invalid category Docker image provenance")
        image_ids[str(root)] = image_id
        pins.add((sha(root / "stage2_identity.json"), sha(root / "source_manifest.json"),
                  sha(root / "installed-packages.txt"), sha(root / "os-packages.txt"),
                  env["research_commit"], env["mp_spdz_commit"],
                  env["mascot_binary_sha256"], env["original_evaluator_sha256"]))
    if len(pins) != 1 or any(ledger != ledgers[0] for ledger in ledgers):
        raise ValueError("Mixed stage-2 source, package manifests, original evaluator or research revision")
    if args.smoke:
        wanted = {
            "array_test/reverse_and_concat", "loop_test/max_adjacent_product",
            "branch_test/sin_or_cos", "math_test/sigmoid",
            "numpy_operation_test/array_from_intrinsic_linspace",
            "numpy_ufunc_test/logsumexp", "syntax_test/second_largest",
        }
        if len(records) != 14 or {(r["task_id"], r["candidate_id"]) for r in records} != {
            (t, c) for t in wanted for c in (0, 1)
        }:
            raise ValueError("Original seven-category stage-2 smoke is incomplete")
        summary = {"scope": "Seven-category 14-candidate authentic stage-2 MASCOT smoke",
                   "tasks": 7, "candidate_records": 14,
                   "accepted": sum(r["oracle_status"] == "ACCEPT" for r in records),
                   "failures_preserved": sum(r["oracle_status"] != "ACCEPT" for r in records),
                   "live_model_calls": 0, "source_verified": True}
    else:
        if len(roots) != 7 or len(records) != 626:
            raise ValueError("Original full stage-2 replay requires seven splits and 626 cases")
        summary = summarize_full(records, ledgers[0])
    summary["native_run_image_ids_by_output_root"] = dict(sorted(image_ids.items()))
    summary["pinned_source_and_package_identity"] = list(next(iter(pins)))
    if args.output.exists():
        raise ValueError("Output summary directory must be fresh")
    args.output.mkdir(parents=True)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (args.output / "outcomes.jsonl").write_text("".join(json.dumps(r) + "\n" for r in sorted(records,
        key=lambda r: (r["task_id"], r["candidate_id"]))))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
