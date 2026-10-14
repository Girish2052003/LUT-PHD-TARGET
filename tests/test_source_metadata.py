import unittest
import hashlib
from scripts.inspect_provided_artifacts import record_files, validate_checksum

class SourceMetadataTest(unittest.TestCase):
    def test_zenodo_v1_files(self):
        metadata = {"files": [{"key": "SPDZCoder.zip", "size": 8, "checksum": "md5:0123",
                             "links": {"self": "https://example.org/a"}}]}
        self.assertEqual(record_files(metadata)[0]["name"], "SPDZCoder.zip")
        self.assertEqual(record_files(metadata)[0]["size"], 8)

    def test_new_zenodo_file_shape(self):
        record = {"files": {"entries": {"x": {"key": "data.zip", "size": 100,
            "links": {"content": "https://example.org/data"}}}}}
        self.assertEqual(record_files(record)[0]["name"], "data.zip")

    def test_checksums_validate_string_and_dictionary_forms(self):
        content = b"real archive bytes"
        md5 = hashlib.md5(content).hexdigest()
        validate_checksum(content, "md5:" + md5)
        validate_checksum(content, {"md5": md5})
        for wrong in ({"md5": "0" * 32}, "md5:" + "0" * 32,
                      "unknown:1234", None, {}):
            with self.assertRaises(ValueError):
                validate_checksum(content, wrong)

if __name__ == "__main__":
    unittest.main()
