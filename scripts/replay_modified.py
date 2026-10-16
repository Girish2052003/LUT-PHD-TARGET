#!/usr/bin/env python3
"""Matched deterministic postprocessing experiment, confined to the replay container.

No generation is simulated. The exact added finalizer statement from each pinned
original pipeline is executed on authentic archived final-stage candidate bytes.
Native benchmark cases and separately specified private-input probes stay distinct.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace

if __package__:
    from .replay_original import EVALUATOR_SHA, Recorder, digest, reset_execution_artifacts, verify_baseline
    from .probe_original_limitations import observe_original_reveals, source_row
else:
    from replay_original import EVALUATOR_SHA, Recorder, digest, reset_execution_artifacts, verify_baseline
    from probe_original_limitations import observe_original_reveals, source_row

TARGETS = {'loop_test/count_distinct': 1, 'loop_test/is_ascending': 0}
INPUTS = [[], [0], [1, 1, 2], [1, 2, 2], [-2, -1, 0], [3, 2, 1],
          [0, 0, 0], [-0.5, 0, 0.5], [0.5, -0.5, 0.5], [-1024, 0, 1024]]


def text_sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


def expected_openings(task, values):
    if task == 'count_distinct':
        return [[0, float(values[j] != values[i])] for i in range(len(values)) for j in range(i)]
    if task == 'is_ascending':
        return [[0, float(a >= b)] for a, b in zip(values, values[1:])]
    raise ValueError('Unknown private-input task')


def private_template(task, values, value_type):
    size = len(values)
    init = f'{value_type}.Array({size})' if size else '[]'
    return f'''# Explicit new private-input diagnostic; not a native benchmark template.
# Party 0 values are private; length, type and the returned count/bit are public.
# insert here #
secret_values = {init}
for i in range({size}):
    secret_values[i] = {value_type}.get_input_from(0)
answer = {task}(secret_values)
print_ln('AUTHORIZED=%s', answer.reveal())
'''


def make_cases(baseline, identity, transform, split=None):
    """Read and transform source text only; do not execute downloaded candidates."""
    cases = []
    references = {r['task_id']: r for r in identity['task_records']}
    selected = [(t, c) for t in references for c in (0, 1) if t.split('/')[0] == split] if split else list(TARGETS.items())
    if not selected:
        raise ValueError('Unknown or empty original split')
    originals = {}
    for task_id, candidate in selected:
        original = source_row(baseline, task_id)[f'response_{candidate}']
        if text_sha(original) != references[task_id]['candidate_sha256']['spdzcoder'][candidate]:
            raise ValueError('Archived candidate identity mismatch')
        template = (baseline / f'data/input_data/{task_id}.mpc').read_text()
        if text_sha(template) != references[task_id]['template_sha256']:
            raise ValueError('Native template identity mismatch')
        changed, events = transform(original, task_id.split('/')[1])
        originals[(task_id, candidate)] = (original, changed, events)
        cases.append({'pair_id': task_id.replace('/', '--') + f'--c{candidate}--native',
                      'task_id': task_id, 'candidate_id': candidate, 'kind': 'native',
                      'inputs': None, 'input_type': None, 'template': template,
                      'baseline': original, 'modified': changed, 'rewrite_events': events})
    if split:
        return cases
    for task_id, candidate in TARGETS.items():
        task = task_id.split('/')[1]
        original, changed, events = originals[(task_id, candidate)]
        probes = [('sfix', values) for values in INPUTS] + [('sint', [1, 1, 2]), ('sint', [-2**30, 0, 2**30])]
        for index, (value_type, values) in enumerate(probes):
            expected = len(set(values)) if task == 'count_distinct' else int(all(a < b for a, b in zip(values, values[1:])))
            for observed in ([True, False] if index in (2, 3) else [True]):
                before, sites_before = observe_original_reveals(original) if observed else (original, [])
                after, sites_after = observe_original_reveals(changed) if observed else (changed, [])
                cases.append({'pair_id': f'{task}--{value_type}--{index}--' + ('observed' if observed else 'control'),
                              'task_id': task_id, 'candidate_id': candidate,
                              'kind': 'private_observed' if observed else 'private_control',
                              'inputs': values, 'input_type': value_type, 'expected_output': expected,
                              'expected_baseline_openings': expected_openings(task, values) if observed else [],
                              'template': private_template(task, values, value_type),
                              'baseline': before, 'modified': after, 'original': original,
                              'transformed': changed, 'rewrite_events': events,
                              'observer_sites': {'baseline': sites_before, 'modified': sites_after}})
    # Locally authored counterexamples from review, never claimed author outputs.
    for label, statements in (
        ('zero_fold', 'acc = sint(1)\n    acc *= 0\n    acc += 1'),
        ('match_bind', 'acc = sint(1)\n    match cint(1):\n        case acc:\n            pass'),
    ):
        code = 'def public_return(arr, x):\n    ' + statements + '\n    acc *= (arr[0] != x).reveal()\n    return acc\n'
        changed, events = transform(code, 'public_return')
        if changed != code or events:
            raise ValueError('Unsupported public-return fixture must remain byte-identical')
        cases.append({'pair_id': 'synthetic--' + label, 'task_id': 'diagnostic/public_return',
                      'candidate_id': None, 'kind': 'synthetic_fallback', 'inputs': [1], 'input_type': 'sint',
                      'expected_output': 1, 'expected_baseline_openings': [], 'rewrite_events': events,
                      'baseline': code, 'modified': changed,
                      'template': "# Locally authored public-return regression fixture.\n# insert here #\narr = sint.Array(1)\narr[0] = sint.get_input_from(0)\nprint_ln('AUTHORIZED=%s', public_return(arr, 2))\n"})
    return cases


def validate_pairs(records, specs, strict_native=True):
    """Accept diagnostic claims only when complete pairs match the fixed policy."""
    expected = {(s['pair_id'], v) for s in specs for v in ('baseline', 'modified')}
    seen = {(r['pair_id'], r['variant']): r for r in records}
    if len(expected) != 2 * len(specs) or len(seen) != len(records) or set(seen) != expected:
        raise ValueError('Missing, unexpected or duplicate paired records')
    for spec in specs:
        before, after = (seen[(spec['pair_id'], v)] for v in ('baseline', 'modified'))
        if any(before[k] != after[k] for k in ('template_sha256', 'inputs_sha256', 'original_source_sha256')):
            raise ValueError('Paired source/input/template mismatch')
        for row in (before, after):
            if row['exception'] is not None:
                raise ValueError('Unresolved harness error')
            if (row['compile_status'] not in {'PASS', 'FAIL', 'TIMEOUT', 'NOT_RUN', 'UNKNOWN'}
                    or row['runtime_status'] not in {'PASS', 'FAIL', 'TIMEOUT', 'NOT_RUN'}
                    or row['oracle_status'] not in {'ACCEPT', 'REJECT'}):
                raise ValueError('Malformed paired execution status')
            if spec['kind'] == 'native' and not strict_native:
                continue  # All native failures remain in full comparison denominators.
            if row['compile_status'] != 'PASS' or row['runtime_status'] != 'PASS':
                raise ValueError('A required smoke/diagnostic did not complete MASCOT')
            if spec['kind'] == 'native':
                if row['oracle_status'] != 'ACCEPT':
                    raise ValueError('Modified or original target failed the unchanged native oracle')
                continue
            outputs = row['authorized_outputs']
            if len(outputs) != 1 or not math.isfinite(float(outputs[0])) or float(outputs[0]) != spec['expected_output']:
                raise ValueError('Authorized output not preserved')
            trace = [[int(site), float(value)] for site, value in row['public_openings']]
            wanted = spec['expected_baseline_openings'] if row['variant'] == 'baseline' else []
            if trace != wanted:
                raise ValueError('Unexpected public opening trace')
    return {'confirmed': True, 'pairs': len(specs), 'executions': len(records),
            'native_pairs': sum(s['kind'] == 'native' for s in specs),
            'private_pairs': sum(s['kind'].startswith('private_') for s in specs),
            'synthetic_pairs': sum(s['kind'] == 'synthetic_fallback' for s in specs)}


def load_pipeline_finalizers(manifest):
    """Execute only the new finalizer slice, not unavailable model-dependent stages."""
    root = Path('/modified')
    modification = json.loads((root / 'modification_manifest.json').read_text())
    if modification['author_archive_sha256'] != manifest['author_archive_sha256']:
        raise ValueError('Modification origin changed')
    changes = {r['path']: r for r in modification['pipeline_changes']}
    for row in manifest['baseline_files']:
        change = changes.get(row['path'])
        if change and change['original_sha256'] != row['sha256']:
            raise ValueError('Modification original hash mismatch')
        if digest(root / row['path']) != (change['modified_sha256'] if change else row['sha256']):
            raise ValueError('Unexpected change to modified source tree')
    extension = root / modification['extension_path']
    if digest(extension) != modification['extension_sha256'] or digest(root / 'original-pipeline.patch') != modification['patch_sha256']:
        raise ValueError('Modification pin mismatch')
    module_spec = importlib.util.spec_from_file_location('secret_arithmetic', extension)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    expected = ast.parse('output, _privacy_rewrites = preserve_secret_arithmetic(output, test_function_name)').body[0]
    finalizers = []
    for relative in ('src/pipeline.py', 'src/pipeline-mp.py'):
        statements = [n for n in ast.walk(ast.parse((root / relative).read_text()))
                      if isinstance(n, ast.Assign) and ast.dump(n) == ast.dump(expected)]
        if len(statements) != 1:
            raise ValueError('Exact patched original finalizer missing or ambiguous')
        finalizers.append(compile(ast.fix_missing_locations(ast.Module(body=statements, type_ignores=[])), relative, 'exec'))

    def transform(source, name):
        results = []
        for finalizer in finalizers:
            namespace = {'preserve_secret_arithmetic': module.preserve_secret_arithmetic,
                         'output': source, 'test_function_name': name, '__builtins__': {}}
            exec(finalizer, namespace)
            results.append((namespace['output'], namespace['_privacy_rewrites']))
        if results[0] != results[1]:
            raise ValueError('Original entry-point finalizers disagree')
        return results[0]
    return transform, modification


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--split', help='Full native comparison for one original category; otherwise diagnostic smoke')
    args = parser.parse_args()
    if (os.environ.get('REPLAY_CONTAINER') != '1' or os.geteuid() == 0
            or {p.name for p in Path('/sys/class/net').iterdir()} != {'lo'}):
        raise RuntimeError('Use the restricted non-root, network-none Docker launcher')
    if any(k in os.environ for k in ('OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GITHUB_TOKEN', 'GH_TOKEN', 'AZURE_OPENAI_API_KEY')):
        raise RuntimeError('No credentials permitted')
    output, baseline = Path('/results'), Path('/baseline')
    if any(output.iterdir()):
        raise ValueError('A fresh result directory is required')
    manifest = json.loads(Path('/harness/source_manifest.json').read_text())
    identity = json.loads(Path('/harness/identity.json').read_text())
    verify_baseline(manifest)
    transform, modification = load_pipeline_finalizers(manifest)
    cases = make_cases(baseline, identity, transform, args.split)
    specs = [{k: v for k, v in c.items() if k not in ('baseline', 'modified', 'template', 'original', 'transformed')} for c in cases]
    (output / 'case-specifications.json').write_text(json.dumps(specs, indent=2) + '\n')
    (output / 'modification_manifest.json').write_text(json.dumps(modification, indent=2) + '\n')
    (output / 'modified-entrypoints').mkdir()
    for name in ('pipeline.py', 'pipeline-mp.py', 'secret_arithmetic.py'):
        shutil.copyfile('/modified/src/' + name, output / 'modified-entrypoints' / name)
    shutil.copyfile('/modified/original-pipeline.patch', output / 'original-pipeline.patch')
    for name in ('source_manifest.json', 'identity.json', 'installed-packages.txt', 'os-packages.txt'):
        shutil.copyfile('/harness/' + name, output / name)
    environment = {'research_commit': os.environ.get('RESEARCH_COMMIT'), 'container_image_id': os.environ.get('REPLAY_IMAGE_ID'),
                   'python': sys.version, 'platform': platform.platform(), 'protocol': 'MASCOT', 'parties': 2,
                   'cpu_models': sorted(set(re.findall(r'^model name\s*:\s*(.*)$', Path('/proc/cpuinfo').read_text(), re.M))),
                   'limits': {'cpus': 2, 'memory_bytes': 6442450944, 'pids': 256}, 'api_calls': 0,
                   'original_evaluator_sha256': EVALUATOR_SHA, 'mode': 'full_native_split' if args.split else 'smoke',
                   'split': args.split, 'randomness': 'Original compiler/protocol defaults; no RNG seed overridden',
                   'pair_order': 'baseline first for even pair index; modified first for odd; same image and job',
                   'generation_scope': 'Only exact added finalizer statements executed; no preceding model stages or responses simulated'}
    (output / 'environment.json').write_text(json.dumps(environment, indent=2) + '\n')
    evaluator_path = baseline / 'evaluation/evaluate_experimental-mp.py'
    if digest(evaluator_path) != EVALUATOR_SHA:
        raise ValueError('Original evaluator changed')
    os.chdir('/run')
    sys.path.insert(0, str(baseline))
    module_spec = importlib.util.spec_from_file_location('original_evaluator', evaluator_path)
    evaluator = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(evaluator)
    setup = subprocess.run(['bash', '/mp-spdz/Scripts/setup-ssl.sh', '2'], capture_output=True, text=True, timeout=60)
    (output / 'ssl-setup.log').write_text(setup.stdout + setup.stderr)
    if setup.returncode:
        raise RuntimeError('Test certificate setup failed')
    scratch = Path('/run/paired-baseline')
    storage = scratch / 'evaluation/evaluation_storage'
    storage.mkdir(parents=True)
    evaluator.__file__ = str(scratch / 'evaluation/evaluate_experimental-mp.py')
    records = []
    for index, case in enumerate(cases):
        split, task = case['task_id'].split('/')
        template = scratch / f'data/input_data/{case["task_id"]}.mpc'
        template.parent.mkdir(parents=True, exist_ok=True)
        template.write_text(case['template'])
        for order, variant in enumerate(('baseline', 'modified') if index % 2 == 0 else ('modified', 'baseline')):
            for old_input in Path('/run/Player-Data').glob('Input-P*'):
                old_input.unlink()
            input_text = None if case['inputs'] is None else ' '.join(map(str, case['inputs'])) + '\n'
            if input_text is not None:
                Path('/run/Player-Data/Input-P0-0').write_text(input_text)
            code = case[variant]
            folder = output / 'logs' / case['pair_id'] / variant
            reset_execution_artifacts(Path('/run'), storage / f'{task}.mpc')
            recorder = Recorder(folder, task, storage)
            evaluator.subprocess = SimpleNamespace(run=recorder.run, TimeoutExpired=subprocess.TimeoutExpired)
            accepted, error = False, None
            start = time.monotonic()
            try:
                accepted = evaluator.insert_compile_run(SimpleNamespace(spdz_path='/mp-spdz'), split, task, code) if code else False
            except Exception as exc:
                error = f'{type(exc).__name__}: {exc}'
            duration = time.monotonic() - start
            last = recorder.attempts[-1] if recorder.attempts else {'compile_status': 'NOT_RUN', 'runtime_status': 'NOT_RUN',
                    'failure_class': 'empty_candidate' if not code else 'harness_error'}
            stdout = (folder / f'attempt-{len(recorder.attempts)-1}.stdout.txt').read_text() if recorder.attempts else ''
            row = {k: v for k, v in specs[index].items()}
            row.update(variant=variant, pair_index=index, execution_order=order, source_sha256=text_sha(code),
                       original_source_sha256=text_sha(case.get('original', case['baseline'])),
                       transformed_source_sha256=text_sha(case.get('transformed', case['modified'])),
                       template_sha256=digest(template), inputs_sha256=text_sha(input_text) if input_text is not None else None,
                       compile_status=last['compile_status'], runtime_status=last['runtime_status'],
                       failure_class='harness_error' if error else (last['failure_class'] or (None if accepted else 'oracle_reject')),
                       oracle_status='ACCEPT' if accepted else 'REJECT', duration_seconds=duration, exception=error,
                       attempts=recorder.attempts, log_path=folder.relative_to(output).as_posix(),
                       authorized_outputs=re.findall(r'^AUTHORIZED=([^\n]+)$', stdout, re.M),
                       public_openings=re.findall(r'^OPEN\[(\d+)\]=([^\n]+)$', stdout, re.M))
            (folder / 'candidate.py.txt').write_text(code)
            (folder / 'template.mpc').write_text(case['template'])
            (folder / 'original.py.txt').write_text(case.get('original', case['baseline']))
            (folder / 'transformed.py.txt').write_text(case.get('transformed', case['modified']))
            if input_text is not None:
                (folder / 'Input-P0-0.txt').write_text(input_text)
            (folder / 'record.json').write_text(json.dumps(row, indent=2) + '\n')
            with (output / 'paired-records.jsonl').open('a') as stream:
                stream.write(json.dumps(row) + '\n')
            records.append(row)
            print(json.dumps({k: row[k] for k in ('pair_id', 'variant', 'compile_status', 'runtime_status', 'oracle_status', 'authorized_outputs', 'public_openings')}), flush=True)
    verify_baseline(manifest)
    load_pipeline_finalizers(manifest)
    try:
        validation = validate_pairs(records, specs, strict_native=not args.split)
    except (ValueError, KeyError, TypeError) as exc:
        validation = {'confirmed': False, 'error': str(exc)}
    summary = {'validation': validation, 'baseline_source_unchanged': True, 'live_model_calls': 0,
               'expected_executions': 2 * len(cases), 'executions': len(records),
               'scope': 'Matched deterministic finalizer replay; private/synthetic probes excluded from native rates'}
    (output / 'paired-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    if not validation['confirmed']:
        raise SystemExit('Paired validation failed; preserve and inspect all evidence: ' + validation['error'])


if __name__ == '__main__':
    main()
