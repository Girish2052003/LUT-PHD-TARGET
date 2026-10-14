#!/usr/bin/env python3
"""Reproduce the PAPER'S Figure 4 bubble-sort before/after-repair logic.

Unlike synthetic leak fixtures, these assignments are transcribed from the
algorithm demonstrated in Figure 4 (p. 8), with an independently constructed
three-element test corpus. The code is not fetched from the original authors'
repository and the six permutations are NOT SPDZEval's original unit tests.
Runs using the real MP-SPDZ compiler + official cleartext emulator.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PIN = "78fe3d8bad4e654276eb3a11a88173195e672f44"
PERMUTATIONS = list(itertools.permutations((1, 2, 3)))


def program(repaired: bool) -> str:
    # Figure 4 (original): incorrect conditional swap leaves elements in place.
    # Figure 4 (repaired): left receives right and right receives left.
    if repaired:
        swaps = (
            "            temp = condition.if_else(arr[j+1], arr[j])\n"
            "            arr[j+1] = condition.if_else(arr[j], arr[j+1])\n"
            "            arr[j] = temp\n")
    else:
        swaps = (
            "            temp = condition.if_else(arr[j], arr[j+1])\n"
            "            arr[j+1] = condition.if_else(arr[j+1], arr[j])\n"
            "            arr[j] = temp\n")
    return (
        "from Compiler.types import Array, sint\n"
        "from Compiler.library import print_ln\n"
        "def bubble_sort(arr):\n"
        "    n = len(arr)\n"
        "    for i in range(n-1):\n"
        "        for j in range(n-1-i):\n"
        "            condition = arr[j] >= arr[j+1]\n" +
        swaps +
        "    return arr\n"
        "a = Array(3, sint)\n"
        "for k in range(3):\n"
        "    a[k] = sint.get_input_from(0)\n"
        "bubble_sort(a)\n"
        "print_ln('SORTED:%s,%s,%s', a[0].reveal(), a[1].reveal(), a[2].reveal())\n"
    )


def command(args, cwd):
    r = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=180)
    return r.returncode, r.stdout


def main(mp: Path, dest: Path):
    mp = mp.resolve()
    if not (mp / "emulate.x").is_file():
        raise FileNotFoundError("Build genuine emulate.x")
    code, revision = command(["git", "rev-parse", "HEAD"], mp)
    if code or revision.strip() != PIN:
        raise ValueError("Wrong MP-SPDZ pinned revision")
    dest.mkdir(parents=True, exist_ok=True)
    observations = []
    for kind, repaired in (("before_repair", False), ("after_repair", True)):
        name = "spdz_paper_figure4_" + kind
        source_path = mp / "Programs" / "Source" / (name + ".mpc")
        if source_path.exists():
            raise FileExistsError("Refusing overwrite: " + str(source_path))
        source = program(repaired)
        (dest / (name + ".mpc")).write_text(source)
        try:
            source_path.write_text(source)
            status, log = command([sys.executable, "compile.py", "-R", "64", name], mp)
            (dest / (name + ".compile.log")).write_text(log)
            if status:
                raise RuntimeError("Compiler rejected " + kind)
            for inputs in PERMUTATIONS:
                tag = "_".join(map(str, inputs))
                prefix = dest.resolve() / (name + "_" + tag)
                Path(str(prefix) + "-P0-0").write_text(
                    "\n".join(str(x) for x in inputs) + "\n")
                status, trace = command(
                    [str(mp / "emulate.x"), name, "-IF", str(prefix)], mp)
                (dest / (name + "_" + tag + ".log")).write_text(trace)
                if status:
                    raise RuntimeError("Emulator failed " + kind + ":" + tag)
                match = re.search(r"SORTED:\s*(-?\d+),(-?\d+),(-?\d+)", trace)
                if not match:
                    raise ValueError("Unparsed sort trace")
                actual = tuple(int(x) for x in match.groups())
                passed = actual == tuple(sorted(inputs))
                observations.append(dict(
                    variant=kind, secret_inputs=inputs,
                    expected=sorted(inputs), actual=actual, correct=passed))
        finally:
            source_path.unlink(missing_ok=True)
    counts = {
        kind: sum(o["correct"] for o in observations if o["variant"] == kind)
        for kind in ("before_repair", "after_repair")
    }
    # The broken Figure 4 swaps when left < right, so it sorts DESCENDING.
    # All six inputs contain distinct values, so none are ascending after it.
    # The corrected version swaps on >=, so all six become ascending.
    if counts["before_repair"] != 0 or counts["after_repair"] != 6:
        raise AssertionError("Unexpected Figure 4 repaired/broken behavior: " + str(counts))
    result = dict(
        experiment="paper_figure4_algorithm_reproduction",
        source="arxiv:2501.00363v2, Figure 4, page 8",
        original_authors_source_checkout=False,
        original_spdzeval_tests=False,
        original_model_generated_samples=False,
        fixed_point=False,
        type="sint",
        mpspdz_commit=PIN,
        emulator="official_cleartext_emulator_using_party_input",
        original_program_correct_per_six=counts["before_repair"],
        repaired_program_correct_per_six=counts["after_repair"],
        traces=observations)
    (dest / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mpspdz", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    r = main(args.mpspdz, args.output)
    print(json.dumps({k: v for k, v in r.items() if k != "traces"}, indent=2))
