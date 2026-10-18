import hashlib
import unittest

from scripts.apply_original_postprocess import patch_pipeline_text


class OriginalPatchTests(unittest.TestCase):
    source = ('from apply_feedback_tc import run_feedback\n'
              'def process():\n'
              '    output, a, b = run_feedback(args)\n'
              '    # Update IR\n'
              '    IR_entry = {}\n')

    def test_patch_runs_finalizer_after_feedback_before_recording(self):
        digest = hashlib.sha256(self.source.encode()).hexdigest()
        changed = patch_pipeline_text(self.source, digest)
        self.assertIn('from secret_arithmetic import preserve_secret_arithmetic', changed)
        self.assertLess(changed.index('run_feedback(args)'), changed.index('output, _privacy_rewrites'))
        self.assertLess(changed.index('output, _privacy_rewrites'), changed.index('IR_entry'))

    def test_patch_rejects_wrong_source_and_ambiguous_anchor(self):
        with self.assertRaisesRegex(ValueError, 'hash'):
            patch_pipeline_text(self.source, '0' * 64)
        source = self.source + '    # Update IR\n'
        with self.assertRaisesRegex(ValueError, 'anchor'):
            patch_pipeline_text(source, hashlib.sha256(source.encode()).hexdigest())
