#!/usr/bin/env python3
"""AcclaimWeb (Santa Rosa County Clerk) public records search driver.

Flow: accept disclaimer -> (optionally Guest sign-in) -> open search type ->
fill -> submit -> capture results table.  Guest/public access only.
"""
import re
import sys
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

BASE = "https://acclaim.srccol.com/AcclaimWeb/"


def _click_text(pg, texts, exact=True):
    for t in texts:
        for e in pg.query_selector_all(
                "a,button,input[type=submit],span,div,li"):
            try:
                if not e.is_visible():
                    continue
                txt = ((e.inner_text() or "") + " " +
                       (e.get_attribute("value") or "")).strip()
            except Exception:
                continue
            hit = (txt == t) if exact else (t.lower() in txt.lower())
            if hit:
                try:
                    e.click()
                    return True
                except Exception:
                    pass
    return False


def boot(pw, state="acclaim_state.json"):
    b = pw.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = b.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        viewport={"width": 1600, "height": 1200})
    pg = ctx.new_page()
    pg.set_default_timeout(60000)
    return b, ctx, pg


def accept_disclaimer(pg):
    """Accept the Acclaim disclaimer if the site presents it."""
    for _ in range(4):
        if "Disclaimer" not in pg.url:
            return True
        if pg.query_selector("#btnButton"):
            pg.click("#btnButton")
        elif not _click_text(pg, ["I accept the conditions above."]):
            return False
        pg.wait_for_timeout(4500)
    return "Disclaimer" not in pg.url


def open_search(pg, path):
    pg.goto(urljoin(BASE, path), wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(3500)
    if "Disclaimer" in pg.url:
        accept_disclaimer(pg)
    return pg.url


def controls(pg):
    out = []
    for i in pg.query_selector_all("input,select,button,textarea"):
        try:
            if not i.is_visible():
                continue
        except Exception:
            continue
        out.append({
            "tag": i.evaluate("e=>e.tagName"), "id": i.get_attribute("id"),
            "name": i.get_attribute("name"), "type": i.get_attribute("type"),
            "value": (i.get_attribute("value") or "")[:60],
            "text": (i.inner_text() or "").strip()[:60]})
    return out


def set_val(pg, sel, val):
    """Set a text input by id or name, handling hidden/visible duplicates."""
    for q in (f"#{sel}", f"[name='{sel}']"):
        for e in pg.query_selector_all(q):
            try:
                e.fill(str(val))
                return True
            except Exception:
                continue
    return False


def submit(pg, label="Search"):
    for q in ("#btnSearch", "input[type=submit]", "button"):
        for e in pg.query_selector_all(q):
            try:
                v = ((e.get_attribute("value") or "") + " " +
                     (e.inner_text() or "")).strip().lower()
                if label.lower() in v:
                    e.click()
                    return True
            except Exception:
                pass
    pg.keyboard.press("Enter")
    return True


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "search/SearchTypeBookPage"
    with sync_playwright() as pw:
        b, ctx, pg = boot(pw)
        print("URL:", open_search(pg, path))
        pg.screenshot(path="acclaim_form.png", full_page=True)
        print("---- TEXT ----")
        print(pg.inner_text("body")[:2000])
        print("---- CONTROLS ----")
        for c in controls(pg):
            print("  ", c)
        ctx.close()
        b.close()