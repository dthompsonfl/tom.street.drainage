#!/usr/bin/env python3
"""Strict editorial/factual scope guard for CURRENT Tom Street documents.

Historical preserved records are deliberately excluded: they are not revised
merely to remove superseded assertions. Checks are narrow, deterministic and
not a substitute for engineer, legal or homeowner review.
"""
from __future__ import annotations

import csv
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
issues: list[str] = []
passed = 0

def check(description: str, good: bool) -> None:
    global passed
    if good:
        passed += 1
    else:
        issues.append(description)
    print(("PASS " if good else "FAIL ") + description)

def text(path: str) -> str:
    p = ROOT / path
    if not p.exists():
        raise FileNotFoundError(path)
    return p.read_text(encoding="utf-8")

def csvrows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

current = [
    "README.md",
    "02_PROPERTY_AND_PARCELS/PARCEL_IDENTITY_REPORT.md",
    "02_PROPERTY_AND_PARCELS/websearch_2266_notes.md",
    "02_PROPERTY_AND_PARCELS/websearch_2268_notes.md",
    "03_PERMITS_AND_INSPECTIONS/2264_Tom_St/DOCUMENT_COMPLETENESS.md",
    "03_PERMITS_AND_INSPECTIONS/2268_Tom_St/DOCUMENT_COMPLETENESS.md",
    "13_PUBLIC_RECORDS_REQUESTS/2264_TOM_ST_COMPLETE_PERMIT_FILE.md",
    "13_PUBLIC_RECORDS_REQUESTS/2268_TOM_ST_COMPLETE_PERMIT_FILE.md",
    "13_PUBLIC_RECORDS_REQUESTS/NWFWMD_ERP_9220-2_FILE.md",
    "13_PUBLIC_RECORDS_REQUESTS/CLERK_DEEDS_PLATS_EASEMENTS.md",
    "13_PUBLIC_RECORDS_REQUESTS/SHARED_TOM_STREET_ROW_AND_DRAINAGE_PLANS.md",
    "15_RECONCILED_DRAFTS/01_HOMEOWNER_BRIEF.md",
    "15_RECONCILED_DRAFTS/02_COUNTY_LETTER_DRAFT.md",
    "15_RECONCILED_DRAFTS/03_PROXY_MEETING_NOTES.md",
    "15_RECONCILED_DRAFTS/06_COMMISSIONER_COVER_LETTER_DRAFT.md",
]
wrong_phrases = [
    r"(?i)\bno fdep-issued erp exists within\b",
    r"(?i)\bthis lot previously carried a mobile home\b",
    r"(?i)\bplans, surveys and as-builts are held in the county.s internal\b",
    r"(?i)\btwo adjacent residential lots\b",
    r"(?i)\bthe driveway drainage design (?:for \d+ )?ties into existing storm structures\b",
    r"(?i)\bthe certified drainage as-builts do not yet exist\b",
    r"(?i)\bno (?:certificate|certification) (?:has been|was) submitted\b",
    r"(?i)\ba plan exists internally but is not portal-visible\b",
]
for path in current:
    content = text(path)
    bad = [pat for pat in wrong_phrases if re.search(pat, content)]
    check("Current narrative avoids unproven categorical claims: " + path,
          not bad)
    if bad:
        print("  Matched rules: " + "; ".join(bad))

for site in ["2264", "2268"]:
    source = text(f"03_PERMITS_AND_INSPECTIONS/{site}_Tom_St/DOCUMENT_COMPLETENESS.md")
    checks = [
        (r"\|\s*11\s*\|[^|]+\|\s*\`NOT_OBTAINED_FOR_SITE\`", "standalone driveway/ROW permit not falsely obtained"),
        (r"\|\s*18\s*\|[^|]+\|\s*\`NOT_OBTAINED_FOR_SITE\`", "site-related ERP not falsely obtained"),
        (r"\|\s*4b\s*\|[^|]+\|\s*\`HISTORICAL_LEAD_UNLINKED\`", "historical mobile home not asserted current"),
        (r"\|\s*6\s*\|[^|]+\|\s*\`NOT_OFFERED_IN_PORTAL\`", "approved grading drawing remains unobtained"),
        (r"\|\s*16\s*\|[^|]+\|\s*\`NOT_OFFERED_IN_PORTAL\`", "drainage as-built not presumed filed or missing"),
    ]
    for expression, desc in checks:
        check(site + ": " + desc, bool(re.search(expression, source)))
    check(site + ": task assignment not falsely proof of absence",
          "Assigned" not in source or "does not" in source.lower() or "unverified" in source.lower())

claims = csvrows("00_CONTROL/EVIDENCE_LEDGER.csv")
exhibits = csvrows("00_CONTROL/EXHIBIT_INDEX.csv")
index = {row["exhibit_id"]: row for row in exhibits}
check("evidence exhibit IDs are unique",
      len(index) == len(exhibits) and len(exhibits) >= 19)
for row in claims:
    eid = (row.get("source_exhibit") or "").strip()
    if eid:
        check(row["claim_id"] + " cites a registered exhibit", eid in index)
for row in exhibits:
    name = row["source_file"]
    path = ROOT / name
    good = path.is_file()
    if good:
        good = (row["sha256"] == digest(path)
                and int(row["bytes"]) == path.stat().st_size)
    check(row["exhibit_id"] + " actual original-byte integrity", good)
    if row["exhibit_id"] in {"EX-16", "EX-17", "EX-18"}:
        check(row["exhibit_id"] + " legal only, not a construction evidence exhibit",
              row["public_release"] == "LEGAL_RESEARCH_ONLY_NOT_MEETING_EXHIBIT")

contradictions = csvrows("00_CONTROL/CONTRADICTION_LOG.csv")
cids = [row["id"] for row in contradictions]
check("contradiction register has twelve uniquely identified resolutions/gaps",
      len(contradictions) >= 12 and len(cids) == len(set(cids)))
for cid in ["CON-03", "CON-04", "CON-06", "CON-09", "CON-11", "CON-12"]:
    record = next((row for row in contradictions if row["id"] == cid), None)
    check(cid + " remains explicitly unresolved or evidence-limited",
          bool(record) and any(word in
              (record["status"] + " " + record["resolution"]).upper()
              for word in ("UNRESOLVED", "UNPROVEN", "NOT_OBTAINED", "VERIFIED_ORIGINALITY")))

readme = text("README.md")
check("root navigation exclusively recommends current packet",
      "15_RECONCILED_DRAFTS/pdf/Tom_Street_Reconciled_Public_Meeting_Draft.pdf" in readme
      and "14_MEETING_PACKET" in readme and "superseded" in readme.lower())
law = text("00_CONTROL/REGULATORY_AND_CASELAW_MATRIX.md")
check("legal status distinguishes planned Oct 22 formatting action",
      "October 22, 2026" in law and "formatting" in law
      and "not" in law.lower())
check("legal matrix does not label PDF metadata timestamp as an enactment",
      "November 10, 2025" in law and "creation" in law.lower())

print(f"\nEDITORIAL/CLAIM VALIDATION: {passed} passed, {len(issues)} failed")
if issues:
    for item in issues:
        print(" - " + item)
sys.exit(1 if issues else 0)
