#!/usr/bin/env python3
"""Pull an MGO permit record directly by project number (no address search),

used to inspect the neighbouring driveway-connection permits that the 2264 Tom St
inspection named as the tie-in points."""

import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:  # noqa: E402
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT  # noqa: E402
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

AUTH = "/tmp/opencode/mgo_auth.json"
API = "https://api.mgoconnect.org"
ROOT = _ROOT

def main(pns, slug):
    out = ROOT / "04_ENGINEERING_AND_DRAINAGE" / "Tom_Street_Shared_System"
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = b.new_context(storage_state=AUTH)
        pg = ctx.new_page()
        pg.set_default_timeout(60000)
        tok = {}
        pg.on("request", lambda r: tok.setdefault("t", r.headers.get("x-csrf-token"))
              if "api.mgoconnect.org" in r.url and r.headers.get("x-csrf-token") else None)
        pg.goto("https://www.mgoconnect.org/cp/search?jid=276&pid=3",
                wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(9000)
        hdr = {"Content-Type": "application/json", "Accept": "application/json",
               "SourcePlatform": "MGO Connect Web",
               "Referer": "https://www.mgoconnect.org/"}
        if tok.get("t"):
            hdr["x-csrf-token"] = tok["t"]
        results = {}
        for pn in pns:
            body = {"filters": {"JURISDICTIONID": 276, "PROJECTTYPEID": 3,
                                "PROJECTNUMBER": pn,
                                "ISADDRESSEXACTMATCH": False,
                                "ISUNITEXACTMATCH": True,
                                "ISSUBDIVISIONEXACTMATCH": False,
                                "ISLOTNUMBEREXACTMATCH": False,
                                "ISPARCELNUMBEREXACTMATCH": False,
                                "EXPANDED": True},
                    "Rows": 50, "OffSet": 0, "SortOrder": 1}
            res = ctx.request.post(API + "/api/v3/cp/project/search-projects",
                                   headers=hdr, data=json.dumps(body),
                                   timeout=45000).json()
            row = next((r for r in (res.get("data") or [])
                        if r.get("projectNumber") == pn), None)
            if not row:
                print(f"{pn}: not found")
                continue
            pid = row["projectID"]
            det = ctx.request.get(
                API + f"/api/v3/cp/project/by-uid/{row['projectUID']}",
                headers=hdr).json()
            ins = ctx.request.get(
                API + f"/api/v3/cp/work-orders/{pid}/inspections",
                headers=hdr).json()
            req = ctx.request.get(
                API + f"/cp/ProjectRequirements/byProjectID/{pid}?forceLoad=false",
                headers=hdr).json()
            results[pn] = {"search_row": row, "detail": det,
                           "inspections": ins, "requirements": req}
            print(f"\n=== {pn} ({row.get('workType')}) - {row.get('projectAddress')}"
                  f" - {row.get('projectStatus')}")
            for x in (ins.get("data") or []):
                print(f"    {x['inspectionDateTime'][:16]}  {x['inspectionStatus']:<12}"
                      f" {x['inspectionType']}")
                if x.get("comments"):
                    print("        >>", x["comments"][:400])
            (out / f"{pn}.json").write_text(json.dumps(results[pn], indent=1))
        (out / f"neighbouring_permits_{slug}.json").write_text(
            json.dumps({k: {"workType": v["search_row"].get("workType"),
                            "address": v["search_row"].get("projectAddress"),
                            "status": v["search_row"].get("projectStatus")}
                        for k, v in results.items()}, indent=1))
        ctx.close()
        b.close()
    print("\nsaved to", out)

if __name__ == "__main__":
    main(sys.argv[1].split(","), sys.argv[2] if len(sys.argv) > 2 else "neighbours")