"""Original source-inventory controls: no false claims of missing or present ablations."""
import io
import tarfile
import unittest
from scripts.inventory_original_ablations import inventory


class OriginalAblationInventoryTests(unittest.TestCase):
    def test_annotates_only_existing_member_paths(self):
        data=io.BytesIO()
        with tarfile.open(fileobj=data,mode="w") as t:
            for name in ("SPDZCoder/evaluation/no_refactoring_test.txt",
                         "SPDZCoder/evaluation/experiment-1-stage_2_SPDZ_output_array_test.txt",
                         "SPDZCoder/unrelated/readme.md","SPDZCoder/.git/private"):
                value=b"x"
                info=tarfile.TarInfo(name)
                info.size=len(value)
                t.addfile(info,io.BytesIO(value))
        with tarfile.open(fileobj=io.BytesIO(data.getvalue())) as t:
            r=inventory(t)
        self.assertEqual(r["matching_entry_count"],2)
        self.assertTrue(any(x["path"].endswith("no_refactoring_test.txt")
                            for x in r["matching_entries"]))
        self.assertEqual(r["fresh_model_calls"],0)

    def test_empty_archive_is_not_misrepresented_as_results(self):
        with tarfile.open(fileobj=io.BytesIO(),mode="w") as t:
            x=inventory(t)
        self.assertEqual(x["matching_entry_count"],0)
        self.assertNotIn("without_refactoring_percent",x)


if __name__=="__main__":
    unittest.main()
