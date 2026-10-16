#!/usr/bin/env python3
"""Interactive MGO Connect sign-in helper.

Run this on YOUR machine. A browser window opens; you sign in to MGO Connect
yourself (Santa Rosa County jurisdiction), then come back here and press Enter.
The browser's session state is written to /tmp/opencode/mgo_auth.json.

Your password is never read, logged, or stored by this script - only the
resulting session cookie file is written, and it lives in /tmp, outside the
evidence repository.

    python3 00_CONTROL/tools/mgo_login_helper.py
"""
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("Install first:  pip install playwright && python -m playwright install chromium")

AUTH = "/tmp/opencode/mgo_auth.json"
LOGIN = "https://www.mgoconnect.org/cp/login"
SEARCH = "https://www.mgoconnect.org/cp/search?jid=276&pid=3"

print(__doc__)
with sync_playwright() as p:
    b = p.chromium.launch(headless=False, args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1400, "height": 950})
    pg = ctx.new_page()
    pg.goto(LOGIN, wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(9000)
    print("\n>>> A browser window is open at", LOGIN)
    print(">>> Sign in with your MGO Connect account, set the jurisdiction to")
    print(">>> Santa Rosa County, then LEAVE THE BROWSER WINDOW OPEN.\n")
    input("Press Enter here once you are signed in and can see the MGO home page... ")
    pg.wait_for_timeout(3000)
    print("Current page:", pg.url)
    if "/cp/login" in pg.url:
        print("WARNING: still on the login page - session may not have been saved.")
    pg.goto(SEARCH, wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(14000)
    print("Search page landed at:", pg.url)
    if "/cp/login" in pg.url:
        print("STILL BLOCKED: MGO redirected back to login. Session not accepted.")
    else:
        print("SUCCESS: authenticated MGO search page is reachable.")
    ctx.storage_state(path=AUTH)
    print("Session written to", AUTH)
    input("Press Enter to close the browser window...")
    ctx.close()
    b.close()