#!/usr/bin/env python3
"""Check durable handoff evidence and render status tables; no network required.

This enforces record consistency, not scientific correctness. Independent review
must still examine whether each narrow completion claim is justified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"NOT_STARTED", "IN_PROGRESS", "BLOCKED", "PASS"}
PREDICATES = ("implemented", "executed", "evidence_preserved", "independently_checked")
BEGIN = "<!-- PHASE_STATUS:BEGIN -->"
END = "<!-- PHASE_STATUS:END -->"


def validate_records(records, checks_key, commit_key):
    seen = set()
    for record in records:
        name = record["id"]
        if name in seen:
            raise ValueError(f"Duplicate identifier: {name}")
        seen.add(name)
        if record["status"] not in STATUSES:
            raise ValueError(f"Unknown status for {name}")
        if record["status"] == "PASS":
            if not all(record.get(checks_key, {}).get(k) is True for k in PREDICATES):
                raise ValueError(f"{name}: PASS requires all four completion predicates")
            if not record.get("evidence_paths"):
                raise ValueError(f"{name}: PASS requires evidence paths")
            if not re.fullmatch(r"[a-f0-9]{40}", record.get(commit_key) or ""):
                raise ValueError(f"{name}: PASS requires an exact evidence commit")


def safe_file(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f"Missing or non-repository evidence: {relative}")
    return path


def validate_gates(phases, requirements, report_authorized, authorization_record):
    phase_status = {p["id"]: p["status"] for p in phases}
    for record in phases + requirements:
        if record["status"] != "PASS":
            continue
        dependencies = record.get("dependencies", record.get("phase_ids", []))
        unfinished = [name for name in dependencies if phase_status.get(name) != "PASS"]
        if unfinished:
            raise ValueError(f"{record['id']}: unfinished prerequisite phases: {unfinished}")
    r9 = next(r for r in requirements if r["id"] == "R9")
    if r9["status"] == "PASS" and any(r["status"] != "PASS" for r in requirements if r["id"] != "R9"):
        raise ValueError("Report readiness requires R1–R8 PASS; accepted exceptions need explicit ledger support")
    if report_authorized:
        if r9["status"] != "PASS":
            raise ValueError("Report authorization requires practical readiness")
        if not authorization_record:
            raise ValueError("Report authorization requires a recorded explicit user instruction")
        safe_file(authorization_record)


def load_and_check():
    progress = json.loads((ROOT / "research/progress.json").read_text())
    ledger = json.loads((ROOT / "research/requirements/assignment_traceability.yaml").read_text())
    phases, requirements = progress["phases"], ledger["requirements"]
    validate_records(phases, "verification", "evidence_commit")
    validate_records(requirements, "completion", "exact_evidence_commit")
    if {r["id"] for r in requirements} != {f"R{i}" for i in range(1, 10)}:
        raise ValueError("Requirement IDs must be exactly R1 through R9")
    phase_ids = {p["id"] for p in phases}
    if progress["resume_phase"] not in phase_ids:
        raise ValueError("Unknown resume phase")
    for record in phases + requirements:
        for path in record["evidence_paths"]:
            safe_file(path)
        for dependency in record.get("dependencies", record.get("phase_ids", [])):
            if dependency not in phase_ids:
                raise ValueError(f"Unknown phase reference: {dependency}")
    for receipt_path in sorted((ROOT / "research/evidence").rglob("receipt.json")):
        receipt = json.loads(receipt_path.read_text())
        for item in receipt["files"]:
            raw = safe_file(item["path"]).read_bytes()
            if len(raw) != item["bytes"] or hashlib.sha256(raw).hexdigest() != item["sha256"]:
                raise ValueError(f"Preserved evidence changed: {item['path']}")
    validate_gates(phases, requirements, progress["report_authorized"], progress.get("report_authorization_record"))
    return progress, ledger


def render(progress, ledger):
    rows = [BEGIN, "", "Read [HANDOFF.md](HANDOFF.md) before continuing. **PASS is limited to the scope shown**;",
            "it does not mean the whole assignment is finished.", "",
            "| Phase | Status | Completion scope |", "|---|---|---|"]
    for p in progress["phases"]:
        rows.append(f"| {p['id']} — {p['title']} | **{p['status']}** | {p['completion_scope']} |")
    rows.extend(["", "Machine-readable state: [research/progress.json](research/progress.json).",
                 "Requirement gates: [R1–R9 ledger](research/requirements/assignment_traceability.md).",
                 "Final report writing remains locked until practical acceptance and explicit authorization.", "", END])
    block = "\n".join(rows)
    readme = (ROOT / "README.md").read_text()
    if BEGIN in readme and END in readme:
        readme = readme[:readme.index(BEGIN)] + block + readme[readme.index(END) + len(END):]
    else:
        heading, remainder = readme.split("\n", 1)
        readme = heading + "\n\n" + block + "\n" + remainder
    lines = ["# Assignment requirements and evidence", "",
             "Generated from `assignment_traceability.yaml` by `scripts/check_handoff.py --render`.",
             "These are practical acceptance gates. Historical milestones do not replace original-system evidence.", "",
             "| ID | Requirement | Status | Phases |", "|---|---|---|---|"]
    for r in ledger["requirements"]:
        lines.append(f"| {r['id']} | {r['title']} | **{r['status']}** | {', '.join(r['phase_ids'])} |")
    for r in ledger["requirements"]:
        lines += ["", f"## {r['id']} — {r['title']}", "", "> " + r["source_sentence"], ""]
        for key in ("scientific_interpretation", "implementation_obligation", "experimental_obligation",
                    "expected_outputs", "acceptance_criteria", "known_limitations", "verification_reviewer"):
            lines.append(f"- **{key.replace('_', ' ').capitalize()}:** {r[key]}")
        lines += [f"- **Evidence:** {', '.join('`'+p+'`' for p in r['evidence_paths']) or 'Pending'}",
                  f"- **Evidence commit:** {r['exact_evidence_commit'] or 'Pending'}",
                  f"- **Workflow identifiers:** {', '.join(r['test_workflow_identifiers']) or 'Pending'}"]
    return {"README.md": readme, "research/requirements/assignment_traceability.md": "\n".join(lines) + "\n"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true", help="refresh generated Markdown from validated records")
    args = parser.parse_args()
    progress, ledger = load_and_check()
    for relative, content in render(progress, ledger).items():
        dest = ROOT / relative
        if args.render:
            dest.write_text(content)
        elif not dest.exists() or dest.read_text() != content:
            raise ValueError(f"Stale generated marker: {relative}; run with --render")
    print(f"Handoff consistent: {len(progress['phases'])} phases, 9 requirements; evidence hashes verified.")


if __name__ == "__main__":
    main()
