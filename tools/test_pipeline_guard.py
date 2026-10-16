#!/usr/bin/env python3
"""Prove every non-dry-run pipeline mode is opt-in before scripts can run."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).with_name('autonomous_evidence_pipeline.py')
spec = importlib.util.spec_from_file_location('tom_street_pipeline', MODULE)
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)


class PipelineSafetyTests(unittest.TestCase):
    def test_every_non_dry_run_mode_requires_consent(self):
        for mode in ('full', 'discover', 'acquire', 'sync', 'verify', 'build'):
            with self.subTest(mode=mode), patch.object(pipeline, 'missing_required_scripts', return_value=[]), \
                patch.object(pipeline, 'run_phase_sequential', side_effect=AssertionError('unexpected execution')), \
                patch.object(pipeline, 'run_phase_parallel', side_effect=AssertionError('unexpected execution')):
                buffer = io.StringIO()
                with contextlib.redirect_stderr(buffer):
                    result = pipeline.main(['--mode', mode])
                self.assertEqual(result, 3, (mode, buffer.getvalue()))
                self.assertIn('BLOCKED_OPERATOR_CONFIRMATION_REQUIRED', buffer.getvalue())

    def test_dry_run_is_safe_and_reports_real_missing_files(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = pipeline.main(['--mode', 'full', '--dry-run'])
        self.assertEqual(code, 0)
        data = json.loads(buf.getvalue())
        declared = {name for group in data['phases'].values() for name in group}
        expected = {name for name in declared if not (MODULE.parent / name).is_file()}
        self.assertEqual(set(data['missing_required_scripts']), expected)
        self.assertEqual(data['ready_to_execute'], not expected)


if __name__ == '__main__':
    unittest.main()
