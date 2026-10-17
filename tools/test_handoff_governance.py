#!/usr/bin/env python3
"""Public-safe technical governance guard. A passing result does NOT supply approvals."""
from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(path: str):
    with (ROOT / path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class HandoffGovernanceTests(unittest.TestCase):
    def test_all_current_mechanical_flags_have_a_specific_technical_row(self):
        inventory = rows("00_CONTROL/RELEASE_PRIVACY_CLASSIFICATION.csv")
        triage = rows("00_CONTROL/INDIVIDUAL_PRIVACY_TECHNICAL_REVIEW_2026-10-16.csv")
        self.assertEqual(len(triage), 67, "Historical baseline flags require individual assessment")
        by_path = {r["file_path"]: r for r in triage}
        self.assertEqual(len(by_path), len(triage))
        flags = {r["path"]: r for r in inventory if r["privacy_class"] == "REVIEW_REQUIRED"}
        self.assertEqual(set(flags), set(by_path),
                         "New flags require a human-limited technical disposition, not automatic clearance")
        for path, r in flags.items():
            self.assertEqual(by_path[path]["source_sha256"], r["sha256"], path)
            state = by_path[path]["review_status"]
            self.assertTrue("PENDING" in state or "NOT_FULLY_INSPECTED" in state, path)
            self.assertEqual(by_path[path]["closure_evidence"], "NOT_CLOSED", path)

    def test_51_historical_remediation_ids_reconciled_without_fabricated_closure(self):
        historical = rows("00_CONTROL/INDEPENDENT_REMEDIATION_REGISTER.csv")
        current = rows("00_CONTROL/CURRENT_51_FINDING_RECONCILIATION_2026-10-16.csv")
        self.assertEqual(len(historical), 51)
        self.assertEqual(len(current), 51)
        self.assertEqual({r["id"] for r in historical}, {r["finding_id"] for r in current})
        self.assertTrue(all(r["historic_finding_preserved"] == "YES" for r in current))
        self.assertTrue(all(r["formal_closure_status"].startswith("NOT_FORMALLY_CLOSED")
                            for r in current))

    def test_no_approvals_or_real_neighbor_observations_are_synthesized(self):
        approvals = rows("00_CONTROL/ATTRIBUTION_AND_PUBLICATION_APPROVAL.csv")
        self.assertGreaterEqual(len(approvals), 8)
        for row in approvals:
            self.assertTrue(row["approval_status"].startswith("AWAITING_"))
            self.assertEqual(row["private_approval_evidence_ref"], "")
            self.assertEqual(row["public_safe_approval_ref"], "")
            self.assertEqual(row["reviewed_utc"], "")
        for p in ["00_CONTROL/USABILITY_TEST_RESULTS_PUBLIC_SAFE.csv",
                  "00_CONTROL/USABILITY_DEFECT_AND_RETEST.csv"]:
            self.assertEqual(rows(p), [], "Do not fabricate actual participant/testing records")

    def test_private_data_controls_and_public_navigation_exist(self):
        for p in [
            ".github/CODEOWNERS", "CONTRIBUTING.md",
            "00_CONTROL/PRIVATE_INTAKE_AND_PORTABLE_METADATA_CONTRACT.md",
            "00_CONTROL/REUSE_AND_RECORD_PROVENANCE_2026-10-16.md",
            "00_CONTROL/REAL_NEIGHBOR_USABILITY_TEST_PROTOCOL_2026-10-16.md",
            "00_CONTROL/GOVERNANCE_AND_CONTINUITY_2026-10-16.md",
            "19_NEIGHBOR_REVIEW/README.md",
        ]:
            self.assertTrue((ROOT / p).is_file(), p)
        home = (ROOT / "README.md").read_text()
        self.assertIn("19_NEIGHBOR_REVIEW/README.md", home)


if __name__ == "__main__":
    unittest.main()
