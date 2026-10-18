#!/usr/bin/env python3
"""Prepare a pinned, *additional* stage-2 evaluator harness; never run author code.

Run AFTER scripts/prepare_original_replay.py. This script intentionally changes
only the disposable Docker build context, never the authentic original baseline,
original evaluator, repository Dockerfile, or previously approved replay tools.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.reproduce_official_scores import COUNTS, parse_results
from scripts.prepare_original_replay import AUTHOR_SHA


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def build_stage2_ledger(baseline, identity, source_manifest):
    indexed = {r["task_id"]: r for r in identity["task_records"]}
    if len(indexed) != len(identity["task_records"]) or len(indexed) != 313:
        raise ValueError("Original 313-task identity is missing or duplicated")
    manifest = {r["path"]: r["sha256"] for r in source_manifest["baseline_files"]}
    if source_manifest["author_archive_sha256"] != AUTHOR_SHA:
        raise ValueError("Incorrect original Zenodo archive")
    ledger = {"schema_version": 1, "author_archive_sha256": AUTHOR_SHA,
              "source_kind": "historical author stage-2, prior to saved stage-3 repair",
              "original_evaluator": "unchanged evaluation/evaluate_experimental-mp.py",
              "live_model_calls": 0, "task_records": [], "categories": {}}
    for category, n in COUNTS.items():
        code_path = f"data/stage_2_SPDZ_output/experiment-1-{category}.jsonl"
        flags_path = f"evaluation/experiment-1-stage_2_SPDZ_output_{category}.txt"
        content = (baseline / code_path).read_bytes()
        saved = (baseline / flags_path).read_bytes()
        if sha(content) != manifest.get(code_path) or sha(saved) != manifest.get(flags_path):
            raise ValueError("Stage-2 candidate/evaluation files differ from pinned archive")
        rows = [json.loads(line) for line in content.splitlines() if line.strip()]
        flags = parse_results(saved.decode("utf-8"), n)
        if len(rows) != n:
            raise ValueError("Stage-2 source category has an unexpected task count")
        for pos, (row, (task, first, second)) in enumerate(zip(rows, flags)):
            name = row.get("test_name")
            original = indexed.get(f"{category}/{task}")
            if original is None or name != task or original["position_in_split"] != pos:
                raise ValueError("Stage-2 candidate, saved flag, and native task ID/order disagree")
            sources = [row.get("response_0"), row.get("response_1")]
            if any(not isinstance(code, str) for code in sources):
                raise ValueError("Expected precisely two stage-2 candidate strings")
            ledger["task_records"].append({
                "task_id": original["task_id"], "category": category,
                "position_in_split": pos, "source_file": code_path,
                "source_file_sha256": sha(content),
                "template_sha256": original["template_sha256"],
                "candidate_sha256": [sha(code.encode("utf-8")) for code in sources],
                "historical_stage2_evaluator_flags": [first, second],
            })
        ledger["categories"][category] = {
            "tasks": n, "candidate_source_path": code_path,
            "candidate_source_sha256": sha(content),
            "historical_evaluation_path": flags_path,
            "historical_evaluation_sha256": sha(saved),
        }
    if len(ledger["task_records"]) != 313 or len({r["task_id"] for r in ledger["task_records"]}) != 313:
        raise ValueError("Expected 313 authentic historical stage-2 tasks")
    return ledger


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--build-dir", type=Path, default=Path("tmp/original-replay-build"))
    args = p.parse_args()
    build = args.build_dir.resolve()
    if not (build / "source_manifest.json").is_file() or not (build / "baseline").is_dir():
        raise ValueError("Run original preparation before stage-2 preparation")
    if (build / "stage2_identity.json").exists() or (build / "replay_stage2.py").exists():
        raise ValueError("Stage-2 preparation must be run exactly once per fresh build")
    source_manifest = json.loads((build / "source_manifest.json").read_text())
    identity = json.loads((build / "identity.json").read_text())
    ledger = build_stage2_ledger(build / "baseline", identity, source_manifest)
    script = ROOT / "scripts/replay_stage2.py"
    if not script.is_file():
        raise ValueError("Reviewed stage-2 evaluator harness is missing")
    dockerfile = build / "Dockerfile"
    original = dockerfile.read_text()
    expected = "COPY replay_original.py probe_original_limitations.py identity.json source_manifest.json /harness/"
    if original.count(expected) != 1:
        raise ValueError("Pinned Dockerfile differs from reviewed harness insertion point")
    updated = original.replace(expected,
        "COPY replay_original.py probe_original_limitations.py replay_stage2.py identity.json stage2_identity.json source_manifest.json /harness/")
    # No change to /baseline, MP-SPDZ source, original evaluator or source_manifest.
    shutil.copy2(script, build / "replay_stage2.py")
    (build / "stage2_identity.json").write_text(json.dumps(ledger, indent=2) + "\n")
    dockerfile.write_text(updated)
    (build / "stage2-harness-extension.json").write_text(json.dumps({
        "scope": "Disposable harness-only extension; original source and evaluator unchanged",
        "original_dockerfile_sha256": sha(original.encode()),
        "modified_build_context_dockerfile_sha256": sha(updated.encode()),
        "added_harness_sha256": sha(script.read_bytes()),
        "stage2_identity_sha256": sha((build / "stage2_identity.json").read_bytes()),
        "original_manifest_sha256": sha((build / "source_manifest.json").read_bytes()),
    }, indent=2) + "\n")
    print("Prepared original stage-2 candidate ledger:", len(ledger["task_records"]),
          "tasks, 626 candidate hashes. Zero API calls; original source untouched.")


if __name__ == "__main__":
    main()
