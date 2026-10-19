#!/usr/bin/env python3
"""Read-only comparison of OFF-TAR publisher README and Zenodo record metadata.

Does not execute original code, evaluate an MPC program, invoke an LLM,
or claim that source URLs / coincident numbers prove historical reproduction.
"""
import argparse
from difflib import unified_diff
from hashlib import md5, sha256
import json
from pathlib import Path
import re
import tarfile

TAR_SHA256 = "a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac"
EXTERNAL_README_MD5 = "1d3416063a6d7e4adc84ace62e082694"
SENSITIVE = re.compile(r"(?i)(api[_-]?key|token|secret|password|authorization|private[_ -]?key|bearer\s)")
INDICATOR = re.compile(
    r"(?i)(without.{0,15}refactor|no[_ -]{0,8}refactor|"
    r"ablati|refactor|reproduc|baseline|evalua|experiment|"
    r"model|gpt|azure|zenodo|github|repository|code)")
URL = re.compile(r"https?://[^\s)>\]]+")
MAX_LINES = 180
MAX_BYTES = 250_000


def safe_lines(text):
    return [(i, line.strip()[:300]) for i, line in enumerate(text.splitlines(), 1)
            if not SENSITIVE.search(line) and INDICATOR.search(line)][:MAX_LINES]


def inspect(original_tar, companion_readme, api_metadata=None):
    t = Path(original_tar).read_bytes()
    ext = Path(companion_readme).read_bytes()
    if sha256(t).hexdigest() != TAR_SHA256:
        raise ValueError("Original TAR checksum mismatch")
    if md5(ext).hexdigest() != EXTERNAL_README_MD5:
        raise ValueError("Zenodo companion README checksum mismatch")
    if len(ext) > MAX_BYTES:
        raise ValueError("Unexpectedly large companion readme")
    with tarfile.open(fileobj=__import__("io").BytesIO(t), mode="r:*") as source:
        matching = [m for m in source if m.isfile() and m.name.rstrip("/") == "SPDZCoder/README.md"]
        if len(matching) != 1:
            raise ValueError("Original TAR root README identity not unique")
        inner = source.extractfile(matching[0]).read(MAX_BYTES + 1)
    if len(inner) > MAX_BYTES:
        raise ValueError("Unexpectedly large embedded README")
    external = ext.decode("utf-8")
    internal = inner.decode("utf-8")
    unified = list(unified_diff(internal.splitlines(), external.splitlines(),
                               fromfile="author-tar-root/README.md",
                               tofile="Zenodo-record-separate-README.md"))
    diffs = [line[:350] for line in unified if not SENSITIVE.search(line)][:MAX_LINES]
    data = None
    status = "NOT_FETCHED"
    if api_metadata is not None:
        path = Path(api_metadata)
        if path.exists() and path.stat().st_size < 2_000_000:
            try:
                data = json.loads(path.read_text("utf-8"))
                status = "AVAILABLE"
            except (json.JSONDecodeError, UnicodeError):
                status = "UNAVAILABLE"
        else:
            status = "UNAVAILABLE"
    summary = {}
    if isinstance(data, dict):
        metadata = data.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        links = data.get("links", {})
        if not isinstance(links, dict):
            links = {}
        props = ["version", "title", "publication_date", "description"]
        summary = {k: (str(metadata.get(k))[:350] if k != "description"
                         else "REDACTED") for k in props if metadata.get(k)}
        summary.update({
            "doi": data.get("doi"),
            "conceptdoi": data.get("conceptdoi"),
            "conceptrecid": data.get("conceptrecid"),
            "record_links": {k: links[k] for k in ["latest", "versions", "self", "parent"] if k in links},
            "related_identifiers": metadata.get("related_identifiers", [])[:50],
            "file_keys": [x.get("key") for x in data.get("files", [])
                          if isinstance(x, dict)][:30],
        })
    urls = sorted({link.rstrip(".,;") for link in URL.findall(external)
                   if not SENSITIVE.search(link)})
    return {
        "source_record": "https://zenodo.org/records/18152253",
        "verified_tar_sha256": sha256(t).hexdigest(),
        "verified_separate_readme_md5": md5(ext).hexdigest(),
        "separate_readme_sha256": sha256(ext).hexdigest(),
        "tar_root_readme_sha256": sha256(inner).hexdigest(),
        "separate_readme_bytes": len(ext),
        "tar_root_readme_bytes": len(inner),
        "same_readme_bytes": ext == inner,
        "readme_diff_lines": diffs,
        "readme_diff_total_line_count": len(unified),
        "separate_readme_research_lines": safe_lines(external),
        "internal_readme_research_lines": safe_lines(internal),
        "companion_link_candidates": urls[:50],
        "publisher_api_metadata_status": status,
        "publisher_api_public_links_and_related_identifiers": summary,
        "no_refactoring_experiment_reproduced": False,
        "historical_model_generation_executed": False,
        "original_native_mpc_rerun": False,
        "limitations": "Separate readme and metadata inspection is source discovery only. "
        "A genuine SPDZCoder no-refactoring result requires original input/outputs "
        "paired by exact task and generation provenance. Historical model calls "
        "cannot be reconstructed from README prose.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tar", required=True)
    ap.add_argument("--companion-readme", required=True)
    ap.add_argument("--api-metadata")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    report = inspect(args.tar, args.companion_readme, args.api_metadata)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: report[k] for k in
        ["same_readme_bytes", "readme_diff_total_line_count",
         "publisher_api_metadata_status", "separate_readme_bytes"]},
        indent=2))


if __name__ == "__main__":
    main()
