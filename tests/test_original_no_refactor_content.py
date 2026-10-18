"""Test original author's content search safely using synthetic TAR bytes only."""
import io
import tarfile
import unittest
from scripts.audit_original_no_refactor_content import scan

def archive(entries):
    buf=io.BytesIO()
    with tarfile.open(fileobj=buf,mode="w") as tar:
        for filename,source in entries.items():
            raw=source.encode()
            info=tarfile.TarInfo("SPDZCoder/"+filename)
            info.size=len(raw)
            tar.addfile(info,io.BytesIO(raw))
    buf.seek(0)
    return buf

class OriginalAblationContentTests(unittest.TestCase):
    def test_recognizes_explicit_nonrefactor_metadata(self):
        with tarfile.open(fileobj=archive({"src/run.py":"# without refactoring branch\n","evaluation/results.txt":"ablation original saved\n"}),mode="r") as tar:
            result=scan(tar)
        self.assertEqual(result["explicit_marker_path_count"],2)
        self.assertEqual(result["scanned_files"],2)
        self.assertFalse(result["generation_executed"])

    def test_normal_refactoring_and_git_are_not_proof(self):
        with tarfile.open(fileobj=archive({"src/logic.py":"normal refactoring\n",".git/config":"without refactoring"}),mode="r") as tar:
            result=scan(tar)
        self.assertEqual(result["explicit_marker_path_count"],0)
        self.assertEqual(result["scanned_files"],1)
        self.assertEqual(result["skipped"]["git"],1)

    def test_secret_lines_not_copied(self):
        with tarfile.open(fileobj=archive({"src/config.py":"api_key='without refactoring'\n"}),mode="r") as tar:
            result=scan(tar)
        self.assertEqual(result["explicit_marker_path_count"],0)
if __name__=="__main__":
    unittest.main()
