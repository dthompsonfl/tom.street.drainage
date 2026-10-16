#!/usr/bin/env python3
"""Offline, primary-record-backed cross-document consistency contract.

This validates CURRENT research narrative and registers only. Historical
superseded artifacts retain their original wording for custody/audit purposes.
A passing result proves the stated invariants, not universal factual truth,
permit compliance, or engineering adequacy.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
failures: list[str] = []
checks = 0

def assert_ok(label: str, condition: bool) -> None:
    global checks
    checks += 1
    print(("PASS " if condition else "FAIL ") + label)
    if not condition:
        failures.append(label)

def load_json(p: str):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))

def load_csv(p: str) -> list[dict[str, str]]:
    with (ROOT / p).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))

def load_text(p: str) -> str:
    return (ROOT / p).read_text(encoding="utf-8")

def only(rows, key, value):
    matches = [r for r in rows if r[key] == value]
    assert_ok(f"exactly one {key}={value}", len(matches) == 1)
    return matches[0] if len(matches) == 1 else {}

SITES = {
    "2264": {"parcel": "21-2S-26-0780-0QQ00-1020", "permit": "BP-2026-1621",
             "lot": "1020", "updated": "2026-10-01"},
    "2268": {"parcel": "21-2S-26-0780-0QQ00-1490", "permit": "BP-2026-1612",
             "lot": "1490", "updated": "2026-10-06"},
}
PARCELS = load_csv("02_PROPERTY_AND_PARCELS/PARCEL_SUMMARY.csv")
INVENTORY = load_csv("00_CONTROL/PERMIT_DOCUMENT_INVENTORY.csv")
CLAIMS = {r["claim_id"]: r for r in load_csv("00_CONTROL/EVIDENCE_LEDGER.csv")}
CHRON = {r["event_id"]: r for r in load_csv("00_CONTROL/CHRONOLOGY.csv")}
SOURCES = {r["source_id"]: r for r in load_csv("00_CONTROL/SOURCE_REGISTER.csv")}
RESPONSIBILITY = load_csv("00_CONTROL/RESPONSIBILITY_MATRIX.csv")
REQUESTS = load_csv("00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv")

for address, truth in SITES.items():
    parcel = load_json(
        f"02_PROPERTY_AND_PARCELS/{address}_Tom_St/"
        f"srcpa_property_record_{truth['parcel']}.json"
    )[0]
    permit = load_json(
        f"03_PERMITS_AND_INSPECTIONS/{address}_Tom_St/"
        f"{truth['permit']}_project_by_uid.json"
    )["data"]
    summary = next((r for r in PARCELS if r["address"].startswith(address+" Tom")), {})
    assert_ok(address+" PA lot/situs/parcel",
        parcel["situsAddress1"] == f"{address} TOM ST"
        and parcel["parcelNumber"] == truth["parcel"]
        and parcel["idLot"] == truth["lot"])
    assert_ok(address+" permit address/number/lot/parcel",
        permit["projectNumber"] == truth["permit"]
        and permit["projectAddress"].startswith(address+" TOM")
        and permit["parcelNumber"].endswith(truth["lot"])
        and permit["lot"] == truth["lot"])
    assert_ok(address+" owner is applicant-independent and from appraiser",
        parcel["ownerName"] == "HOLIDAY BUILDERS INC"
        and permit["applicantBusinessName"].upper() == "HOLIDAY BUILDERS INC")
    assert_ok(address+" local parcel summary agrees with primary",
        summary.get("verified_parcel") == truth["parcel"]
        and summary.get("verified_owner") == parcel["ownerName"])
    assert_ok(address+" archive dates not mistaken for current status",
        permit["dateIssued"].startswith("2026-03-23")
        and permit["dateCreated"].startswith("2026-02-11")
        and permit["dateUpdated"].startswith(truth["updated"])
        and permit["status"] == "Active")
    refresh = load_json(
        "03_PERMITS_AND_INSPECTIONS/STATUS_REFRESH/"
        f"{truth['permit']}_status_refresh.json"
    )
    assert_ok(address+" summary was NOT a new live retrieval",
        "archived" in refresh["status_verification_scope"].lower()
        and refresh["status_at_refresh"] == "Active")
    for item in INVENTORY:
        if item["document_id"].startswith("DOC-"+address):
            assert_ok(item["document_id"]+" site-specific parcel binding",
                item["parcel_id"] == truth["parcel"]
                and item["property_address"].startswith(address+" Tom"))
            if item["permit_number"].startswith("BP-"):
                assert_ok(item["document_id"]+" correct permit binding",
                    item["permit_number"] == truth["permit"])
    asserted = CLAIMS[f"CLM-{'004' if address=='2264' else '005'}"]["claim"]
    assert_ok(address+" ledger uses archived update/issue/creation dates",
        truth["updated"] in asserted
        and "2026-03-23" in asserted
        and "2026-02-11" in asserted)

assert_ok("2265 is not one of the two construction permit sites",
    only(PARCELS, "address", "2265 Tom St Navarre FL 32566").get("verified_parcel")
    == "21-2S-26-0780-0QQ00-1180")
assert_ok("2266 historic/current temporal distinction",
    "saved" in CLAIMS["CLM-003"]["claim"].lower()
    or "archived" in CLAIMS["CLM-003"]["claim"].lower())
assert_ok("1996 and 2000 chronology entries do not certify current lot continuity",
    "continuity" in CHRON["CH-001"]["certainty"].lower()
    and "unverified" in CHRON["CH-002"]["certainty"].lower())
assert_ok("resident photos are not assigned to target parcels without provenance",
    "unverified" in CHRON["CH-016"]["address"].lower()
    and CHRON["CH-016"]["date_observed"] == "UNKNOWN")
assert_ok("FEMA is a point result, not a whole-parcel classification",
    "sampled" in CLAIMS["CLM-014"]["claim"].lower()
    and "whole-parcel" in CLAIMS["CLM-014"]["claim"].lower())
assert_ok("ERP source remains a limited proximity lead",
    "limited" in CLAIMS["CLM-013"]["claim"].lower()
    and "not prove" in CLAIMS["CLM-013"]["limitation"].lower())
fdep = next((r for r in RESPONSIBILITY if r["role"] == "State ERP authority (separate)"), {})
assert_ok("FDEP responsibility is conditional, not falsely ruled out",
    fdep.get("certainty") == "POTENTIAL_AUTHORITY_SCOPE_UNVERIFIED")
for id in ["SRC-100", "SRC-101"]:
    assert_ok(id+" later authenticated access reconciled",
        SOURCES[id]["status"] == "HISTORICAL_GUEST_SEARCH_BLOCKED_SUPERSEDED")
assert_ok("archived attachment search distinguished from County-held files",
    SOURCES["SRC-102"]["status"] == "TESTED_CUSTOMER_ATTACHMENT_NOT_OFFERED")

base = {
    "2264_TOM_ST_COMPLETE_PERMIT_FILE.md",
    "2268_TOM_ST_COMPLETE_PERMIT_FILE.md",
    "CLERK_DEEDS_PLATS_EASEMENTS.md",
    "NWFWMD_ERP_9220-2_FILE.md",
    "SHARED_TOM_STREET_ROW_AND_DRAINAGE_PLANS.md",
}
supplemental = {
    "COUNTY_PUBLIC_WORKS_DRAINAGE_WORK_REQUEST_DRAFT.md",
    "FDEP_CONSTRUCTION_STORMWATER_CGP_RECORDS_DRAFT.md",
}
actual = {p.name for p in (ROOT/"13_PUBLIC_RECORDS_REQUESTS").glob("*.md")}
assert_ok("five foundational and two supplemental drafts exactly tracked",
    actual == base | supplemental)
for name in actual:
    content = load_text("13_PUBLIC_RECORDS_REQUESTS/"+name)
    assert_ok(name+" clearly unsent", "DRAFTED_NOT_SUBMITTED" in content[:500])
assert_ok("request receipt tracker not falsely submitted",
    all((r.get("submitted") or "").upper() != "TRUE"
        for r in REQUESTS))
assert_ok("canonical release guide accurately counts seven drafts",
    "five foundational" in load_text("15_RECONCILED_DRAFTS/README.md").lower()
    and "two supplemental" in load_text("15_RECONCILED_DRAFTS/README.md").lower())

release = load_json("15_RECONCILED_DRAFTS/pdf/RELEASE_MANIFEST.json")
assert_ok("current combined packet is five-page DRAFT, not signed",
    release["release_status"] == "DRAFT_NOT_APPROVED_FOR_EXTERNAL_DISTRIBUTION"
    and release["photo_originals_included"] is False
    and next(r["pages"] for r in release["outputs"]
             if "Public_Meeting_Draft" in r["pdf"]) == 5)
assert_ok("legacy meeting publications explicitly withdrawn",
    "SUPERSEDED" in load_text("14_MEETING_PACKET/RELEASE_README.md").upper())
assert_ok("canonical release guide has no four-page typo",
    "four-page" not in load_text("15_RECONCILED_DRAFTS/README.md").lower())

for path in (
    "00_CONTROL/ACQUISITION_CHECKPOINT.md",
    "00_CONTROL/ACQUISITION_RESULTS.md",
    "00_CONTROL/PROGRESS.md",
    "00_CONTROL/CURRENT_STATE_RECONCILIATION.md",
    "00_CONTROL/INDEPENDENT_AUDIT_2026-10-16.md",
):
    body = load_text(path)[:430].upper()
    assert_ok(path+" marked historical/superseded",
        "HISTORICAL" in body or "SUPERSEDED" in body)

# Only scan CURRENT claims, not original evidence or historical errata.
current_docs = [ROOT/"README.md"]
for category in (
    "02_PROPERTY_AND_PARCELS",
    "03_PERMITS_AND_INSPECTIONS",
    "04_ENGINEERING_AND_DRAINAGE",
    "13_PUBLIC_RECORDS_REQUESTS",
    "15_RECONCILED_DRAFTS",
    "16_ARCHIVE_RECONCILIATION",
):
    current_docs.extend((ROOT/category).rglob("*.md"))
current_docs.extend(ROOT/"00_CONTROL"/x for x in (
    "REGULATORY_AND_CASELAW_MATRIX.md",
    "JURISDICTION_AND_AUTHORITY_SCOPE_2026-10-15.md",
    "NEXT_ACTIONS.md",
    "OPEN_QUESTIONS.md",
))
historical_comparisons = {
    "15_RECONCILED_DRAFTS/04_CROSS_SOURCE_RECONCILIATION.md",
}
for path in sorted(set(current_docs)):
    rel = path.relative_to(ROOT).as_posix()
    if rel in historical_comparisons:
        continue  # This table explicitly quotes superseded claims as evidence.
    value = path.read_text(encoding="utf-8")
    forbidden = [
        r"\b2266 tom (?:st(?:reet)?) (?:never existed|does not exist)\b",
        r"\b(?:both|these) parcels (?:are|lie|were) (?:in|within) (?:fema )?zone x\b",
        r"\bno fdep(?:-issued)? erp exists\b",
        r"\bcertified drainage as built.{0,60}\bhas not been submitted\b",
        r"\bthe engineer.s certification does not exist\b",
        r"\bthe drainage pipe (?:has been|was) installed\b",
        r"\b(?:no|none) (?:approved|submitted) (?:grading|drainage) plans? exist\b",
        r"\b(?:pdf )?creationdate 2026-01-13 (?:is|means) (?:an? )?(?:ordinance|adoption)\b",
    ]
    bad = [rule for rule in forbidden if re.search(rule, value, re.I | re.S)]
    assert_ok("current narrative does not assert unverified fact: "+rel, not bad)
    if bad:
        print("  matched: "+"; ".join(bad))

print(f"\nREPOSITORY CONSISTENCY CONTRACT: {checks-len(failures)} passed / {len(failures)} failed")
if failures:
    print("Unmet invariants:\n"+"\n".join("- "+name for name in failures))
sys.exit(bool(failures))
