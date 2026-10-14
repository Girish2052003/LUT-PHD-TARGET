#!/usr/bin/env python3
"""Create a byte-preserving, data-only working copy of the public Zenodo release.

No author code is executed. Git history, compiled caches, credential files,
binary outputs and unknown archive paths are intentionally excluded.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
import zipfile

ROOT = "SPDZCoder/"
KEEP_DIRECTORIES = (
    "data/", "src/", "evaluation/", "utility/", "scripts/",
    "spdzcoder_various_LLM_as_backbone/",
)
ALLOWED_EXTENSIONS = {".py", ".json", ".jsonl", ".txt", ".md", ".sh", ".mpc",
                      ".csv", ".toml", ".yaml", ".yml"}
MAX_PER_FILE = 25 * 1024 * 1024
MAX_ALL_FILES = 3000
EXPECTED_MD5 = "3c6d7707d7aecc051d35312f81405c66"


def wanted(name: str) -> bool:
    candidate = PurePosixPath(name)
    # Validate exactly the spelling written to the ZIP, not a normalized alias.
    if candidate.as_posix() != name or candidate.is_absolute() or "\\" in name:
        return False
    parts = candidate.parts
    if len(parts) < 2 or parts[0] != "SPDZCoder":
        return False
    if any(p in ("..", ".", ".git", "__pycache__", ".venv", "node_modules")
           or p.startswith(".") for p in parts[1:]):
        return False
    inner = "/".join(parts[1:])
    if inner in ("README.md", "requirement.txt", "requirements.txt"):
        return True
    if not any(inner.startswith(p) for p in KEEP_DIRECTORIES):
        return False
    if any(t in name.lower() for t in ("private_key", "secret_key", "credentials",
                                       "id_rsa", ".env", "/player-data/")):
        return False
    return candidate.suffix.lower() in ALLOWED_EXTENSIONS


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tar", default="results/official_artifacts/SPDZCoder.tar")
    parser.add_argument("--output", default="results/official_artifacts/spdzcoder-public-research-snapshot.zip")
    args = parser.parse_args()
    archive = Path(args.tar)
    data_hash = hashlib.md5(archive.read_bytes()).hexdigest()  # Zenodo's published MD5
    if data_hash != EXPECTED_MD5:
        raise ValueError("Zenodo original TAR checksum differs from published checksum")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    collected = []
    seen = set()
    sizes = Counter()
    with tarfile.open(archive, "r:*") as src, zipfile.ZipFile(
            output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as dst:
        members = src.getmembers()
        if len(members) > 5000:
            raise ValueError("Unexpectedly large archive")
        for member in members:
            if not member.isfile() or not wanted(member.name):
                continue
            if member.size > MAX_PER_FILE:
                raise ValueError(f"Unexpectedly large source/data file: {member.name}")
            handle = src.extractfile(member)
            if handle is None:
                raise ValueError(f"Unreadable file: {member.name}")
            raw = handle.read(MAX_PER_FILE + 1)
            if len(raw) != member.size:
                raise ValueError(f"File changed during reading: {member.name}")
            relative = member.name[len(ROOT):]
            if relative in seen:
                raise ValueError(f"Duplicate export path: {relative}")
            seen.add(relative)
            dst.writestr(relative, raw)
            sizes[relative.split("/")[0]] += 1
            collected.append({"path": relative, "bytes": len(raw),
                              "sha256": hashlib.sha256(raw).hexdigest()})
            if len(collected) > MAX_ALL_FILES:
                raise ValueError("Unexpectedly many source files")
        dst.writestr("ZENODO_SOURCE_MANIFEST.json", json.dumps({
            "source_url": "https://zenodo.org/records/18152253",
            "original_tar_md5": EXPECTED_MD5, "files": collected
        }, indent=2) + "\n")
    print("RESEARCH SNAPSHOT:", output, "bytes=", output.stat().st_size)
    print("SELECTED ORIGINAL FILES:", len(collected))
    print("SELECTED DIRECTORY COUNTS:", dict(sizes))
    print("NUMBER OF MPC TEST PROGRAMS:", sum(
        x["path"].startswith("data/input_data/") and x["path"].endswith(".mpc")
        for x in collected))
    print("STUDY NOTE: no code was executed; author .git internals were excluded.")


if __name__ == "__main__":
    main()
