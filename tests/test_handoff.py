import copy
import unittest

from scripts.check_handoff import validate_records, validate_gates


class HandoffGateTests(unittest.TestCase):
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
