"""Pure synthetic negative/positive original-source preflight tests."""
import io
import json
import tarfile
import unittest
from scripts.no_refactoring_source_preflight import analyze

def fake_archive(entries):
    b=io.BytesIO()
    with tarfile.open(fileobj=b,mode="w") as tar:
        for path,text in entries.items():
            raw=text.encode()
            f=tarfile.TarInfo("SPDZCoder/"+path)
            f.size=len(raw)
            tar.addfile(f,io.BytesIO(raw))
    b.seek(0)
    return b

class NoRefactoringSourcePreflightTests(unittest.TestCase):
    def test_source_task_inventory_does_not_claim_generated_ablation(self):
        sample={
            "data/input_processed_data/array_test.json":
                json.dumps({"test_name":"foo","source":"def foo(x):\n    return x + 1\n"})+"\n",
            "data/stage_1_IR_output/experiment-1-array_test_intermediate_representation.jsonl":
                json.dumps({"test_name":"foo","source":"def foo(x):\n    return x + 1\n"})+"\n",
            "data/stage_2_SPDZ_output/experiment-1-array_test.jsonl":
                json.dumps({"test_name":"foo","response_0":"ok","response_1":"ok"})+"\n",
        }
        with tarfile.open(fileobj=fake_archive(sample)) as tar:
            r=analyze(tar,{"array_test":1})
        self.assertEqual(r["task_count"],1)
        self.assertEqual(r["parseable_top_level_python_source_tasks"],1)
        self.assertEqual(r["source_field_occurrence_counts"]["source"],1)
        self.assertFalse(r["paper_no_refactoring_reproduced"])
        self.assertEqual(r["live_model_api_calls"],0)
    def test_inconsistent_original_stage_task_identity_fails_closed(self):
        sample={
            "data/input_processed_data/array_test.json":'{"test_name":"foo"}\n',
            "data/stage_1_IR_output/experiment-1-array_test_intermediate_representation.jsonl":'{"test_name":"wrong"}\n',
            "data/stage_2_SPDZ_output/experiment-1-array_test.jsonl":'{"test_name":"foo"}\n',
        }
        with tarfile.open(fileobj=fake_archive(sample)) as tar:
            with self.assertRaisesRegex(ValueError,"identity/order"):
                analyze(tar,{"array_test":1})
if __name__=="__main__":unittest.main()
