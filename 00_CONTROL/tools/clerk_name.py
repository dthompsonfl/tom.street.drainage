#!/usr/bin/env python3
"""Santa Rosa County Clerk (AcclaimWeb) name search with date narrowing.

Public Guest access only.
"""

import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:  # noqa: E402
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT  # noqa: E402
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

from acclaim_search import boot, open_search, set_val  # noqa: E402

ROOT = _ROOT
OUT = ROOT / "00_CONTROL/SYSTEM_RAW"

def rows_of(pg):
    out = []
    for tr in pg.query_selector_all("table tr"):
        c = [re.sub(r"\s+", " ", (x.inner_text() or "").strip())
             for x in tr.query_selector_all("th,td")]
        if len(c) >= 8 and c[0].isdigit():
            out.append(c)
    return out

def search(name, dfrom="1/1/2014", dto="10/15/2026", radio="Both",
           doctype="", tag=None):
    tag = tag or re.sub(r"[^A-Za-z0-9]+", "_", f"{name}_{dfrom}_{dto}")
    with sync_playwright() as pw:
        b, ctx, pg = boot(pw)
        open_search(pg, "search/SearchTypeName")
        if radio:
            try:
                pg.click(f"#{radio}", force=True)
            except Exception:
                pass
        pg.fill("#SearchOnName", name)
        pg.fill("#RecordDateFrom", dfrom)
        pg.fill("#RecordDateTo", dto)
        if doctype:
            set_val(pg, "DocTypesDisplay-input", doctype)
        pg.wait_for_timeout(600)
        pg.click("#btnSearch")
        pg.wait_for_timeout(11000)
        t = pg.inner_text("body")
        alert = re.search(r"(The number of results exceeded.*?|No records.*?)",
                          t, re.I)
        allrows, seen = [], set()
        for _ in range(12):
            for r in rows_of(pg):
                if tuple(r) not in seen:
                    seen.add(tuple(r))
                    allrows.append(r)
            nxt = None
            for a in pg.query_selector_all("a,span,li,input"):
                try:
                    lab = ((a.inner_text() or "") +
                           (a.get_attribute("value") or "")).strip().lower()
                except Exception:
                    continue
                if lab == "next" and a.is_visible():
                    nxt = a
                    break
            if not nxt:
                break
            nxt.click()
            pg.wait_for_timeout(5000)
        m = re.search(r"Displaying items\s+[\d-]+\s+of\s+([\d,]+)", t)
        OUT.mkdir(parents=True, exist_ok=True)
        fp = OUT / f"acclaim_name_{tag}.html"
        fp.write_text(pg.content(), encoding="utf-8")
        meta = {"query_name": name, "from": dfrom, "to": dto, "radio": radio,
                "total_reported": m.group(1) if m else None,
                "alert": alert.group(1) if alert else None,
                "rows": allrows, "url": pg.url,
                "retrieved_utc": datetime.now(timezone.utc).isoformat()}
        ctx.close()
        b.close()
    (OUT / f"acclaim_name_{tag}.json").write_text(json.dumps(meta, indent=1))
    return meta

if __name__ == "__main__":
    nm = sys.argv[1]
    d1 = sys.argv[2] if len(sys.argv) > 2 else "1/1/2014"
    d2 = sys.argv[3] if len(sys.argv) > 3 else "10/15/2026"
    r = search(nm, d1, d2)
    print("QUERY:", r["query_name"], r["from"], "->", r["to"],
          "| total:", r["total_reported"], "| alert:", r["alert"])
    print("ROWS:", len(r["rows"]))
    w = csv.writer(sys.stdout)
    w.writerow(["row", "consideration", "direct", "indirect", "record_date",
                "book_type", "book_page", "instrument", "doc_type",
                "doc_link", "case", "legal"])
    for x in r["rows"]:
        w.writerow(x[:12])