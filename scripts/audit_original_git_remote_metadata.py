#!/usr/bin/env python3
"""Check original author .git CONFIG remote provenance plus v1 companion README.

All source is treated as inert data. No Git commands, checkout, hooks, model
generation or MPC execution. Strip credentials and nonpublic remote paths.
"""
import argparse
from configparser import ConfigParser
from hashlib import sha256, md5
import io
import json
from pathlib import Path
import re
import tarfile
from urllib.parse import urlsplit

TAR_SHA = "a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac"
V1_README_MD5 = "c3169b06f6cb0a18ec248f91de234e6f"
TRUSTED_PUBLIC_GIT = {"github.com","gitlab.com","bitbucket.org","codeberg.org"}
MAX_FILE = 100000

def clean_remote(value):
    value = value.strip()
    public = None
    host = ""
    if re.match(r"^git@[^:]+:",value):
        left,right = value.split(":",1)
        host = left.removeprefix("git@").lower()
        public = right
    else:
        parts=urlsplit(value)
        host=(parts.hostname or "").lower()
        if parts.username or parts.password:
            public = None
        elif parts.scheme in {"http","https","ssh"}:
            public=parts.path.lstrip("/")
    if host in TRUSTED_PUBLIC_GIT and public:
        if re.fullmatch(r"[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+(?:\.git)?",public):
            return {"host":host,"public_repository":public.removesuffix(".git"),
                    "remote_url_sha256":sha256(value.encode()).hexdigest()}
    return {"host": host if host in TRUSTED_PUBLIC_GIT else "NONPUBLIC_OR_UNKNOWN",
            "public_repository": None, "remote_url_sha256":sha256(value.encode()).hexdigest()}

def inspect(tar_bytes,v1_readme):
    if sha256(tar_bytes).hexdigest()!=TAR_SHA:
        raise ValueError("Original v2 TAR SHA-256 mismatch")
    if md5(v1_readme).hexdigest()!=V1_README_MD5:
        raise ValueError("Original v1 README MD5 mismatch")
    important = ["SPDZCoder/.git/config","SPDZCoder/.git/HEAD",
                 "SPDZCoder/.git/packed-refs","SPDZCoder/.gitmodules",
                 "SPDZCoder/README.md"]
    found={}
    with tarfile.open(fileobj=io.BytesIO(tar_bytes),mode="r:*") as tar:
        for name in important:
            try:
                entry=tar.getmember(name)
            except KeyError:
                continue
            if not entry.isfile() or entry.size>MAX_FILE:
                continue
            f=tar.extractfile(entry)
            if f:
                found[name]=f.read(MAX_FILE+1)
    config=ConfigParser(interpolation=None)
    config.optionxform = str
    remotes=[]
    git_config=found.get("SPDZCoder/.git/config",b"")
    if git_config:
        config.read_string(git_config.decode("utf-8",errors="replace"))
        for section in config.sections():
            if section.startswith('remote "') and section.endswith('"'):
                if config.has_option(section,"url"):
                    remotes.append({"remote_name":section[8:-1],
                                    **clean_remote(config.get(section,"url"))})
    root=found.get("SPDZCoder/README.md",b"")
    return {
      "original_v2_tar_sha256":sha256(tar_bytes).hexdigest(),
      "official_v1_readme_md5":md5(v1_readme).hexdigest(),
      "official_v1_readme_sha256":sha256(v1_readme).hexdigest(),
      "embedded_tar_readme_sha256":sha256(root).hexdigest() if root else None,
      "v1_readme_matches_embedded_v2_tar_readme":bool(root) and v1_readme==root,
      "git_config_present":bool(git_config),
      "git_remote_refs":remotes,
      "git_head_sha256":sha256(found["SPDZCoder/.git/HEAD"]).hexdigest()
                    if "SPDZCoder/.git/HEAD" in found else None,
      "packed_refs_present":"SPDZCoder/.git/packed-refs" in found,
      "gitmodules_present":"SPDZCoder/.gitmodules" in found,
      "report_limits":"Only publicly recognizable Git remote host/repo values are disclosed. "
         "Presence of remote is not evidence of a surviving public repo, ablation output "
         "or historical LLM generation. No original code, Git commands, MPC or API calls executed.",
      "experiment_reproduced":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tar",type=Path,required=True)
    p.add_argument("--v1-readme",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=inspect(a.tar.read_bytes(),a.v1_readme.read_bytes())
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
