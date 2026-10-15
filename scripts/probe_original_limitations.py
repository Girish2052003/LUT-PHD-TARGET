#!/usr/bin/env python3
"""Explicit diagnostic witnesses, separate from archived-candidate benchmark scores.

Executes the unchanged author evaluator only in the restricted replay container.
Known-wrong functions are diagnostic mutations, never claimed model responses.
Privacy observations print only values already publicly opened by original code.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from types import SimpleNamespace

if __package__:
    from .replay_original import EVALUATOR_SHA, Recorder, digest, reset_execution_artifacts, verify_baseline
else:
    from replay_original import EVALUATOR_SHA, Recorder, digest, reset_execution_artifacts, verify_baseline


def observe_original_reveals(code):
    """Wrap the public result of each existing opening; never open an extra value."""
    class Observe(ast.NodeTransformer):
        def __init__(self):
            self.sites = []

        def visit_Call(self, node):
            self.generic_visit(node)
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'reveal':
                site = len(self.sites)
                self.sites.append({'site': site, 'line': node.lineno, 'expression': ast.unparse(node)})
                return ast.copy_location(ast.Call(func=ast.Name(id='__witness_observe_open', ctx=ast.Load()),
                                                 args=[node, ast.Constant(site)], keywords=[]), node)
            return node
    observer = Observe()
    tree = observer.visit(ast.parse(code))
    instrumented = ast.unparse(ast.fix_missing_locations(tree)) + '''\n\ndef __witness_observe_open(value, site):
    print_ln('OPEN[%s]=%s', site, value)
    return value
'''
    return instrumented, observer.sites


def privacy_template(task, length):
    call = 'count_distinct(secret_values)' if task == 'count_distinct' else 'lower_bound(secret_values, 4)'
    return f'''# Diagnostic harness, not an original native template.
# Party 0 owns the values. Length (3), x (4 for lower_bound) and result are public.
# insert here #
secret_values = sfix.Array({length})
for i in range({length}):
    secret_values[i] = sfix.get_input_from(0)
answer = {call}
print_ln('AUTHORIZED=%s', answer.reveal())
'''


def source_row(root, task_id):
    split, name = task_id.split('/')
    rows = [json.loads(line) for line in (root / f'data/stage_3_output/experiment-1-{split}.jsonl').read_text().splitlines()]
    return next(r for r in rows if r['test_name'] == name)


def validate_diagnostics(records):
    """Demand semantic evidence, not merely successful process termination."""
    if len(records) != 16 or len({r['case_id'] for r in records}) != 16:
        raise ValueError('Expected 16 unique diagnostic/control cases')
    if any(r['runtime_status'] != 'PASS' for r in records):
        raise ValueError('A diagnostic/control did not complete MASCOT execution')
    native = [r for r in records if r['template_kind'] == 'byte-identical native template']
    if len(native) != 8 or not all(r['author_oracle_accepted'] for r in native):
        raise ValueError('Native oracle false-positive hypothesis was not confirmed')
    for r in native:
        expected_marker = not (r['task_id'] == 'branch_test/pass_or_not' and r['source_kind'] == 'diagnostic_zero_mutation')
        if r['native_success_marker'] != expected_marker:
            raise ValueError('Native success-marker prediction differs from observation')
    findings = {}
    for task, pairs, expected, opening_count in (
        ('loop_test/count_distinct', [(1, 1, 2), (1, 2, 2)], 2, 3),
        ('loop_test/lower_bound', [(1, 3, 5), (2, 3, 6)], 1, 6),
    ):
        group = [r for r in records if r['task_id'] == task]
        keys = {(tuple(r['inputs']), r['source_kind']) for r in group}
        wanted = {(p, kind) for p in pairs for kind in ('archived_private_input', 'public_opening_observer')}
        if len(group) != 4 or keys != wanted:
            raise ValueError('Missing or duplicate private-input control/observation')
        traces = []
        for r in sorted(group, key=lambda x: tuple(x['inputs'])):
            if len(r['authorized_outputs']) != 1:
                raise ValueError('Expected exactly one authorized output')
            result = float(r['authorized_outputs'][0])
            if not math.isfinite(result) or result != expected:
                raise ValueError('Authorized output differs between paired inputs or instrumentation')
            if r['source_kind'] == 'public_opening_observer':
                trace = [(int(site), float(value)) for site, value in r['public_openings']]
                if len(trace) != opening_count or not all(math.isfinite(v) for _, v in trace):
                    raise ValueError('Opening count/value differs from original source prediction')
                values = r['inputs']
                if task.endswith('count_distinct'):
                    expected_trace = [(0, float(values[j] != values[i])) for i in range(3) for j in range(i)]
                    if trace != expected_trace:
                        raise ValueError('Opened inequality pattern differs from the private inputs')
                elif [v for site, v in trace if site == 0] != [4 - x for x in values]:
                    raise ValueError('Opened differences do not reconstruct the private array')
                traces.append(trace)
        if len(traces) != 2 or traces[0] == traces[1]:
            raise ValueError('Same permitted output did not yield distinct public observations')
        findings[task] = {'same_authorized_output': expected, 'distinct_public_traces': True,
                          'observed_openings_per_execution': opening_count,
                          'original_and_observed_outputs_agree': True}
    return {'confirmed': True, 'native_oracle_false_positives': 4, 'privacy_witnesses': findings}


def main():
    if os.environ.get('REPLAY_CONTAINER') != '1' or os.geteuid() == 0 or {p.name for p in Path('/sys/class/net').iterdir()} != {'lo'}:
        raise RuntimeError('Use the restricted non-root, network-none Docker launcher')
    if any(k in os.environ for k in ('OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GITHUB_TOKEN', 'GH_TOKEN', 'AZURE_OPENAI_API_KEY')):
        raise RuntimeError('No credentials permitted')
    output = Path('/results')
    if any(output.iterdir()):
        raise ValueError('A fresh result directory is required')
    baseline = Path('/baseline')
    manifest = json.loads(Path('/harness/source_manifest.json').read_text())
    verify_baseline(manifest)
    original_evaluator = baseline / 'evaluation/evaluate_experimental-mp.py'
    if digest(original_evaluator) != EVALUATOR_SHA:
        raise ValueError('Original evaluator changed')
    os.chdir('/run');sys.path.insert(0, str(baseline))
    spec = importlib.util.spec_from_file_location('original_evaluator', original_evaluator)
    evaluator = importlib.util.module_from_spec(spec);spec.loader.exec_module(evaluator)
    setup = subprocess.run(['bash', '/mp-spdz/Scripts/setup-ssl.sh', '2'], capture_output=True, text=True, timeout=60)
    (output / 'ssl-setup.log').write_text(setup.stdout + setup.stderr)
    if setup.returncode:
        raise RuntimeError('Test certificate setup failed')
    # Redirect only the evaluator's location-based lookup to disposable copies.
    # The evaluator's source/function body and the immutable baseline are intact.
    diagnostic_root = Path('/run/diagnostic-baseline')
    storage = diagnostic_root / 'evaluation/evaluation_storage';storage.mkdir(parents=True)
    evaluator.__file__ = str(diagnostic_root / 'evaluation/evaluate_experimental-mp.py')
    identity = {r['task_id']: r for r in json.loads(Path('/harness/identity.json').read_text())['task_records']}
    cases = []
    for task_id in ('branch_test/pass_or_not', 'branch_test/median', 'loop_test/second_largest', 'syntax_test/second_largest'):
        name = task_id.split('/')[1]
        reference = identity[task_id]
        candidate = next(i for i, accepted in enumerate(reference['archived_acceptance']) if accepted)
        control = source_row(baseline, task_id)[f'response_{candidate}']
        assert hashlib.sha256(control.encode()).hexdigest() == reference['candidate_sha256']['spdzcoder'][candidate]
        wrong = 'def pass_or_not(score):\n    return sint(0), sint(0)\n' if name == 'pass_or_not' else f'def {name}(arr):\n    return sfix(0)\n'
        for kind, code in (('archived_control', control), ('diagnostic_zero_mutation', wrong)):
            cases.append({'case_id': task_id.replace('/', '--') + '--' + kind, 'task_id': task_id,
                          'source_kind': kind, 'original_candidate_id': candidate if kind == 'archived_control' else None,
                          'diagnostic_intended_decision': 'REJECT' if kind == 'diagnostic_zero_mutation' else 'CONTROL',
                          'code': code, 'template': (baseline / f'data/input_data/{task_id}.mpc').read_text(),
                          'template_kind': 'byte-identical native template', 'inputs': None, 'observer_sites': []})
    for task_id, pairs, expected in (('loop_test/count_distinct', [[1, 1, 2], [1, 2, 2]], 2),
                                    ('loop_test/lower_bound', [[1, 3, 5], [2, 3, 6]], 1)):
        original = source_row(baseline, task_id)['response_1']
        assert hashlib.sha256(original.encode()).hexdigest() == identity[task_id]['candidate_sha256']['spdzcoder'][1]
        observed, sites = observe_original_reveals(original)
        for pair, inputs in enumerate(pairs):
            for kind, code in (('archived_private_input', original), ('public_opening_observer', observed)):
                cases.append({'case_id': task_id.replace('/', '--') + f'--pair-{pair}--{kind}', 'task_id': task_id,
                              'source_kind': kind, 'original_candidate_id': 1,
                              'original_source_sha256': hashlib.sha256(original.encode()).hexdigest(),
                              'code': code, 'template': privacy_template(task_id.split('/')[1], len(inputs)),
                              'template_kind': 'explicit diagnostic private-input harness', 'inputs': inputs,
                              'expected_authorized_output': expected, 'observer_sites': sites if kind == 'public_opening_observer' else []})
    records = []
    for case in cases:
        split, name = case['task_id'].split('/')
        native = diagnostic_root / f'data/input_data/{case["task_id"]}.mpc'
        native.parent.mkdir(parents=True, exist_ok=True);native.write_text(case['template'])
        for old_input in Path('/run/Player-Data').glob('Input-P*'):
            old_input.unlink()
        if case['inputs'] is not None:
            Path('/run/Player-Data/Input-P0-0').write_text(' '.join(map(str, case['inputs'])) + '\n')
        reset_execution_artifacts(Path('/run'), storage / f'{name}.mpc')
        folder = output / case['case_id']
        recorder = Recorder(folder, name, storage)
        evaluator.subprocess = SimpleNamespace(run=recorder.run, TimeoutExpired=subprocess.TimeoutExpired)
        accepted = evaluator.insert_compile_run(SimpleNamespace(spdz_path='/mp-spdz'), split, name, case['code'])
        last = recorder.attempts[-1]
        stdout = (folder / f'attempt-{len(recorder.attempts)-1}.stdout.txt').read_text()
        record = {k: v for k, v in case.items() if k not in ('code', 'template')}
        record.update(source_sha256=hashlib.sha256(case['code'].encode()).hexdigest(), template_sha256=digest(native),
                      author_oracle_accepted=accepted, runtime_status=last['runtime_status'], attempts=recorder.attempts,
                      native_success_marker='Pass the test' in stdout.splitlines(),
                      authorized_outputs=re.findall(r'^AUTHORIZED=([^\n]+)$', stdout, re.M),
                      public_openings=re.findall(r'^OPEN\[(\d+)\]=([^\n]+)$', stdout, re.M))
        (folder / 'candidate.py.txt').write_text(case['code']);(folder / 'template.mpc').write_text(case['template'])
        (folder / 'record.json').write_text(json.dumps(record, indent=2) + '\n')
        records.append(record)
        print(json.dumps({k: record[k] for k in ('case_id', 'runtime_status', 'author_oracle_accepted', 'authorized_outputs', 'public_openings')}), flush=True)
    verify_baseline(manifest)
    try:
        validation = validate_diagnostics(records)
    except (ValueError, KeyError, TypeError) as exc:
        validation = {'confirmed': False, 'error': str(exc)}
    summary = {'scope': 'Diagnostic witnesses; excluded from archived-candidate benchmark scores',
               'research_commit': os.environ.get('RESEARCH_COMMIT'), 'container_image_id': os.environ.get('REPLAY_IMAGE_ID'),
               'original_evaluator_sha256': EVALUATOR_SHA, 'baseline_source_unchanged': True, 'live_model_calls': 0,
               'cases': records, 'source_manifest': manifest, 'validation': validation,
               'policy': 'For private-input probes only, party0 array values are secret; length, x and returned count/index are public. Attacker is an honest-but-curious other protocol participant observing values explicitly opened to all parties. Both parties run on one isolated test host; this does not model host compromise.',
               'observer_scope': 'Observer wrapper prints and returns each already-opened value; it introduces no additional reveal calls. Original and instrumented executions are both retained.'}
    (output / 'diagnostic-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    shutil.copyfile('/harness/installed-packages.txt', output / 'installed-packages.txt')
    shutil.copyfile('/harness/os-packages.txt', output / 'os-packages.txt')
    if not validation['confirmed']:
        raise SystemExit('A diagnostic hypothesis was not confirmed; inspect the preserved evidence: ' + validation['error'])


if __name__ == '__main__':
    main()
