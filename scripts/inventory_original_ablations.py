#!/usr/bin/env python3
"""Independently inventory available ORIGINAL author ablation artifacts by filename.

This is a source/provenance inventory only. Never infer a no-refactoring
pass-rate from merely named directories or from stage-2 vs stage-3 outputs.
No code from the downloaded original archive is executed.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import tarfile

ARCHIVE_SHA256 = "a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac"
SPLITS = ("array_test", "loop_test", "branch_test", "math_test",
          "numpy_operation_test", "numpy_ufunc_test", "syntax_test")
PATTERN = re.compile(r"(?i)(?:ablati|refactor|without|no[_-]|baseline|stage[_-][123]|feedback|repair|experiment)")
PREFIX = "SPDZCoder/"


def inventory(tar):
    entries, contexts = [], Counter()
    for item in tar:
        if not item.isfile() or not item.name.startswith(PREFIX):
            continue
        name = item.name[len(PREFIX):]
        if name.startswith(".git/") or "/.git/" in name:
            continue
        scope = name.split("/", 1)[0]
        contexts[scope] += 1
        if not PATTERN.search(name):
            continue
        entries.append({"path": name, "bytes": item.size,
                        "category_markers": [category for category in SPLITS if category in name]})
    entries.sort(key=lambda item: item["path"])
    # This is purposefully NOT an outcome parser: no causal ablation claims.
    return {
        "scope": "Complete filename-only search for accessible author ablation/stage/baseline artifacts",
        "source_kind": "Original released Zenodo archive, not independent reconstruction",
        "matching_entries": entries,
        "matching_entry_count": len(entries),
        "top_level_regular_file_counts": dict(sorted(contexts.items())),
        "original_seven_categories": list(SPLITS),
        "fresh_model_calls": 0, "native_mpc_executions": 0,
        "limitations": "Matching filenames do not prove availability or validity of a no-refactoring evaluation. "
                       "Inspect exact task IDs, source strings, evaluation flags and instructions before "
                       "claiming a controlled or archived ablation reproduction.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tar", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if hashlib.sha256(a.tar.read_bytes()).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("Authentic authors' archive checksum does not match")
    with tarfile.open(a.tar, "r:*") as tar:
        out = inventory(tar)
    out["archive_sha256"] = ARCHIVE_SHA256
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print("Original candidate ablation/stage filenames inspected:", out["matching_entry_count"])


if __name__ == "__main__":
    main()
