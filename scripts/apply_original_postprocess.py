"""Prepare a separately pinned modification without executing original code."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'src/pipeline.py': 'a60dfcdc454f6da53436c5b6819bf4d3999a29ff0647bbdf78842b81137d5eaf',
    'src/pipeline-mp.py': '23c51c95a6892da6c2812e7eee65243d404c0423dd7e478758a4c0fc0b50b52f',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def patch_pipeline_text(source, expected_sha):
    if hashlib.sha256(source.encode()).hexdigest() != expected_sha:
        raise ValueError('Original pipeline hash mismatch')
    anchor = 'from apply_feedback_tc import run_feedback\n'
    markers = list(re.finditer(r'(?m)^( +)# Update IR$', source))
    if source.count(anchor) != 1 or len(markers) != 1:
        raise ValueError('Original patch anchor missing or ambiguous')
    indent = markers[0].group(1)
    changed = source.replace(anchor, anchor + 'from secret_arithmetic import preserve_secret_arithmetic\n', 1)
    changed = changed.replace(indent + '# Update IR',
                              indent + '# Girish modification: preserve secret comparison masks.\n'
                              + indent + 'output, _privacy_rewrites = preserve_secret_arithmetic(output, test_function_name)\n\n'
                              + indent + '# Update IR', 1)
    ast.parse(changed)  # Syntax inspection only; never execute author code here.
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', required=True)
    args = parser.parse_args()
    build = Path(args.build_dir).resolve()
    manifest = json.loads((build / 'source_manifest.json').read_text())
    for item in manifest['baseline_files']:
        if sha(build / 'baseline' / item['path']) != item['sha256']:
            raise ValueError('Prepared original source changed: ' + item['path'])
    modified = build / 'modified'
    shutil.copytree(build / 'baseline', modified)
    changes, patches = [], []
    for relative, original_sha in PINS.items():
        source = (build / 'baseline' / relative).read_text()
        changed = patch_pipeline_text(source, original_sha)
        target = modified / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(changed)
        patches.extend(difflib.unified_diff(source.splitlines(True), changed.splitlines(True),
                                           fromfile='a/' + relative, tofile='b/' + relative))
        changes.append({'path': relative, 'original_sha256': original_sha, 'modified_sha256': sha(target)})
    extension = modified / 'src/secret_arithmetic.py'
    shutil.copyfile(ROOT / 'research/modifications/secret_arithmetic.py', extension)
    (modified / 'original-pipeline.patch').write_text(''.join(patches))
    metadata = {'scope': 'Final-output comparison-mask postprocessor in both actual original pipeline entry points',
                'author_archive_sha256': manifest['author_archive_sha256'], 'pipeline_changes': changes,
                'extension_path': 'src/secret_arithmetic.py', 'extension_sha256': sha(extension),
                'patch_sha256': sha(modified / 'original-pipeline.patch'), 'generation_executed': False,
                'attribution': 'Original SPDZCoder source: https://zenodo.org/records/18152253, CC BY 4.0. Pipeline additions and secret_arithmetic.py are Girish project modifications.'}
    (modified / 'modification_manifest.json').write_text(json.dumps(metadata, indent=2) + '\n')
    shutil.copyfile(ROOT / 'scripts/replay_modified.py', build / 'replay_modified.py')
    shutil.copyfile(ROOT / 'research/modifications/Dockerfile', build / 'Dockerfile')
    print(json.dumps(metadata, indent=2))


if __name__ == '__main__':
    main()
