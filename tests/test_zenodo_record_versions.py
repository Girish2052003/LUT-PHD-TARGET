"""Synthetic publisher API-version response regression tests."""
import unittest
from scripts.audit_zenodo_record_versions import analyze
class VersionAuditTests(unittest.TestCase):
    def test_two_versions_and_file_identity_are_retained(self):
        response={"hits":{"hits":[
            {"id":1,"doi":"10.5281/zenodo.1","metadata":{"version":"v1","title":"SPDZCoder Artifacts"},"files":[{"key":"old.tar","size":200}]},
            {"id":2,"metadata":{"version":"v2"},"files":[{"key":"new.tar","size":300}]}
        ]}}
        records=analyze(response)
        self.assertEqual([x["id"] for x in records],[1,2])
        self.assertEqual(records[0]["files"][0]["key"],"old.tar")
    def test_invalid_shape_does_not_silently_count_as_no_versions(self):
        with self.assertRaisesRegex(ValueError,"No record"):
            analyze({"error":"not found"})
if __name__=="__main__":
    unittest.main()
