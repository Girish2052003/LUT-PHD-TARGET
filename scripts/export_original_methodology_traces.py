#!/usr/bin/env python3
"""Export seven genuine saved SPDZCoder methodology traces; never execute author code.

The stage snapshots are HISTORICAL publisher data, not fresh model generations.
This read-only export does not reconstruct missing prompts, intermediate repairs,
model API calls, or stage-internal tool traffic. It verifies task identities,
candidate hashes and published archive provenance before writing any evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile

SOURCE_SHA256 = "a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac"
PREFIX = "SPDZCoder/"
SAMPLES = (
    "array_test/reverse_and_concat",
    "loop_test/max_adjacent_product",
    "branch_test/sin_or_cos",
    "math_test/sigmoid",
    "numpy_operation_test/array_from_intrinsic_linspace",
    "numpy_ufunc_test/logsumexp",
    "syntax_test/second_largest",
)
COUNTS = {
    "array_test": 43, "loop_test": 97, "branch_test": 34, "math_test": 38,
    "numpy_operation_test": 32, "numpy_ufunc_test": 34, "syntax_test": 35,
}
STAGES = (
    ("input_processed", "data/input_processed_data/{category}.json"),
    ("stage_1_refactor", "data/stage_1_IR_output/experiment-1-{category}_intermediate_representation.jsonl"),
    ("stage_2_generate_reflect", "data/stage_2_SPDZ_output/experiment-1-{category}.jsonl"),
    ("stage_3_final", "data/stage_3_output/experiment-1-{category}.jsonl"),
)
MAX_BYTES = 12_000_000


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_regular(tar, path):
    member = tar.getmember(PREFIX + path)
    if not member.isfile() or member.size > MAX_BYTES:
        raise ValueError("Not a bounded regular author file: " + path)
    fp = tar.extractfile(member)
    if fp is None:
        raise ValueError("Author file unreadable: " + path)
    raw = fp.read(MAX_BYTES + 1)
    if len(raw) != member.size:
        raise ValueError("Incomplete author file: " + path)
    return raw


def records(raw, count):
    # The authors' files with .json suffix are JSON Lines in this release.
    lines = [line for line in raw.splitlines(keepends=True) if line.strip()]
    if len(lines) != count:
        raise ValueError("Stage has missing/extra task records")
    rows = []
    for line in lines:
        row = json.loads(line)
        if not isinstance(row, dict) or not isinstance(row.get("test_name"), str):
            raise ValueError("Malformed stage task record")
        rows.append((row, sha(line)))
    if len({row["test_name"] for row, _ in rows}) != len(rows):
        raise ValueError("Duplicate task identity within stage")
    return rows


def inspect(tar, identity):
    originals = {row["task_id"]: row for row in identity["task_records"]}
    if len(originals) != len(identity["task_records"]) or len(originals) != 313:
        raise ValueError("Original task identity ledger is incomplete")
    if len(SAMPLES) != 7 or {s.split("/")[0] for s in SAMPLES} != set(COUNTS):
        raise ValueError("Missing or duplicated category")
    source_files = identity["source_files"]
    result = []
    for task_id in SAMPLES:
        category, name = task_id.split("/")
        reference = originals[task_id]
        position = reference["position_in_split"]
        selected = {}
        id_order = None
        for stage, pattern in STAGES:
            path = pattern.format(category=category)
            raw = read_regular(tar, path)
            if path in source_files and sha(raw) != source_files[path]:
                raise ValueError("Stage differs from validated official source: " + path)
            stage_rows = records(raw, COUNTS[category])
            ordered_ids = [row["test_name"] for row, _ in stage_rows]
            if id_order is not None and ordered_ids != id_order:
                raise ValueError("Source-stage task order drift: " + path)
            id_order = ordered_ids
            if id_order[position] != name:
                raise ValueError("Stage position differs from authentic identity")
            selected[stage] = {
                "original_file": path, "file_sha256": sha(raw), "line_number": position + 1,
                "line_sha256": stage_rows[position][1],
                "source": "authentic saved author stage snapshot",
                "fields": stage_rows[position][0],
            }
        if len(set(id_order)) != COUNTS[category]:
            raise ValueError("Stage task identity mismatch")
        original_native = read_regular(tar, reference["template_path"])
        if sha(original_native) != reference["template_sha256"]:
            raise ValueError("Native original template mismatch")
        for candidate in (0, 1):
            source = selected["stage_3_final"]["fields"].get(f"response_{candidate}")
            if not isinstance(source, str) or sha(source.encode("utf-8")) != reference["candidate_sha256"]["spdzcoder"][candidate]:
                raise ValueError("Archived final-stage candidate differs from task ledger")
        stage2 = selected["stage_2_generate_reflect"]["fields"]
        stage3 = selected["stage_3_final"]["fields"]
        changed = {
            f"candidate_{candidate}": (
                stage2.get(f"response_{candidate}") != stage3.get(f"response_{candidate}")
                if isinstance(stage2.get(f"response_{candidate}"), str) else None)
            for candidate in (0, 1)
        }
        result.append({
            "task_id": task_id, "category": category,
            "position_in_original_category_zero_based": position,
            "native_template": {"path": reference["template_path"], "sha256": reference["template_sha256"],
                                "content": original_native.decode("utf-8")},
            "stages": selected,
            "stage2_vs_final_source_changed": changed,
            "original_archived_native_acceptance": reference["archived_acceptance"],
            "candidate_source_sha256": reference["candidate_sha256"]["spdzcoder"],
            "provenance": "Only historically saved author rows and native source; model steps not reexecuted.",
            "missing_intermediate_history": [
                "Per-rule refactoring prompts and intermediate conversations not established by this snapshot",
                "Pre-self-reflection generated candidate not reconstructed",
                "Intermediate repair attempts, model API traffic, and tool call order not reconstructed",
            ],
        })
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tar", type=Path, required=True)
    p.add_argument("--identity", type=Path,
                   default=Path("research/evidence/2026-10-14/identity_verified_scores.json"))
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if sha(args.tar.read_bytes()) != SOURCE_SHA256:
        raise ValueError("Zenodo archive SHA256 does not match pinned source")
    identity = json.loads(args.identity.read_text())
    with tarfile.open(args.tar, "r:*") as tar:
        traces = inspect(tar, identity)
    args.output.mkdir(parents=True, exist_ok=False)
    rows = []
    for trace in traces:
        category = trace["category"]
        payload = json.dumps(trace, ensure_ascii=False, indent=2) + "\n"
        (args.output / (category + ".json")).write_text(payload)
        rows.append({"task_id": trace["task_id"], "artifact_path": category + ".json",
                     "artifact_sha256": sha(payload.encode("utf-8")),
                     "stages": list(trace["stages"]),
                     "stage2_vs_final_source_changed": trace["stage2_vs_final_source_changed"],
                     "archived_acceptance": trace["original_archived_native_acceptance"]})
    summary = {
        "archive_sha256": SOURCE_SHA256, "sample_count": len(rows),
        "physical_categories": sorted(COUNTS), "original_task_count": 313,
        "stage_labels": [s for s, _ in STAGES],
        "fresh_author_model_calls": 0,
        "fresh_stage_execution": False,
        "traces": rows,
        "limitation": "Saved source stages only: no invented repair transcripts or new LLM calls; not independent generation reproduction.",
    }
    (args.output / "manifest.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
