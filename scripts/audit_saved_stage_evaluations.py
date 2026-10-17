#!/usr/bin/env python3
"""Compare historically saved stage-2 and stage-3 native evaluation flags, if released.

Read-only artifact metadata; neither runs MPC nor calls an LLM. A historical
stage-2 to stage-3 difference is NOT a controlled ablation or causal repair gain.
Missing stage-2 evaluation files remain MISSING instead of being synthesized.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import tarfile

from scripts.reproduce_official_scores import COUNTS, parse_results

ZENODO_SHA = "a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac"


def inspect(tar, identity):
    paths = [m.name.removeprefix("SPDZCoder/") for m in tar.getmembers()
             if m.isfile() and m.name.startswith("SPDZCoder/evaluation/")]
    archive_ids = {r["task_id"]: r for r in identity["task_records"]}
    if len(archive_ids) != 313:
        raise ValueError("Original task identity ledger differs")
    report = {"source": "original authors' archived stage evaluation logs",
              "fresh_mpc_executions": 0, "live_llm_calls": 0,
              "categories": {}, "missing_categories": [],
              "scope_limitations": "Historical stage comparison, not controlled no-repair ablation. Logs and candidate stage changes do not prove causes."}
    for category, count in COUNTS.items():
        # Detect any true stage-2 assessment logs; do not assume filenames.
        matched = [p for p in paths if "experiment-1-stage_2" in p
                   and p.endswith("_" + category + ".txt")]
        if len(matched) > 1:
            raise ValueError("Ambiguous stage-2 evaluation source for " + category)
        if not matched:
            report["missing_categories"].append(category)
            report["categories"][category] = {"status": "MISSING_STAGE2_EVALUATION",
                                              "tasks": count, "reason": "Official release does not provide a uniquely matching stage-2 evaluator log."}
            continue
        path = matched[0]
        member = tar.getmember("SPDZCoder/" + path)
        if member.size > 8_000_000:
            raise ValueError("Oversized authors' stage-2 evaluation log")
        raw = tar.extractfile(member).read()
        flags = parse_results(raw.decode("utf-8"), count)
        expected = [r for r in identity["task_records"] if r["task_id"].startswith(category + "/")]
        expected.sort(key=lambda r: r["position_in_split"])
        if [name for name, *_ in flags] != [r["task_id"].split("/")[1] for r in expected]:
            raise ValueError("Stage-2 native evaluation identity/order differs")
        transitions = Counter()
        examples = []
        for (name, before0, before1), record in zip(flags, expected):
            after0, after1 = record["archived_acceptance"]
            for index, old, new in ((0, before0, after0), (1, before1, after1)):
                transitions["gain" if not old and new else "loss" if old and not new else "unchanged"] += 1
                if old != new:
                    examples.append({"task_id": category + "/" + name,
                                     "candidate_id": index, "stage2_accepted": old,
                                     "stage3_accepted": new})
        report["categories"][category] = {
            "status": "SAVED_LOG_COMPARISON",
            "source_path": path, "source_sha256": hashlib.sha256(raw).hexdigest(),
            "tasks": count, "stage2_first": sum(x[1] for x in flags),
            "stage2_second": sum(x[2] for x in flags),
            "stage2_union": sum(x[1] or x[2] for x in flags),
            "stage3_first": sum(r["archived_acceptance"][0] for r in expected),
            "stage3_second": sum(r["archived_acceptance"][1] for r in expected),
            "stage3_union": sum(any(r["archived_acceptance"]) for r in expected),
            "candidate_transitions": dict(transitions), "changed_decisions": examples,
        }
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tar", type=Path, required=True)
    p.add_argument("--identity", type=Path,
                   default=Path("research/evidence/2026-10-14/identity_verified_scores.json"))
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if hashlib.sha256(args.tar.read_bytes()).hexdigest() != ZENODO_SHA:
        raise ValueError("Original published source archive differs")
    identity = json.loads(args.identity.read_text())
    with tarfile.open(args.tar, "r:*") as tar:
        result = inspect(tar, identity)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("Original saved stage-2 evaluation categories:",
          sum(v["status"] == "SAVED_LOG_COMPARISON" for v in result["categories"].values()))
    print("Missing stage-2 evaluation categories:", result["missing_categories"])


if __name__ == "__main__":
    main()
