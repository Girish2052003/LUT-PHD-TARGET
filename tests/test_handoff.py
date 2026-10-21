import copy
import hashlib
import unittest
from unittest.mock import patch, Mock

from scripts.check_handoff import validate_records, validate_gates, validate_exception_decisions, render


class HandoffGateTests(unittest.TestCase):
    def test_render_reflects_drafting_permission_without_granting_submission(self):
        progress = {"phases": [], "report_authorized": True}
        text = render(progress, {"requirements": []})["README.md"]
        marker = text.split("<!-- PHASE_STATUS:BEGIN -->")[1].split("<!-- PHASE_STATUS:END -->")[0]
        self.assertIn("Final report drafting is authorized", marker)
        self.assertIn("External submission is not authorized", marker)
        self.assertNotIn("writing remains locked", marker)
        progress["report_authorized"] = False
        text = render(progress, {"requirements": []})["README.md"]
        self.assertIn("Final report writing remains locked", text)

    def setUp(self):
        self.phase = {
            "id": "A", "status": "PASS", "evidence_paths": ["HANDOFF.md"],
            "evidence_commit": "a" * 40,
            "verification": dict.fromkeys(
                ("implemented", "executed", "evidence_preserved", "independently_checked"), True),
        }

    def test_pass_requires_execution_and_independent_check(self):
        for key in ("implemented", "executed", "evidence_preserved", "independently_checked"):
            phase = copy.deepcopy(self.phase)
            phase["verification"][key] = False
            with self.assertRaisesRegex(ValueError, "PASS requires"):
                validate_records([phase], "verification", "evidence_commit")

    def test_pass_requires_evidence_and_exact_commit(self):
        for key, value in (("evidence_paths", []), ("evidence_commit", "main")):
            phase = copy.deepcopy(self.phase)
            phase[key] = value
            with self.assertRaises(ValueError):
                validate_records([phase], "verification", "evidence_commit")

    def test_duplicate_and_unknown_status_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_records([self.phase, self.phase], "verification", "evidence_commit")
        self.phase["status"] = "DONE_ENOUGH"
        with self.assertRaisesRegex(ValueError, "status"):
            validate_records([self.phase], "verification", "evidence_commit")

    def test_completed_phase_cannot_skip_unfinished_dependency(self):
        phases = [{"id": "D", "status": "NOT_STARTED", "dependencies": []},
                  {"id": "E", "status": "PASS", "dependencies": ["D"]}]
        with self.assertRaisesRegex(ValueError, "unfinished"):
            validate_gates(phases, [{"id": "R9", "status": "BLOCKED"}], False, None)

    def test_passed_requirement_requires_its_phases(self):
        phases = [{"id": "D", "status": "IN_PROGRESS", "dependencies": []}]
        requirements = [{"id": "R5", "status": "PASS", "phase_ids": ["D"]},
                        {"id": "R9", "status": "BLOCKED"}]
        with self.assertRaisesRegex(ValueError, "unfinished"):
            validate_gates(phases, requirements, False, None)

    def test_report_authorization_requires_practical_readiness(self):
        with self.assertRaisesRegex(ValueError, "readiness"):
            validate_gates([], [{"id": "R9", "status": "BLOCKED"}], True, "placeholder")

    def test_report_phase_cannot_pass_when_r9_is_blocked(self):
        phases = [{"id": "REPORT", "status": "PASS", "completion_scope": "Complete"}]
        requirements = [{"id": "R9", "status": "BLOCKED"}]
        with self.assertRaisesRegex(ValueError, "contradicts R9"):
            validate_gates(phases, requirements, False, None)

    def test_report_scope_cannot_claim_all_while_r2_remains_open(self):
        phases = [{"id": "REPORT", "status": "BLOCKED",
                   "completion_scope": "Practical R1–R8 accepted; report locked"}]
        requirements = [
            {"id": f"R{i}", "status": "IN_PROGRESS" if i == 2 else "PASS"}
            for i in range(1, 9)
        ] + [{"id": "R9", "status": "BLOCKED"}]
        with self.assertRaisesRegex(ValueError, "contradicts unfinished"):
            validate_gates(phases, requirements, False, None)
        phases[0]["completion_scope"] = "R2 still IN_PROGRESS; final report locked"
        validate_gates(phases, requirements, False, None)

    def _pending(self, name="HISTORICAL_LLM", targets=None):
        return {
            "id": name, "status": "PENDING",
            "requirement_ids": targets or ["R2", "R3", "R8"],
            "evidence_paths": [],
            "authorization_record": None,
            "authorization_sha256": None,
            "decision_quote": None,
            "decision_date": None,
            "limitations": "Not independently reproduced",
        }

    def _approved(self, record):
        text = b"Explicitly accepted by Girish for this fictional unit-test fixture."
        approved = copy.deepcopy(record)
        approved.update({
            "status": "ACCEPTED",
            "authorization_record": "research/requirements/test-decision.txt",
            "authorization_sha256": hashlib.sha256(text).hexdigest(),
            "decision_quote": "Explicitly accepted by Girish for this fictional unit-test fixture.",
            "decision_date": "2026-10-18",
            "authorization_scope": "REPORT_READINESS",
        })
        return approved, text

    def test_research_merge_permission_cannot_accept_report_scope(self):
        item, fake_bytes = self._approved(self._pending(targets=["R2"]))
        item["authorization_scope"] = "RESEARCH_INTEGRATION"
        req = [{"id": "R2", "status": "IN_PROGRESS", "phase_ids": [],
                "required_exception_ids": ["HISTORICAL_LLM"]},
               {"id": "R9", "status": "PASS", "phase_ids": []}]
        with patch("scripts.check_handoff.safe_file",
                   return_value=Mock(read_bytes=lambda: fake_bytes)):
            with self.assertRaisesRegex(ValueError, "scoped irreproducibility"):
                validate_gates([], req, False, None, [item])
            req[-1]["status"] = "BLOCKED"
            validate_gates([], req, False, None, [item])

    def test_accepted_decision_requires_a_known_authorization_scope(self):
        for scope in (None, "ALL_ACTIONS"):
            item, fake_bytes = self._approved(self._pending(targets=["R2"]))
            item["authorization_scope"] = scope
            with patch("scripts.check_handoff.safe_file",
                       return_value=Mock(read_bytes=lambda: fake_bytes)):
                with self.assertRaisesRegex(ValueError, "authorization scope"):
                    validate_exception_decisions([item], [{"id": "R2"}])

    def test_pending_exception_cannot_claim_approval(self):
        invalid = self._pending()
        invalid["decision_quote"] = "I approve"
        with self.assertRaisesRegex(ValueError, "impersonate"):
            validate_exception_decisions([invalid], [{"id": "R2"}, {"id": "R3"}, {"id": "R8"}])

    def test_missing_or_changed_exception_approval_rejected(self):
        item, fake_bytes = self._approved(self._pending())
        with self.assertRaisesRegex(ValueError, "Missing"):
            validate_exception_decisions([item], [{"id": "R2"}, {"id": "R3"}, {"id": "R8"}])
        with patch("scripts.check_handoff.safe_file",
                   return_value=Mock(read_bytes=lambda: b"not the approved message")):
            with self.assertRaisesRegex(ValueError, "Changed"):
                validate_exception_decisions([item], [{"id": "R2"}, {"id": "R3"}, {"id": "R8"}])
        with patch("scripts.check_handoff.safe_file",
                   return_value=Mock(read_bytes=lambda: fake_bytes)):
            item["decision_quote"] = "Never said that"
            with self.assertRaisesRegex(ValueError, "quote absent"):
                validate_exception_decisions([item], [{"id": "R2"}, {"id": "R3"}, {"id": "R8"}])

    def test_report_readiness_requires_both_scoped_exceptions(self):
        phases = [{"id": "G", "status": "PASS", "dependencies": []},
                  {"id": "REPORT", "status": "BLOCKED", "dependencies": ["G"]}]
        req = [{"id": "R2", "status": "IN_PROGRESS", "phase_ids": [],
                "required_exception_ids": ["HISTORICAL_LLM"]},
               {"id": "R3", "status": "IN_PROGRESS", "phase_ids": [],
                "required_exception_ids": ["HISTORICAL_LLM", "NO_REFACTORING"]},
               {"id": "R8", "status": "IN_PROGRESS", "phase_ids": [],
                "required_exception_ids": ["HISTORICAL_LLM"]},
               {"id": "R9", "status": "PASS", "phase_ids": ["G"]}]
        model, fake_bytes = self._approved(self._pending())
        ablation, _ = self._approved(self._pending("NO_REFACTORING", ["R3"]))
        with patch("scripts.check_handoff.safe_file",
                   return_value=Mock(read_bytes=lambda: fake_bytes)):
            with self.assertRaisesRegex(ValueError, "scoped irreproducibility"):
                validate_gates(phases, req, False, None, [model])
            # Formal readiness is permitted ONLY for specifically approved
            # exceptions; REPORT writing itself stays BLOCKED.
            validate_gates(phases, req, False, None, [model, ablation])

    def test_exception_cannot_cover_unrelated_unfinished_requirement(self):
        phases = [{"id": "G", "status": "PASS", "dependencies": []}]
        req = [{"id": "R5", "status": "IN_PROGRESS", "phase_ids": []},
               {"id": "R9", "status": "PASS", "phase_ids": ["G"]}]
        with self.assertRaisesRegex(ValueError, "R5 PASS"):
            validate_gates(phases, req, False, None, [])

    def test_r9_readiness_can_be_independent_from_report_phase(self):
        phases = [{"id": "G", "status": "PASS", "dependencies": []},
                  {"id": "REPORT", "status": "BLOCKED", "dependencies": ["G"]}]
        req = [{"id": "R1", "status": "PASS", "phase_ids": ["G"]},
               {"id": "R9", "status": "PASS", "phase_ids": ["G"]}]
        validate_gates(phases, req, False, None, [])
