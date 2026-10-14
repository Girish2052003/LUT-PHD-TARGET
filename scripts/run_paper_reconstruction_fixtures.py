#!/usr/bin/env python3
"""Run transparent, DETERMINISTIC fixture comparison of reconstructed pipeline.

This is not the authors' model, not SPDZEval, and not an LLM pass@k result.
It tests whether an added privacy screen catches direct leaks that ordinary
functional output checks (represented by a controlled fixture) miss.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from spdz_audit.paper_reconstruction import (
    Evaluation, PaperPipeline, ReplayModel, match_rules
)

# Every test is hand-labeled and published here. They are purpose-built
# security regressions rather than an unbiased sample of LLM translations.
SAFE = "def f(x):\n    return x + 1\n"
SAFE_OBLIVIOUS = "def f(x):\n    return (x > 0).if_else(x, -x)\n"
CASES = [
    dict(id="direct_reveal", original=SAFE,
         candidate="def f(x):\n    unused = x.reveal()\n    return x + 1\n",
         repaired=SAFE, unsafe=True),
    dict(id="nested_reveal", original=SAFE,
         candidate="def f(x):\n    return x.reveal() + 1\n",
         repaired=SAFE, unsafe=True),
    dict(id="explicit_print", original=SAFE,
         candidate="def f(x):\n    print_ln(x)\n    return x + 1\n",
         repaired=SAFE, unsafe=True),
    dict(id="public_secret_branch", original=SAFE,
         candidate="def f(x):\n    if x > 0:\n        return x\n    return -x\n",
         repaired=SAFE_OBLIVIOUS, unsafe=True),
    dict(id="derived_secret_branch", original=SAFE,
         candidate="def f(x):\n    y = x + 1\n    if y > 0:\n        return y\n    return -y\n",
         repaired=SAFE, unsafe=True),
    dict(id="secret_loop_bound", original=SAFE,
         candidate="def f(x):\n    for i in range(x):\n        pass\n    return x + 1\n",
         repaired=SAFE, unsafe=True),
    dict(id="secret_index", original=SAFE,
         candidate="def f(x):\n    return x[x]\n",
         repaired=SAFE, unsafe=True),
    dict(id="clear_arithmetic_control", original=SAFE,
         candidate=SAFE, repaired=SAFE, unsafe=False),
    dict(id="oblivious_selection_control", original=SAFE,
         candidate=SAFE_OBLIVIOUS, repaired=SAFE_OBLIVIOUS, unsafe=False),
]


def script_for(case: dict, modified: bool):
    # CFP answers here are exact pass-through fixtures, not LLM refactors.
    script = [
        dict(stage="refactor:" + rule, response=case["original"])
        for rule in match_rules(case["original"])
    ]
    script += [
        dict(stage="generate", response=case["candidate"]),
        dict(stage="reflect", response=case["candidate"])
    ]
    if modified and case["unsafe"]:
        script.append(dict(stage="repair:1", response=case["repaired"]))
    return script


def experiment():
    # A functional-only oracle that intentionally overlooks leaks.
    # It is a controlled *synthetic* oracle, NOT a real runtime test.
    result = []
    for case in CASES:
        record = dict(id=case["id"], expected_unsafe=case["unsafe"],
                      baseline={}, modified={})
        for mode, modified in [("baseline", False), ("modified", True)]:
            model = ReplayModel(script_for(case, modified))
            pipe = PaperPipeline(model, lambda _: Evaluation(True),
                                 privacy_extension=modified)
            attempt = pipe.run(case["original"])
            record[mode] = dict(
                accepted=attempt.result.passed,
                repairs=attempt.repairs,
                issues_on_final=attempt.issues,
                stages=attempt.stages,
                generated=attempt.generated,
                final=attempt.final,
                model_backend="deterministic_replay",
                evaluator="synthetic_functional_only_acceptance",
                number_of_fixture_responses=len(model.calls)
            )
        result.append(record)
    return dict(
        experiment="synthetic_privacy_screen_reconstruction",
        original_implementation_reproduced=False,
        original_spdzeval_reproduced=False,
        actual_llm_calls=0,
        functional_oracle="deliberately_synthetic_always_true",
        privacy_screen_not_security_proof=True,
        n_cases=len(result), n_labeled_unsafe=sum(x["expected_unsafe"] for x in result),
        baseline_accepted_unsafe=sum(
            x["expected_unsafe"] and x["baseline"]["accepted"] for x in result),
        modified_accepted_unsafe=sum(
            x["expected_unsafe"] and x["modified"]["accepted"] and
            any(x["modified"]["final"] == x["baseline"]["final"]
                for _ in (0,)) for x in result),
        modified_repaired=sum(x["modified"]["repairs"] > 0 for x in result),
        modified_accepted=sum(x["modified"]["accepted"] for x in result),
        cases=result
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results" / "paper-reconstruction-fixture.json")
    args = parser.parse_args()
    results = experiment()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({k: v for k, v in results.items() if k != "cases"}, indent=2))
