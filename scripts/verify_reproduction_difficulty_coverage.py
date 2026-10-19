#!/usr/bin/env python3
"""Check exact original-source R8 difficulty accounting; not a model replay.

All 626 genuine stage-2 saved author program candidates, 644 native attempts,
compiler/runtime/oracle rejects and the FAILED aggregator are retained.
Only repository JSON receipts are read; no network, native code or model calls.
"""
from __future__ import annotations
from collections import Counter
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIRST="research/evidence/2026-10-18/stage2-original-full-independent-acceptance.json"
SECOND="research/evidence/2026-10-18/phase-g-stage2-raw-secondary-independent-audit.json"
DIFFICULTIES="research/evidence/2026-10-18/stage2-native-reproduction-difficulties.json"

def verify(stage, secondary, issues):
    def same(*x):
        if len(set(x))!=1:
            raise ValueError("Conflicting independently reported original-source values: "+repr(x))
        return x[0]
    n=same(stage["candidate_executions"],secondary["candidate_record_count"],issues["source_candidate_count"])
    tasks=same(stage["original_task_count"],secondary["task_count"])
    attempts=same(stage["raw_native_attempts"],secondary["native_attempt_count"],issues["raw_native_attempt_count"])
    if n!=626 or tasks!=313 or attempts!=644:
        raise ValueError("Original task/candidate/attempt coverage incomplete")
    if stage["original_source_archive_sha256"]!=secondary.get("original_source_archive_sha256",stage["original_source_archive_sha256"]):
        raise ValueError("Source archive mismatch")
    if not stage["original_evaluator_unchanged"] if "original_evaluator_unchanged" in stage else False:
        raise ValueError("Source author oracle not unchanged")
    comp=same(stage["compiler_statuses"]["FAIL"],secondary["native_compilation"]["FAIL"],issues["original_native_candidate_status_totals"]["compile_fail"])
    compiled=same(stage["compiler_statuses"]["PASS"],secondary["native_compilation"]["PASS"],issues["original_native_candidate_status_totals"]["runtime_completed"])
    rejected=same(stage["native_oracle_rejects_after_runtime"],secondary["failure_classes"]["oracle_reject"],issues["original_native_candidate_status_totals"]["original_oracle_reject_after_runtime"])
    accepted=same(stage["original_native_results"]["candidates_accepted"],secondary["original_oracle"]["ACCEPT"],issues["original_native_candidate_status_totals"]["original_oracle_accept"])
    failed=stage["original_native_results"]["candidates_rejected"]
    if (comp,compiled,rejected,accepted,failed)!=(147,479,34,445,181):
        raise ValueError("Original failure matrix changed")
    if comp+compiled!=n or compiled!=rejected+accepted or comp+rejected!=failed:
        raise ValueError("Failure categories do not partition original candidates")
    if sum(issues["compile_terminal_exception_types"].values())!=comp:
        raise ValueError("Compiler exception inventory incomplete")
    if sum(v["compile_fail"] for v in issues["failure_counts_by_category"].values())!=comp or sum(v["native_oracle_reject_after_runtime"] for v in issues["failure_counts_by_category"].values())!=rejected:
        raise ValueError("Seven-category failure matrix mismatch")
    if len(issues["failure_counts_by_category"])!=7:
        raise ValueError("Missing category")
    retries=same(issues["original_native_candidate_status_totals"]["retrying_candidates"],secondary["retrying_candidates"])
    timeouts=same(issues["original_native_candidate_status_totals"]["timed_out_attempts"],secondary["timed_out_attempts"])
    if retries!=14 or timeouts!=18 or attempts<=n:
        raise ValueError("Retries/timeouts not accounted for")
    if stage["accepted_without_completed_runtime"]!=0:
        raise ValueError("Invalid accepted program never completed runtime")
    if len(stage["archived_vs_fresh_disagreements"])!=3 or len(secondary["saved_vs_fresh_disagreements"])!=3:
        raise ValueError("Original saved/fresh disagreements hidden")
    for metric,expected in (("first",229),("second",216),("union",262)):
        if stage["original_native_results"][metric]!=expected or secondary["fresh_"+metric]!=expected:
            raise ValueError("Original fresh success counts changed")
    if stage["original_native_run_conclusion"]!="failure_due_to_aggregate_artifact_path_only" or secondary["original_native_job_result"]!="all_seven_categories_success_original_aggregate_failed_due_to_artifact_path":
        raise ValueError("Original failed aggregator falsely promoted to success")
    if stage["artifact_only_recovery_conclusion"]!="success" or secondary["recovery_workflow_conclusion"]!="success_zero_native_candidate_reruns":
        raise ValueError("Artifact-only recovery changed")
    if not issues["reported_reproduction_difficulty"] or len(issues["reported_reproduction_difficulty"])<5:
        raise ValueError("Missing non-native-model reproduction difficulties")
    return {
        "scope":"R8 honest documentation: all enumerated original stage-2 626 candidates and 644 native attempts; source identity, original oracle limits, actual red aggregator + separate green artifact recovery",
        "original_author_archive_sha256":stage["original_source_archive_sha256"],
        "original_native_run_id":stage["original_native_run_id"],
        "original_native_run_conclusion":"FAIL: aggregator artifact prefix, despite seven category jobs SUCCESS",
        "artifact_only_recovery_run_id":stage["artifact_only_recovery_run_id"],
        "artifact_only_recovery_conclusion":"SUCCESS: artifact-only recovery; no candidate reruns",
        "tasks":tasks, "candidates":n,"attempts":attempts,
        "compiler_failures":comp,"native_runtime_completed":compiled,
        "native_oracle_rejections_after_runtime":rejected,
        "original_oracle_acceptances":accepted,
        "nonaccepted":failed,
        "retrying_candidates":retries,"timed_out_attempts":timeouts,
        "archived_fresh_disagreement_count":3,
        "source_failure_taxonomy":issues["compile_terminal_exception_types"],
        "category_failure_taxonomy":issues["failure_counts_by_category"],
        "other_documented_difficulties":issues["reported_reproduction_difficulty"],
        "historical_GPT4_Azure_model_stage_reproduced":False,
        "paper_original_no_refactoring_ablation_reproduced":False,
        "original_author_model_calls_this_audit":0,
        "native_MPC_executions_this_audit":0,
        "professor_report_authorized":False,
        "limits":"This proves complete categorization for the enumerated 626 saved stage-2 candidates only, NOT every run in the whole project or underlying mathematical correctness; missing original model calls/ablation remain NOT REPRODUCED."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stage2",type=Path,default=ROOT/FIRST)
    p.add_argument("--secondary",type=Path,default=ROOT/SECOND)
    p.add_argument("--difficulties",type=Path,default=ROOT/DIFFICULTIES)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    def load(path):return json.loads(path.read_text())
    record=verify(load(a.stage2),load(a.secondary),load(a.difficulties))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:record[k] for k in
        ("tasks","candidates","attempts","compiler_failures","native_oracle_rejections_after_runtime","original_oracle_acceptances","retrying_candidates","timed_out_attempts","archived_fresh_disagreement_count")},indent=2))

if __name__=="__main__":main()
