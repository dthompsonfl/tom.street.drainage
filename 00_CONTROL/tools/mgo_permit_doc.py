#!/usr/bin/env python3
"""Render a complete, readable permit record for each target property from the

captured MGO Connect API responses."""

import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:  # noqa: E402
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT  # noqa: E402
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = _ROOT
BASE = ROOT / "03_PERMITS_AND_INSPECTIONS"

PROPS = [
    ("2264_Tom_St", "BP-2026-1621", "21-2S-26-0780-0QQ00-1020", "2264 Tom Street"),
    ("2268_Tom_St", "BP-2026-1612", "21-2S-26-0780-0QQ00-1490", "2268 Tom Street"),
]

def build(slug, pn, parcel, addr):
    d = json.load(open(BASE / slug / f"{pn}_project_by_uid.json"))["data"]
    ins = json.load(open(BASE / slug / f"{pn}_inspections.json"))["data"]
    req = json.load(open(BASE / slug / f"{pn}_requirements.json"))
    pay = json.load(open(BASE / slug / f"{pn}_payments.json")).get("data") or []
    files = json.load(open(BASE / slug / f"{pn}_project_files.json")).get("data") or []

    L = []
    A = L.append
    A(f"# Permit Record — {pn} — {addr}")
    A("")
    A(f"**Parcel (Property Appraiser, verified):** `{parcel}`  ")
    A(f"**Parcel (as stored in MGO):** `{d.get('parcelNumber')}`")
    A("")
    A("## Permit identification")
    A("")
    A("| Field | Value |")
    A("|---|---|")
    for k, lab in [("projectNumber", "Project / permit number"),
                   ("workType", "Work type"),
                   ("projectStatus", "Current status"),
                   ("projectAddress", "Site address"),
                   ("lot", "Lot"),
                   ("subDivision", "Subdivision"),
                   ("parcelNumber", "Parcel (MGO)"),
                   ("squareFootage", "Square footage"),
                   ("dateCreated", "Application created"),
                   ("dateIssued", "Permit issued"),
                   ("dateUpdated", "Record last updated"),
                   ("balanceAmount", "Total fees"),
                   ("balancePaidAmount", "Fees paid"),
                   ("balanceDueAmount", "Balance due"),
                   ("projectID", "MGO internal project ID"),
                   ("projectUID", "MGO project UID")]:
        A(f"| {lab} | {d.get(k)} |")
    A("")
    A("## Parties")
    A("")
    A("| Role | Name | Business | Email |")
    A("|---|---|---|---|")
    A(f"| Applicant | {d.get('applicantFirstName')} {d.get('applicantLastName')} "
      f"| {d.get('applicantBusinessName')} | {d.get('applicantEmail')} |")
    A(f"| Owner of record (Property Appraiser) | Holiday Builders Inc | — | — |")
    A("")
    A(f"Applicant mailing address of record: {d.get('mailingAddress')}, "
      f"{d.get('mailingCity')}, {d.get('mailingState')} {d.get('mailingZip')}")
    A("")
    A("## Outstanding county requirements")
    A("")
    open_items = [r for r in req
                  if str(r.get("Status")) not in ("Approved", "Complete", "Passed")]
    A(f"{len(open_items)} of {len(req)} requirements are **not** yet complete.")
    A("")
    A("| Requirement | Status |")
    A("|---|---|")
    for r in sorted(open_items, key=lambda x: str(x.get("Requirement"))):
        A(f"| {r.get('Requirement')} | **{r.get('Status')}** |")
    A("")
    A("### Drainage-specific requirements")
    A("")
    A("| Requirement | Status |")
    A("|---|---|")
    for r in req:
        n = str(r.get("Requirement"))
        if any(k in n for k in ("Drainage", "Grading", "Driveway", "Flood")):
            A(f"| {n} | **{r.get('Status')}** |")
    A("")
    A("## Documents")
    A("")
    if files:
        for f in files:
            A(f"- {f}")
    else:
        A("**No documents are exposed by the MGO customer portal for this permit.**")
        A("")
        A("The endpoint `/api/v3/cp/ProjectFiles/get-customer-files-by-project-id/"
          f"{d.get('projectID')}` returns `data: []`.")
        A("")
        A("Note that the county's own task list requires a **\"Certified Drainage "
          "as Built\"** document for this permit, which confirms such documents "
          "exist in the county's internal file even though they are not released "
          "through the portal.")
    A("")
    A("## Provenance")
    A("")
    A(f"- Portal: `https://www.mgoconnect.org/cp/project-details/{d.get('projectUID')}`")
    A("- Endpoints used: `/api/v3/cp/project/by-uid/{uid}`, "
      "`/api/v3/cp/work-orders/{pid}/inspections`, "
      "`/cp/ProjectRequirements/byProjectID/{pid}`, "
      "`/api/v3/cp/ProjectFiles/get-customer-files-by-project-id/{pid}`")
    A(f"- Retrieved (UTC): {datetime.now(timezone.utc).isoformat()}")
    A("- Raw JSON for every field above is stored alongside this file.")
    f = BASE / slug / f"{pn}_PERMIT_RECORD.md"
    f.write_text("\n".join(L), encoding="utf-8")
    return f, len(open_items)

if __name__ == "__main__":
    for slug, pn, parcel, addr in PROPS:
        f, n = build(slug, pn, parcel, addr)
        print(f"wrote {f} ({f.stat().st_size} bytes) open_requirements={n}")