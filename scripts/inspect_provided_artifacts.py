#!/usr/bin/env python3
"""Inspect the sources Professor Kumar linked without executing downloaded code.

The metadata output is intentionally useful even when an archive is too large
to fetch within GitHub Actions. Archives are listed but never extracted.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tarfile
import time
import urllib.error
import urllib.request
import zipfile

ZENODO_ID = "18152253"
ACM_DOI = "10.1145/3845985"
MAX_FILES_TO_PRINT = 80
MAX_TOTAL_ARCHIVE_ENTRIES = 20000


def fetch(url: str, max_bytes: int = 3_000_000) -> bytes:
    req = urllib.request.Request(url, headers={
        "User-Agent": "SPDZCoder-research-reproduction/0.1 (academic artifact audit)",
        "Accept": "application/json, application/vnd.zenodo.v1+json;q=0.9, */*;q=0.2",
    })
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                data = response.read(max_bytes + 1)
                if len(data) > max_bytes:
                    raise ValueError(f"Response exceeded {max_bytes} byte cap: {url}")
                return data
        except (OSError, urllib.error.HTTPError) as exc:
            last_error = exc
            if attempt != 2:
                time.sleep(2 + attempt * 3)
    raise RuntimeError(f"Retrieval failed for {url}: {last_error}") from last_error


def record_files(record: dict) -> list[dict]:
    files = record.get("files", [])
    if isinstance(files, dict):
        files = list((files.get("entries") or {}).values())
    results = []
    for item in files:
        if not isinstance(item, dict):
            continue
        access = item.get("links") or {}
        results.append({
            "name": str(item.get("key") or item.get("filename") or item.get("id") or ""),
            "size": item.get("size", 0),
            "checksum": item.get("checksum") or (item.get("checksum") or {}).get("md5")
            if not isinstance(item.get("checksum"), dict) else item.get("checksum"),
            "url": access.get("self") or access.get("content") or access.get("download"),
        })
    return results


def inspect_archive(path: Path) -> dict:
    names: list[str] = []
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_TOTAL_ARCHIVE_ENTRIES:
                raise ValueError("Archive has too many entries to audit safely")
            names = [entry.filename for entry in entries if not entry.is_dir()]
            archive_type = "zip"
    elif tarfile.is_tarfile(path):
        with tarfile.open(path, "r:*") as archive:
            entries = archive.getmembers()
            if len(entries) > MAX_TOTAL_ARCHIVE_ENTRIES:
                raise ValueError("Archive has too many entries to audit safely")
            names = [entry.name for entry in entries if entry.isfile()]
            archive_type = "tar"
    else:
        return {"type": "unknown", "note": "Not a recognized ZIP or TAR archive"}
    names.sort()
    lower = [x.lower() for x in names]
    py = [x for x in names if x.endswith(".py")]
    suites = [x for x in names if re.search(r"spdzeval|benchmark|test|refactor|prompt|config|readme", x, re.I)]
    print(f"ARCHIVE: {path.name} ({archive_type}); {len(names)} files; {len(py)} Python files")
    for name in suites[:MAX_FILES_TO_PRINT]:
        print(f"  FILE: {name}")
    return {"type": archive_type, "n_files": len(names), "n_python": len(py),
            "candidate_files": suites, "all_files": names}


def download_archive(file: dict, dest: Path, size_cap: int) -> dict:
    name = file["name"]
    url = file.get("url")
    declared_size = file.get("size") or 0
    if not url or not name.lower().endswith((".zip", ".tar", ".tar.gz", ".tgz")):
        return {"downloaded": False, "reason": "not downloadable supported archive"}
    if not isinstance(declared_size, int) or declared_size > size_cap:
        return {"downloaded": False, "reason": "size exceeds configured cap", "declared_size": declared_size}
    data = fetch(url, max_bytes=size_cap)
    digest = hashlib.sha256(data).hexdigest()
    md5 = hashlib.md5(data).hexdigest()  # provenance only, not a security primitive
    expected = file.get("checksum")
    if isinstance(expected, str) and ":" in expected:
        kind, value = expected.split(":", 1)
        actual = {"md5": md5, "sha256": digest}.get(kind.lower())
        if actual and value.lower() != actual:
            raise ValueError(f"Published {kind} checksum mismatch for {name}")
    path = dest / Path(name).name
    path.write_bytes(data)
    info = inspect_archive(path)
    return {"downloaded": True, "size": len(data), "sha256": digest,
            "md5": md5, "archive": info}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/official_artifacts")
    parser.add_argument("--download-under-mib", type=int, default=60)
    args = parser.parse_args()
    dest = Path(args.output)
    dest.mkdir(parents=True, exist_ok=True)
    result: dict = {
        "source": {"zenodo": f"https://zenodo.org/records/{ZENODO_ID}",
                   "doi": f"https://doi.org/{ACM_DOI}"},
        "retrieval_errors": {},
    }
    try:
        record = json.loads(fetch(f"https://zenodo.org/api/records/{ZENODO_ID}"))
        metadata = record.get("metadata") or {}
        files = record_files(record)
        result["zenodo"] = {
            "id": record.get("id"),
            "title": metadata.get("title"),
            "doi": record.get("doi"),
            "publication_date": metadata.get("publication_date"),
            "creators": metadata.get("creators"),
            "license": metadata.get("license"),
            "description": metadata.get("description"),
            "files": files,
        }
        print("ZENODO TITLE:", result["zenodo"]["title"])
        print("ZENODO DOI:", result["zenodo"]["doi"])
        for f in files:
            print("ZENODO FILE:", f["name"], "size=", f["size"],
                  "checksum=", f["checksum"], "URL=", f["url"])
        for f in files:
            try:
                f["inspection"] = download_archive(f, dest,
                    args.download_under_mib * 1024 * 1024)
            except Exception as exc:
                f["inspection"] = {"error": str(exc)}
                print("ARCHIVE DOWNLOAD ERROR:", f["name"], str(exc))
    except Exception as exc:
        print("ZENODO ERROR:", exc)
        result["retrieval_errors"]["zenodo"] = str(exc)
    try:
        crossref = json.loads(fetch(f"https://api.crossref.org/works/{ACM_DOI}"))
        work = crossref.get("message", {})
        result["acm"] = {
            "doi": work.get("DOI"), "title": work.get("title"),
            "authors": work.get("author"), "container_title": work.get("container-title"),
            "published": work.get("published"), "URL": work.get("URL"),
            "relation": work.get("relation"),
        }
        print("ACM PAPER TITLE:", result["acm"]["title"])
        print("ACM DOI:", result["acm"]["doi"])
    except Exception as exc:
        print("ACM DOI METADATA ERROR:", exc)
        result["retrieval_errors"]["crossref"] = str(exc)

    (dest / "source_manifest.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return 0 if not result["retrieval_errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
