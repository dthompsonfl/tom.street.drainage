#!/usr/bin/env python3
"""Read-only Tom Street administrative and publication consistency gate.

Checks documentary bookkeeping, not legal compliance, drainage design, whether
an agency answered a request, or permission to distribute homeowner evidence.
No external network, no write, no importing executable acquisition scripts.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


class AdministrationAudit:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.details: dict = {}

    def require(self, condition: bool, explanation: str):
        if not condition:
            self.errors.append(explanation)

    def read_text(self, relative_path: str) -> str:
        p = self.root / relative_path
        if not p.is_file():
            self.errors.append(f"required file absent: {relative_path}")
            return ""
        return p.read_text(encoding="utf-8")

    def csv(self, relative_path: str, required: tuple[str, ...]) -> list[dict[str, str]]:
        raw = self.read_text(relative_path)
        if not raw:
            return []
        reader = csv.DictReader(raw.splitlines())
        headers = reader.fieldnames or []
        self.require(all(k in headers for k in required), f"missing columns in {relative_path}: {set(required)-set(headers)}")
        records = list(reader)
        self.require(not any(None in row for row in records), f"malformed CSV row in {relative_path}")
        return records

    def unique(self, rows: list[dict], column: str, path: str) -> None:
        values = [r.get(column, "").strip() for r in rows]
        self.require(all(values), f"blank {column} in {path}")
        repeated = [name for name, n in Counter(values).items() if name and n > 1]
        self.require(not repeated, f"duplicate {column} in {path}: {repeated[:6]}")

    def inside(self, path: Path) -> bool:
        try:
            return path.resolve().is_relative_to(self.root)
        except (OSError, ValueError):
            return False

    def check_records(self) -> None:
        path = "00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv"
        rows = self.csv(path, ("gap_id", "gap", "status", "request_file", "submitted", "submission_date", "receipt_id", "closure_evidence"))
        self.unique(rows, "gap_id", path)
        counts = Counter(row.get("status", "").strip() or "UNCLASSIFIED" for row in rows)
        self.details["records_gaps"] = {"total": len(rows), "by_status": dict(sorted(counts.items())), "sent_with_receipt": 0}
        for row in rows:
            gap = row.get("gap_id", "<unknown>")
            flag = row.get("submitted", "").strip().upper()
            self.require(flag in ("TRUE", "FALSE"), f"{gap}: submitted must be TRUE or FALSE")
            date = (row.get("submission_date") or "").strip()
            receipt = (row.get("receipt_id") or "").strip()
            if flag == "TRUE":
                self.require(bool(date and receipt), f"{gap}: sent status requires transmission date and receipt reference")
                if date:
                    try:
                        datetime.fromisoformat(date.replace("Z", "+00:00"))
                    except ValueError:
                        self.errors.append(f"{gap}: invalid transmission date: {date}")
                if date and receipt:
                    self.details["records_gaps"]["sent_with_receipt"] += 1
            elif date or receipt:
                self.errors.append(f"{gap}: unsent row has a submission date or receipt; reconcile against outgoing evidence")
            request_file = (row.get("request_file") or "").strip()
            if request_file:
                target = self.root / request_file
                self.require(self.inside(target) and target.is_file(), f"{gap}: missing request template: {request_file}")
            status = row.get("status", "").strip().upper()
            if status in {"COMPLETE", "CLOSED", "RESOLVED", "RECEIVED_VERIFIED", "OBTAINED_VERIFIED"}:
                self.require(bool((row.get("closure_evidence") or "").strip()), f"{gap}: closed without source-linked closure evidence")
        # Formally distinct request/service templates need not equal the row count.
        self.require(len(rows) > 0, "gap register contains no records")

    def check_registers(self) -> None:
        sets = (
            ("00_CONTROL/SOURCE_REGISTER.csv", "source_id"),
            ("00_CONTROL/EVIDENCE_LEDGER.csv", "claim_id"),
            ("00_CONTROL/EXHIBIT_INDEX.csv", "exhibit_id"),
            ("00_CONTROL/PERMIT_DOCUMENT_INVENTORY.csv", "document_id"),
            ("00_CONTROL/CHRONOLOGY.csv", "event_id"),
        )
        self.details["registers"] = {}
        for path, column in sets:
            rows = self.csv(path, (column,))
            self.unique(rows, column, path)
            self.details["registers"][column] = len(rows)
        design = self.csv("00_CONTROL/DESIGN_VS_FIELD_MATRIX.csv", ("item_id", "approved_value", "observed_or_surveyed_value", "status"))
        self.unique(design, "item_id", "00_CONTROL/DESIGN_VS_FIELD_MATRIX.csv")
        self.details["design_vs_field"] = dict(Counter(row["status"].strip() for row in design))

    def check_current_claim_alignment(self) -> None:
        original = "02_PROPERTY_AND_PARCELS/PRE_REQUEST_OCT16_PRIMARY_LOOKUPS/ORIGINAL_CLERK_PLAT_BOOK_A_PAGE_70.pdf"
        if (self.root / original).is_file():
            self.require("PLAT A/70" in self.read_text("00_CONTROL/OPEN_QUESTIONS.md"),
                         "open questions omit recovered original PLAT A/70")
        if (self.root / "00_CONTROL/RECORDS_ACQUISITION_MATRIX.csv").is_file():
            rows = self.csv("00_CONTROL/RECORDS_ACQUISITION_MATRIX.csv", ("agency_custodian", "status", "outcome"))
            clerk = [r for r in rows if "Clerk (AcclaimWeb)" in r.get("agency_custodian", "")]
            for r in clerk:
                if "original two-sheet Crescent Shores PLAT A/70 downloaded" in r.get("outcome", ""):
                    self.require("ERROR" not in r["status"].upper(),
                                 "Clerk matrix still labels the recovered original plat as an acquisition error")
        builder = self.read_text("tools/build_reconciled_packet.py")
        # Source-controlled entry count, not a file-system/URL inference.
        declared = re.search(r'"file_scope":\s*"([^"]+)"', builder)
        if declared:
            self.require("five" in declared.group(1).lower(),
                         "release generator has obsolete file_scope count: " + declared.group(1))
        else:
            self.errors.append("release generator lacks explicit file_scope documentation")
        for rel in ("15_RECONCILED_DRAFTS/README.md", "PUBLICATION_AND_VERSIONING.md"):
            body = self.read_text(rel)
            self.require("DRAFT" in body, f"{rel}: public documents must remain explicitly draft until homeowner sign-off")
        self.details["scope_note"] = "Mechanical source/register check; not agency confirmation, engineering determination, or resident publication approval"

    def check_links(self) -> None:
        review = [
            "README.md", "NEIGHBOR_REVIEW_GUIDE.md", "PUBLIC_EVIDENCE_GUIDE.md",
            "PUBLICATION_AND_VERSIONING.md", "15_RECONCILED_DRAFTS/README.md",
            "00_CONTROL/OPEN_QUESTIONS.md", "00_CONTROL/NEXT_ACTIONS.md",
            "00_CONTROL/COMMUNITY_READINESS_2026-10-16.md",
            "00_CONTROL/DOCUMENT_STATUS_AND_NEIGHBOR_REVIEW_2026-10-16.md",
            "00_CONTROL/READING_ORDER_AND_SNAPSHOT_STATUS.md",
            "00_CONTROL/PRE_REQUEST_PRIMARY_SOURCE_REVIEW_2026-10-16.md",
        ]
        review += [p.relative_to(self.root).as_posix() for p in sorted((self.root / "18_NEIGHBOR_TOOLKIT").rglob("*.md"))]
        reviewed = 0
        for rel in review:
            text = self.read_text(rel)
            if not text:
                continue
            reviewed += 1
            for raw in re.findall(r'!?\[[^\]]*\]\(([^)\n]+)\)', text):
                destination = raw.split(' "', 1)[0].strip()
                if not destination or destination.startswith(("#", "http:", "https:", "mailto:", "data:")):
                    continue
                destination = unquote(destination).split("#", 1)[0].split("?", 1)[0]
                if not destination:
                    continue
                target = (self.root / rel).parent / destination
                self.require(self.inside(target) and target.exists(), f"broken local link in {rel}: {destination}")
        self.details["links"] = {"current_markdown_files_checked": reviewed}

    def check_privacy_boundary(self) -> None:
        root = self.root / "18_NEIGHBOR_TOOLKIT"
        risky = []
        safe_pdf_names = {
            "Tom_Street_Neighbor_Documentation_Forms.pdf", "03_Event_Observation.pdf",
            "04_Photo_and_Video_Index.pdf", "10_Request_and_Response.pdf",
            "11_Meeting_and_Inspection_Notes.pdf", "13_Documented_Roles.pdf",
            "14_Original_Files_and_Handoff.pdf", "16_Missing_Records_Checklist.pdf",
            "18_Continuation_Page.pdf",
        }
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            suffix = p.suffix.lower()
            if suffix in {".md", ".csv"}:
                continue
            if p.parent.name == "print" and suffix == ".pdf" and p.name in safe_pdf_names:
                continue
            risky.append(p.relative_to(self.root).as_posix())
        self.require(not risky, "unexpected files in public neighbor toolkit: " + ", ".join(risky))
        self.details["privacy_boundary"] = {"unexpected_files": len(risky), "rule": "blank forms only; never completed resident data"}

    def run(self) -> dict:
        self.check_records()
        self.check_registers()
        self.check_current_claim_alignment()
        self.check_links()
        self.check_privacy_boundary()
        return {"status": "PASS" if not self.errors else "FAIL", "errors": self.errors,
                "warnings": self.warnings, "summary": self.details,
                "disclaimer": "Does not establish project/site completeness, plan approval, or evidence authenticity"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strict", action="store_true", help="exit nonzero for mechanical discrepancies")
    ap.add_argument("--root", type=Path, default=ROOT, help="repository checkout root (test/dry-run use only)")
    args = ap.parse_args(argv)
    result = AdministrationAudit(args.root).run()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if args.strict and result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
