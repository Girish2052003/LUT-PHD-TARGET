import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.check_paired_smoke_gate import CRITICAL_PATHS, check_gate


class PairedGateTests(unittest.TestCase):
    def test_gate_binds_prepared_modification_and_harness_to_accepted_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pins = {}
            for path in CRITICAL_PATHS:
                file = root / path
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text('reviewed source\n')
                pins[path] = hashlib.sha256(file.read_bytes()).hexdigest()
            preserved = root / 'accepted-manifest.json'
            preserved.write_text('{"extension":"reviewed"}\n')
            built = root / 'build-manifest.json'
            built.write_bytes(preserved.read_bytes())
            receipt = {'acceptance': {'status': 'PASS', 'scope': '32-pair restricted smoke',
                       'independently_checked': True, 'launch_source_sha256': pins,
                       'modification_manifest': {'path': 'accepted-manifest.json',
                           'sha256': hashlib.sha256(preserved.read_bytes()).hexdigest()}}}
            check_gate(root, receipt, built)
            built.write_text('{"extension":"new untested"}\n')
            with self.assertRaisesRegex(ValueError, 'modification'):
                check_gate(root, receipt, built)
            built.write_bytes(preserved.read_bytes())
            (root / 'scripts/replay_modified.py').write_text('new untested harness\n')
            with self.assertRaisesRegex(ValueError, 'source'):
                check_gate(root, receipt, built)

    def test_gate_rejects_incomplete_approval_or_launch_pins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for accepted in (False, True):
                receipt = {'acceptance': {'status': 'PASS', 'scope': '32-pair restricted smoke',
                           'independently_checked': accepted, 'launch_source_sha256': {}}}
                with self.assertRaises(ValueError):
                    check_gate(root, receipt, root / 'missing')
