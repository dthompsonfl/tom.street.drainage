#!/usr/bin/env python3
"""Open an MGO Connect permit record and enumerate every document, plan,
attachment, inspection and revision tab the county exposes.

Usage:
  python3 mgo_record.py BP-2026-1621 2264_Tom_St
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


def prepare(pg):
    pg.goto("https://www.mgoconnect.org/cp/search?jid=276&pid=3",
            wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(8000)
    if pg.query_selector_all("[role=combobox]"):
        for i in (0, 1):
            b = pg.query_selector_all("[role=combobox]")
            if len(b) > i:
                b[i].click()
                pg.wait_for_timeout(2200)
                key = "florida" if i == 0 else "santa rosa"
                for o in pg.query_selector_all("li[role=option]"):
                    if key in o.inner_text().strip().lower():
                        o.click()
                        break
                pg.wait_for_timeout(2200)
        for bt in pg.query_selector_all("button"):
            if bt.inner_text().strip() == "Continue":
                bt.click()
                break
        pg.wait_for_timeout(12000)


def open_project(pg, project_number, slug):
    api = []
    pg.on("request", lambda r: api.append(
        {"method": r.method, "url": r.url[:400],
         "post": (r.post_data or "")[:2000]})
        if "api.mgoconnect.org" in r.url else None)
    prepare(pg)
    e = pg.query_selector("input[placeholder='Project Number']")
    e.fill(project_number)
    pg.wait_for_timeout(1200)
    for b in pg.query_selector_all("button"):
        if b.inner_text().strip() == "Search" and b.is_visible():
            b.click()
            break
    pg.wait_for_timeout(15000)
    print("results page:", pg.url)
    # click the project number link / row
    clicked = False
    for sel in ("a", "td", "span"):
        for x in pg.query_selector_all(sel):
            try:
                t = (x.inner_text() or "").strip()
                if t == project_number and x.is_visible():
                    x.click()
                    clicked = True
                    break
            except Exception:
                pass
        if clicked:
            break
    print("row clicked:", clicked)
    pg.wait_for_timeout(16000)
    out = ROOT / "03_PERMITS_AND_INSPECTIONS" / slug
    out.mkdir(parents=True, exist_ok=True)
    f = out / f"{project_number}_record_page.html"
    f.write_text(pg.content(), encoding="utf-8")
    pg.screenshot(path=str(out / f"{project_number}_record.png"), full_page=True)
    print("RECORD URL:", pg.url)
    print("saved:", f, f.stat().st_size)
    print("sha256:", hashlib.sha256(f.read_bytes()).hexdigest())
    print("---- RECORD TEXT ----")
    print(pg.inner_text("body")[:6000])
    print("---- TABS / BUTTONS ----")
    for i in pg.query_selector_all("button,a,li[role=tab],.p-tab"):
        try:
            if not i.is_visible():
                continue
        except Exception:
            continue
        t = (i.inner_text() or "").strip()
        if t and len(t) < 60:
            print("   ", t)
    (out / f"{project_number}_api_calls.json").write_text(json.dumps(api, indent=1))
    print("api calls:", len(api))
    return api


if __name__ == "__main__":
    pn, slug = sys.argv[1], sys.argv[2]
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = b.new_context(storage_state=AUTH, viewport={"width": 1700, "height": 1400})
        pg = ctx.new_page()
        pg.set_default_timeout(80000)
        open_project(pg, pn, slug)
        ctx.storage_state(path=AUTH)
        ctx.close()
        b.close()