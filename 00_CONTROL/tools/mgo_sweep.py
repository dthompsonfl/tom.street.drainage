#!/usr/bin/env python3
"""Lean MGO Connect sweep: confirm whether any permit other than the two single-
family permits exists for the Tom Street frontage, using targeted developer,
subdivision and neighbouring-address queries. Per-request timeouts are enforced
so a slow endpoint cannot stall the run."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

AUTH = "/tmp/opencode/mgo_auth.json"
API = "https://api.mgoconnect.org"
ROOT = Path("/home/dylan/Tom-Street-Drainage-Investigation")
OUT = ROOT / "03_PERMITS_AND_INSPECTIONS/SYSTEM_RAW"

QUERIES = [
    ("BUSINESSNAME", "Holiday Builders INC"),
    ("BUSINESSNAME", "Holiday Builders"),
    ("BUSINESSNAME", "Hadleigh Hills"),
    ("SUBDIVISION", "CRESCENT SHORES"),
    ("PARCELNUMBER", "212S2607800QQ001020"),
    ("PARCELNUMBER", "212S2607800QQ001490"),
    ("ADDRESS", "2260 TOM ST"),
    ("ADDRESS", "2270 TOM ST"),
    ("ADDRESS", "2265 TOM ST"),
    ("ADDRESS", "2266 TOM ST"),
    ("ADDRESS", "2267 TOM ST"),
    ("ADDRESS", "2274 TOM ST"),
]


def search(ctx, hdr, key, val):
    body = {"filters": {"JURISDICTIONID": 276, "PROJECTTYPEID": 3, key: val,
                        "ISADDRESSEXACTMATCH": False, "ISUNITEXACTMATCH": True,
                        "ISSUBDIVISIONEXACTMATCH": False,
                        "ISLOTNUMBEREXACTMATCH": False,
                        "ISPARCELNUMBEREXACTMATCH": False, "EXPANDED": True},
            "Rows": 300, "OffSet": 0, "SortOrder": 1}
    try:
        r = ctx.request.post(API + "/api/v3/cp/project/search-projects",
                             headers=hdr, data=json.dumps(body), timeout=45000)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
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
        hdr = {"Content-Type": "application/json", "Accept": "application/json",
               "SourcePlatform": "MGO Connect Web",
               "Referer": "https://www.mgoconnect.org/"}
        if tok.get("t"):
            hdr["x-csrf-token"] = tok["t"]
        found, log = {}, []
        for key, val in QUERIES:
            res = search(ctx, hdr, key, val)
            if res.get("error"):
                print(f"{key:13} {val:<26} -> ERROR {res['error'][:60]}")
                continue
            data = res.get("data") or []
            log.append({"key": key, "val": val, "n": len(data)})
            for row in data:
                if row.get("projectNumber"):
                    found[row["projectNumber"]] = row
            print(f"{key:13} {val:<26} -> {len(data)}")
        OUT.mkdir(parents=True, exist_ok=True)
        blob = {"retrieved_utc": datetime.now(timezone.utc).isoformat(),
                "queries": log, "unique_projects": len(found), "projects": found}
        f = OUT / "mgo_sweep_results.json"
        f.write_text(json.dumps(blob, indent=1))
        print(f"\nUNIQUE PROJECTS: {len(found)}")
        for pn, r in sorted(found.items()):
            print(f"  {pn:<24} {str(r.get('workType'))[:30]:<32} "
                  f"{str(r.get('projectStatus'))[:24]:<26} "
                  f"{str(r.get('projectAddress')):<16} "
                  f"parcel={r.get('parcelNumber')} "
                  f"id={r.get('projectID')}")
        print("saved", f)
        ctx.close()
        b.close()