#!/usr/bin/env python3
"""Direct authenticated MGO Connect API access using the logged-in browser
context (shares cookies/headers). Used for bulk permit and document retrieval.

Endpoints discovered from the live application:
  POST /api/v3/cp/project/search-projects
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

AUTH = "/tmp/opencode/mgo_auth.json"
API = "https://api.mgoconnect.org"
ROOT = Path("/home/dylan/Tom-Street-Drainage-Investigation")


def ctx_with_auth(p, url="https://www.mgoconnect.org/cp/home"):
    b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = b.new_context(storage_state=AUTH,
                        viewport={"width": 1600, "height": 1100})
    pg = ctx.new_page()
    pg.goto(url, wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(7000)
    return b, ctx, pg


def search_projects(ctx, **filters):
    f = {"JURISDICTIONID": 276, "PROJECTTYPEID": 3,
         "ISADDRESSEXACTMATCH": False, "ISUNITEXACTMATCH": True,
         "ISSUBDIVISIONEXACTMATCH": False, "ISLOTNUMBEREXACTMATCH": False,
         "ISPARCELNUMBEREXACTMATCH": False, "EXPANDED": True}
    f.update(filters)
    body = {"filters": f, "Rows": 200, "OffSet": 0, "SortOrder": 1}
    r = ctx.request.post(API + "/api/v3/cp/project/search-projects",
                         data=json.dumps(body),
                         headers={"Content-Type": "application/json"})
    try:
        return r.json()
    except Exception:
        return {"status": r.status, "text": r.text()[:2000]}


if __name__ == "__main__":
    with sync_playwright() as p:
        b, ctx, pg = ctx_with_auth(p)
        which = sys.argv[1] if len(sys.argv) > 1 else "address"
        val = sys.argv[2] if len(sys.argv) > 2 else "2264 TOM ST"
        key = {"address": "ADDRESS", "parcel": "PARCELNUMBER",
               "projectnumber": "PROJECTNUMBER",
               "business": "BUSINESSNAME"}.get(which, "ADDRESS")
        res = search_projects(ctx, **{key: val})
        print("KEY:", key, "=", val)
        print(json.dumps(res, indent=1)[:6000])
        ctx.close()
        b.close()