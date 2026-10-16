#!/usr/bin/env python3
"""Fetch three *public* original legal-source PDFs with exact allowlisted URLs.

Does not fetch private records, interact with permit accounts, or send requests.
Never treats DEP final-order *index reports* as the signed underlying orders.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "08_LEGAL_AND_REGULATORY" / "SOURCE" / "PRIMARY_AUTHORITY"
MAX_BYTES = 25_000_000
SOURCES = (
    (
        "Westland_Skating_Center_v_Gus_Machado_Buick_Fla_1989_CORRECTED_OPINION.pdf",
        "https://library.law.fsu.edu/Digital-Collections/flsupct/dockets/72492/op-72492.pdf",
        11,
        "Florida Supreme Court corrected opinion; not a factual finding on Tom Street",
    ),
    (
        "FDEP_FINAL_ORDER_INDEX_2023_Q1.pdf",
        "https://floridadep.gov/sites/default/files/Final_Order_Report_-_January_1,_2023_-_March_31,_2023.pdf",
        7,
        "DEP index listing Holiday Builders OGC 22-2720 / DEP23-0087; NOT the signed consent order",
    ),
    (
        "FDEP_FINAL_ORDER_INDEX_2024_Q1.pdf",
        "https://floridadep.gov/sites/default/files/Final_Order_Report_-_January_1,_2024_-_March_31,_2024.pdf",
        5,
        "DEP index listing Holiday Builders Inc OGC 23-1387 / DEP24-0006; NOT the signed consent order",
    ),
)

def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()

def verified_pdf(payload: bytes, expected_pages: int) -> int:
    if len(payload) > MAX_BYTES or len(payload) < 2000 or not payload.startswith(b"%PDF-"):
        raise ValueError("Fetched bytes are not a plausible PDF or exceed the 25MB limit")
    pages = len(PdfReader(io.BytesIO(payload), strict=False).pages)
    if pages != expected_pages:
        raise ValueError("Unexpected PDF pages: expected %d, got %d" % (expected_pages, pages))
    return pages

def run():
    OUT.mkdir(parents=True, exist_ok=True)
    findings = []
    for name, url, expected_pages, scope in SOURCES:
        record = {"file": str((OUT / name).relative_to(ROOT)), "source_url": url,
                  "expected_pages": expected_pages, "interpretation_limit": scope}
        dest = OUT / name
        try:
            if dest.exists():
                raw = dest.read_bytes()
                status = "ALREADY_PRESERVED_UNCHANGED"
            else:
                request = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; TomStreetEvidenceAcquisition/1.0)"
                })
                with urllib.request.urlopen(request, timeout=35) as response:
                    raw = response.read(MAX_BYTES + 1)
                    record["redirect_url"] = response.geturl()
                status = "PUBLIC_PDF_CAPTURED"
            pages = verified_pdf(raw, expected_pages)
            if not dest.exists():
                tmp = dest.with_suffix(".pdf.tmp")
                tmp.write_bytes(raw)
                os.replace(tmp, dest)
            record.update({"status": status, "bytes": len(raw),
                           "sha256": sha256(raw), "validated_pages": pages})
        except Exception as exc:
            record.update({"status": "NOT_CAPTURED", "error": type(exc).__name__ + ": " + str(exc)[:250]})
        findings.append(record)
        print(record["file"], record["status"], record.get("sha256", ""), record.get("error", ""))
    manifest = {
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Public primary-source legal research, not a lot-specific engineering finding",
        "final_orders_signed_pdf_obtained": False,
        "all_public_pdfs_captured": all(f["status"] != "NOT_CAPTURED" for f in findings),
        "sources": findings,
    }
    (OUT / "ACQUISITION_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return all(f["status"] != "NOT_CAPTURED" for f in findings)

if __name__ == "__main__":
    run()
