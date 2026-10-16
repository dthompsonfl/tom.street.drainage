#!/usr/bin/env python3
"""Search the authenticated MGO Connect permit & project search for Santa Rosa
County (JID=276, PID=3), then open and capture each matching project record
and every attachment listed against it.

Search fields available on the form:
  Project Number | Project Name | Project Alias | Project Description
  Created After / Before | Address Search Autocomplete | Unit #
  Subdivision | Lot Number | Parcel Number
  First Name | Last Name | Business Name

Usage:
  python3 mgo_search.py parcel 21-2S-26-0780-0QQ00-1020
  python3 mgo_search.py address "2264 Tom St"
  python3 mgo_search.py business "Holiday Builders"
"""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

AUTH = "/tmp/opencode/mgo_auth.json"
ROOT = Path("/home/dylan/Tom-Street-Drainage-Investigation")
OUT = ROOT / "03_PERMITS_AND_INSPECTIONS/SYSTEM_RAW"
SEARCH = "https://www.mgoconnect.org/cp/search?jid=276&pid=3"

PLACEHOLDER = {
    "parcel": "Parcel Number",
    "address": "Address Search Autocomplete",
    "lot": "Lot Number",
    "subdivision": "Subdivision",
    "projectnumber": "Project Number",
    "projectname": "Project Name",
    "business": "Business Name",
    "lastname": "Last Name",
    "firstname": "First Name",
}


def open_app(pg):
    pg.goto(SEARCH, wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(9000)
    if "/cp/login" in pg.url or pg.query_selector_all("[role=combobox]"):
        pg.goto("https://www.mgoconnect.org/cp/home",
                wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(9000)
        b = pg.query_selector_all("[role=combobox]")
        if len(b) >= 2:
            b[0].click()
            pg.wait_for_timeout(2200)
            for o in pg.query_selector_all("li[role=option]"):
                if o.inner_text().strip().lower().startswith("florida"):
                    o.click()
                    break
            pg.wait_for_timeout(2500)
            b = pg.query_selector_all("[role=combobox]")
            b[1].click()
            pg.wait_for_timeout(2200)
            for o in pg.query_selector_all("li[role=option]"):
                if "santa rosa" in o.inner_text().strip().lower():
                    o.click()
                    break
            pg.wait_for_timeout(2200)
            for bt in pg.query_selector_all("button"):
                if bt.inner_text().strip() == "Continue":
                    bt.click()
                    break
            pg.wait_for_timeout(12000)
        pg.goto(SEARCH, wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(14000)
    return pg.url


def do_search(pg, kind, value):
    url = open_app(pg)
    if "/cp/login" in url:
        print("NOT AUTHENTICATED")
        return []
    ph = PLACEHOLDER[kind]
    filled = False
    for e in pg.query_selector_all(f"input[placeholder='{ph}']"):
        try:
            if e.is_visible():
                e.fill(value)
                pg.wait_for_timeout(1500)
                # autocomplete dropdown
                for o in pg.query_selector_all("li, .p-autocomplete-item, [role=option]"):
                    t = (o.inner_text() or "").strip()
                    if t and value.lower()[:8] in t.lower():
                        o.click()
                        break
                filled = True
                break
        except Exception:
            pass
    print(f"filled {ph}={value!r}: {filled}")
    for e in pg.query_selector_all("button"):
        if e.inner_text().strip() == "Search" and e.is_visible():
            e.click()
            break
    pg.wait_for_timeout(16000)
    return extract(pg)


def extract(pg):
    txt = pg.inner_text("body")
    m = re.search(r"Showing\s+(\d+)\s+to\s+(\d+)\s+of\s+(\d+)\s+entries", txt)
    total = int(m.group(3)) if m else 0
    rows = []
    for tr in pg.query_selector_all("table tr"):
        cells = [re.sub(r"\s+", " ", (c.inner_text() or "").strip())
                 for c in tr.query_selector_all("th,td")]
        if len(cells) >= 3 and any(cells) and not cells[0].lower().startswith("project #"):
            rows.append(cells)
    print("TOTAL ENTRIES:", total, "| rows captured:", len(rows))
    return {"total": total, "rows": rows, "text": txt}


if __name__ == "__main__":
    kind, value = sys.argv[1], sys.argv[2]
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = b.new_context(storage_state=AUTH, viewport={"width": 1700, "height": 1300})
        pg = ctx.new_page()
        pg.set_default_timeout(75000)
        res = do_search(pg, kind, value)
        tag = re.sub(r"[^A-Za-z0-9]+", "_", f"{kind}_{value}")
        OUT.mkdir(parents=True, exist_ok=True)
        f = OUT / f"mgo_search_{tag}.html"
        f.write_text(pg.content(), encoding="utf-8")
        print("saved:", f, f.stat().st_size, "bytes")
        pg.screenshot(path=f"mgo_{tag}.png", full_page=True)
        ctx.storage_state(path=AUTH)
        ctx.close()
        b.close()
    print("---- RESULT TEXT ----")
    print(res.get("text", "")[:3000])
    print("---- ROWS ----")
    for r in res.get("rows", [])[:40]:
        print(r)