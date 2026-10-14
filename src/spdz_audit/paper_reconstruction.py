"""Independent reconstruction of the SPDZCoder three-stage architecture.

Not the original authors' implementation. The paper publishes representative
prompt templates but no complete runnable source or SPDZEval benchmark.
"""
from __future__ import annotations
import ast
from dataclasses import dataclass, field
import re
from typing import Callable, Protocol
from .paper_prompts import (refactor_prompt, generation_prompt,
                            reflection_prompt, repair_prompt)

# Rule names and categories from Dong et al., Table 1 (page 4).
# Descriptions here are disclosed reconstructions, not verbatim original prompts.
RULES = (
    ("Linear_NonLinear", "Rewrite nonlinear functions into basic functions."),
    ("DataStructure", "Replace advanced container methods."),
    ("SyntaxSugar", "Replace syntactic sugar with explicit code."),
    ("RewriteWhileLoop", "Use a bounded for loop when semantically justified."),
    ("EliminateAdvancedArrayOperations", "Expand advanced NumPy and array methods."),
    ("EliminateBreak", "Use an explicit break flag."),
    ("EliminateContinue", "Use an explicit continue flag."),
    ("NestedIf_MultipleReturn", "Flatten nested branches and multiple returns."),
    ("ChainedComparison", "Expand chained comparisons."),
    ("ObliviousForm", "Replace secret-dependent branches with oblivious operations."),
)


def extract_code(text: str) -> str:
    fence = r"\x60{3}"
    match = re.search(fence + r"(?:python|mpc|mp-spdz|MP-SPDZ)?\s*\n(.*?)" + fence, text, re.S)
    result = (match.group(1) if match else text).strip()
    if not result:
        raise ValueError("Missing generated code")
    ast.parse(result)
    return result + "\n"


def match_rules(code: str) -> list[str]:
    nodes = list(ast.walk(ast.parse(code)))
    call_attrs = {n.func.attr for n in nodes
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    names = {n.id for n in nodes if isinstance(n, ast.Name)}
    matched = set()
    if call_attrs & {"exp", "sin", "cos", "tan", "arcsin", "arctan", "log10"}:
        matched.add("Linear_NonLinear")
    if call_attrs & {"append", "pop", "extend", "reshape", "flatten", "sort"}:
        matched.add("DataStructure")
    if any(isinstance(n, (ast.IfExp, ast.ListComp, ast.DictComp, ast.GeneratorExp))
           for n in nodes):
        matched.add("SyntaxSugar")
    if any(isinstance(n, ast.While) for n in nodes):
        matched.add("RewriteWhileLoop")
    if names & {"numpy", "np"} or any(isinstance(n, ast.Slice) for n in nodes):
        matched.add("EliminateAdvancedArrayOperations")
    if any(isinstance(n, ast.Break) for n in nodes):
        matched.add("EliminateBreak")
    if any(isinstance(n, ast.Continue) for n in nodes):
        matched.add("EliminateContinue")
    if sum(isinstance(n, ast.Return) for n in nodes) > 1:
        matched.add("NestedIf_MultipleReturn")
    if any(isinstance(n, ast.Compare) and len(n.ops) > 1 for n in nodes):
        matched.add("ChainedComparison")
    if any(isinstance(n, (ast.If, ast.IfExp)) for n in nodes):
        matched.add("ObliviousForm")
    return [name for name, _ in RULES if name in matched]


def signature(code: str) -> tuple[str, int]:
    tree = ast.parse(code)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    if len(functions) != 1:
        raise ValueError("Expected exactly one function")
    fn = functions[0]
    return fn.name, len(fn.args.args)


class Model(Protocol):
    def complete(self, stage: str, messages: list[dict], temperature: float) -> str: ...


class ReplayModel:
    """Scripted responses for testing, NEVER genuine sampled model generations."""
    def __init__(self, steps: list[dict[str, str]]):
        self.remaining = list(steps)
        self.calls = []

    def complete(self, stage: str, messages: list[dict], temperature: float) -> str:
        if not self.remaining:
            raise ValueError("Scripted replay exhausted")
        step = self.remaining.pop(0)
        if step["stage"] != stage:
            raise ValueError("Replay stage mismatch: " + stage)
        self.calls.append({"stage": stage, "messages": messages, "temperature": temperature})
        return step["response"]


@dataclass
class Evaluation:
    passed: bool
    kind: str = "functionality"
    message: str = ""

    def __post_init__(self):
        if type(self.passed) is not bool or self.kind not in {"functionality", "compile_runtime"}:
            raise ValueError("Invalid evaluator response")


class PrivacyScreen:
    """Conservative syntactic check only, NOT a noninterference proof.

    Function inputs are presumed secret; permitted final output must be handled
    outside the function. Unknown aliases and external effects are out of scope.
    """
    def check(self, code: str) -> list[str]:
        problems: set[str] = set()
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = node.func
                if isinstance(fn, ast.Attribute) and fn.attr in {"reveal", "reveal_list"}:
                    problems.add("explicit-secret-reveal")
                if isinstance(fn, ast.Name) and fn.id in {
                    "print", "print_ln", "print_str", "print_float",
                    "eval", "exec", "open", "__import__"}:
                    problems.add("unauthorized-output-or-dynamic-call")
            if not isinstance(node, ast.FunctionDef):
                continue
            tainted = {a.arg for a in node.args.args}
            for _ in range(5):
                for inner in ast.walk(node):
                    if isinstance(inner, ast.Assign) and any(
                        isinstance(n, ast.Name) and n.id in tainted
                        for n in ast.walk(inner.value)
                    ):
                        for target in inner.targets:
                            tainted.update(n.id for n in ast.walk(target)
                                           if isinstance(n, ast.Name))
            for inner in ast.walk(node):
                if isinstance(inner, (ast.If, ast.While)) and any(
                    isinstance(n, ast.Name) and n.id in tainted
                    for n in ast.walk(inner.test)
                ):
                    problems.add("secret-dependent-public-branch")
                if isinstance(inner, ast.For) and any(
                    isinstance(n, ast.Name) and n.id in tainted
                    for n in ast.walk(inner.iter)
                ):
                    problems.add("secret-dependent-loop-bound")
                if isinstance(inner, ast.Subscript) and any(
                    isinstance(n, ast.Name) and n.id in tainted
                    for n in ast.walk(inner.slice)
                ):
                    problems.add("possibly-secret-index")
        return sorted(problems)


@dataclass
class Attempt:
    rules: list[str]
    cfp: str
    generated: str
    final: str
    result: Evaluation
    repairs: int
    issues: list[str] = field(default_factory=list)
    stages: list[str] = field(default_factory=list)


class PaperPipeline:
    """Refactor->generate->reflect->repair, with model and evaluator injected.

    The pipeline never executes model-supplied source by itself. Production
    evaluation must use a sandboxed compiler/test harness with resource limits.
    """
    def __init__(self, model: Model, evaluator: Callable[[str], Evaluation],
                 *, privacy_extension: bool = False, max_feedback: int = 3,
                 temperature: float = 0.7):
        if type(max_feedback) is not int or max_feedback < 0:
            raise ValueError("Invalid feedback limit")
        if not isinstance(temperature, (int, float)) or not 0 <= temperature <= 2:
            raise ValueError("Invalid temperature")
        self.model = model
        self.evaluator = evaluator
        self.privacy_extension = privacy_extension
        self.max_feedback = max_feedback
        self.temperature = temperature
        self.events = []
        self.screen = PrivacyScreen()

    def ask(self, stage: str, instruction: str, source: str) -> str:
        messages = [{"role": "system", "content": instruction},
                    {"role": "user", "content": source}]
        response = self.model.complete(stage, messages, self.temperature)
        self.events.append({"stage": stage, "messages": messages, "response": response})
        return extract_code(response)

    def run(self, source: str) -> Attempt:
        before = signature(source)
        selected = match_rules(source)
        cfp, stages = source, []
        for name, description in RULES:
            if name in selected:
                stage = "refactor:" + name
                cfp = self.ask(stage,
                    refactor_prompt(name, description), cfp)
                if signature(cfp) != before:
                    raise ValueError("Refactor changed the function signature")
                stages.append(stage)
        generated = self.ask("generate",
            generation_prompt(selected), cfp)
        stages.append("generate")
        candidate = self.ask("reflect",
            reflection_prompt(), generated)
        stages.append("reflect")
        repairs = 0
        while True:
            issues = self.screen.check(candidate) if self.privacy_extension else []
            result = (Evaluation(False, "functionality", "privacy-screen: " + ", ".join(issues))
                      if issues else self.evaluator(candidate))
            if result.passed or repairs >= self.max_feedback:
                return Attempt(selected, cfp, generated, candidate, result,
                               repairs, issues, stages)
            repairs += 1
            stage = "repair:" + str(repairs)
            candidate = self.ask(stage,
                repair_prompt(result.kind),
                "Canonical Python:\n" + cfp + "\nMP-SPDZ code:\n" +
                candidate + "\nError kind: " + result.kind +
                "\nError: " + result.message)
            stages.append(stage)
