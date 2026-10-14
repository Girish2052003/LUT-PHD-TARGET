import unittest
from scripts.inspect_provided_artifacts import record_files

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

if __name__ == "__main__":
    unittest.main()
