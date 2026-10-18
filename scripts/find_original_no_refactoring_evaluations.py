#!/usr/bin/env python3
"""Read-only grouped author evaluation-log search for paper's no-refactor RQ2.

A group matching the paper's numbers is NOT automatically a no-refactoring
variant. Correct original experiment/source linkage must be checked separately.
"""
from collections import defaultdict
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.reproduce_official_scores import COUNTS, parse_results

ARCHIVE="a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac"
TARGET_FIRST=104  # 33.23% of 313 as Table 6 reports
TARGET_UNION=142  # 45.37% of 313 as Table 6 reports
MAX_FILE=8_000_000


def group_name(path, categories=COUNTS):
    if not path.startswith("evaluation/") or not path.endswith(".txt"):
        return None
    for category in sorted(categories,key=len,reverse=True):
        suffix=category+".txt"
        if path.endswith(suffix):
            base=path[:-len(suffix)].rstrip("-_")
            if not base: return None
            return (base,category)
    return None


def scan(tar, identity):
    original={x["task_id"]:x for x in identity["task_records"]}
    if len(original)!=313:
        raise ValueError("Original task identity inventory missing")
    grouped=defaultdict(dict)
    for item in tar:
        if not item.isfile() or not item.name.startswith("SPDZCoder/evaluation/") or item.size > MAX_FILE:
            continue
        path=item.name.removeprefix("SPDZCoder/")
        group=group_name(path)
        if group:
            key,category=group
            if category in grouped[key]:
                raise ValueError("Ambiguous duplicated saved original evaluation category")
            grouped[key][category]=(path,item.size)
    all_groups=[]
    for name,found in sorted(grouped.items()):
        if set(found)!=set(COUNTS):
            continue
        categories={}
        failures={}
        for category, (source_path,size) in found.items():
            item=tar.getmember("SPDZCoder/"+source_path)
            raw=tar.extractfile(item).read()
            if len(raw)!=size: raise ValueError("Original evaluation record truncated")
            try:
                flags=parse_results(raw.decode("utf-8"), COUNTS[category])
                expected=sorted((r for r in original.values() if r["task_id"].startswith(category+"/")),
                                key=lambda r:r["position_in_split"])
                if len(expected)!=COUNTS[category] or [f[0] for f in flags] != [r["task_id"].split("/")[1] for r in expected]:
                    raise ValueError("Task names/order do not match original native tasks")
                categories[category]={"source_path":source_path,"sha256":hashlib.sha256(raw).hexdigest(),
                    "n":len(flags),"first":sum(r[1] for r in flags),
                    "second":sum(r[2] for r in flags),
                    "union":sum(r[1] or r[2] for r in flags)}
            except (ValueError,UnicodeDecodeError,KeyError,IndexError) as exc:
                failures[category]=str(exc)
        if failures:
            all_groups.append({"group":name,"status":"UNPARSEABLE_OR_NOT_SPDZEVAL","errors":failures})
            continue
        first=sum(c["first"] for c in categories.values())
        second=sum(c["second"] for c in categories.values())
        union=sum(c["union"] for c in categories.values())
        all_groups.append({"group":name,"status":"SAVED_ORIGINAL_EVALUATION_GROUP",
                           "first":first,"second":second,"union":union,
                           "same_numbers_as_paper_no_refactoring":first==TARGET_FIRST and union==TARGET_UNION,
                           "categories":categories})
    matched=[g for g in all_groups if g.get("same_numbers_as_paper_no_refactoring")]
    return {
      "scope":"Search publisher saved original seven-category task-identified native evaluation groups",
      "paper_table6_without_refactoring":{"first":TARGET_FIRST,"union":TARGET_UNION,"tasks":313},
      "groups_evaluated":len(all_groups),"groups_matching_both_numbers":matched,
      "no_refactoring_provenance_status":"UNCONFIRMED_EVEN_IF_NUMERICALLY_MATCHED",
      "groups":all_groups,
      "fresh_llm_calls":0,"fresh_mpc_executions":0,
      "limitations":"Coincidentally equal native scores do not prove a group uses no-refactoring source code. A paper-to-source exact experiment mapping is required before treating any match as this ablation.",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tar",type=Path,required=True)
    p.add_argument("--identity",type=Path,default=ROOT/"research/evidence/2026-10-14/identity_verified_scores.json")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if hashlib.sha256(args.tar.read_bytes()).hexdigest()!=ARCHIVE:
        raise ValueError("Original authors' archive checksum mismatch")
    identity=json.loads(args.identity.read_text())
    with tarfile.open(args.tar,"r:*") as tar:
        result=scan(tar,identity)
    result["original_archive_sha256"]=ARCHIVE
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print("Distinct complete original seven-category evaluation groups:",result["groups_evaluated"],
          "numerical Table6 no-refactoring candidates:",len(result["groups_matching_both_numbers"]))


if __name__=="__main__":
    main()
