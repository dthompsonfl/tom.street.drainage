#!/usr/bin/env python3
"""MGO Connect (Santa Rosa County, JID=276) permit search and document download.

MGO requires an authenticated account for permit search. This tool never stores
or logs credentials. It consumes a Playwright storage-state file that the user
produces by signing in through the normal MGO login form.

Expected storage state path (kept OUTSIDE the evidence repository):
    /tmp/opencode/mgo_auth.json

Usage:
    python3 mgo_client.py probe
    python3 mgo_client.py search "2264 Tom St"
    python3 mgo_client.py search "21-2S-26-0780-0QQ00-1020"
"""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path("/home/dylan/Tom-Street-Drainage-Investigation")
OUT = ROOT / "03_PERMITS_AND_INSPECTIONS/SYSTEM_RAW"
AUTH = "/tmp/opencode/mgo_auth.json"
SEARCH_URL = "https://www.mgoconnect.org/cp/search?jid=276&pid=3"


def launch(state=AUTH):
    p = sync_playwright().start()
    kw = {"user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
          "viewport": {"width": 1700, "height": 1200}}
    ctxargs = {"storage_state": state} if Path(state).exists() else {}
    b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = b.new_context(**ctxargs, **kw)
    pg = ctx.new_page()
    pg.set_default_timeout(75000)
    return p, b, ctx, pg


def save_html(pg, tag):
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    p = OUT / f"mgo_{tag}_{stamp}.html"
    p.write_text(pg.content(), encoding="utf-8")
    return {"relative_path": str(p.relative_to(ROOT)),
            "bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "url": pg.url,
            "retrieved_utc": datetime.now(timezone.utc).isoformat()}


def probe():
    p, b, ctx, pg = launch()
    pg.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(16000)
    print("LANDED:", pg.url)
    if "/cp/login" in pg.url:
        print("RESULT: NOT AUTHENTICATED - MGO still requires a login.")
        print("Sign in at https://www.mgoconnect.org/cp/login and save the")
        print("storage state to", AUTH)
        ctx.close()
        b.close()
        p.stop()
        return
    info = save_html(pg, "probe")
    print("SEARCH PAGE OK:", info)
    print("---- TEXT ----")
    print(pg.inner_text("body")[:4000])
    print("---- CONTROLS ----")
    for i in pg.query_selector_all("input,select,button,textarea"):
        try:
            if not i.is_visible():
                continue
        except Exception:
            continue
        print(f"  <{i.evaluate('e=>e.tagName')}> id={i.get_attribute('id')!r} "
              f"name={i.get_attribute('name')!r} type={i.get_attribute('type')!r} "
              f"ph={i.get_attribute('placeholder')!r} "
              f"txt={(i.inner_text() or '').strip()[:40]!r}")
    ctx.storage_state(path=AUTH)
    ctx.close()
    b.close()
    p.stop()


def search(term):
    p, b, ctx, pg = launch()
    pg.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(16000)
    if "/cp/login" in pg.url:
        print("NOT AUTHENTICATED")
        ctx.close()
        b.close()
        p.stop()
        return
    filled = False
    for sel in ["#SearchOnName", "#searchTerm", "#searchText",
                "input[placeholder*='earch']", "input[type=text]"]:
        for e in pg.query_selector_all(sel):
            try:
                if e.is_visible():
                    e.fill(term)
                    filled = True
                    break
            except Exception:
                pass
        if filled:
            break
    print("search field filled:", filled)
    if filled:
        for bsel in ["#btnSearch", "button:has-text('Search')",
                     "input[type=submit]"]:
            for e in pg.query_selector_all(bsel):
                try:
                    if e.is_visible():
                        e.click()
                        break
                except Exception:
                    pass
        pg.wait_for_timeout(15000)
    tag = re.sub(r"[^A-Za-z0-9]+", "_", term)
    info = save_html(pg, f"search_{tag}")
    print("SAVED:", info)
    print("---- RESULTS TEXT ----")
    print(pg.inner_text("body")[:5000])
    ctx.storage_state(path=AUTH)
    ctx.close()
    b.close()
    p.stop()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "probe"
    if cmd == "probe":
        probe()
    elif cmd == "search":
        search(sys.argv[2])
    else:
        raise SystemExit(__doc__)