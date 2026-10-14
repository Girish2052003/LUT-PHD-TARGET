"""Opt-in model adapter and API-Doc baseline reconstruction for SPDZCoder.

No network call occurs when importing this module. Reproducing the published
numbers also requires the original benchmark, exact prompts and historic model.
The paper's API-Doc baseline prompt is in Appendix Table 13 (representative
implementation here). Logged token usage is returned by the remote API, not
estimated from source length.
"""
from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
from typing import Callable

from .paper_reconstruction import Evaluation, extract_code

DEFAULT_MODEL = "gpt-4-turbo-2024-04-09"


class ChatCompletionModel:
    def __init__(self, *, model: str = DEFAULT_MODEL, api_key: str | None = None,
                 endpoint: str = "https://api.openai.com/v1/chat/completions"):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY required; no live call was attempted")
        if not endpoint.startswith("https://"):
            raise ValueError("TLS endpoint required")
        self.endpoint = endpoint
        self.history = []

    def complete(self, stage: str, messages: list[dict],
                 temperature: float) -> str:
        request_bytes = json.dumps({
            "model": self.model, "messages": messages, "temperature": temperature
        }).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint, data=request_bytes, method="POST",
            headers={
                "Authorization": "Bearer " + self.api_key,
                "Content-Type": "application/json"
            })
        with urllib.request.urlopen(request, timeout=120) as response:
            record = json.load(response)
        choices = record.get("choices") or []
        if not choices or not isinstance(choices[0]["message"].get("content"), str):
            raise RuntimeError("Model returned no ordinary text response")
        self.history.append({
            "stage": stage,
            "model_requested": self.model,
            "model_actual": record.get("model"),
            "completion_id": record.get("id"),
            "finish_reason": choices[0].get("finish_reason"),
            "usage": record.get("usage"),
            # Never store credential in history or artifact logs.
        })
        return choices[0]["message"]["content"]


class APIDocBaseline:
    """Reconstruction of Table 13, not a recovered exact baseline codebase."""
    def __init__(self, model: ChatCompletionModel,
                 evaluator: Callable[[str], Evaluation], api_documentation: str,
                 temperature: float = 0.7):
        if not api_documentation.strip():
            raise ValueError("Actual MP-SPDZ documentation required")
        self.model, self.evaluator = model, evaluator
        self.api_documentation = api_documentation
        self.temperature = temperature
        self.events = []

    def run(self, source: str) -> dict:
        summary_prompt = [
            {"role": "system", "content":
                "You explain Python functionality accurately in no more than five sentences."},
            {"role": "user", "content":
                "Explain the inputs, outputs, functions and key variables of this Python:\n" + source}
        ]
        summary = self.model.complete("api_doc_summarize", summary_prompt,
                                      self.temperature)
        generation_prompt = [
            {"role": "system", "content":
                "Write an MP-SPDZ function with the same semantics as this Python. "
                "Use secret types, preserve parameters, avoid revealing inputs and "
                "use the provided API documentation."},
            {"role": "user", "content":
                "MP-SPDZ API documentation:\n" + self.api_documentation +
                "\nPython source:\n" + source + "\nFunctional description:\n" + summary +
                "\nReturn only MP-SPDZ code."}
        ]
        generated = extract_code(self.model.complete(
            "api_doc_generate", generation_prompt, self.temperature))
        evaluation = self.evaluator(generated)
        return {
            "source": source, "summary": summary,
            "candidate": generated, "passed": evaluation.passed,
            "failure_kind": evaluation.kind, "failure_message": evaluation.message,
            "reconstruction_not_original_implementation": True
        }
