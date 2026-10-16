#!/usr/bin/env python3
"""Open an MGO Connect permit record via Search -> Row actions -> View Project,
then capture every tab, field and document list the county exposes.

Usage: python3 mgo_open.py BP-2026-1621 2264_Tom_St "2264 TOM ST"
"""
import hashlib
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

AUTH = "/tmp/opencode/mgo_auth.json"
ROOT = Path("/home/dylan/Tom-Street-Drainage-Investigation")


def auth_page(p, url):
    b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = b.new_context(storage_state=AUTH, viewport={"width": 1700, "height": 1400})
    pg = ctx.new_page()
    pg.set_default_timeout(80000)
    pg.goto(url, wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(9000)
    return b, ctx, pg


def search_and_open(pg, address, project_number):
    pg.goto("https://www.mgoconnect.org/cp/search?jid=276&pid=3",
            wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(9000)
    pg.fill("input[placeholder='Address Search Autocomplete']", address)
    pg.wait_for_timeout(1800)
    for b in pg.query_selector_all("button"):
        if b.inner_text().strip() == "Search" and b.is_visible():
            b.click()
            break
    pg.wait_for_timeout(15000)
    for r in pg.query_selector_all("table tbody tr"):
        if project_number in (r.inner_text() or ""):
            r.query_selector("span[aria-label='Row actions']").click()
            pg.wait_for_timeout(4000)
            for item in pg.query_selector_all(".grid-action-item"):
                if "view project" in (item.inner_text() or "").lower():
                    item.click()
                    break
            break
    pg.wait_for_timeout(18000)
    return pg.url


if __name__ == "__main__":
    pn, slug, addr = sys.argv[1], sys.argv[2], sys.argv[3]
    api = []
    with sync_playwright() as p:
        b, ctx, pg = auth_page(p, "https://www.mgoconnect.org/cp/home")
        pg.on("request", lambda r: api.append(
            {"m": r.method, "u": r.url.replace("api.mgoconnect.org", "")[:300],
             "p": (r.post_data or "")[:600]})
            if "api.mgoconnect.org" in r.url and "signalr" not in r.url
            and "software-version" not in r.url else None)
        url = search_and_open(pg, addr, pn)
        print("PROJECT URL:", url)
        out = ROOT / "03_PERMITS_AND_INSPECTIONS" / slug
        out.mkdir(parents=True, exist_ok=True)
        f = out / f"{pn}_project.html"
        f.write_text(pg.content(), encoding="utf-8")
        pg.screenshot(path=str(out / f"{pn}_project.png"), full_page=True)
        print("saved:", f, f.stat().st_size,
              hashlib.sha256(f.read_bytes()).hexdigest()[:24])
        txt = pg.inner_text("body")
        (out / f"{pn}_project_text.txt").write_text(txt)
        print("---- PROJECT TEXT ----")
        print(txt[:7000])
        print("---- TABS/BUTTONS ----")
        seen = set()
        for i in pg.query_selector_all("button,a,li[role=tab],.p-tab,.nav-link,span"):
            try:
                if not i.is_visible():
                    continue
            except Exception:
                continue
            t = (i.inner_text() or "").strip()
            if t and len(t) < 45 and t not in seen:
                seen.add(t)
                print("   ", t)
        (out / f"{pn}_api.json").write_text(json.dumps(api, indent=1))
        print("---- API ----")
        for a in dict.fromkeys(tuple(x.items()) for x in api):
            print("  ", a["m"], a["u"])
        ctx.storage_state(path=AUTH)
        ctx.close()
        b.close()