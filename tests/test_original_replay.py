import unittest
from pathlib import Path
import tempfile
import subprocess

from scripts.replay_original import classify_attempt, reset_execution_artifacts
from scripts.prepare_original_replay import export_mp_sources


class ReplayOutcomeTests(unittest.TestCase):
    def test_nonzero_runtime_exit_is_not_hidden_by_author_acceptance(self):
        got = classify_attempt(1, False, True, True)
        self.assertEqual(got, {"compile_status": "PASS", "runtime_status": "FAIL",
                               "failure_class": "runtime_failure"})

    def test_compile_failure_never_implies_secure_execution(self):
        got = classify_attempt(1, False, False, False)
        self.assertEqual(got["compile_status"], "FAIL")
        self.assertEqual(got["runtime_status"], "NOT_RUN")

    def test_timeout_keeps_phase_information(self):
        got = classify_attempt(None, True, True, True)
        self.assertEqual(got["compile_status"], "PASS")
        self.assertEqual(got["runtime_status"], "TIMEOUT")
        self.assertEqual(got["failure_class"], "timeout")

    def test_runtime_success_is_separate_from_oracle_acceptance(self):
        got = classify_attempt(0, False, True, True)
        self.assertEqual(got["runtime_status"], "PASS")
        self.assertEqual(got["failure_class"], None)
        self.assertNotIn("oracle_status", got)

    def test_partial_schedule_is_not_successful_compilation(self):
        got = classify_attempt(1, False, True, False)
        self.assertEqual(got["compile_status"], "UNKNOWN")
        self.assertEqual(got["runtime_status"], "NOT_RUN")
        self.assertEqual(got["failure_class"], "incomplete_compilation_evidence")
        self.assertEqual(classify_attempt(-9, True, True, False)["compile_status"], "TIMEOUT")

    def test_later_empty_or_failed_candidate_cannot_inherit_earlier_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for folder in ("Programs", "logs"):
                (root / folder).mkdir()
                (root / folder / "earlier-success").write_text("old result")
            combined = root / "candidate.mpc"
            combined.write_text("earlier candidate")
            reset_execution_artifacts(root, combined)
            self.assertFalse(combined.exists())
            self.assertFalse((root / "Programs").exists())
            self.assertFalse((root / "logs").exists())


class CompilerSourceTests(unittest.TestCase):
    def test_export_uses_commit_bytes_and_excludes_untracked_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, target = root / "repo", root / "export"
            repo.mkdir()
            def git(*args):
                return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.DEVNULL)
            git("init")
            (repo / "Compiler").mkdir()
            (repo / "Compiler" / "tracked.py").write_text("original compiler bytes\n")
            (repo / "Scripts").mkdir()
            for name in ("compile-run.py", "mascot.sh", "run-common.sh", "setup-ssl.sh"):
                (repo / "Scripts" / name).write_text("original script\n")
            git("add", ".")
            git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", "fixture")
            commit = git("rev-parse", "HEAD").decode().strip()
            (repo / "Compiler" / "tracked.py").write_text("changed working tree\n")
            (repo / "Compiler" / "untracked.py").write_text("must not enter export\n")
            records = export_mp_sources(repo, target, commit)
            self.assertEqual((target / "Compiler" / "tracked.py").read_text(), "original compiler bytes\n")
            self.assertFalse((target / "Compiler" / "untracked.py").exists())
            self.assertEqual(len(records), 5)
            self.assertTrue(all(len(item["sha256"]) == 64 for item in records))
