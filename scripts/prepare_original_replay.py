#!/usr/bin/env python3
"""Prepare a minimal, checksum-pinned replay build context; execute no author code."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.export_official_snapshot import wanted
from scripts.reproduce_official_scores import reproduce

AUTHOR_SHA = "a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac"
MP_ARCHIVE_SHA = "e83efcbbe9b295fe276450f3d4aa6e822f35d4bf348c87dee4877b4fed4e5f40"
MP_COMMIT = "6cc3fccef0904764364eb8e285519cd34028f325"
AUTHOR_URL = "https://zenodo.org/records/18152253/files/SPDZCoder.tar?download=1"
MP_URL = "https://github.com/data61/MP-SPDZ/releases/download/v0.3.6/mp-spdz-0.3.6.tar.xz"


def obtain(path: Path, url: str, digest: str, size: int):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        # curl's connection/low-speed limits permit recovery from a stalled link.
        subprocess.run(["curl", "-fLsS", "--retry", "3", "--max-time", "600",
                        "--speed-limit", "1024", "--speed-time", "45", url,
                        "-o", str(path)], check=True)
    raw = path.read_bytes()
    if len(raw) != size or hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError("Source archive integrity mismatch: " + str(path))


def export_mp_sources(repo: Path, target: Path, commit: str):
    """Read tracked bytes from Git's object store, never the working tree."""
    paths = ["Compiler", *["Scripts/" + name for name in
             ("compile-run.py", "mascot.sh", "run-common.sh", "setup-ssl.sh")]]
    raw = subprocess.check_output(["git", "-C", str(repo), "archive", commit, *paths])
    records = []
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        for member in archive:
            if member.isdir():
                continue
            relative = PurePosixPath(member.name)
            if not member.isfile() or relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Unexpected MP-SPDZ Git archive member: " + member.name)
            data = archive.extractfile(member).read()
            dest = target / member.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            dest.chmod(0o755 if member.mode & 0o111 else 0o644)
            records.append({"path": member.name, "sha256": hashlib.sha256(data).hexdigest()})
    return records


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--build-dir", default="tmp/original-replay-build")
    p.add_argument("--author-tar", default="tmp/source-cache/SPDZCoder.tar")
    p.add_argument("--mp-archive", default="tmp/source-cache/mp-spdz-0.3.6.tar.xz")
    p.add_argument("--mp-repo", default="tmp/MP-SPDZ-0.3.6")
    args = p.parse_args()
    build = Path(args.build_dir).resolve()
    if build.exists():
        raise ValueError("Use a fresh build directory; refusing to overwrite an earlier experiment")
    author, binary, mp_repo = (Path(x).resolve() for x in (args.author_tar, args.mp_archive, args.mp_repo))
    obtain(author, AUTHOR_URL, AUTHOR_SHA, 65761280)
    obtain(binary, MP_URL, MP_ARCHIVE_SHA, 87738604)
    if not mp_repo.exists():
        subprocess.run(["git", "clone", "--depth=1", "--branch", "v0.3.6",
                        "https://github.com/data61/MP-SPDZ.git", str(mp_repo)], check=True)
    actual = subprocess.check_output(["git", "-C", str(mp_repo), "rev-parse", "HEAD"], text=True).strip()
    if actual != MP_COMMIT or subprocess.check_output(["git", "-C", str(mp_repo), "status", "--porcelain", "--untracked-files=no"], text=True).strip():
        raise ValueError("MP-SPDZ source is not the clean pinned revision")
    build.mkdir(parents=True)
    baseline = build / "baseline"
    manifest = []
    with tarfile.open(author) as tar:
        names = set()
        for member in tar:
            if not member.isfile() or not wanted(member.name):
                continue
            relative = member.name[len("SPDZCoder/"):]
            if relative in names or member.size > 25 * 1024 * 1024:
                raise ValueError("Duplicate or oversized source member: " + relative)
            names.add(relative)
            raw = tar.extractfile(member).read()
            dest = baseline / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
            manifest.append({"path": relative, "sha256": hashlib.sha256(raw).hexdigest()})
    (build / "identity.json").write_text(json.dumps(reproduce(author), indent=2) + "\n")
    target = build / "mp-spdz"
    mp_sources = export_mp_sources(mp_repo, target, MP_COMMIT)
    with tarfile.open(binary) as tar:
        member = tar.getmember("mp-spdz-0.3.6/bin/Linux-amd64/mascot-party.x")
        if not member.isfile():
            raise ValueError("Runtime binary is not a regular file")
        exe = target / "mascot-party.x"
        exe.write_bytes(tar.extractfile(member).read())
        exe.chmod(0o755)
    metadata = {"author_archive_sha256": AUTHOR_SHA, "mp_spdz_commit": MP_COMMIT,
                "mp_spdz_version": "0.3.6", "binary_archive_sha256": MP_ARCHIVE_SHA,
                "mascot_binary_sha256": hashlib.sha256(exe.read_bytes()).hexdigest(),
                "baseline_files": manifest,
                "mp_source_files": mp_sources,
                "source_revision_note": "Python compiler/scripts from pinned git commit; runtime from official same-version release",
                "api_calls_authorized": False}
    (build / "source_manifest.json").write_text(json.dumps(metadata, indent=2) + "\n")
    for name in ("replay_original.py", "probe_original_limitations.py"):
        shutil.copy2(ROOT / "scripts" / name, build / name)
    for name in ("Dockerfile", "requirements.txt"):
        shutil.copy2(ROOT / "research" / "replay" / name, build / name)
    print("Prepared original baseline without executing author code:", build)
    print("Selected original files:", len(manifest))


if __name__ == "__main__":
    main()
