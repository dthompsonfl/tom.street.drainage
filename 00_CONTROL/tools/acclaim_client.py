#!/usr/bin/env python3
"""Santa Rosa County Clerk (AcclaimWeb) client.

Public/Guest access only. Accepts the site disclaimer and signs in as Guest.
Captures console errors and page structure so the search form can be mapped.
"""
import sys

from playwright.sync_api import sync_playwright

BASE = "https://acclaim.srccol.com"


def start(pw):
    b = pw.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = b.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        viewport={"width": 1600, "height": 1100})
    pg = ctx.new_page()
    pg.set_default_timeout(45000)
    pg.goto(BASE + "/AcclaimWeb/", wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(4000)
    return b, ctx, pg


def accept_and_guest(pg):
    """Accept disclaimer then sign in as Guest. Returns True on success."""
    # Disclaimer checkbox + accept
    for sel in ["#chkDisclaimer", "input[type=checkbox]"]:
        for e in pg.query_selector_all(sel):
            try:
                if e.is_visible() and not e.is_checked():
                    e.check()
                    break
            except Exception:
                pass
    for txt in ["Accept Disclaimer", "Accept", "I Agree"]:
        for e in pg.query_selector_all("a,button,input[type=submit],span,div"):
            try:
                t = (e.inner_text() or e.get_attribute("value") or "").strip()
            except Exception:
                continue
            if t == txt and e.is_visible():
                e.click()
                pg.wait_for_timeout(4000)
                return True
    return False


def login_guest(pg):
    for sel in ["#lnkGuest", "a:has-text('Guest')", "text=Guest"]:
        for e in pg.query_selector_all(sel):
            try:
                if e.is_visible():
                    e.click()
                    pg.wait_for_timeout(6000)
                    return True
            except Exception:
                pass
    return False


if __name__ == "__main__":
    with sync_playwright() as pw:
        b, ctx, pg = start(pw)
        print("URL:", pg.url)
        print("accept:", accept_and_guest(pg))
        print("URL:", pg.url)
        print("guest:", login_guest(pg))
        print("URL:", pg.url)
        pg.wait_for_timeout(4000)
        pg.screenshot(path="acclaim_state.png", full_page=True)
        ctx.storage_state(path="acclaim_state.json")
        print("---- TEXT ----")
        print(pg.inner_text("body")[:3000])
        print("---- FORM CONTROLS ----")
        for i in pg.query_selector_all("input,select,button,a"):
            try:
                vis = i.is_visible()
            except Exception:
                vis = False
            if not vis:
                continue
            print(f"  <{i.evaluate('e=>e.tagName')}> id={i.get_attribute('id')!r} "
                  f"name={i.get_attribute('name')!r} type={i.get_attribute('type')!r} "
                  f"val={(i.get_attribute('value') or '')[:40]!r} "
                  f"txt={(i.inner_text() or '').strip()[:45]!r}")
        ctx.close()
        b.close()