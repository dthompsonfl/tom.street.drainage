#!/usr/bin/env python3
"""Append the MGO Connect permit evidence to SOURCE_REGISTER.csv and

PERMIT_DOCUMENT_INVENTORY.csv, generated from the actual captured files."""

import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:  # noqa: E402
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT  # noqa: E402
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = _ROOT
CTL = ROOT / "00_CONTROL"
BASE = ROOT / "03_PERMITS_AND_INSPECTIONS"
RETRIEVED = "2026-10-16T"  # UTC session continues past local midnight

def sha(rel):
    p = ROOT / rel
    return (p.stat().st_size, __import__("hashlib").sha256(p.read_bytes()).hexdigest()) \
        if p.exists() else (None, None)

PROPS = [
    dict(slug="2264_Tom_St", pn="BP-2026-1621", parcel="21-2S-26-0780-0QQ00-1020",
         addr="2264 Tom Street", uid="DBFA3383-592A-4486-A392-F88065C90F95",
         pid=17513349, sf=2704, ninsp=15,
         prior="1996-2765-000-B-0 / -E-0 / -M-0 / -P-0 (Mobile Home, Electrical, Mechanical, Plumbing), all 1996-07-18"),
    dict(slug="2268_Tom_St", pn="BP-2026-1612", parcel="21-2S-26-0780-0QQ00-1490",
         addr="2268 Tom Street", uid="677D3AE3-F348-4B97-A37C-8B0BC05CEAF7",
         pid=17513025, sf=2312, ninsp=11,
         prior="2000-4250-000-B-0 / -E-0 / -G-0 / -P-0 (Mobile Home, Electrical, Gas, Plumbing), all 2000-12-14"),
]

SOURCE_ROWS = []
DOC_ROWS = []

for i, p in enumerate(PROPS, start=110):
    slug, pn, parcel, addr = p["slug"], p["pn"], p["parcel"], p["addr"]
    d = json.load(open(BASE / slug / f"{pn}_project_by_uid.json"))["data"]
    ins = json.load(open(BASE / slug / f"{pn}_inspections.json"))["data"]
    req = json.load(open(BASE / slug / f"{pn}_requirements.json"))
    openreq = [r for r in req if str(r.get("Status")) not in
               ("Approved", "Complete", "Passed")]
    base = f"03_PERMITS_AND_INSPECTIONS/{slug}"

    for n, (suffix, title) in enumerate([
            ("project_by_uid.json", "MGO permit record - full project detail"),
            ("inspections.json", f"MGO inspection history - {p['ninsp']} inspections"),
            ("requirements.json", f"MGO task/requirement list - {len(openreq)} items outstanding"),
            ("project_files.json", "MGO customer document endpoint response (empty)"),
            ("contacts.json", "MGO project contacts"),
            ("fees.json", "MGO fee lines charged on the permit"),
            ("types.json", "MGO permit types charged on the permit"),
            ("payments.json", "MGO payment record"),
            ("work_orders.json", "MGO work orders (empty)")], start=1):
        rel = f"{base}/{pn}_{suffix}"
        size, sha256 = sha(rel)
        if size is None:
            continue
        SOURCE_ROWS.append({
            "source_id": f"SRC-{i}{n}",
            "document_title": f"{title} — {pn} ({addr})",
            "issuing_agency": "Santa Rosa County Development Services (MGO Connect)",
            "record_system": "mgoconnect.org/cp (JID=276)",
            "source_identifier": f"{pn} / projectUID {p['uid']}",
            "retrieval_date_utc": "2026-10-15/16 (session)",
            "original_url": f"https://www.mgoconnect.org/cp/project-details/{p['uid']}",
            "local_relative_path": rel,
            "file_type": "application/json",
            "file_size_bytes": size,
            "sha256_hash": sha256,
            "status": "DOWNLOADED_VERIFIED",
            "verification_method": "Official MGO API response parsed; fields cross-checked against portal UI",
            "notes": "Authenticated retrieval. No credential stored in this repository.",
        })

    for rel, title, cat in [
        (f"{base}/{pn}_PERMIT_RECORD.md", "Permit record summary (rendered from official API data)", "Permit Metadata"),
        (f"{base}/{pn}_INSPECTION_HISTORY.md", "Inspection history with county inspector comments", "Inspections"),
        (f"{base}/{slug}/{pn}_PERMIT_RECORD.md" if False else f"{base}/{pn}_PERMIT_RECORD.md",
         "Permit record summary", "Permit Metadata"),
    ]:
        size, sha256 = sha(rel)
        if size:
            SOURCE_ROWS.append({
                "source_id": f"SRC-{i}D{abs(hash(title)) % 90 + 10}",
                "document_title": f"{title} — {pn} ({addr})",
                "issuing_agency": "Santa Rosa County Development Services (MGO Connect)",
                "record_system": "mgoconnect.org/cp (JID=276)",
                "source_identifier": f"{pn} / projectUID {p['uid']}",
                "retrieval_date_utc": "2026-10-15/16 (session)",
                "original_url": f"https://www.mgoconnect.org/cp/project-details/{p['uid']}",
                "local_relative_path": rel,
                "file_type": "text/markdown",
                "file_size_bytes": size,
                "sha256_hash": sha256,
                "status": "DOWNLOADED_VERIFIED",
                "verification_method": "Rendered directly from the official API JSON stored alongside it",
                "notes": "",
            })

    # Permit metadata rows for the document inventory
    DOC_ROWS.append(dict(
        document_id=f"DOC-{slug.split('_')[0]}-0001",
        property_address=addr, parcel_id=parcel, permit_number=pn,
        issuing_agency="Santa Rosa County Development Services",
        source_document_id=f"projectUID {p['uid']}",
        document_title="Building permit - New Single Family (R), Active",
        document_date_revision=f"created {d.get('dateCreated')}; issued {d.get('dateIssued')}; updated {d.get('dateUpdated')}",
        acquisition_status="DOWNLOADED_VERIFIED", reason_unavailable="",
        local_relative_path=f"{base}/{pn}_PERMIT_RECORD.md",
        notes=f"Applicant {d.get('applicantFirstName')} {d.get('applicantLastName')} "
              f"({d.get('applicantBusinessName')}). {p['sf']} sq ft. Status Active."))
    DOC_ROWS.append(dict(
        document_id=f"DOC-{slug.split('_')[0]}-0002",
        property_address=addr, parcel_id=parcel, permit_number=pn,
        issuing_agency="Santa Rosa County Development Services",
        source_document_id=f"projectUID {p['uid']}",
        document_title=f"Inspection history - {p['ninsp']} inspections with county comments",
        document_date_revision="through 2026-10-01",
        acquisition_status="DOWNLOADED_VERIFIED", reason_unavailable="",
        local_relative_path=f"{base}/{pn}_INSPECTION_HISTORY.md",
        notes="Includes Site Grading/Drainage and Driveway Line & Grade inspections."))
    DOC_ROWS.append(dict(
        document_id=f"DOC-{slug.split('_')[0]}-0003",
        property_address=addr, parcel_id=parcel, permit_number=pn,
        issuing_agency="Santa Rosa County Development Services",
        source_document_id=f"ProjectRequirements projectID {p['pid']}",
        document_title="County task/requirement list - outstanding items including 'Certified Drainage as Built'",
        document_date_revision="as of retrieval",
        acquisition_status="DOWNLOADED_VERIFIED", reason_unavailable="",
        local_relative_path=f"{base}/{pn}_requirements.json",
        notes=f"{len(openreq)} requirements not complete. 'Certified Drainage as Built' = Assigned."))
    for n, (title, cat, note) in enumerate([
        ("Approved site plan / plot plan", "Approved Plans",
         "MGO ProjectFiles endpoint returns an empty list; plan exists internally but is not portal-visible"),
        ("Approved grading plan and revisions", "Grading and Surveys",
         "County charged an 'Erosion Control/Site Grade Flat Fee', confirming a grading plan was reviewed"),
        ("Existing-conditions / topographic survey", "Grading and Surveys", "Not portal-visible"),
        ("Erosion and sediment control plan", "Drainage and Stormwater",
         "Fee line confirms county review; document not portal-visible"),
        ("Driveway plan and culvert details", "Driveway and ROW",
         "Design captured in the driveway inspection comments; drawing not portal-visible"),
        ("Certified Drainage as Built", "As-Builts and Certifications",
         "County requirement 'Certified Drainage as Built' is still Assigned - NOT yet submitted or approved"),
        ("Certificate of Occupancy", "Certificates of Occupancy",
         "Requirement 'Issue CO' still Assigned; permit status remains Active"),
        ("Final grading / Site Grading & Drainage final inspection", "Inspections",
         "Requirement 'Site Grading / Drainage (final construction)' = Not Complete"),
        ("Plan review comments and correction notices", "Correspondence",
         "One Partial Pass on 2264 (windload); no plan-review comment record exposed"),
    ], start=10):
        DOC_ROWS.append(dict(
            document_id=f"DOC-{slug.split('_')[0]}-{n:04d}",
            property_address=addr, parcel_id=parcel, permit_number=pn,
            issuing_agency="Santa Rosa County Development Services",
            source_document_id=f"{pn} (MGO)",
            document_title=title, document_date_revision="",
            acquisition_status="NOT_OFFERED_IN_PORTAL" if n != 16 else "AUTHENTICATION_REQUIRED",
            reason_unavailable="MGO Connect customer portal exposes zero documents for this permit",
            local_relative_path="", notes=note))

if __name__ == "__main__":
    raise SystemExit("LEGACY REGISTER BUILDER DISABLED: outdated source assumptions and duplicate identifiers. Use current acquisition and canonical reconciliation tools; never overwrite validated registers with these bootstrap fixtures.")
    # append to SOURCE_REGISTER
    f = CTL / "SOURCE_REGISTER.csv"
    existing = list(csv.DictReader(f.open()))
    have = {r["local_relative_path"] for r in existing}
    added = [r for r in SOURCE_ROWS if r["local_relative_path"] not in have]
    rows = existing + added
    with f.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(existing[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"SOURCE_REGISTER.csv: {len(existing)} -> {len(rows)} (+{len(added)})")

    # replace the AUTHENTICATION_REQUIRED permit rows with real data
    g = CTL / "PERMIT_DOCUMENT_INVENTORY.csv"
    inv = list(csv.DictReader(g.open()))
    inv = [r for r in inv
           if r["document_id"] not in
           ("DOC-2264-9001", "DOC-2268-9001", "DOC-2264-9002", "DOC-2268-9002")]
    inv.extend(DOC_ROWS)
    with g.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(inv[0].keys()))
        w.writeheader()
        w.writerows(inv)
    print(f"PERMIT_DOCUMENT_INVENTORY.csv: {len(inv)} rows")

    # refresh acquisition matrix
    h = CTL / "RECORDS_ACQUISITION_MATRIX.csv"
    mat = list(csv.DictReader(h.open()))
    for r in mat:
        if r["agency_custodian"].startswith("Santa Rosa County Development Services"):
            r["search_performed"] = ("Authenticated MGO Connect customer session. Address, parcel, "
                                     "project-number, business-name, subdivision and full 2200-2300 "
                                     "Tom St address sweep.")
            r["search_date"] = "2026-10-15/16"
            r["outcome"] = ("SUCCESS - BP-2026-1621 (2264 Tom St) and BP-2026-1612 (2268 Tom St) "
                            "located, opened, and their metadata, inspections, requirements, fees, "
                            "contacts and payments retrieved in full.")
            r["obtained"] = "YES (metadata, inspections, requirements)"
            r["file_path"] = "03_PERMITS_AND_INSPECTIONS/2264_Tom_St/, 2268_Tom_St/"
            r["status"] = "DOWNLOADED_VERIFIED"
            r["barriers"] = ("County customer portal exposes ZERO document attachments for either "
                             "permit (ProjectFiles endpoint returns an empty list). No plans, surveys, "
                             "grading sheets or as-builts are portal-visible at any access level.")
            r["next_action"] = ("Chapter 119 request for all plan/survey/as-built attachments; "
                                "13_PUBLIC_RECORDS_REQUESTS/2264_TOM_ST_COMPLETE_PERMIT_FILE.md and "
                                "2268_TOM_ST_COMPLETE_PERMIT_FILE.md are drafted.")
        if r["agency_custodian"].startswith("Santa Rosa County Clerk"):
            r["search_performed"] += ("; subdivision StoryMaps for 2020-2026 searched for "
                                      "'Crescent Shores'/'Hadleigh Hills' - zero hits")
    with h.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(mat[0].keys()))
        w.writeheader()
        w.writerows(mat)
    print(f"RECORDS_ACQUISITION_MATRIX.csv: {len(mat)} rows refreshed")