#!/usr/bin/env python3
"""Bulk MGO Connect project search across address variants, developer names,
subdivisions and parcels, using the authenticated API.

Usage: python3 mgo_bulksearch.py
"""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

AUTH = "/tmp/opencode/mgo_auth.json"
API = "https://api.mgoconnect.org"
ROOT = Path("/home/dylan/Tom-Street-Drainage-Investigation")
OUT = ROOT / "03_PERMITS_AND_INSPECTIONS/SYSTEM_RAW"

QUERIES = []
# Whole-street sweep: every address on the 2200-2300 block of Tom St
for n in list(range(2200, 2300, 2)) + list(range(2201, 2300, 2)):
    QUERIES.append(("ADDRESS", f"{n} TOM ST"))
# Target parcels exactly (MGO stores parcels without separators)
for pid in ("212S2607800QQ001020", "212S2607800QQ001490",
            "212S2607800QQ001060", "212S2607800QQ001180"):
    QUERIES.append(("PARCELNUMBER", pid))
# Developer / builder variants
for b in ("Holiday Builders", "HOLIDAY BUILDERS INC", "Holiday Builders Inc",
          "Hadleigh", "Hadleigh Hills"):
    QUERIES.append(("BUSINESSNAME", b))
# Subdivision
for s in ("CRESCENT SHORES", "Crescent Shores"):
    QUERIES.append(("SUBDIVISION", s))


def search(ctx, hdr, key, val):
    body = {"filters": {"JURISDICTIONID": 276, "PROJECTTYPEID": 3, key: val,
                        "ISADDRESSEXACTMATCH": False, "ISUNITEXACTMATCH": True,
                        "ISSUBDIVISIONEXACTMATCH": False,
                        "ISLOTNUMBEREXACTMATCH": False,
                        "ISPARCELNUMBEREXACTMATCH": False, "EXPANDED": True},
            "Rows": 300, "OffSet": 0, "SortOrder": 1}
    try:
        r = ctx.request.post(API + "/api/v3/cp/project/search-projects",
                             headers=hdr, data=json.dumps(body))
        return r.json()
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = b.new_context(storage_state=AUTH, viewport={"width": 1600, "height": 1000})
        pg = ctx.new_page()
        pg.set_default_timeout(80000)
        tok = {}
        pg.on("request", lambda r: tok.setdefault("t", r.headers.get("x-csrf-token"))
              if "api.mgoconnect.org" in r.url and r.headers.get("x-csrf-token") else None)
        pg.goto("https://www.mgoconnect.org/cp/search?jid=276&pid=3",
                wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(10000)
        hdr = {"Content-Type": "application/json", "Accept": "application/json",
               "SourcePlatform": "MGO Connect Web",
               "Referer": "https://www.mgoconnect.org/",
               "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
        if tok.get("t"):
            hdr["x-csrf-token"] = tok["t"]

        found = {}
        log = []
        for key, val in QUERIES:
            res = search(ctx, hdr, key, val)
            data = res.get("data") or []
            if data:
                log.append({"key": key, "val": val, "n": len(data)})
            for row in data:
                pn = row.get("projectNumber")
                if pn:
                    found[pn] = row
            print(f"{key:13} {val:<28} -> {len(data)}")
        OUT.mkdir(parents=True, exist_ok=True)
        blob = {"retrieved_utc": datetime.now(timezone.utc).isoformat(),
                "queries": log, "projects": found}
        f = OUT / "mgo_bulk_search_results.json"
        f.write_text(json.dumps(blob, indent=1))
        print(f"\nUNIQUE PROJECTS: {len(found)}")
        for pn, r in sorted(found.items()):
            print(f"  {pn:<24} {r.get('workType','')[:32]:<34} "
                  f"{r.get('projectStatus',''):<26} {r.get('projectAddress','')}"
                  f"  parcel={r.get('parcelNumber')}")
        print("saved", f, f.stat().st_size)
        ctx.storage_state(path=AUTH)
        ctx.close()
        b.close()