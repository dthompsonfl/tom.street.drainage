#!/usr/bin/env python3
"""Pull the full MGO Connect record for a permit: project detail, project
files/documents, work orders, inspections, contacts, types and requirements.

The x-csrf-token is captured from the live page (the application issues one per
session); it is never written to disk.
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

PROJECT_NUMBER = sys.argv[1] if len(sys.argv) > 1 else "BP-2026-1621"
SLUG = sys.argv[2] if len(sys.argv) > 2 else "2264_Tom_St"
ADDRESS = sys.argv[3] if len(sys.argv) > 3 else "2264 TOM ST"

ENDPOINTS = [
    ("project_by_uid", "/api/v3/cp/project/by-uid/{uid}"),
    ("project_files", "/api/v3/cp/ProjectFiles/get-customer-files-by-project-id/{pid}"),
    ("work_orders", "/api/v3/cp/work-orders/{pid}"),
    ("inspections", "/api/v3/cp/work-orders/{pid}/inspections"),
    ("types", "/api/v3/types/get-types-by-project-id/{pid}"),
    ("contacts", "/api/v3/cp/project-contacts/{pid}"),
    ("payments", "/api/v3/cp/project-payments/{pid}"),
    ("fees", "/api/v3/cp/project-type-fees/type-fees/{pid}?isProjectContractor=false"),
]


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = b.new_context(storage_state=AUTH, viewport={"width": 1700, "height": 1300})
        pg = ctx.new_page()
        pg.set_default_timeout(80000)
        token = {}
        pg.on("request", lambda r: token.setdefault("t", r.headers.get("x-csrf-token"))
              if "api.mgoconnect.org" in r.url and r.headers.get("x-csrf-token") else None)

        pg.goto("https://www.mgoconnect.org/cp/search?jid=276&pid=3",
                wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(9000)
        pg.fill("input[placeholder='Address Search Autocomplete']", ADDRESS)
        pg.wait_for_timeout(1800)
        for bb in pg.query_selector_all("button"):
            if bb.inner_text().strip() == "Search" and bb.is_visible():
                bb.click()
                break
        pg.wait_for_timeout(15000)
        uid = pid = None
        for r in pg.query_selector_all("table tbody tr"):
            if PROJECT_NUMBER in (r.inner_text() or ""):
                r.query_selector("span[aria-label='Row actions']").click()
                pg.wait_for_timeout(4000)
                for item in pg.query_selector_all(".grid-action-item"):
                    if "view project" in (item.inner_text() or "").lower():
                        item.click()
                        break
                break
        pg.wait_for_timeout(18000)
        url = pg.url
        m = re.search(r"project-details/([0-9A-Fa-f-]{36})", url)
        uid = m.group(1) if m else None
        print("PROJECT UID:", uid)

        hdr = {"Content-Type": "application/json", "Accept": "application/json",
               "SourcePlatform": "MGO Connect Web",
               "Referer": "https://www.mgoconnect.org/",
               "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
        if token.get("t"):
            hdr["x-csrf-token"] = token["t"]

        # project id comes from the live API traffic
        pid = None
        for c in []:
            pass
        det = ctx.request.get(API + f"/api/v3/cp/project/by-uid/{uid}", headers=hdr).json()
        out = ROOT / "03_PERMITS_AND_INSPECTIONS" / SLUG
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{PROJECT_NUMBER}_project_by_uid.json").write_text(json.dumps(det, indent=1))
        data = det.get("data") or {}
        pid = data.get("projectID") or data.get("projectId")
        if not pid:
            # search-projects has projectID
            body = {"filters": {"JURISDICTIONID": 276, "PROJECTTYPEID": 3,
                                "PROJECTNUMBER": PROJECT_NUMBER,
                                "ISADDRESSEXACTMATCH": False,
                                "ISUNITEXACTMATCH": True,
                                "ISSUBDIVISIONEXACTMATCH": False,
                                "ISLOTNUMBEREXACTMATCH": False,
                                "ISPARCELNUMBEREXACTMATCH": False,
                                "EXPANDED": True},
                    "Rows": 50, "OffSet": 0, "SortOrder": 1}
            res = ctx.request.post(API + "/api/v3/cp/project/search-projects",
                                   headers=hdr, data=json.dumps(body)).json()
            for row in (res.get("data") or []):
                if row.get("projectNumber") == PROJECT_NUMBER:
                    pid = row.get("projectID")
        print("PROJECT ID:", pid)

        bundle = {}
        for name, tmpl in ENDPOINTS:
            if "{uid}" in tmpl:
                ep = tmpl.format(uid=uid)
            elif pid:
                ep = tmpl.format(pid=pid)
            else:
                continue
            try:
                r = ctx.request.get(API + ep, headers=hdr)
                try:
                    body = r.json()
                except Exception:
                    body = {"status": r.status, "text": r.text()[:1500]}
            except Exception as e:
                body = {"error": str(e)}
            bundle[name] = {"endpoint": ep, "status": r.status, "body": body}
            n = ""
            if isinstance(body, dict):
                d = body.get("data")
                n = f"{len(d)} items" if isinstance(d, list) else (
                    "obj" if isinstance(d, dict) else "")
            print(f"  {name:16} {r.status} {n}")
            (out / f"{PROJECT_NUMBER}_{name}.json").write_text(json.dumps(body, indent=1))

        ctx.storage_state(path=AUTH)
        ctx.close()
        b.close()
    print("saved bundle under 03_PERMITS_AND_INSPECTIONS/" + SLUG)


if __name__ == "__main__":
    main()