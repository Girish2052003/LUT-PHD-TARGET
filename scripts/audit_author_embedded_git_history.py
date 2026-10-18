#!/usr/bin/env python3
"""Read-only Git-object archaeology on EMBEDDED original author .git history.

Parses Git loose objects in the checksum-pinned Zenodo TAR as inert bytes.
Does not extract a repository, run Git/hooks, execute code, invoke models/MPC,
or follow filesystem paths. Git packfiles, if present, remain explicitly
uninspected and prevent a complete-history conclusion.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import tarfile
import zlib

PIN = "a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac"
EXPLICIT = re.compile(r"(?i)(without.{0,12}refactor|no[_ -]{0,8}refactor|ablation|skip.{0,20}refactor|disable.{0,20}refactor)")
PATH_RE = re.compile(r"(?i)(refactor|ablation|without|no[_-]refactor)")
SECRET = re.compile(r"(?i)(api[_-]?key|access[_-]?token|client[_-]?secret|password|private key)")
LOOSE = re.compile(r"^SPDZCoder/\.git/objects/([0-9a-f]{2})/([0-9a-f]{38})$")
MAX_OBJECT = 16_000_000

def scan(tar):
    types, skipped = Counter(), Counter()
    tree_objects, commit_objects, blobs = {}, {}, {}
    packfiles, refs, direct_paths = [], [], []
    for f in tar:
        if not f.isfile() or not f.name.startswith("SPDZCoder/.git/"):
            continue
        if f.size > MAX_OBJECT:
            skipped["oversized"] += 1
            continue
        stream = tar.extractfile(f)
        if stream is None:
            skipped["missing"] += 1
            continue
        raw = stream.read(MAX_OBJECT+1)
        if len(raw) != f.size:
            raise ValueError("Truncated embedded Git item: "+f.name)
        match = LOOSE.fullmatch(f.name)
        if not match:
            if f.name.endswith(".pack"):
                packfiles.append({"path": f.name.removeprefix("SPDZCoder/"), "bytes":f.size})
            elif (f.name.endswith("packed-refs") or "/refs/" in f.name or "/logs/" in f.name):
                refs.append({"path":f.name.removeprefix("SPDZCoder/"),"sha256":hashlib.sha256(raw).hexdigest()})
            skipped["git_metadata_not_loose_object"] += 1
            continue
        object_hash = "".join(match.groups())
        try:
            decompressed = zlib.decompress(raw)
        except zlib.error as e:
            raise ValueError("Invalid Git zlib object: "+object_hash) from e
        if len(decompressed) > MAX_OBJECT or hashlib.sha1(decompressed).hexdigest() != object_hash:
            raise ValueError("Git object integrity failure: "+object_hash)
        marker, separator, data = decompressed.partition(b"\0")
        if not separator:
            raise ValueError("Missing Git object header")
        object_kind, space, length = marker.partition(b" ")
        if not space or not length.isdigit() or int(length) != len(data):
            raise ValueError("Git object length mismatch")
        kind=object_kind.decode("ascii")
        types[kind] += 1
        if kind=="tree":
            nodes = []
            i=0
            while i < len(data):
                stop=data.find(b"\0",i)
                if stop < 0 or stop+21 > len(data):
                    raise ValueError("Invalid Git tree entry")
                mode, separator, basename=data[i:stop].partition(b" ")
                if not separator:
                    raise ValueError("Invalid Git mode/name")
                sha=data[stop+1:stop+21].hex()
                nodes.append((mode.decode("ascii"),basename.decode("utf-8","replace"),sha))
                i=stop+21
            tree_objects[object_hash] = nodes
        elif kind=="commit":
            commit_objects[object_hash] = data[:25000].decode("utf-8","replace")
        elif kind=="blob":
            blobs[object_hash] = data

    possible_paths=set()
    unresolvable_roots=0
    for commit_id, text in commit_objects.items():
        root=next((line[5:45] for line in text.splitlines() if line.startswith("tree ")),None)
        if not root or root not in tree_objects:
            unresolvable_roots+=1
            continue
        todo=[("",root)]
        count=0
        while todo:
            prefix,parent=todo.pop()
            count+=1
            if count>30000:
                raise ValueError("Git tree expansion safety limit")
            for mode,name,oid in tree_objects.get(parent,[]):
                path=(prefix+"/"+name).lstrip("/")
                if PATH_RE.search(path):
                    possible_paths.add(path)
                if mode.startswith("40") and oid in tree_objects:
                    todo.append((path,oid))
    explicit_matches=[]
    hit_blobs=set()
    for oid,data in blobs.items():
        if len(data)>4_000_000 or b"\0" in data:
            continue
        try:
            content=data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for line_number,line in enumerate(content.splitlines(),1):
            if SECRET.search(line):
                continue
            if EXPLICIT.search(line):
                hit_blobs.add(oid)
                if len(explicit_matches)<100:
                    explicit_matches.append({"git_blob_id":oid,"line":line_number,"text":line.strip()[:180]})
    return {"scope":"Checksum-verified original TAR embedded .git LOOSE object and all commit trees; read-only no code execution",
            "git_object_counts":dict(sorted(types.items())),"commit_roots_examined":len(commit_objects),
            "unresolvable_commit_roots":unresolvable_roots,
            "git_blob_object_count":len(blobs),"embedded_git_packfiles":packfiles,
            "history_complete_with_loose_objects":len(packfiles)==0 and unresolvable_roots==0,
            "ref_or_log_metadata":refs[:45],
            "tree_paths_matching_refactor_or_ablation":sorted(possible_paths)[:100],
            "tree_path_match_count":len(possible_paths),
            "blobs_with_explicit_ablation_markers":len(hit_blobs),
            "explicit_git_blob_matches":explicit_matches,
            "skipped":dict(skipped),"original_archive_sha256":PIN,
            "historical_model_calls":0,"native_mpc_executions":0,
            "limits":"Git blob lexical matches/path names are clues only, not matched original no-refactoring experiments. Missing Git packed objects require further review; absence of hits does NOT prove original experiment never existed."}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--tar",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    if hashlib.sha256(args.tar.read_bytes()).hexdigest()!=PIN:
        raise ValueError("Authentic author TAR mismatch")
    with tarfile.open(args.tar,"r:*") as tar:
        outcome=scan(tar)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(outcome,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"git_objects":outcome["git_object_counts"],"commits":outcome["commit_roots_examined"],"explicit_matching_blobs":outcome["blobs_with_explicit_ablation_markers"],"packed_history":bool(outcome["embedded_git_packfiles"])}))
if __name__=="__main__":
    main()
