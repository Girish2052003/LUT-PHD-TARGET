"""Fail-closed checks for independent author-TAR to executed native MPC source audit."""
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
from scripts.check_native_stage2_mpc_against_tar import audit,read_tar,sha

class NativeStage2AuthorTarTests(unittest.TestCase):
    def test_rejects_seven_missing_category_inputs(self):
        with self.assertRaisesRegex(ValueError, "Exactly seven"):
            audit(Path("/missing/SPDZCoder.tar"), [])

    def test_rejects_unpinned_archive_even_for_seven_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"SPDZCoder.tar"
            p.write_bytes(b"NOT OFFICIAL")
            with self.assertRaisesRegex(ValueError,"authentic"):
                audit(p,[Path(td)/f"{n}.zip" for n in range(7)])

    def test_rejects_unbounded_tar_members(self):
        with tarfile.open(fileobj=io.BytesIO(), mode="w") as tar:
            with self.assertRaises(KeyError):
                read_tar(tar,"data/stage_2_SPDZ_output/missing.jsonl")

    def test_known_hash(self):
        self.assertEqual(sha(b""),"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

if __name__=="__main__":
    unittest.main()
