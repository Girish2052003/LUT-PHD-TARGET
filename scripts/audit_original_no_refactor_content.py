#!/usr/bin/env python3
"""Read-only original-author TAR CONTENT search for no-refactoring provenance."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import tarfile

PIN = "a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac"
ROOTS = {"src", "data", "evaluation", "analysis", "utility", "scripts", "experiment", "experiments", "result", "results", "README.md", "run.sh", "requirement.txt", "requirements.txt"}
EXPLICIT = re.compile(r"(?i)(without.{0,12}refactor|no[_\s-]{0,8}refactor|ablation|skip.{0,20}refactor|disable.{0,20}refactor|refactor.{0,12}(off|false|disabled))")
RELATED = re.compile(r"(?i)(refactoring|apply_high_rules|azure[-_]gpt4|gpt-4-turbo|stage_1_ir_output|stage_2_spdz_output|baseline)")
REDACT = re.compile(r"(?i)(api[_-]?key|access[_-]?token|client[_-]?secret|password|authorization|PRIVATE KEY)")
EXTS = {".py", ".sh", ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".csv"}

def scan(tar):
    scanned, skipped, root_files = Counter(), Counter(), Counter()
    exact_paths, explicit_matches, source_anchors = set(), [], []
    total_bytes = 0
    for entry in tar:
        if not entry.isfile() or not entry.name.startswith("SPDZCoder/"):
            continue
        path = entry.name.removeprefix("SPDZCoder/")
        root = path.split("/",1)[0]
        root_files[root] += 1
        if ".git/" in path or path.startswith(".git/"):
            skipped["git"] += 1
            continue
        if root not in ROOTS or (Path(path).suffix.lower() not in EXTS and root not in {"README.md","run.sh"}):
            skipped["other_scopes_or_binary"] += 1
            continue
        if entry.size > 8_000_000:
            skipped["too_large"] += 1
            continue
        if total_bytes + entry.size > 250_000_000:
            raise ValueError("Bounded scan exceeded safe text byte limit")
        fd = tar.extractfile(entry)
        if fd is None:
            skipped["unreadable"] += 1
            continue
        raw = fd.read(8_000_001)
        if len(raw) != entry.size or b"\x00" in raw:
            skipped["binary_or_truncated"] += 1
            continue
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            skipped["undecodable"] += 1
            continue
        total_bytes += entry.size
        scanned[root] += 1
        within = 0
        for line_no, line in enumerate(content.splitlines(),1):
            if REDACT.search(line):
                continue
            if EXPLICIT.search(line):
                exact_paths.add(path)
                if len(explicit_matches) < 180 and within < 10:
                    explicit_matches.append({"path":path,"line":line_no,"text":line.strip()[:220],"source_sha256":hashlib.sha256(raw).hexdigest()})
                within += 1
            if (Path(path).suffix.lower() in {".py",".sh",".md"} and RELATED.search(line)
                and len(source_anchors) < 100 and sum(x["path"]==path for x in source_anchors)<8):
                source_anchors.append({"path":path,"line":line_no,"text":line.strip()[:200]})
    return {"original_archive_sha256":PIN,"scope":"Author-original textual src/data/evaluation/utility/analysis/readme content; bounded; no code executed",
      "scanned_files":sum(scanned.values()),"scanned_bytes":total_bytes,
      "scanned_roots":dict(sorted(scanned.items())),"skipped":dict(sorted(skipped.items())),
      "all_regular_file_root_counts":dict(sorted(root_files.items())),
      "explicit_marker_paths":sorted(exact_paths),"explicit_marker_path_count":len(exact_paths),
      "explicit_matches":explicit_matches,"explicit_match_details_capped":len(explicit_matches)>=180,
      "source_anchors":source_anchors,"generation_executed":False,"native_mpc_executed":False,
      "limitations":"Lexical content hits and numerical equality are NOT original-system no-refactoring result provenance. No hits is not proof of historical impossibility."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tar",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if hashlib.sha256(a.tar.read_bytes()).hexdigest()!=PIN:
        raise ValueError("Original author archive SHA-256 mismatch")
    with tarfile.open(a.tar,"r:*") as tar:
        result=scan(tar)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"scanned_files":result["scanned_files"],"explicit_marker_path_count":result["explicit_marker_path_count"]}))

if __name__=="__main__":
    main()
