#!/usr/bin/env python3
"""Read-only guard: current Tom Street materials must use Santa Rosa local law.

State/regional and federal agencies may appear. Preserved historical sources,
raw captures and superseded releases are excluded: rewriting them would damage
evidence integrity. This does not assert legal applicability or completeness.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = (
    "README.md",
    "00_CONTROL/JURISDICTION_AND_AUTHORITY_SCOPE_2026-10-15.md",
    "00_CONTROL/REGULATORY_AND_CASELAW_MATRIX.md",
    "15_RECONCILED_DRAFTS/README.md",
    "15_RECONCILED_DRAFTS/01_HOMEOWNER_BRIEF.md",
    "15_RECONCILED_DRAFTS/02_COUNTY_LETTER_DRAFT.md",
    "15_RECONCILED_DRAFTS/03_PROXY_MEETING_NOTES.md",
    "15_RECONCILED_DRAFTS/06_COMMISSIONER_COVER_LETTER_DRAFT.md",
    "13_PUBLIC_RECORDS_REQUESTS/2264_TOM_ST_COMPLETE_PERMIT_FILE.md",
    "13_PUBLIC_RECORDS_REQUESTS/2268_TOM_ST_COMPLETE_PERMIT_FILE.md",
    "13_PUBLIC_RECORDS_REQUESTS/SHARED_TOM_STREET_ROW_AND_DRAINAGE_PLANS.md",
    "13_PUBLIC_RECORDS_REQUESTS/CLERK_DEEDS_PLATS_EASEMENTS.md",
    "13_PUBLIC_RECORDS_REQUESTS/COUNTY_PUBLIC_WORKS_DRAINAGE_WORK_REQUEST_DRAFT.md",
    "13_PUBLIC_RECORDS_REQUESTS/FDEP_CONSTRUCTION_STORMWATER_CGP_RECORDS_DRAFT.md",
    "13_PUBLIC_RECORDS_REQUESTS/NWFWMD_ERP_9220-2_FILE.md",
)
# County names are prohibited here as controlling *local* jurisdiction.
# Geographic waterbodies, lawful statewide agencies and historic source files
# are not subject to this keyword gate.
FOREIGN_COUNTY = re.compile(
    r"\b(?:okaloosa|escambia|walton|bay|holmes|washington)\s+county\b",
    re.IGNORECASE,
)
FOREIGN_DOMAINS = (
    "myokaloosa.com",
    "okaloosa.fl.gov",
    "escambia.fl.gov",
    "myescambia.com",
    "co.walton.fl.us",
)
SITES = (
    ("2264", "BP-2026-1621", "21-2S-26-0780-0QQ00-1020"),
    ("2268", "BP-2026-1612", "21-2S-26-0780-0QQ00-1490"),
)

def scan_current_scope(text: str) -> list[str]:
    problems = []
    for hit in FOREIGN_COUNTY.finditer(text):
        problems.append("Foreign local-county jurisdiction: " + hit.group())
    for domain in FOREIGN_DOMAINS:
        if domain in text.lower():
            problems.append("Foreign county source domain: " + domain)
    return problems

def run() -> list[str]:
    errors: list[str] = []
    for rel in ACTIVE:
        file = ROOT / rel
        if not file.is_file():
            errors.append("Current document missing: " + rel)
            continue
        contents = file.read_text(encoding="utf-8")
        errors.extend(rel + ": " + msg for msg in scan_current_scope(contents))
    scope = (ROOT / ACTIVE[1]).read_text(encoding="utf-8")
    legal = (ROOT / ACTIVE[2]).read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for phrase in (
        "Santa Rosa County",
        "4.04.01.D.4",
        "4.04.01.E",
        "October 22, 2026",
        "street-maintainer",
        "2026-16",
        "Florida DEP",
        "NWFWMD",
        "FEMA",
    ):
        if phrase not in scope:
            errors.append("Missing jurisdiction/version boundary: " + phrase)
    for phrase in ("4.04.01.D.4", "4.04.01.E", "2026-16"):
        if phrase not in legal:
            errors.append("Legal matrix missing: " + phrase)
    if "JURISDICTION_AND_AUTHORITY_SCOPE_2026-10-15.md" not in readme:
        errors.append("README does not link jurisdiction control")
    for address, permit, parcel in SITES:
        path = ROOT / (
            f"03_PERMITS_AND_INSPECTIONS/{address}_Tom_St/"
            f"{permit}_project_by_uid.json"
        )
        if not path.is_file():
            errors.append("Saved permit capture missing: " + str(path))
            continue
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))["data"]
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f"Saved permit invalid: {address}: {exc}")
            continue
        if obj.get("projectNumber") != permit or address not in obj.get("projectAddress", ""):
            errors.append(f"Saved Santa Rosa MGO permit identity mismatched: {address}")
        if not str(obj.get("parcelNumber", "")).endswith(parcel[-4:]):
            errors.append(f"Saved Santa Rosa MGO parcel identity mismatched: {address}")
    return errors

def self_test() -> None:
    assert not scan_current_scope("Santa Rosa County; Florida DEP; NWFWMD; FEMA; Escambia Bay")
    assert scan_current_scope("County rule: Okaloosa County") == [
        "Foreign local-county jurisdiction: Okaloosa County"
    ]
    assert scan_current_scope("See https://okaloosa.fl.gov/ordinances")
    print("Jurisdiction guard self-test PASS")

if __name__ == "__main__":
    self_test()
    failures = run()
    for failure in failures:
        print("FAIL " + failure)
    if failures:
        sys.exit(f"Jurisdiction guard FAIL ({len(failures)} checks)")
    print(f"Jurisdiction guard PASS: {len(ACTIVE)} active docs; 2 saved MGO identities")
