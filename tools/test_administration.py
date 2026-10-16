#!/usr/bin/env python3
"""Read-only synthetic fixture tests for the Tom Street administration gate."""
from __future__ import annotations
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("check_administration.py")
spec = importlib.util.spec_from_file_location("check_administration", MODULE)
audit_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_mod)


class AdministrationGateTests(unittest.TestCase):
    def fixture(self, root: Path):
        def save(rel, content):
            p=root/rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        save("00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv",
             "gap_id,gap,status,request_file,submitted,submission_date,receipt_id,closure_evidence\n"
             "GAP-01,Approved site,REQUEST_DRAFTED,13_PUBLIC_RECORDS_REQUESTS/one.md,FALSE,,,\n")
        save("13_PUBLIC_RECORDS_REQUESTS/one.md", "# Request\nStatus: DRAFTED_NOT_SUBMITTED\n")
        registers=(("SOURCE_REGISTER", "source_id"), ("EVIDENCE_LEDGER", "claim_id"),
                   ("EXHIBIT_INDEX", "exhibit_id"), ("PERMIT_DOCUMENT_INVENTORY", "document_id"),
                   ("CHRONOLOGY", "event_id"))
        for fn,col in registers:save("00_CONTROL/"+fn+".csv",col+"\n"+col+"-1\n")
        save("00_CONTROL/DESIGN_VS_FIELD_MATRIX.csv",
             "item_id,approved_value,observed_or_surveyed_value,status\nDVF-01,NOT_OBTAINED,NOT_MEASURED,NOT_TESTABLE\n")
        save("00_CONTROL/RECORDS_ACQUISITION_MATRIX.csv",
             "agency_custodian,status,outcome\nSanta Rosa County Clerk (AcclaimWeb),PARTIAL_ORIGINAL_PLAT_OBTAINED,PARTIAL - original two-sheet Crescent Shores PLAT A/70 downloaded\n")
        save("00_CONTROL/OPEN_QUESTIONS.md", "# Open questions\nPLAT A/70 recovered\n")
        save("tools/build_reconciled_packet.py", 'manifest = {"file_scope": "Five explicitly named public-safe Markdown drafts"}')
        save("15_RECONCILED_DRAFTS/README.md", "# DRAFT\n")
        save("PUBLICATION_AND_VERSIONING.md", "# DRAFT controls\n")
        save("18_NEIGHBOR_TOOLKIT/README.md", "# Blank forms\n")
        for item in ("README.md", "NEIGHBOR_REVIEW_GUIDE.md", "PUBLIC_EVIDENCE_GUIDE.md",
                     "00_CONTROL/NEXT_ACTIONS.md", "00_CONTROL/COMMUNITY_READINESS_2026-10-16.md",
                     "00_CONTROL/DOCUMENT_STATUS_AND_NEIGHBOR_REVIEW_2026-10-16.md",
                     "00_CONTROL/READING_ORDER_AND_SNAPSHOT_STATUS.md",
                     "00_CONTROL/PRE_REQUEST_PRIMARY_SOURCE_REVIEW_2026-10-16.md"):
            save(item, "# Current\n")
        save("02_PROPERTY_AND_PARCELS/PRE_REQUEST_OCT16_PRIMARY_LOOKUPS/ORIGINAL_CLERK_PLAT_BOOK_A_PAGE_70.pdf", "synthetic fixture")
        return save

    def test_valid_fixture_passes(self):
        with tempfile.TemporaryDirectory() as path:
            self.fixture(Path(path))
            result = audit_mod.AdministrationAudit(Path(path)).run()
            self.assertEqual(result["errors"], [], result["errors"])

    def test_unsent_request_cannot_have_receipt(self):
        with tempfile.TemporaryDirectory() as path:
            save = self.fixture(Path(path))
            save("00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv",
                 "gap_id,gap,status,request_file,submitted,submission_date,receipt_id,closure_evidence\n"
                 "GAP-01,Plan,REQUEST_DRAFTED,13_PUBLIC_RECORDS_REQUESTS/one.md,FALSE,2026-10-16,ABC,\n")
            result = audit_mod.AdministrationAudit(Path(path)).run()
            self.assertTrue(any("unsent row" in x for x in result["errors"]))

    def test_submitted_request_requires_date_and_receipt(self):
        with tempfile.TemporaryDirectory() as path:
            save = self.fixture(Path(path))
            save("00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv",
                 "gap_id,gap,status,request_file,submitted,submission_date,receipt_id,closure_evidence\n"
                 "GAP-01,Plan,REQUEST_DRAFTED,13_PUBLIC_RECORDS_REQUESTS/one.md,TRUE,,,\n")
            result = audit_mod.AdministrationAudit(Path(path)).run()
            self.assertTrue(any("sent status" in x for x in result["errors"]))

    def test_clerk_partial_record_cannot_still_be_search_error(self):
        with tempfile.TemporaryDirectory() as path:
            save = self.fixture(Path(path))
            save("00_CONTROL/RECORDS_ACQUISITION_MATRIX.csv",
                 "agency_custodian,status,outcome\nSanta Rosa County Clerk (AcclaimWeb),ERROR_REQUIRES_FOLLOWUP,PARTIAL - original two-sheet Crescent Shores PLAT A/70 downloaded\n")
            result = audit_mod.AdministrationAudit(Path(path)).run()
            self.assertTrue(any("Clerk matrix" in x for x in result["errors"]))

    def test_duplicate_source_id_is_error(self):
        with tempfile.TemporaryDirectory() as path:
            save = self.fixture(Path(path))
            save("00_CONTROL/SOURCE_REGISTER.csv", "source_id\nSRC-001\nSRC-001\n")
            result = audit_mod.AdministrationAudit(Path(path)).run()
            self.assertTrue(any("duplicate source_id" in x for x in result["errors"]))

    def test_bad_link_is_error(self):
        with tempfile.TemporaryDirectory() as path:
            save = self.fixture(Path(path))
            save("18_NEIGHBOR_TOOLKIT/README.md", "# Guide\n[Broken](nonexistent.pdf)\n")
            result = audit_mod.AdministrationAudit(Path(path)).run()
            self.assertTrue(any("broken local link" in x for x in result["errors"]))

    def test_unapproved_media_in_public_toolkit_is_error(self):
        with tempfile.TemporaryDirectory() as path:
            save = self.fixture(Path(path))
            save("18_NEIGHBOR_TOOLKIT/my_family_photo.jpg", "fixture")
            result = audit_mod.AdministrationAudit(Path(path)).run()
            self.assertTrue(any("unexpected files" in x for x in result["errors"]))

    def test_five_source_contract_cannot_regress_to_four(self):
        with tempfile.TemporaryDirectory() as path:
            save = self.fixture(Path(path))
            save("tools/build_reconciled_packet.py", 'manifest = {"file_scope": "Four explicitly named public-safe Markdown drafts"}')
            result = audit_mod.AdministrationAudit(Path(path)).run()
            self.assertTrue(any("obsolete file_scope count" in x for x in result["errors"]))


if __name__ == "__main__":
    unittest.main()
