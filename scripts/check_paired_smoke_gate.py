#!/usr/bin/env python3
"""Bind a full launch to the exact independently accepted smoke modification."""
import argparse
import hashlib
import json
from pathlib import Path

CRITICAL_PATHS = {
    'scripts/apply_original_postprocess.py', 'scripts/replay_modified.py',
    'scripts/verify_paired_replay.py', 'research/modifications/secret_arithmetic.py',
    'research/modifications/Dockerfile', 'scripts/run_original_replay_container.sh',
    'scripts/prepare_original_replay.py', 'scripts/replay_original.py',
    'scripts/probe_original_limitations.py', 'research/replay/requirements.txt',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_gate(root, receipt, built_manifest):
    root = root.resolve()
    accepted = receipt['acceptance']
    if (accepted['status'] != 'PASS' or accepted['scope'] != '32-pair restricted smoke'
            or accepted['independently_checked'] is not True):
        raise ValueError('Targeted smoke is not independently accepted')
    pins = accepted['launch_source_sha256']
    if set(pins) != CRITICAL_PATHS:
        raise ValueError('Accepted launch source pins are incomplete')
    for path, expected in pins.items():
        if sha(root / path) != expected:
            raise ValueError('Launch source changed since accepted smoke: ' + path)
    record = accepted['modification_manifest']
    preserved = (root / record['path']).resolve()
    if not preserved.is_relative_to(root) or not preserved.is_file() or sha(preserved) != record['sha256']:
        raise ValueError('Accepted modification evidence missing or changed')
    if sha(built_manifest) != record['sha256']:
        raise ValueError('Prepared modification differs from accepted smoke')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--built-manifest', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    check_gate(root, json.loads(args.receipt.read_text()), args.built_manifest)
    print('Full launch uses the exact independently accepted smoke modification and critical harness sources.')


if __name__ == '__main__':
    main()
