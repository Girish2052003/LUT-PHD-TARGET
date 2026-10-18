#!/usr/bin/env python3
"""Recompute paired evidence from raw streams and independently reinsert source.

Reads downloaded source as data only. No candidate or original module executes.
Run at the same research revision as the experiment.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.modifications.secret_arithmetic import preserve_secret_arithmetic
from scripts.prepare_original_replay import AUTHOR_SHA, MP_COMMIT, MP_ARCHIVE_SHA
from scripts.apply_original_postprocess import PINS, patch_pipeline_text
from scripts.replay_modified import make_cases, text_sha, validate_pairs
from scripts.replay_original import EVALUATOR_SHA, classify_attempt, digest


def inserted_source(code, template):
    lines = template.splitlines(keepends=True)
    positions = [i for i, line in enumerate(lines) if re.search(r'\#(\s)?insert(\s|\_)here(\s)\#', line)]
    if not positions or not code:
        raise ValueError('Cannot reconstruct original insertion')
    index = positions[0]
    lines[index] = lines[index] if lines[index].endswith('\n') else lines[index] + '\n'
    return ''.join(lines[:index + 1]) + code + ('' if code.endswith('\n') else '\n') + ''.join(lines[index + 1:])


def check_observations(row, stdout):
    if (row['authorized_outputs'] != re.findall(r'^AUTHORIZED=([^\n]+)$', stdout, re.M)
            or row['public_openings'] != [list(match) for match in re.findall(r'^OPEN\[(\d+)\]=([^\n]+)$', stdout, re.M)]):
        raise ValueError('Diagnostic observations differ from raw stdout')


def verify_pair_run(root, baseline):
    root = root.resolve()
    environment = json.loads((root / 'environment.json').read_text())
    manifest = json.loads((root / 'source_manifest.json').read_text())
    identity = json.loads((root / 'identity.json').read_text())
    reference_identity = json.loads((ROOT / 'research/evidence/2026-10-14/identity_verified_scores.json').read_text())
    if identity != reference_identity:
        raise ValueError('Original identity differs from accepted 313-task ledger')
    accepted_environment = ROOT / 'research/evidence/2026-10-15/original-smoke/smoke'
    if manifest != json.loads((accepted_environment / 'source_manifest.json').read_text()):
        raise ValueError('Source manifest differs from independently accepted baseline')
    for name in ('installed-packages.txt', 'os-packages.txt'):
        if digest(root / name) != digest(accepted_environment / name):
            raise ValueError('Resolved packages differ from the pinned baseline: ' + name)
    if (manifest['author_archive_sha256'] != AUTHOR_SHA or manifest['mp_spdz_commit'] != MP_COMMIT
            or manifest['binary_archive_sha256'] != MP_ARCHIVE_SHA
            or manifest['mascot_binary_sha256'] != '2a592fec9a9f9d0e7e8148bdf9ee7a67811dd6781c333981b386f3d1b7c8a5b3'):
        raise ValueError('Pinned original environment changed')
    if (environment['original_evaluator_sha256'] != EVALUATOR_SHA or environment['api_calls'] != 0
            or environment['protocol'] != 'MASCOT' or environment['parties'] != 2
            or environment['limits'] != {'cpus': 2, 'memory_bytes': 6442450944, 'pids': 256}):
        raise ValueError('Paired execution conditions changed')
    for row in manifest['baseline_files']:
        if digest(baseline / row['path']) != row['sha256']:
            raise ValueError('Provided original tree differs from manifest')
    modification = json.loads((root / 'modification_manifest.json').read_text())
    if digest(ROOT / 'research/modifications/secret_arithmetic.py') != modification['extension_sha256']:
        raise ValueError('Verify using the exact experiment postprocessor revision')
    if digest(root / 'modified-entrypoints/secret_arithmetic.py') != modification['extension_sha256']:
        raise ValueError('Preserved extension differs')
    if digest(root / 'original-pipeline.patch') != modification['patch_sha256']:
        raise ValueError('Preserved patch differs')
    for row in modification['pipeline_changes']:
        if row['path'] not in PINS or row['original_sha256'] != PINS[row['path']]:
            raise ValueError('Original pipeline origin mismatch')
        expected = patch_pipeline_text((baseline / row['path']).read_text(), PINS[row['path']])
        if (root / 'modified-entrypoints' / Path(row['path']).name).read_text() != expected:
            raise ValueError('Patched pipeline differs from regenerated original-source patch')
        if digest(root / 'modified-entrypoints' / Path(row['path']).name) != row['modified_sha256']:
            raise ValueError('Preserved patched pipeline differs')
    if {row['path'] for row in modification['pipeline_changes']} != set(PINS) or len(modification['pipeline_changes']) != 2:
        raise ValueError('Expected both original pipeline entry points')
    cases = make_cases(baseline, identity, preserve_secret_arithmetic, environment['split'])
    specs = [{k: v for k, v in c.items() if k not in ('baseline', 'modified', 'template', 'original', 'transformed')} for c in cases]
    if specs != json.loads((root / 'case-specifications.json').read_text()):
        raise ValueError('Case specification not regenerated from the fixed protocol')
    case_map = {c['pair_id']: (i, c) for i, c in enumerate(cases)}
    records = [json.loads(line) for line in (root / 'paired-records.jsonl').read_text().splitlines()]
    validation = validate_pairs(records, specs, strict_native=environment['split'] is None)
    for position, row in enumerate(records):
        index, case = case_map[row['pair_id']]
        variant = row['variant']
        if any(row[k] != v for k, v in specs[index].items()):
            raise ValueError('Record metadata differs from case specification')
        expected_order = ('baseline', 'modified') if index % 2 == 0 else ('modified', 'baseline')
        if row['pair_index'] != index or row['execution_order'] != expected_order.index(variant) or position != 2 * index + row['execution_order']:
            raise ValueError('Matched execution ordering changed')
        folder = (root / row['log_path']).resolve()
        if not folder.is_relative_to(root) or folder != root / 'logs' / case['pair_id'] / variant:
            raise ValueError('Unexpected raw evidence path')
        if json.loads((folder / 'record.json').read_text()) != row:
            raise ValueError('Per-case record mismatch')
        expected_files = {'candidate.py.txt': case[variant], 'template.mpc': case['template'],
                          'original.py.txt': case.get('original', case['baseline']),
                          'transformed.py.txt': case.get('transformed', case['modified'])}
        for filename, content in expected_files.items():
            if (folder / filename).read_text() != content:
                raise ValueError('Source/observer/template differs from expected transformation: ' + filename)
        for key, filename in (('source_sha256', 'candidate.py.txt'), ('template_sha256', 'template.mpc'),
                              ('original_source_sha256', 'original.py.txt'), ('transformed_source_sha256', 'transformed.py.txt')):
            if row[key] != digest(folder / filename):
                raise ValueError('Per-case digest mismatch')
        if case['inputs'] is None:
            if row['inputs_sha256'] is not None or (folder / 'Input-P0-0.txt').exists():
                raise ValueError('Invented native party inputs')
        else:
            inputs = ' '.join(map(str, case['inputs'])) + '\n'
            if (folder / 'Input-P0-0.txt').read_text() != inputs or row['inputs_sha256'] != text_sha(inputs):
                raise ValueError('Private input mismatch')
        if not isinstance(row['duration_seconds'], (int, float)) or not math.isfinite(row['duration_seconds']) or row['duration_seconds'] < 0:
            raise ValueError('Invalid duration')
        attempts, stdout, accepted = row['attempts'], '', False
        if len(attempts) > 3 or (attempts and attempts[-1]['timed_out'] and len(attempts) != 3):
            raise ValueError('Original retry budget changed')
        if not attempts and case[variant]:
            raise ValueError('Missing nonempty candidate execution')
        for number, attempt in enumerate(attempts):
            source = (folder / f'attempt-{number}.mpc').read_text()
            stdout = (folder / f'attempt-{number}.stdout.txt').read_text()
            stderr = (folder / f'attempt-{number}.stderr.txt').read_text()
            if source != inserted_source(case[variant], case['template']):
                raise ValueError('Original evaluator insertion mismatch')
            for value, key in ((source, 'combined_source_sha256'), (stdout, 'stdout_sha256'), (stderr, 'stderr_sha256')):
                if text_sha(value) != attempt[key]:
                    raise ValueError('Raw attempt digest mismatch')
            task = case['task_id'].split('/')[1]
            if attempt['command'] != f'/mp-spdz/Scripts/compile-run.py -E mascot /run/paired-baseline/evaluation/evaluation_storage/{task}.mpc':
                raise ValueError('Original command/protocol changed')
            timeout = (150 if any(s in case['task_id'].split('/')[0] for s in ('math', 'ufunc')) else 60) + 30 * number
            if attempt['timeout_seconds'] != timeout or (number < len(attempts) - 1 and not attempt['timed_out']):
                raise ValueError('Original retry progression changed')
            runtime = 'mascot-party.x' in stderr and 'Running ' in stderr
            status = classify_attempt(attempt['returncode'], attempt['timed_out'], attempt['schedule_present'], runtime)
            if attempt['runtime_launch_marker'] != runtime or any(attempt[k] != v for k, v in status.items()):
                raise ValueError('Attempt classification mismatch')
            if runtime and len(list(folder.glob(f'attempt-{number}-party-*.log'))) != 2:
                raise ValueError('Missing two-party logs')
            accepted = not attempt['timed_out'] and 'pass' in stdout.lower() and 'Traceback' not in stderr.strip()
        last = attempts[-1] if attempts else {'compile_status': 'NOT_RUN', 'runtime_status': 'NOT_RUN', 'failure_class': 'empty_candidate'}
        if any(row[k] != last[k] for k in ('compile_status', 'runtime_status')) or (row['oracle_status'] == 'ACCEPT') != accepted:
            raise ValueError('Final classification differs from raw streams')
        failure = last['failure_class'] or (None if accepted else 'oracle_reject')
        if row['failure_class'] != failure:
            raise ValueError('Failure class mismatch')
        check_observations(row, stdout)
    summary = json.loads((root / 'paired-summary.json').read_text())
    if (summary['validation'] != validation or summary['baseline_source_unchanged'] is not True or summary['live_model_calls'] != 0
            or summary['executions'] != len(records) or summary['expected_executions'] != len(records)):
        raise ValueError('Run summary differs from raw verification')
    return records, validation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    args = parser.parse_args()
    records, validation = verify_pair_run(args.root, args.baseline)
    print(json.dumps({'raw_evidence_verified': True, **validation}, indent=2))


if __name__ == '__main__':
    main()
