#!/usr/bin/env python3
"""Read-only exact Zenodo version lineage / related artifact inventory.

Consumes only official Zenodo record JSON, never executes author code,
downloads a historical model, calls a model API or infers experimental scores.
"""
import argparse
import json
from pathlib import Path

def compact_record(item):
    if not isinstance(item, dict):
        return {}
    meta=item.get("metadata")
    if not isinstance(meta, dict):meta={}
    parent=item.get("parent")
    if not isinstance(parent,dict):parent={}
    links=item.get("links")
    if not isinstance(links,dict):links={}
    files=item.get("files") or []
    if isinstance(files,dict):files=files.get("entries") or []
    if isinstance(files,dict):files=[{"key":k,**(v if isinstance(v,dict) else {})} for k,v in files.items()]
    saved=[]
    for file in files:
        if isinstance(file,dict):
            checksum=file.get("checksum")
            if isinstance(checksum,str):checksum=checksum[:160]
            saved.append({"key":file.get("key"),"size":file.get("size"),"checksum":checksum})
    return {"id":item.get("id"),"doi":item.get("doi"),"conceptdoi":item.get("conceptdoi"),
            "version":meta.get("version"),"title":meta.get("title"),
            "publication_date":meta.get("publication_date"),
            "parent_id":parent.get("id"),
            "self":links.get("self"),"record":links.get("self_html"),
            "files":saved[:30],
            "related_identifiers":[{"identifier":x.get("identifier"),"relation":x.get("relation")}
                                   for x in meta.get("related_identifiers",[])
                                   if isinstance(x,dict)][:35]}

def analyze(payload):
    if not isinstance(payload,dict):
        raise ValueError("Unexpected Zenodo API response")
    items=[]
    if isinstance(payload.get("hits"),dict) and isinstance(payload["hits"].get("hits"),list):
        items=payload["hits"]["hits"]
    elif isinstance(payload.get("hits"),list):
        items=payload["hits"]
    elif "id" in payload:
        items=[payload]
    else:
        raise ValueError("No record or version data in supplied metadata")
    return [compact_record(x) for x in items]

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--versions",required=True,type=Path)
    a.add_argument("--parent",required=True,type=Path)
    a.add_argument("--output",required=True,type=Path)
    args=a.parse_args()
    r={"requested_versions_api":"https://zenodo.org/api/records/18152253/versions",
       "requested_parent_api":"https://zenodo.org/api/records/17974882",
       "versions_status":"UNAVAILABLE","parent_status":"UNAVAILABLE",
       "versions":[],"parent_record":[],
       "model_calls":0,"native_mpc_reruns":0,
       "limitations":"Record lineage cannot establish presence of original ablation without opening, hashing, and linking the precise source/result files."}
    for title,path,out in [("versions",args.versions,"versions"),("parent",args.parent,"parent_record")]:
        try:
            raw=json.loads(path.read_text())
            values=analyze(raw)
            r[out]=values
            r[title+"_status"]="AVAILABLE"
        except (ValueError,UnicodeError,OSError,TypeError) as exc:
            r[title+"_error_type"]=type(exc).__name__
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"versions_status":r["versions_status"],
                      "parent_status":r["parent_status"],
                      "version_ids":[x["id"] for x in r["versions"]],
                      "versions_file_lists":[{"id":x["id"],"files":x["files"]} for x in r["versions"]]},indent=2))

if __name__=="__main__":
    main()
