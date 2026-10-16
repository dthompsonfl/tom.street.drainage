#!/usr/bin/env python3
"""Synthetic offline checks for the read-only public administrative snapshot."""
from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("report_current_status", HERE / "report_current_status.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def writecsv(root: Path, path: str, rows: list[dict[str, str]]):
    out = root / path
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def fixture(root: Path):
    for _, path, key in module.COUNTS:
        writecsv(root, path, [{key: "TEST-01"}])
    writecsv(root, "00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv", [
        {"gap_id":"GAP-01", "status":"REQUEST_DRAFTED", "submitted":"FALSE", "submission_date":"", "receipt_id":"", "closure_evidence":""},
        {"gap_id":"GAP-02", "status":"PARTIAL_OBTAINED", "submitted":"FALSE", "submission_date":"", "receipt_id":"", "closure_evidence":""},
    ])
    writecsv(root, "00_CONTROL/DESIGN_VS_FIELD_MATRIX.csv", [{"item_id":"DVF-01", "status":"NOT_TESTABLE"}])
    writecsv(root, "00_CONTROL/INDEPENDENT_REMEDIATION_REGISTER.csv", [{"id":"TS-001", "status":"OPEN"}])


class LiveStatusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        fixture(self.root)

    def test_counts_from_current_rows_and_historical_not_live(self):
        data = module.collect(self.root)
        self.assertEqual(data["record_requests"]["unresolved"], 2)
        self.assertEqual(data["record_requests"]["gap_rows"], 2)
        self.assertEqual(data["record_requests"]["sent_with_dated_receipt"], 0)
        self.assertEqual(data["historical_audit"]["status"], "FROZEN_AUDIT_NOT_CURRENT_DEFECT_COUNT")
        self.assertEqual(data["design_vs_field"]["statuses"], {"NOT_TESTABLE": 1})

    def test_sent_without_receipt_rejected(self):
        path = "00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv"
        writecsv(self.root, path, [{"gap_id":"GAP-01", "status":"REQUEST_DRAFTED", "submitted":"TRUE", "submission_date":"2026-10-16", "receipt_id":"", "closure_evidence":""}])
        with self.assertRaisesRegex(module.StatusError,"requires a dated receipt"):
            module.collect(self.root)

    def test_unsent_with_receipt_rejected(self):
        path = "00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv"
        writecsv(self.root, path, [{"gap_id":"GAP-01", "status":"REQUEST_DRAFTED", "submitted":"FALSE", "submission_date":"", "receipt_id":"PRIVATE-EMAIL", "closure_evidence":""}])
        with self.assertRaisesRegex(module.StatusError,"unsent request"):
            module.collect(self.root)

    def test_closed_without_source_rejected(self):
        path = "00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv"
        writecsv(self.root, path, [{"gap_id":"GAP-01", "status":"CLOSED", "submitted":"TRUE", "submission_date":"2026-10-16", "receipt_id":"PUBLIC-ID", "closure_evidence":""}])
        with self.assertRaisesRegex(module.StatusError,"source-linked"):
            module.collect(self.root)

    def test_duplicate_gap_id_rejected(self):
        path = "00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv"
        row = {"gap_id":"GAP-01", "status":"REQUEST_DRAFTED", "submitted":"FALSE", "submission_date":"", "receipt_id":"", "closure_evidence":""}
        writecsv(self.root, path, [row,row])
        with self.assertRaisesRegex(module.StatusError,"duplicate gap_id"):
            module.collect(self.root)

    def test_does_not_echo_private_references(self):
        path = "00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv"
        writecsv(self.root, path, [{"gap_id":"GAP-01", "status":"SUBMITTED_AWAITING_RECORDS", "submitted":"TRUE", "submission_date":"2026-10-16", "receipt_id":"secret-internal-contact+phone-123", "closure_evidence":""}])
        raw = module.markdown(module.collect(self.root))
        self.assertNotIn("secret-internal-contact", raw)
        self.assertIn("recorded dated submission and receipt: **1**", raw)

    def test_no_output_files_written(self):
        before = sorted(x.as_posix() for x in self.root.rglob("*"))
        module.collect(self.root)
        after = sorted(x.as_posix() for x in self.root.rglob("*"))
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
