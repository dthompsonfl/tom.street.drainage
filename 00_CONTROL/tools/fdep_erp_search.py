#!/usr/bin/env python3
"""Search the Florida Water Permits ERP portal by site address.

Public, no login.  Saves results HTML + extracted record rows as evidence.
"""

import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:  # noqa: E402
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT  # noqa: E402
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = _ROOT
OUT = ROOT / "09_ENVIRONMENTAL_PERMITS/SYSTEM_RAW"
URL = "http://flwaterpermits.com/agws10/fpperp1/"

def search(addr, tag):
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = b.new_context(viewport={"width": 1500, "height": 1000})
        pg = ctx.new_page()
        pg.set_default_timeout(60000)
        pg.goto(URL, wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(8000)
        pg.fill("#locText", addr)
        pg.click("#imgLoc")
        pg.wait_for_timeout(16000)
        txt = pg.inner_text("body")
        pg.screenshot(path=f"fwp_{tag}.png", full_page=True)
        OUT.mkdir(parents=True, exist_ok=True)
        f = OUT / f"flwaterpermits_erp_{tag}.html"
        f.write_text(pg.content(), encoding="utf-8")
        rec = {"query_address": addr, "url": pg.url,
               "retrieved_utc": datetime.now(timezone.utc).isoformat(),
               "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
               "bytes": f.stat().st_size, "relative_path": str(f.relative_to(ROOT))}
        ctx.close()
        b.close()
    return rec, txt

if __name__ == "__main__":
    addr = sys.argv[1]
    tag = re.sub(r"[^A-Za-z0-9]+", "_", addr)
    rec, txt = search(addr, tag)
    print("QUERY:", rec["query_address"])
    print("SAVED:", rec["relative_path"], rec["bytes"], "bytes")
    print("---- PAGE TEXT ----")
    print(txt[:4000])