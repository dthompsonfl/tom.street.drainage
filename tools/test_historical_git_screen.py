#!/usr/bin/env python3
"""Test technical history audit with *fictional* short-lived credentials only."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

PATH = Path(__file__).with_name("audit_historical_git_refs.py")
spec = importlib.util.spec_from_file_location("historical_git_audit", PATH)
audit = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(audit)


def git(root: Path, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


class HistoricalScreenTests(unittest.TestCase):
    def test_detects_removed_fictional_secret_without_public_disclosure_or_history_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source-repo"
            root.mkdir()
            git(root, "init", "-q")
            git(root, "config", "user.name", "Synthetic Fixture Only")
            git(root, "config", "user.email", "fixture@example.invalid")
            archive = root / "portal_session_api_calls.json"
            fictional = "ACCESS_TOKEN=fictional_for_test_only_0123456789abcdef"
            archive.write_text(fictional + "\n", encoding="ascii")
            git(root, "add", ".")
            git(root, "commit", "-m", "fictional history", "-q")
            archive.unlink()
            git(root, "add", "-A")
            git(root, "commit", "-m", "remove fictional fixture", "-q")
            before = git(root, "rev-parse", "HEAD").strip()
            saved = audit.ROOT
            try:
                audit.ROOT = root
                output = root / "summary.json"
                capture = io.StringIO()
                with contextlib.redirect_stdout(capture):
                    summary = audit.review(output)
                raw = output.read_text(encoding="utf-8")
                self.assertNotIn(fictional, raw)
                self.assertNotIn(fictional, capture.getvalue())
                self.assertEqual(summary["source_bytes_modified"], 0)
                self.assertFalse(summary["git_checkout_shallow"])
                self.assertGreaterEqual(summary["potential_credential_like_blobs"], 1)
                self.assertEqual(before, git(root, "rev-parse", "HEAD").strip())
                self.assertGreaterEqual(summary["scan_counts"]["reachable_blobs"], 1)
            finally:
                audit.ROOT = saved


if __name__ == "__main__":
    unittest.main()
