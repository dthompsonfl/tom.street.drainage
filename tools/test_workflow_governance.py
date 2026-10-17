#!/usr/bin/env python3
"""Fail closed if unreviewed GitHub workflows can write to main.

This is a static safety guard, not a permissions/branch-protection probe.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


class TestWorkflowGovernance(unittest.TestCase):
    def test_all_workflows_are_repository_read_only(self):
        files = sorted(WORKFLOWS.glob("*.yml"))
        self.assertGreaterEqual(len(files), 27)
        unsafe = [p.name for p in files if re.search(
            r"(?m)^\s*contents:\s*write\s*(?:#.*)?$", p.read_text(encoding="utf-8")
        )]
        self.assertEqual(unsafe, [], "Workflows requiring writes must use reviewed integration")

    def test_no_direct_main_writer_or_ignored_rebase_failure(self):
        found = []
        for p in WORKFLOWS.glob("*.yml"):
            source = p.read_text(encoding="utf-8")
            if re.search(r"(?m)^\s*(?:git\s+push\s+origin\s+(?:HEAD:main|main)|git\s+push\s+--force)", source):
                found.append(f"{p.name}: direct or force push")
            if re.search(r"git\s+(?:pull|rebase)[^\n]*\|\|\s*true", source):
                found.append(f"{p.name}: ignored Git synchronization failure")
        self.assertEqual(found, [])

    def test_manual_acquisition_produces_a_reviewable_artifact_without_publishing(self):
        capture_jobs = [
            p for p in WORKFLOWS.glob("*.yml")
            if p.name.startswith("acquire-") or p.name in {
                "audit-fdep-aerial-provenance.yml",
                "audit-historical-evidence.yml",
                "preserve-public-authorities.yml",
                "preserve-reviewed-question-sources.yml",
                "render-crescent-shores-plat.yml",
            }
        ]
        self.assertEqual(len(capture_jobs), 21)
        for p in capture_jobs:
            workflow = p.read_text(encoding="utf-8")
            self.assertIn("actions/upload-artifact@v4", workflow, p.name)
            self.assertIn("00_CONTROL/tools/classify_for_release.py --check", workflow, p.name)
            self.assertIn("retention-days: 7", workflow, p.name)
            self.assertNotIn("contents: write", workflow, p.name)

    def test_source_acquisitions_are_operator_initiated_only(self):
        for p in WORKFLOWS.glob("*.yml"):
            if not (p.name.startswith("acquire-") or p.name in {
                "audit-fdep-aerial-provenance.yml",
                "audit-historical-evidence.yml",
                "preserve-public-authorities.yml",
                "preserve-reviewed-question-sources.yml",
                "render-crescent-shores-plat.yml",
            }):
                continue
            text = p.read_text(encoding="utf-8")
            self.assertRegex(text, r"(?m)^\s*workflow_dispatch\s*:", p.name)
            self.assertNotRegex(text, r"(?m)^\s*push\s*:", p.name)


if __name__ == "__main__":
    unittest.main()
