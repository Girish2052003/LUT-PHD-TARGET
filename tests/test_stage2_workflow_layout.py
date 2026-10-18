"""Prevent recurrence of the documented original stage-2 aggregation-only failure.

No Docker, native MPC execution, model calls, or GitHub token is needed.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Stage2ArtifactLayoutTests(unittest.TestCase):
    def test_native_download_aggregation_uses_real_artifact_root(self):
        workflow = (ROOT / ".github/workflows/original-stage2-mascot.yml").read_text()
        self.assertIn("merge-multiple: true", workflow)
        self.assertIn("path: results/stage2-full-artifacts", workflow)
        self.assertIn("--root results/stage2-full-artifacts \\", workflow)
        self.assertNotIn("--root results/stage2-full-artifacts/stage2-full", workflow)

    def test_recovery_stays_evidence_only_and_pinned(self):
        workflow = (ROOT / ".github/workflows/stage2-artifact-aggregation.yml").read_text()
        self.assertIn("run-id: 39075744038", workflow)
        self.assertIn("--root results/stage2-artifacts \\", workflow)
        self.assertIn("All seven original run ZIP source views rebuilt without rerunning candidates", workflow)


if __name__ == "__main__":
    unittest.main()
