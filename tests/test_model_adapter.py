import io
import json
import unittest
from unittest.mock import patch

from spdz_audit.model_adapter import APIDocBaseline, ChatCompletionModel
from spdz_audit.paper_reconstruction import Evaluation


class ModelAdapterTests(unittest.TestCase):
    def test_fails_without_opt_in_credentials(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}):
            with self.assertRaisesRegex(ValueError, "required"):
                ChatCompletionModel()
        with self.assertRaises(ValueError):
            ChatCompletionModel(api_key="placeholder", endpoint="http://unsafe.test")

    def test_chat_payload_and_true_usage_recording_with_mock_http_only(self):
        calls = []
        payload = {
            "id": "test_fake_completion",
            "model": "gpt-4-turbo-2024-04-09",
            "choices": [{"message": {"content": "def f(x):\n return x"},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 89, "completion_tokens": 14}
        }

        def fake_urlopen(request, timeout):
            calls.append(json.loads(request.data.decode()))
            self.assertEqual(timeout, 120)
            self.assertIn("Bearer placeholder", request.get_header("Authorization"))
            return io.BytesIO(json.dumps(payload).encode())

        with patch("urllib.request.urlopen", fake_urlopen):
            model = ChatCompletionModel(api_key="placeholder")
            text = model.complete("generate", [{"role": "user", "content": "test"}], .7)
        self.assertIn("return x", text)
        self.assertEqual(calls[0]["temperature"], .7)
        self.assertEqual(calls[0]["model"], "gpt-4-turbo-2024-04-09")
        self.assertEqual(model.history[0]["usage"]["prompt_tokens"], 89)
        self.assertNotIn("placeholder", str(model.history))

    def test_api_doc_baseline_requires_documentation(self):
        model = ChatCompletionModel(api_key="placeholder")
        with self.assertRaises(ValueError):
            APIDocBaseline(model, lambda _: Evaluation(True), "")

    def test_api_doc_baseline_builds_two_distinct_stage_prompts(self):
        class FixtureModel:
            calls = []
            def complete(self, stage, messages, temperature):
                self.calls.append((stage, messages))
                if stage == "api_doc_summarize":
                    return "Returns x unchanged."
                if stage == "api_doc_generate":
                    return "def f(x):\n    return x\n"
                raise ValueError(stage)

        model = FixtureModel()
        result = APIDocBaseline(
            model, lambda code: Evaluation("return x" in code),
            "from Compiler.types import sfix").run("def f(x):\n    return x\n")
        self.assertTrue(result["passed"])
        self.assertEqual([x[0] for x in model.calls],
                         ["api_doc_summarize", "api_doc_generate"])
        self.assertIn("from Compiler.types import sfix",
                      model.calls[1][1][1]["content"])
        self.assertTrue(result["reconstruction_not_original_implementation"])


if __name__ == "__main__":
    unittest.main()
