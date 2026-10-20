#!/usr/bin/env python3
"""Recheck pinned raw evidence without executing any author/generated program.

GitHub Actions supplies a read-only artifact token to gh. Original code is read
as data. Existing auditors recalculate outcomes; no native/model run is launched.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.verify_paired_replay import inserted_source, verify_pair_run
from scripts.verify_reproduction_difficulty_coverage import verify,verify_register,ROOT as PROJECT,FIRST,SECOND,DIFFICULTIES,TAXONOMY
from scripts.audit_stage2_full_zips import audit as audit_stage2
from scripts.audit_stage2_phase_g_secondary import audit as audit_secondary
from scripts.check_native_stage2_mpc_against_tar import audit as audit_tar
from scripts.audit_paired_controls import audit as audit_paired

REPO="Girish2052003/LUT-PHD-TARGET"

def read(path):
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def api(path):
    return json.loads(subprocess.check_output(["gh","api",f"/repos/{REPO}/{path}"],text=True,timeout=90))

def command(args):
    subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,check=True,timeout=1200)

def unpack(path,dest):
    dest.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(path) as z:
        total=0
        names=set()
        for member in z.infolist():
            p=PurePosixPath(member.filename)
            total+=member.file_size
            if (p.is_absolute() or ".." in p.parts or "\\" in member.filename
                    or member.filename in names or stat.S_ISLNK(member.external_attr>>16)
                    or member.file_size>100_000_000 or total>1_000_000_000):
                raise ValueError("Unsafe archive member")
            names.add(member.filename)
        z.extractall(dest)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cache",type=Path,default=Path("tmp/final-audit"))
    p.add_argument("--output",type=Path,default=Path("results/final-audit"))
    a=p.parse_args()
    a.cache=a.cache.resolve();a.output=a.output.resolve()
    a.cache.mkdir(parents=True,exist_ok=False);a.output.mkdir(parents=True,exist_ok=False)
    inputs=read(ROOT/"research/final_audit_artifacts.json")["artifacts"]
    if len(inputs)!=31 or len({r["id"] for r in inputs})!=31:
        raise ValueError("Incomplete artifact manifest")
    downloaded={};metadata=[]
    for item in inputs:
        meta=api(f"actions/artifacts/{item['id']}")
        if (meta["id"]!=item["id"] or meta["expired"] or
                meta["digest"]!="sha256:"+item["sha256"] or
                meta["workflow_run"]["id"]!=item["run"] or
                meta["workflow_run"]["head_sha"]!=item["commit"]):
            raise ValueError("Remote artifact identity differs")
        folder=a.cache/item["family"];folder.mkdir(exist_ok=True)
        name=(f"original-stage2-{item['key']}.zip" if item["family"]=="stage2" and item["key"]!="recovery"
              else "stage2-native-recovery-evidence.zip" if item["key"]=="recovery"
              else item["key"]+".zip")
        path=folder/name
        with path.open("wb") as fp:
            subprocess.run(["gh","api",f"/repos/{REPO}/actions/artifacts/{item['id']}/zip"],
                           stdout=fp,check=True,timeout=180)
        if sha(path)!=item["sha256"] or path.stat().st_size!=meta["size_in_bytes"]:
            raise ValueError("Downloaded ZIP bytes differ")
        downloaded[item["family"],item["key"]]=path
        metadata.append({**item,"bytes":path.stat().st_size,"expires_at":meta["expires_at"]})
    # Only this original evaluator preparation executes: it reads pinned archives
    # and exports Git objects. No candidate imports, compilation or model calls.
    build=a.cache/"build"
    command(["scripts/prepare_original_replay.py","--build-dir",build,
             "--author-tar",a.cache/"SPDZCoder.tar","--mp-archive",a.cache/"mp-spdz.tar.xz",
             "--mp-repo",a.cache/"mp-source"])
    baseline=build/"baseline"
    for item in inputs:
        if item["family"] in ("final","paired") and item["key"]!="summary":
            unpack(downloaded[item["family"],item["key"]],a.cache/(item["family"]+"-raw")/str(item["id"]))
    command(["scripts/summarize_original_replay.py","--root",a.cache/"final-raw","--output",a.output/"final-native"])
    final_rows=[json.loads(line) for line in (a.output/"final-native/outcomes.jsonl").read_text().splitlines()]
    # Close the old automated-verifier gap: reconstruct every final-stage
    # compiled input from authentic original candidate and native template.
    original_sources={}
    for file in (a.cache/"final-raw").rglob("outcomes.jsonl"):
        for row in [json.loads(l) for l in file.read_text().splitlines()]:
            split,task=row["task_id"].split("/")
            source=(f"data/stage_3_output/experiment-1-{split}.jsonl" if row["system"]=="spdzcoder"
                    else f"data/baseline_output/gpt4-1-{split}.jsonl")
            if source not in original_sources:
                records=[json.loads(l) for l in (baseline/source).read_text().splitlines() if l.strip()]
                original_sources[source]={r["test_name"]:r for r in records}
                if len(original_sources[source])!=len(records):raise ValueError("Duplicate author task")
            code=original_sources[source][task][f"response_{row['candidate_id']}"]
            template=(baseline/f"data/input_data/{row['task_id']}.mpc").read_text()
            if hashlib.sha256(code.encode()).hexdigest()!=row["source_sha256"]:
                raise ValueError("Original candidate text identity changed")
            for i in range(len(row["attempts"])):
                path=file.parent/row["log_path"]/f"attempt-{i}.mpc"
                if path.read_text()!=inserted_source(code,template):
                    raise ValueError("Original native compiled input differs from insertion")
    stage_zips=[v for (f,k),v in downloaded.items() if f=="stage2" and k!="recovery"]
    stage_audit=audit_stage2(stage_zips)
    secondary=audit_secondary(a.cache/"stage2")
    source_audit=audit_tar(a.cache/"SPDZCoder.tar",stage_zips)
    # Recount terminal exception types directly from the original final stderr.
    taxonomy=Counter()
    import re
    for path in stage_zips:
        with zipfile.ZipFile(path) as z:
            key=path.name[len("original-stage2-"):-4]
            for row in [json.loads(l) for l in z.read(key+"/outcomes.jsonl").splitlines()]:
                if row["compile_status"]=="FAIL":
                    err=z.read(key+"/"+row["log_path"]+f"/attempt-{len(row['attempts'])-1}.stderr.txt").decode()
                    lines=[l.strip() for l in err.splitlines() if re.match(r"^[\w.]+(?:Error|Exception):",l.strip())]
                    name=lines[-1].split(":",1)[0] if lines else "unclassified_terminal_stderr"
                    taxonomy[name]+=1
    if dict(taxonomy)!=TAXONOMY:raise ValueError("Raw compiler taxonomy differs; inspect stderr")
    command(["scripts/summarize_paired_replay.py","--root",a.cache/"paired-raw",
             "--baseline",baseline,"--output",a.output/"paired-native"])
    paired_audit=audit_paired(downloaded["paired","summary"],
        [v for (f,k),v in downloaded.items() if f=="paired" and k!="summary"])
    smoke,smoke_validation=verify_pair_run(ROOT/"research/evidence/2026-10-16/paired-smoke/paired-smoke",baseline)
    r8=verify(read(ROOT/FIRST),read(ROOT/SECOND),read(ROOT/DIFFICULTIES))
    r8["project_difficulty_index"]=verify_register(read(ROOT/"research/reproduction_difficulties.json"),ROOT)
    workflow_states={}
    for run,expected in ((38703569637,"success"),(39075744038,"failure"),(39080161119,"success"),(38989067493,"success")):
        state=api(f"actions/runs/{run}")
        if state["status"]!="completed" or state["conclusion"]!=expected:
            raise ValueError("Historical failure/recovery status was changed")
        workflow_states[str(run)]={k:state[k] for k in ("head_sha","run_attempt","status","conclusion")}
    result={"scope":"Independent re-audit of preserved original native data; no new native MPC or model execution",
        "research_commit":os.environ.get("GITHUB_SHA"),"workflow_run":os.environ.get("GITHUB_RUN_ID"),
        "raw_artifacts":metadata,"historical_workflows":workflow_states,
        "final_native_candidate_records":len(final_rows),"final_native_exact_source_insertion":len(final_rows),
        "final_native_attempts":sum(len(r["attempts"]) for r in final_rows),
        "stage2":stage_audit,"stage2_secondary":secondary,"stage2_source":source_audit,
        "stage2_raw_taxonomy":dict(taxonomy),"paired":paired_audit,
        "targeted_smoke":{"records":len(smoke),"validation":smoke_validation},
        "difficulty_documentation":r8,"new_model_calls":0,"new_native_executions":0,
        "historical_generation_reproduced":False,"genuine_no_refactoring_reproduced":False,
        "report_authorized":False}
    (a.output/"acceptance.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"source_insertion_records":len(final_rows),"stage2_records":secondary["candidate_count"],
        "paired_records":paired_audit["executions"],"smoke_records":len(smoke),
        "raw_artifacts":len(metadata),"new_model_calls":0,"new_native_executions":0}))
    # Compact machine-readable receipt is printed for remote review when no local
    # execution environment is available. It contains no token or private key.
    print("AUDIT_RECEIPT="+json.dumps(result,sort_keys=True))

if __name__=="__main__":main()
