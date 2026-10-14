"""Paired semantic experiment on a disclosed, deliberately targeted stress set."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import re
import subprocess

from .lowering import lower, lowered_callable, original_callable
from .metrics import paired_counts

MODES = ('baseline', 'safe')


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _validate_tasks(tasks: list[dict]) -> list[dict]:
    if not isinstance(tasks, list) or not tasks:
        raise ValueError('A nonempty task list is required')
    seen = set()
    for task in tasks:
        if not isinstance(task, dict) or set(task) != {'id', 'family', 'source', 'boundaries'}:
            raise ValueError('Each task needs exactly id, family, source and boundaries')
        for name in ('id', 'family'):
            if not isinstance(task[name], str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,63}', task[name]):
                raise ValueError('Task names must be simple safe identifiers')
        if task['id'] in seen:
            raise ValueError('Task IDs must be unique')
        seen.add(task['id'])
        if (not isinstance(task['boundaries'], list) or not task['boundaries']
                or any(type(x) not in (int, float) or not math.isfinite(x) for x in task['boundaries'])):
            raise ValueError('Boundaries must be nonempty finite numeric lists')
        lower(task['source'])
    return tasks


def load_tasks(path: Path) -> list[dict]:
    document = json.loads(path.read_text())
    if not isinstance(document, dict) or 'tasks' not in document:
        raise ValueError('Benchmark must be an object containing tasks')
    return _validate_tasks(document['tasks'])


def _inputs(task: dict, seeds: list[int], random_count: int) -> list[dict]:
    # Fixed-point-friendly held-out grid. Sampling is without replacement within
    # each seed and excludes explicit boundaries. Across seeds repeats are retained
    # and disclosed; input rows are NOT independent task samples for pass@k.
    records = [dict(kind='boundary', seed=None, x=x) for x in dict.fromkeys(task['boundaries'])]
    grid = [i / 16 for i in range(-256, 257) if i / 16 not in task['boundaries']]
    for seed in seeds:
        generator = random.Random(seed)
        records.extend(dict(kind='seeded_grid', seed=seed, x=x) for x in generator.sample(grid, random_count))
    return records


def run(tasks: list[dict], output: Path, seeds: list[int] | None = None, random_count: int = 100) -> dict:
    tasks = _validate_tasks(tasks)
    seeds = [17, 29, 43] if seeds is None else seeds
    if (not seeds or any(type(s) is not int for s in seeds) or len(set(seeds)) != len(seeds)
            or type(random_count) is not int or not 0 <= random_count <= 400):
        raise ValueError('Use unique integer seeds and 0..400 random inputs per seed')
    output.mkdir(parents=True, exist_ok=True)
    generated = output / 'generated'
    generated.mkdir(exist_ok=True)
    rows, task_results, manifest = [], [], []
    mode_counts = {mode: Counter() for mode in MODES}
    family_counts = defaultdict(lambda: {mode: Counter() for mode in MODES})
    for task in tasks:
        source = task['source']
        original = original_callable(source)
        functions = {mode: lowered_callable(source, mode) for mode in MODES}
        source_hashes = {'original': digest(source)}
        for mode in MODES:
            for backend, suffix in [('python', 'py'), ('mpspdz', 'mpc')]:
                code = lower(source, mode=mode, backend=backend)
                filename = f'{task["id"]}_{mode}.{suffix}'
                (generated/filename).write_text(code)
                source_hashes[f'{mode}_{backend}'] = digest(code)
        inputs = _inputs(task, seeds, random_count)
        good = {mode: [] for mode in MODES}
        for input_id, record in enumerate(inputs):
            x = record['x']
            try:
                expected = original(x)
            except Exception as error:
                raise ValueError(f'Reference invalid for {task["id"]} at x={x}: {error}') from error
            if not math.isfinite(expected):
                raise ValueError('Reference produced a nonfinite answer')
            for mode in MODES:
                row = dict(task=task['id'], family=task['family'], mode=mode,
                           input_id=input_id, **record, expected=expected)
                try:
                    actual = functions[mode](x)
                    row['actual'] = actual if math.isfinite(actual) else None
                    if not math.isfinite(actual):
                        row['status'] = 'nonfinite'
                    else:
                        row['status'] = 'pass' if math.isclose(actual, expected, abs_tol=1e-10, rel_tol=1e-10) else 'mismatch'
                except Exception as error:
                    row.update(status='exception', actual=None, exception_type=type(error).__name__, message=str(error))
                passed = row['status'] == 'pass'
                good[mode].append(passed)
                mode_counts[mode][row['status']] += 1
                family_counts[task['family']][mode][row['status']] += 1
                rows.append(row)
        task_results.append(dict(task=task['id'], family=task['family'], inputs=len(inputs),
                                 unique_inputs=len({r['x'] for r in inputs}),
                                 passed={mode: all(good[mode]) for mode in MODES},
                                 passed_inputs={mode: sum(good[mode]) for mode in MODES},
                                 paired_inputs=paired_counts(good['baseline'], good['safe'])))
        manifest.append(dict(task=task['id'], sha256=source_hashes))
    input_count = len(rows) // 2
    summary = dict(
        experiment='independent_domain_safety_stress_test', original_spdzeval=False,
        metric='deterministic_accuracy_not_pass_at_k', tasks=len(tasks), inputs=input_count,
        seeds=seeds, random_inputs_per_seed=random_count,
        input_distribution='unique boundaries plus seeded samples from {-256/16,...,256/16}; repeats across seeds retained',
        tolerance=dict(abs=1e-10, rel=1e-10), task_results=task_results,
        paired_tasks=paired_counts([t['passed']['baseline'] for t in task_results], [t['passed']['safe'] for t in task_results]),
        modes={}, families={})
    for mode in MODES:
        summary['modes'][mode] = dict(passed_tasks=sum(t['passed'][mode] for t in task_results),
                                      passed_inputs=mode_counts[mode]['pass'], outcomes=dict(mode_counts[mode]))
    for family, counts in sorted(family_counts.items()):
        entries = [t for t in task_results if t['family'] == family]
        summary['families'][family] = dict(tasks=len(entries), inputs=sum(t['inputs'] for t in entries),
                                          **{mode: dict(passed_tasks=sum(t['passed'][mode] for t in entries),
                                                        passed_inputs=counts[mode]['pass'], outcomes=dict(counts[mode])) for mode in MODES})
    raw = ''.join(json.dumps(row, sort_keys=True, allow_nan=False) + '\n' for row in rows)
    (output/'observations.jsonl').write_text(raw)
    (output/'observations.jsonl.gz').write_bytes(gzip.compress(raw.encode(), mtime=0))
    (output/'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    (output/'source_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], text=True))
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit, dirty = None, None
    provenance = dict(timestamp_utc=datetime.now(timezone.utc).isoformat(), python=platform.python_version(),
                      platform=platform.platform(), git_head=commit, git_dirty=dirty,
                      note='Source manifest hashes identify exact generated code even if worktree is dirty.',
                      benchmark_sha256=digest(json.dumps(tasks, sort_keys=True)),
                      observations_sha256=digest(raw), llm_calls=0)
    (output/'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    return summary
