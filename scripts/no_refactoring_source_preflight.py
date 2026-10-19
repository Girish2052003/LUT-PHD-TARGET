#!/usr/bin/env python3
"""Read-only, no-cost original source input preflight for missing ablation.

THIS DOES NOT REPRODUCE the original paper's no-refactoring scores.
No historical LLM outputs are generated, no paid API calls or MPC run.
"""
import argparse
import ast
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import tarfile

SHA="a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac"
COUNTS={"array_test":43,"loop_test":97,"branch_test":34,"math_test":38,
 "numpy_operation_test":32,"numpy_ufunc_test":34,"syntax_test":35}
PATHS={
 "original_input":"data/input_processed_data/{category}.json",
 "refactored":"data/stage_1_IR_output/experiment-1-{category}_intermediate_representation.jsonl",
 "generated":"data/stage_2_SPDZ_output/experiment-1-{category}.jsonl",
}
MAX_BYTES=15000000

def h(data):return sha256(data).hexdigest()

def read(tar,path):
    obj=tar.getmember("SPDZCoder/"+path)
    if not obj.isfile() or obj.size>MAX_BYTES:
        raise ValueError("Source file absent or oversized: "+path)
    f=tar.extractfile(obj)
    if f is None:raise ValueError("Unable to read: "+path)
    b=f.read(MAX_BYTES+1)
    if len(b)!=obj.size:raise ValueError("Truncated author bytes: "+path)
    return b

def parse(b,n,path):
    lines=[line for line in b.splitlines(keepends=True) if line.strip()]
    if len(lines)!=n:raise ValueError("Original task count differs: "+path)
    result=[]
    for line in lines:
        obj=json.loads(line)
        if not isinstance(obj,dict) or not isinstance(obj.get("test_name"),str):
            raise ValueError("Missing source task key: "+path)
        result.append((obj,h(line)))
    if len(set(obj["test_name"] for obj,_ in result))!=n:
        raise ValueError("Duplicate original task key: "+path)
    return result

def source_fields(obj):
    found=[]
    for k,v in obj.items():
        if k=="test_name" or not isinstance(v,str):continue
        if "def " not in v and "class " not in v and "import " not in v:continue
        try:ast.parse(v)
        except (ValueError,SyntaxError):continue
        found.append({"field":k,"sha256":h(v.encode()),"bytes":len(v.encode())})
    return found

def analyze(tar,counts=COUNTS):
    out=[]; file_provenance={}; by_field=Counter()
    for category,expected in counts.items():
        files={}; data={}
        for stage,template in PATHS.items():
            path=template.format(category=category)
            raw=read(tar,path)
            data[stage]=parse(raw,expected,path)
            files[stage]={"path":path,"sha256":h(raw)}
        ids=[[x["test_name"] for x,_ in data[k]] for k in PATHS]
        if any(ids[0]!=other for other in ids[1:]):
            raise ValueError("Original stage task identity/order differs: "+category)
        for i,test_name in enumerate(ids[0]):
            raw=data["original_input"][i][0]
            candidates=source_fields(raw)
            by_field.update(x["field"] for x in candidates)
            out.append({
                "task_id":category+"/"+test_name,"position_in_split":i,
                "original_input_row_sha256":data["original_input"][i][1],
                "refactored_row_sha256":data["refactored"][i][1],
                "already_generated_row_sha256":data["generated"][i][1],
                "plausible_unmodified_python_fields":candidates,
                "input_field_types":{k:type(v).__name__ for k,v in raw.items()},
            })
        file_provenance[category]={"count":expected,"stage_files":files}
    if len(out)!=sum(counts.values()) or len({r["task_id"] for r in out})!=len(out):
        raise ValueError("Not all source task identities match")
    return {
       "source":"Official original author Zenodo TAR; three author-stage input files per category",
       "original_archive_sha256":SHA,"task_count":len(out),
       "categories":file_provenance,"task_records":out,
       "parseable_top_level_python_source_tasks":sum(bool(r["plausible_unmodified_python_fields"]) for r in out),
       "source_field_occurrence_counts":dict(by_field),
       "live_model_api_calls":0,"native_mpc_executions":0,
       "historical_no_refactoring_results_recovered":False,
       "paper_no_refactoring_reproduced":False,
       "no_refactoring_model_budget_authorized":False,
       "next_dependency":"Confirm exact original no-refactoring prompt and original model snapshot/deployment; get explicit legal billable model authorization. Only two newly generated candidates per original task and untouched author native evaluator can give a separately labeled new ablation.",
       "limits":"Python-field identification is only syntax-based and may miss nested source. Historical refactored stage2 candidates cannot be relabeled as no-refactoring LLM outputs. Source hashes are not an experimental pass-rate."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tar",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if h(args.tar.read_bytes())!=SHA:raise ValueError("Original author TAR SHA256 mismatch")
    with tarfile.open(args.tar,"r:*") as tar:r=analyze(tar)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({k:r[k] for k in [
        "task_count","parseable_top_level_python_source_tasks",
        "source_field_occurrence_counts","live_model_api_calls","paper_no_refactoring_reproduced"
    ]},indent=2))
if __name__=="__main__":main()
