#!/usr/bin/env python3
"""Real MP-SPDZ cleartext-emulator demonstration of an explicit extra leak.

This models a source function that returns the CONSTANT zero for all secrets.
A generated baseline fixture sneaks an extra print of the secret into the code.
Both versions return the same zero (so a primary-output test passes), but only
the leaky version exposes the input in an unauthorized secondary output.

This is an independently authored, intentional witness, NOT a generated
SPDZCoder output, proof of the paper's original code, or an MPC protocol proof.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from spdz_audit.paper_reconstruction import PrivacyScreen

PIN = "78fe3d8bad4e654276eb3a11a88173195e672f44"
INPUTS = [-3, 5]
FRAGMENTS = {
    "baseline": ("def f(x):\n"
                 "    print_ln('UNAUTHORIZED_SECRET:%s', x.reveal())\n"
                 "    return sfix(0)\n"),
    "modified": ("def f(x):\n"
                 "    return sfix(0)\n"),
}


def process(command, cwd, timeout=180):
    result = subprocess.run(command, cwd=cwd, text=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=timeout)
    return result.returncode, result.stdout


def compare(mpspdz: Path, output: Path) -> dict:
    mpspdz = mpspdz.resolve()
    if not (mpspdz / "emulate.x").is_file():
        raise FileNotFoundError("Build genuine MP-SPDZ emulate.x first")
    status, sha = process(["git", "rev-parse", "HEAD"], mpspdz, timeout=10)
    if status or sha.strip() != PIN:
        raise ValueError("Wrong MP-SPDZ compatibility commit")
    output.mkdir(parents=True, exist_ok=True)
    results = []
    gate = PrivacyScreen()
    for mode, function in FRAGMENTS.items():
        problems = gate.check(function)
        if mode == "baseline" and not problems:
            raise AssertionError("Privacy-screen did not detect explicit leak")
        if mode == "modified" and problems:
            raise AssertionError("Unexpected privacy-screen false positive")
        name = "spdz_unauthorized_leak_" + mode
        path = mpspdz / "Programs" / "Source" / (name + ".mpc")
        if path.exists():
            raise FileExistsError("Refusing to overwrite existing MP-SPDZ source")
        program = ("from Compiler.types import sfix\n"
                   "from Compiler.library import print_ln\n" +
                   function +
                   "\nx = sfix.get_input_from(0)\n" +
                   "answer = f(x)\n" +
                   "print_ln('AUTHORIZED_RESULT:%s', answer.reveal())\n")
        (output / (name + ".mpc")).write_text(program)
        try:
            path.write_text(program)
            status, log = process(
                [sys.executable, "compile.py", "-R", "64", name], mpspdz)
            (output / (name + ".compile.log")).write_text(log)
            if status:
                raise RuntimeError("MP-SPDZ compile failed for " + mode)
            for x in INPUTS:
                prefix = output.resolve() / ("inputs_" + mode + "_" + str(x))
                Path(str(prefix) + "-P0-0").write_text(str(x) + "\n")
                status, trace = process(
                    [str(mpspdz / "emulate.x"), name, "-IF", str(prefix)],
                    mpspdz)
                (output / (mode + "_" + str(x) + ".emulate.log")).write_text(trace)
                if status:
                    raise RuntimeError("Emulator returned nonzero for " + mode)
                result_tokens = re.findall(
                    r"AUTHORIZED_RESULT:\s*([-+]?\d+(?:\.\d+)?)", trace)
                leak_tokens = re.findall(
                    r"UNAUTHORIZED_SECRET:\s*([-+]?\d+(?:\.\d+)?)", trace)
                if len(result_tokens) != 1 or abs(float(result_tokens[0])) > 0.01:
                    raise AssertionError("Primary function output must remain zero")
                leaked = [float(y) for y in leak_tokens]
                if mode == "baseline" and (len(leaked) != 1 or
                                            abs(leaked[0] - x) > 0.01):
                    raise AssertionError("Baseline leak not reproduced in trace")
                if mode == "modified" and leaked:
                    raise AssertionError("Modified mode still revealed input")
                results.append(dict(mode=mode, secret_input=x,
                                    authorized_output=float(result_tokens[0]),
                                    unauthorized_reveals=leaked,
                                    privacy_screen_issues=problems,
                                    compile="success", emulation="success"))
        finally:
            path.unlink(missing_ok=True)
    record = dict(
        experiment="independent_explicit_leak_counterexample",
        source_paper_code=False,
        original_spdzeval=False,
        original_spdzcoder=False,
        mpspdz_commit=PIN,
        runtime="official_cleartext_emulator_with_party_input",
        real_mpc_protocol=False,
        model_generations=0,
        experiment_comparison="same_constant_function_output_with_extra_side_output",
        inputs=INPUTS, observations=results)
    (output / "summary.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mpspdz", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "privacy-witness")
    a = parser.parse_args()
    result = compare(a.mpspdz, a.output)
    print(json.dumps(result, indent=2))
