"""Import-time validation for the ORIGINAL SPDZEval, if/when authors supply it.

We do not fabricate missing tasks. The schema here is our explicit, documented
interchange format; it is not claimed to be the author's native dataset format.
"""
from __future__ import annotations
from collections import Counter
import ast
import json
from pathlib import Path
import re

PAPER_SPLITS = {
    "array": 43, "loop": 97, "branch": 34,
    "math": 38, "numpy": 66, "syntax": 35
}
TOTAL = sum(PAPER_SPLITS.values())  # 313


def validate(entries: list[dict], *, require_complete: bool = True) -> dict:
    if not isinstance(entries, list):
        raise ValueError("Dataset must be a list")
    seen = set()
    counts = Counter()
    for task in entries:
        if not isinstance(task, dict) or set(task) != {
            "id", "split", "python_source", "mpspdz_reference", "tests"}:
            raise ValueError("Each original task must have ID, split, both sources, tests")
        identifier = task["id"]
        if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", identifier):
            raise ValueError("Invalid task identifier")
        if identifier in seen:
            raise ValueError("Duplicate task identifier")
        seen.add(identifier)
        split = task["split"]
        if split not in PAPER_SPLITS:
            raise ValueError("Unknown SPDZEval split")
        counts[split] += 1
        for key in ("python_source", "mpspdz_reference"):
            source = task[key]
            if not isinstance(source, str) or not source.strip():
                raise ValueError("Missing official " + key)
            ast.parse(source)
        tests = task["tests"]
        if not isinstance(tests, list) or not tests:
            raise ValueError("Cannot evaluate a task without original test cases")
        for case in tests:
            if not isinstance(case, dict) or set(case) != {"args", "expected"}:
                raise ValueError("Each test requires args and expected")
            if not isinstance(case["args"], list):
                raise ValueError("Test args must be a list")
    if require_complete and (len(entries) != TOTAL or
                             dict(counts) != PAPER_SPLITS):
        raise ValueError("Complete 313-case SPDZEval with exact six split counts required")
    return {
        "entry_count": len(entries), "per_split": dict(counts),
        "paper_total": TOTAL,
        "matches_paper_structure": len(entries) == TOTAL and dict(counts) == PAPER_SPLITS,
        "semantic_correctness_unchecked": True,
        "provenance_must_be_original_author_artifact": True
    }


def load(path: Path, *, require_complete: bool = True) -> tuple[list[dict], dict]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict) or set(payload) != {"format", "entries", "provenance"}:
        raise ValueError("Expected explicit format/entries/provenance")
    if payload["format"] != "SPDZCoder-normalized-import-v1":
        raise ValueError("Unexpected normalized import format")
    provenance = payload["provenance"]
    if not isinstance(provenance, dict) or not provenance.get("source_url"):
        raise ValueError("Original artifact source URL is required")
    summary = validate(payload["entries"], require_complete=require_complete)
    summary["source_url"] = provenance["source_url"]
    summary["source_sha256"] = provenance.get("source_sha256")
    return payload["entries"], summary
