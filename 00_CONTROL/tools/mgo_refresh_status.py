#!/usr/bin/env python3
"""Refresh the current MGO Connect status of both target permits.

Re-reads the authoritative county record so that any statement in the
repository about permit status carries a current capture timestamp rather than
only the original acquisition timestamp.

Run:  python3 00_CONTROL/tools/mgo_refresh_status.py
"""
import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT, rel, sha256_file, utcnow  # noqa: E402

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

AUTH = "/tmp/opencode/mgo_auth.json"
API = "https://api.mgoconnect.org"
OUT = _ROOT / "03_PERMITS_AND_INSPECTIONS" / "STATUS_REFRESH"

TARGETS = [
    ("2264_Tom_St", "BP-2026-1621", "21-2S-26-0780-0QQ00-1020"),
    ("2268_Tom_St", "BP-2026-1612", "21-2S-26-0780-0QQ00-1490"),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = b.new_context(storage_state=AUTH, viewport={"width": 1500, "height": 1000})
        pg = ctx.new_page()
        pg.set_default_timeout(60000)
        tok = {}
        pg.on("request", lambda r: tok.setdefault("t", r.headers.get("x-csrf-token"))
              if "api.mgoconnect.org" in r.url and r.headers.get("x-csrf-token") else None)
        pg.goto("https://www.mgoconnect.org/cp/search?jid=276&pid=3",
                wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(10000)
        if "/cp/login" in pg.url:
            print("SESSION EXPIRED - re-authentication required.")
            ctx.storage_state(path=AUTH)
            ctx.close(); b.close()
            return
        hdr = {"Content-Type": "application/json", "Accept": "application/json",
               "SourcePlatform": "MGO Connect Web",
               "Referer": "https://www.mgoconnect.org/"}
        if tok.get("t"):
            hdr["x-csrf-token"] = tok["t"]
        for slug, pn, parcel in TARGETS:
            body = {"filters": {"JURISDICTIONID": 276, "PROJECTTYPEID": 3,
                                "PROJECTNUMBER": pn,
                                "ISADDRESSEXACTMATCH": False,
                                "ISUNITEXACTMATCH": True,
                                "ISSUBDIVISIONEXACTMATCH": False,
                                "ISLOTNUMBEREXACTMATCH": False,
                                "ISPARCELNUMBEREXACTMATCH": False,
                                "EXPANDED": True},
                    "Rows": 50, "OffSet": 0, "SortOrder": 1}
            row = next((r for r in (ctx.request.post(
                API + "/api/v3/cp/project/search-projects", headers=hdr,
                data=json.dumps(body), timeout=45000).json().get("data") or [])
                if r.get("projectNumber") == pn), None)
            if not row:
                print(f"  {pn}: NOT FOUND")
                continue
            pid, uid = row["projectID"], row["projectUID"]
            det = ctx.request.get(API + f"/api/v3/cp/project/by-uid/{uid}",
                                  headers=hdr).json().get("data") or {}
            req = ctx.request.get(
                API + f"/cp/ProjectRequirements/byProjectID/{pid}?forceLoad=false",
                headers=hdr).json()
            ins = ctx.request.get(API + f"/api/v3/cp/work-orders/{pid}/inspections",
                                  headers=hdr).json().get("data") or []
            files = ctx.request.get(
                API + f"/api/v3/cp/ProjectFiles/get-customer-files-by-project-id/{pid}",
                headers=hdr).json().get("data") or []
            open_req = [r for r in req
                        if str(r.get("Status")) not in ("Approved", "Complete",
                                                        "Passed")]
            blob = {
                "retrieved_utc": utcnow(),
                "permit_number": pn, "parcel_property_appraiser": parcel,
                "parcel_mgo": det.get("parcelNumber"),
                "status_at_refresh": det.get("projectStatus"),
                "status_in_search_index": row.get("projectStatus"),
                "dateCreated": det.get("dateCreated"),
                "dateIssued": det.get("dateIssued"),
                "dateUpdated": det.get("dateUpdated"),
                "applicant": {"name": f"{det.get('applicantFirstName')} "
                                      f"{det.get('applicantLastName')}",
                              "business": det.get("applicantBusinessName")},
                "subdivision": det.get("subDivision"),
                "lot": det.get("lot"),
                "squareFootage": det.get("squareFootage"),
                "customer_files_exposed": len(files),
                "inspection_count": len(ins),
                "latest_inspection": max((i["inspectionDateTime"] for i in ins),
                                         default=None),
                "requirement_count": len(req),
                "open_requirement_count": len(open_req),
                "certificate_of_occupancy_requirement": next(
                    ({"requirement": r.get("Requirement"),
                      "status": r.get("Status")}
                     for r in req if "Issue CO" in str(r.get("Requirement"))),
                    None),
                "certified_drainage_as_built_requirement": next(
                    ({"requirement": r.get("Requirement"),
                      "status": r.get("Status")}
                     for r in req
                     if "Certified Drainage as Built" in str(r.get("Requirement"))),
                    None),
                "open_requirements": [
                    {"requirement": r.get("Requirement"), "status": r.get("Status")}
                    for r in sorted(open_req, key=lambda x: str(x.get("Requirement")))],
            }
            f = OUT / f"{pn}_status_refresh.json"
            f.write_text(json.dumps(blob, indent=1))
            print(f"  {pn}: status={blob['status_at_refresh']} "
                  f"updated={blob['dateUpdated']} "
                  f"open_reqs={blob['open_requirement_count']} "
                  f"CO={blob['certificate_of_occupancy_requirement']} "
                  f"DAB={blob['certified_drainage_as_built_requirement']}")
        ctx.storage_state(path=AUTH)
        ctx.close(); b.close()
    print("wrote", rel(OUT))


if __name__ == "__main__":
    main()