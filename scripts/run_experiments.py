#!/usr/bin/env python3
"""Run from a clean checkout; standard library only, no API key needed."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from spdz_audit.experiment import load_tasks, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark', type=Path, default=ROOT/'experiments/benchmark.json')
    parser.add_argument('--output', type=Path, default=ROOT/'results/semantic')
    args = parser.parse_args()
    result = run(load_tasks(args.benchmark), args.output)
    print(json.dumps({key: result[key] for key in ['tasks', 'inputs', 'modes', 'paired_tasks']}, indent=2))


if __name__ == '__main__':
    main()
