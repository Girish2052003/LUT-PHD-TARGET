#!/usr/bin/env python3
"""Reconcile original-source R8 receipts and the project difficulty index.

All 626 genuine stage-2 saved author program candidates, 644 native attempts,
compiler/runtime/oracle rejects and the FAILED aggregator are retained.
Only repository JSON receipts are read; no network, native code or model calls.
"""
from __future__ import annotations
import hashlib
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIRST="research/evidence/2026-10-18/stage2-original-full-independent-acceptance.json"
SECOND="research/evidence/2026-10-18/phase-g-stage2-raw-secondary-independent-audit.json"
DIFFICULTIES="research/evidence/2026-10-18/stage2-native-reproduction-difficulties.json"


ARCHIVE_SHA = "a8ea14150dc1d4ddf53eb4ead450d88139d09b680683f673029877ce0c6e00ac"
CATEGORIES = {"array_test":43,"loop_test":97,"branch_test":34,"math_test":38,
              "numpy_operation_test":32,"numpy_ufunc_test":34,"syntax_test":35}
SOURCE_ARTIFACTS = {"array_test":12117009220,"loop_test":12118480819,
    "branch_test":12117428647,"math_test":12118110941,"numpy_operation_test":12116744908,
    "numpy_ufunc_test":12118278472,"syntax_test":12117610306}
TAXONOMY = {"AttributeError":56,"ImportError":28,"TypeError":22,
    "Compiler.exceptions.CompilerError":18,"NameError":17,"IndexError":2,
    "SyntaxError":1,"ValueError":1,"unclassified_terminal_stderr":2}
DISAGREEMENTS = {("branch_test/choice_of_the_knight",1,False,True),
    ("math_test/pi_to_the_x",1,False,True),("math_test/spring_rocket",1,False,True)}
REQUIRED_FAMILIES = {
    "initial_artifact_discovery","environment_and_confinement",
    "final_native_download_and_recovery","final_native_failures","stage2_native_failures",
    "stage2_aggregation_recovery","native_oracle_limits","source_and_trace_discrepancies",
    "patch_scope_and_costs","paired_control_variability","historical_generation",
    "genuine_no_refactoring","readiness_accounting_repair",
}

def verify_register(register, root):
    """Validate indexed difficulty coverage and evidence bytes, not prose truth."""
    rows=register["entries"]
    ids=[r["id"] for r in rows]
    if register["schema_version"]!=1 or set(ids)!=REQUIRED_FAMILIES or len(ids)!=len(set(ids)):
        raise ValueError("Incomplete or duplicated project difficulty family")
    evidence={}
    for row in rows:
        if row["status"] not in {"RESOLVED","RESOLVED_WITH_SCOPE","DOCUMENTED_LIMITATION","BLOCKED","IN_PROGRESS"}:
            raise ValueError("Invalid difficulty status")
        if not all(isinstance(row[k],str) and row[k].strip() for k in ("problem","resolution")):
            raise ValueError("Missing problem/cause or resolution/blocker")
        if any(type(n) is not int or n<=0 for n in row["runs"]) or len(row["runs"])!=len(set(row["runs"])):
            raise ValueError("Malformed run identity")
        if not row["evidence_paths"]:
            raise ValueError("Unlinked reproduction difficulty")
        for relative in row["evidence_paths"]:
            path=(root/relative).resolve()
            if not path.is_relative_to(root.resolve()) or not path.is_file():
                raise ValueError("Missing or unsafe difficulty evidence: "+relative)
            evidence[relative]=hashlib.sha256(path.read_bytes()).hexdigest()
    for name in ("historical_generation","genuine_no_refactoring"):
        row=next(r for r in rows if r["id"]==name)
        if row["status"]!="BLOCKED" or "NOT REPRODUCED" not in row["resolution"]:
            raise ValueError("Unreproduced historical experiment was hidden")
    return {"families":len(rows),"evidence_sha256":dict(sorted(evidence.items())),
            "scope":"Index coverage and linked file integrity; scientific truth requires raw audit and review."}


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
    if stage["original_source_archive_sha256"]!=ARCHIVE_SHA:
        raise ValueError("Source archive mismatch")
    if (stage["original_native_run_id"]!=39075744038 or secondary["original_native_run_id"]!=39075744038
            or issues["source_run"]!=39075744038
            or stage["artifact_only_recovery_run_id"]!=39080161119
            or secondary["artifact_only_recovery_run_id"]!=39080161119
            or stage["original_native_run_commit"]!="1e3c95d5357cd8b913a11916e562b6de7d633ccb"
            or stage["artifact_only_recovery_commit"]!="58197ee4b93c70a04cc19f4c15a319eba3b4f4d8"):
        raise ValueError("Original source/recovery run identity mismatch")
    if (stage["source_run_artifact_ids"]!=SOURCE_ARTIFACTS
            or secondary["original_source_zip_ids"]!=SOURCE_ARTIFACTS
            or stage["recovery_artifact_id"]!=12118194181
            or secondary["recovery_zip_artifact_id"]!=12118194181
            or stage["recovery_artifact_zip_sha256"]!="4ba5dc8c0470c1cf02633bb4722a204558b3c3d591a863c10cb5e28c572ba12c"
            or stage["recovery_artifact_zip_sha256"]!=secondary["recovery_zip_sha256"]):
        raise ValueError("Original artifact provenance mismatch")
    # The actual receipt schema records this as a source-execution check, not a
    # Boolean field. This validates its documented assertion; raw evidence is
    # independently rechecked by the final-evidence workflow.
    if "Original source, original 2-party MASCOT evaluator, original published test oracle unchanged" not in stage["source_execution_checks"]:
        raise ValueError("Unchanged-original-oracle evidence assertion missing")
    if (stage["runtime_statuses"]!={"PASS":479,"NOT_RUN":147}
            or secondary["native_runtime"]!=stage["runtime_statuses"]):
        raise ValueError("Original runtime partition mismatch")
    comp=same(stage["compiler_statuses"]["FAIL"],secondary["native_compilation"]["FAIL"],issues["original_native_candidate_status_totals"]["compile_fail"])
    compiled=same(stage["compiler_statuses"]["PASS"],secondary["native_compilation"]["PASS"],issues["original_native_candidate_status_totals"]["runtime_completed"])
    rejected=same(stage["native_oracle_rejects_after_runtime"],secondary["failure_classes"]["oracle_reject"],issues["original_native_candidate_status_totals"]["original_oracle_reject_after_runtime"])
    accepted=same(stage["original_native_results"]["candidates_accepted"],secondary["original_oracle"]["ACCEPT"],issues["original_native_candidate_status_totals"]["original_oracle_accept"])
    failed=stage["original_native_results"]["candidates_rejected"]
    if (comp,compiled,rejected,accepted,failed)!=(147,479,34,445,181):
        raise ValueError("Original failure matrix changed")
    if comp+compiled!=n or compiled!=rejected+accepted or comp+rejected!=failed:
        raise ValueError("Failure categories do not partition original candidates")
    if issues["compile_terminal_exception_types"]!=TAXONOMY:
        raise ValueError("Compiler exception identities or unclassified cases changed")
    if sum(issues["compile_terminal_exception_types"].values())!=comp:
        raise ValueError("Compiler exception inventory incomplete")
    if sum(v["compile_fail"] for v in issues["failure_counts_by_category"].values())!=comp or sum(v["native_oracle_reject_after_runtime"] for v in issues["failure_counts_by_category"].values())!=rejected:
        raise ValueError("Seven-category failure matrix mismatch")
    if set(issues["failure_counts_by_category"])!=set(CATEGORIES) or set(secondary["category_metrics"])!=set(CATEGORIES):
        raise ValueError("Missing or foreign category")
    for category,n_tasks in CATEGORIES.items():
        stats=secondary["category_metrics"][category]
        failures=issues["failure_counts_by_category"][category]
        if (stats["tasks"]!=n_tasks or stats["candidates"]!=2*n_tasks
                or failures["compile_fail"]!=stats["compiler_failures"]
                or failures["native_oracle_reject_after_runtime"]!=
                   2*n_tasks-stats["compiler_failures"]-stats["first"]-stats["second"]):
            raise ValueError("Category failure partition differs from independent audit")
    retries=same(issues["original_native_candidate_status_totals"]["retrying_candidates"],secondary["retrying_candidates"])
    timeouts=same(issues["original_native_candidate_status_totals"]["timed_out_attempts"],secondary["timed_out_attempts"])
    if retries!=14 or timeouts!=18 or attempts<=n:
        raise ValueError("Retries/timeouts not accounted for")
    if stage["accepted_without_completed_runtime"]!=0:
        raise ValueError("Invalid accepted program never completed runtime")
    for rows in (stage["archived_vs_fresh_disagreements"],secondary["saved_vs_fresh_disagreements"]):
        if (len(rows)!=3 or any(type(r["candidate_id"]) is not int or
                type(r["saved"]) is not bool or type(r["fresh"]) is not bool for r in rows)
                or {(r["task_id"],r["candidate_id"],r["saved"],r["fresh"]) for r in rows}!=DISAGREEMENTS):
            raise ValueError("Original saved/fresh disagreement identities changed")
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
        "report_authorization_granted_by_this_audit":False,
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
    record["project_difficulty_index"]=verify_register(load(ROOT/"research/reproduction_difficulties.json"),ROOT)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:record[k] for k in
        ("tasks","candidates","attempts","compiler_failures","native_oracle_rejections_after_runtime","original_oracle_acceptances","retrying_candidates","timed_out_attempts","archived_fresh_disagreement_count")},indent=2))

if __name__=="__main__":main()
