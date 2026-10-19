"""Synthetic original Git provenance tests with secret-safe URL treatment."""
import io
import tarfile
import unittest
from hashlib import md5,sha256
from unittest.mock import patch
from scripts import audit_original_git_remote_metadata as mod

def tar_bytes(entries):
    f=io.BytesIO()
    with tarfile.open(fileobj=f,mode="w") as t:
        for name,content in entries.items():
            d=content.encode()
            i=tarfile.TarInfo("SPDZCoder/"+name)
            i.size=len(d)
            t.addfile(i,io.BytesIO(d))
    return f.getvalue()

class GitRemoteTests(unittest.TestCase):
    def test_public_remote_and_v1_version_readme_match(self):
        prior=b"Original author instructions\n"
        source=tar_bytes({
           ".git/config":'[remote "origin"]\n\turl = git@github.com:AuthorCode/SPDZCoder.git\n',
           "README.md":prior.decode()
        })
        with patch.object(mod,"TAR_SHA",sha256(source).hexdigest()), \
             patch.object(mod,"V1_README_MD5",md5(prior).hexdigest()):
            output=mod.inspect(source,prior)
        self.assertTrue(output["git_config_present"])
        self.assertTrue(output["v1_readme_matches_embedded_v2_tar_readme"])
        self.assertEqual(output["git_remote_refs"][0]["public_repository"],
                         "AuthorCode/SPDZCoder")
        self.assertFalse(output["experiment_reproduced"])

    def test_bearer_credentials_not_output(self):
        value="https://leak:secret@private.internal/myrepo"
        output=mod.clean_remote(value)
        self.assertEqual(output["host"],"NONPUBLIC_OR_UNKNOWN")
        self.assertIsNone(output["public_repository"])
        self.assertNotIn("secret",str(output))

    def test_sha_rejects_wrong_author_tar(self):
        with self.assertRaisesRegex(ValueError,"TAR SHA"):
            mod.inspect(b"fake",b"fake")

if __name__=="__main__":
    unittest.main()
