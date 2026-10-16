#!/usr/bin/env python3
"""Probe MGO Connect for customer-visible documents, permit card / receipt

reports, and project photos on a given permit."""

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

pn = sys.argv[1]
slug = sys.argv[2]
addr = sys.argv[3]

base = ROOT / "03_PERMITS_AND_INSPECTIONS" / slug
proj = json.load(open(base / f"{pn}_project_by_uid.json"))["data"]
pid = proj["projectID"]
uid = proj["projectUID"]

CANDIDATES = [
    f"/api/v3/cp/ProjectFiles/get-customer-files-by-project-id/{pid}",
    f"/api/v3/cp/project-files/{pid}",
    f"/api/v3/cp/project/{pid}/files",
    f"/api/v3/cp/project/{pid}/documents",
    f"/api/v3/cp/ProjectDocuments/{pid}",
    f"/api/v3/cp/project-photos/{pid}",
    f"/api/v3/cp/project/{pid}/photos",
    f"/api/v3/cp/project/{pid}/receipt",
    f"/api/v3/cp/reports/permit-receipt/{pid}",
    f"/api/v3/cp/project/{pid}/permit",
    f"/api/v3/cp/project/{pid}/print",
    f"/api/v3/cp/project-public-comments/get-by-project-id/{pid}",
    f"/cp/ProjectRequirements/byProjectID/{pid}?forceLoad=false",
]

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = b.new_context(storage_state=AUTH)
    pg = ctx.new_page()
    pg.goto("https://www.mgoconnect.org/cp/search?jid=276&pid=3",
            wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(9000)
    tok = {}
    pg.on("request", lambda r: tok.setdefault("t", r.headers.get("x-csrf-token"))
          if "api.mgoconnect.org" in r.url and r.headers.get("x-csrf-token") else None)
    pg.goto("https://www.mgoconnect.org/cp/project-details/" + uid,
            wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(14000)
    print("PROJECT PAGE:", pg.url)
    print("---- VISIBLE TABS ----")
    for i in pg.query_selector_all("a,button,li,.p-tab,.nav-link,span[role=tab]"):
        try:
            if i.is_visible():
                t = (i.inner_text() or "").strip()
                if t and len(t) < 40:
                    print("   ", t)
        except Exception:
            pass
    hdr = {"Accept": "application/json, */*",
           "Referer": "https://www.mgoconnect.org/",
           "SourcePlatform": "MGO Connect Web"}
    if tok.get("t"):
        hdr["x-csrf-token"] = tok["t"]
    for c in CANDIDATES:
        try:
            r = ctx.request.get(API + c, headers=hdr)
            body = r.body()
            ct = r.headers.get("content-type", "")
            print(f"\n{c}\n   -> {r.status} {ct} {len(body)}b")
            if body[:4] == b"%PDF" or "pdf" in ct:
                fn = base / f"{pn}_{c.rsplit('/',1)[-1]}.pdf"
                fn.write_bytes(body)
                print("   SAVED PDF:", fn)
            else:
                print("   ", body[:400])
        except Exception as e:
            print(c, "ERR", e)
    ctx.close()
    b.close()