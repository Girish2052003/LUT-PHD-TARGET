"""Pure inert Git loose-object archaeology test, no Git execution."""
import hashlib
import io
import tarfile
import unittest
import zlib
from scripts.audit_author_embedded_git_history import scan

def payload(artifacts):
    buffer=io.BytesIO()
    with tarfile.open(fileobj=buffer,mode="w") as tar:
        for name,raw in artifacts.items():
            desc=tarfile.TarInfo("SPDZCoder/.git/"+name)
            desc.size=len(raw)
            tar.addfile(desc,io.BytesIO(raw))
    buffer.seek(0)
    return buffer

def git_obj(kind,raw):
    content=(kind+" "+str(len(raw))).encode()+b"\0"+raw
    digest=hashlib.sha1(content).hexdigest()
    return digest,"objects/"+digest[:2]+"/"+digest[2:],zlib.compress(content)

class EmbeddedGitScannerTests(unittest.TestCase):
    def test_detects_hidden_ablation_blob_and_commit_history_path(self):
        blob_id,blob_path,blob_comp=git_obj("blob",b"# without refactoring variant\n")
        entry=b"100644 no_refactoring.py\0"+bytes.fromhex(blob_id)
        tree_id,tree_path,tree_comp=git_obj("tree",entry)
        commit_id,commit_path,commit_comp=git_obj("commit",("tree "+tree_id+"\nauthor A <a@b> 0 +0000\n\ncommit\n").encode())
        with tarfile.open(fileobj=payload({blob_path:blob_comp,tree_path:tree_comp,commit_path:commit_comp}),mode="r") as tar:
            result=scan(tar)
        self.assertEqual(result["blobs_with_explicit_ablation_markers"],1)
        self.assertIn("no_refactoring.py",result["tree_paths_matching_refactor_or_ablation"])
        self.assertTrue(result["history_complete_with_loose_objects"])

    def test_packfile_fails_open_to_unknown_not_historical_absence(self):
        with tarfile.open(fileobj=payload({"objects/pack/x.pack":b"PACKbad"}),mode="r") as tar:
            result=scan(tar)
        self.assertEqual(len(result["embedded_git_packfiles"]),1)
        self.assertFalse(result["history_complete_with_loose_objects"])
if __name__=="__main__":
    unittest.main()
