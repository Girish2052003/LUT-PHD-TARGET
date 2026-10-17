#!/usr/bin/env python3
"""Complete native paired accounting; no security diagnostics enter pass rates."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import random
import re
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.replay_original import digest
from scripts.verify_paired_replay import verify_pair_run


def paired_binary(before, after):
    if not before or len(before) != len(after) or any(type(x) is not bool for x in before + after):
        raise ValueError('Expected nonempty matched Boolean task outcomes')
    n = len(before)
    gains = sum(not b and a for b, a in zip(before, after))
    losses = sum(b and not a for b, a in zip(before, after))
    discordant = gains + losses
    p = min(1.0, 2 * sum(math.comb(discordant, k) for k in range(min(gains, losses) + 1)) / 2**discordant) if discordant else 1.0
    differences = [int(a) - int(b) for b, a in zip(before, after)]
    rng = random.Random(20261016)
    samples = sorted(100 * sum(rng.choices(differences, k=n)) / n for _ in range(10000)) if discordant else [0.0] * 10000
    return {'tasks': n, 'baseline_accepted': sum(before), 'modified_accepted': sum(after),
            'gained': gains, 'lost': losses, 'unchanged': n - discordant,
            'difference_percentage_points': 100 * (gains - losses) / n,
            'mcnemar_exact_two_sided_p': p,
            'bootstrap_95_percentile_pp': [samples[249], samples[9749]],
            'bootstrap_replicates': 10000, 'bootstrap_seed': 20261016,
            'uncertainty_scope': 'Exploratory task-resampling interval for this fixed archive; a degenerate interval with no observed discordance is not a population-equivalence proof. No multiplicity-adjusted significance claim.'}


def aggregate_native(records, identity):
    tasks = [r['task_id'] for r in identity['task_records']]
    if len(set(tasks)) != len(tasks) or not tasks:
        raise ValueError('Invalid task inventory')
    wanted = {(t, c, v) for t in tasks for c in (0, 1) for v in ('baseline', 'modified')}
    seen = {}
    for row in records:
        key = (row['task_id'], row['candidate_id'], row['variant'])
        if row['kind'] != 'native' or type(row['candidate_id']) is not int or key not in wanted or key in seen:
            raise ValueError('Unexpected, nonnative or duplicate paired outcome')
        if row['oracle_status'] not in {'ACCEPT', 'REJECT'}:
            raise ValueError('Malformed author acceptance')
        seen[key] = row
    if set(seen) != wanted:
        raise ValueError(f'Incomplete paired native replay: expected {len(wanted)}, got {len(seen)}')

    def accepted(task, candidate, variant):
        return seen[(task, candidate, variant)]['oracle_status'] == 'ACCEPT'

    def metric(ids, variant):
        first = sum(accepted(t, 0, variant) for t in ids)
        second = sum(accepted(t, 1, variant) for t in ids)
        union = sum(any(accepted(t, c, variant) for c in (0, 1)) for t in ids)
        return {'tasks': len(ids), 'first_accepted': first, 'second_accepted': second, 'union_accepted': union,
                'first_percent': 100 * first / len(ids), 'second_percent': 100 * second / len(ids), 'union_percent': 100 * union / len(ids)}

    categories = sorted({t.split('/')[0] for t in tasks})
    variants = {}
    for variant in ('baseline', 'modified'):
        rows = [r for r in records if r['variant'] == variant]
        durations = [r['duration_seconds'] for r in rows]
        if any(not isinstance(x, (int, float)) or not math.isfinite(x) or x < 0 for x in durations):
            raise ValueError('Malformed duration')
        variants[variant] = {'overall': metric(tasks, variant),
                             'categories': {s: metric([t for t in tasks if t.split('/')[0] == s], variant) for s in categories},
                             'compile_statuses': dict(Counter(r['compile_status'] for r in rows)),
                             'runtime_statuses': dict(Counter(r['runtime_status'] for r in rows)),
                             'failure_classes': dict(Counter(r['failure_class'] or 'none' for r in rows)),
                             'accepted_without_completed_runtime': sum(r['oracle_status'] == 'ACCEPT' and r['runtime_status'] != 'PASS' for r in rows),
                             'candidate_wall_seconds': {'total': sum(durations), 'mean': statistics.mean(durations), 'median': statistics.median(durations)}}
    matrix = []
    for task in tasks:
        for candidate in (0, 1):
            before, after = (seen[(task, candidate, v)] for v in ('baseline', 'modified'))
            if any(before[k] != after[k] for k in ('original_source_sha256', 'transformed_source_sha256')):
                raise ValueError('Paired transformation identity mismatch')
            fields = ('compile_status', 'runtime_status', 'oracle_status', 'failure_class', 'duration_seconds')
            matrix.append({'task_id': task, 'candidate_id': candidate,
                           'source_changed': before['original_source_sha256'] != before['transformed_source_sha256'],
                           'baseline': {k: before[k] for k in fields}, 'modified': {k: after[k] for k in fields},
                           'acceptance_delta': int(after['oracle_status'] == 'ACCEPT') - int(before['oracle_status'] == 'ACCEPT'),
                           'wall_seconds_delta': after['duration_seconds'] - before['duration_seconds'],
                           'rewrite_events': after['rewrite_events']})
    outcomes = {}
    for measure in ('first', 'second', 'union'):
        decisions = [[(any(accepted(t, c, v) for c in (0, 1)) if measure == 'union' else accepted(t, 0 if measure == 'first' else 1, v)) for t in tasks]
                     for v in ('baseline', 'modified')]
        outcomes[measure] = paired_binary(*decisions)
    transitions = {'rejected_to_accepted': sum(r['acceptance_delta'] == 1 for r in matrix),
                   'accepted_to_rejected': sum(r['acceptance_delta'] == -1 for r in matrix),
                   'unchanged_decision': sum(r['acceptance_delta'] == 0 for r in matrix)}
    groups = {}
    for changed in (False, True):
        rows = [r for r in matrix if r['source_changed'] == changed]
        groups['changed_source' if changed else 'byte_identical_source'] = {
            'candidate_pairs': len(rows), 'accepted_to_rejected': sum(r['acceptance_delta'] == -1 for r in rows),
            'rejected_to_accepted': sum(r['acceptance_delta'] == 1 for r in rows),
            'wall_seconds_difference_mean': statistics.mean(r['wall_seconds_delta'] for r in rows) if rows else None,
            'note': 'One paired run per candidate; variation in byte-identical sources is not a postprocessing effect. Timing is descriptive.'}
    summary = {'scope': 'Unchanged original oracle acceptance on complete authentic final-stage native data; not independent functional correctness or model generation',
               'tasks': len(tasks), 'candidate_pairs': len(matrix), 'executions': len(records), 'live_model_calls': 0,
               'variants': variants, 'paired_task_outcomes': outcomes, 'candidate_transitions': transitions, 'source_change_groups': groups,
               'ablation': 'Only postprocessor enabled versus disabled; same authentic candidate bytes, template, native oracle, compiler, resource budget and protocol within each pair'}
    return summary, matrix


def runtime_costs(folder, attempts):
    """Reported last-attempt costs; absent/ambiguous metrics stay null."""
    if not attempts:
        return {}
    text = (folder / f'attempt-{len(attempts)-1}.stdout.txt').read_text()
    patterns = {'runtime_seconds': r'^Time = ([\d.eE+-]+) seconds\s*$',
                'global_sent_mb': r'^Global data sent = ([\d.eE+-]+) MB \(all parties\)\s*$',
                'compiler_integer_opens': r'^\s*(\d+) integer opens\s*$',
                'compiler_integer_triples': r'^\s*(\d+) integer triples\s*$',
                'compiler_integer_bits': r'^\s*(\d+) integer bits\s*$',
                'compiler_vm_rounds': r'^\s*(\d+) virtual machine rounds\s*$'}
    result = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text, re.M)
        result[key] = float(matches[0]) if len(matches) == 1 and math.isfinite(float(matches[0])) else None
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    records, costs, pins = [], [], set()
    for file in sorted(args.root.rglob('paired-records.jsonl')):
        root = file.parent
        env = json.loads((root / 'environment.json').read_text())
        if env['mode'] != 'full_native_split' or not env['split']:
            raise ValueError('Smoke/diagnostic evidence must not enter native aggregate')
        rows, _ = verify_pair_run(root, args.baseline)
        records.extend(rows)
        pins.add((env['research_commit'], digest(root / 'source_manifest.json'), digest(root / 'modification_manifest.json'),
                  digest(root / 'installed-packages.txt'), digest(root / 'os-packages.txt')))
        for row in rows:
            costs.append({k: row[k] for k in ('task_id', 'candidate_id', 'variant', 'runtime_status')} |
                         {'last_attempt_reported_costs': runtime_costs(root / row['log_path'], row['attempts'])})
    if len(pins) != 1:
        raise ValueError('Missing or mixed research/environment pins')
    identity = json.loads((ROOT / 'research/evidence/2026-10-14/identity_verified_scores.json').read_text())
    summary, matrix = aggregate_native(records, identity)
    summary['research_commit'] = next(iter(pins))[0]
    args.output.mkdir(parents=True, exist_ok=False)
    for filename, data in (('summary.json', summary), ('failure_matrix.json', matrix), ('reported_costs.json', costs)):
        (args.output / filename).write_text(json.dumps(data, indent=2) + '\n')
    (args.output / 'paired-records.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in sorted(records, key=lambda r: (r['task_id'], r['candidate_id'], r['variant']))))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
