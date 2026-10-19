"""No-network behavior regression tests for companion README evidence comparison."""
import io
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from hashlib import md5, sha256

from scripts import audit_zenodo_companion_readme as scan


class ZenodoCompanionTests(unittest.TestCase):
    @staticmethod
    def make_tar(readme):
        file=io.BytesIO()
        with tarfile.open(fileobj=file,mode="w") as tar:
            raw=readme.encode()
            desc=tarfile.TarInfo("SPDZCoder/README.md")
            desc.size=len(raw)
            tar.addfile(desc,io.BytesIO(raw))
        return file.getvalue()

    def test_identical_readme_does_not_claim_missing_experiment(self):
        ext=b"Original source evaluation and model notes\n"
        raw=self.make_tar(ext.decode())
        with tempfile.TemporaryDirectory() as temp, \
          patch.object(scan,"TAR_SHA256",sha256(raw).hexdigest()), \
          patch.object(scan,"EXTERNAL_README_MD5",md5(ext).hexdigest()):
            tarpath=Path(temp)/"a.tar"; tarpath.write_bytes(raw)
            extpath=Path(temp)/"readme.md"; extpath.write_bytes(ext)
            report=scan.inspect(tarpath,extpath)
        self.assertTrue(report["same_readme_bytes"])
        self.assertFalse(report["no_refactoring_experiment_reproduced"])
        self.assertEqual(report["publisher_api_metadata_status"],"NOT_FETCHED")

    def test_differing_off_tar_instructions_are_reported(self):
        readme="Original evaluation results\n"
        ext=b"Original evaluation results\nWithout refactoring instructions are here\n"
        raw=self.make_tar(readme)
        with tempfile.TemporaryDirectory() as temp, \
          patch.object(scan,"TAR_SHA256",sha256(raw).hexdigest()), \
          patch.object(scan,"EXTERNAL_README_MD5",md5(ext).hexdigest()):
            p=Path(temp)/"a.tar";p.write_bytes(raw)
            q=Path(temp)/"README.md";q.write_bytes(ext)
            report=scan.inspect(p,q)
        self.assertFalse(report["same_readme_bytes"])
        self.assertTrue(any("Without refactoring" in x for x in report["readme_diff_lines"]))
        self.assertFalse(report["no_refactoring_experiment_reproduced"])

    def test_mismatching_authenticity_pins_fail_closed(self):
        ext=b"README\n"; raw=self.make_tar(ext.decode())
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"a.tar"; p.write_bytes(raw)
            q=Path(temp)/"README.md"; q.write_bytes(ext)
            with self.assertRaisesRegex(ValueError,"Original TAR checksum"):
                scan.inspect(p,q)


if __name__=="__main__":
    unittest.main()
