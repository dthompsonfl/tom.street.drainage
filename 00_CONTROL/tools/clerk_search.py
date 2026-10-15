#!/usr/bin/env python3
"""Run and persist Santa Rosa County Clerk (AcclaimWeb) public searches.

Usage examples:
  python3 clerk_search.py name "HOLIDAY BUILDERS"
  python3 clerk_search.py bookpage 3492 700
  python3 clerk_search.py legal "POPE SUBD"
Results are printed as TSV and the full result HTML is saved for evidence.
"""
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, "/home/dylan/Tom-Street-Drainage-Investigation/00_CONTROL/tools")
from acclaim_search import boot, open_search, set_val, submit  # noqa: E402

OUT = Path("/home/dylan/Tom-Street-Drainage-Investigation/00_CONTROL/SYSTEM_RAW")


def collect_rows(pg):
    rows = []
    for t in pg.query_selector_all("table tr"):
        cells = [(c.inner_text() or "").strip() for c in t.query_selector_all("th,td")]
        cells = [re.sub(r"\s+", " ", c) for c in cells]
        if len(cells) >= 8 and cells[0].isdigit():
            rows.append(cells)
    return rows


def save(name, pg):
    OUT.mkdir(parents=True, exist_ok=True)
    html = pg.content()
    p = OUT / f"acclaim_{name}_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.html"
    p.write_text(html, encoding="utf-8")
    return {"path": str(p.relative_to(Path("/home/dylan/Tom-Street-Drainage-Investigation"))),
            "bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "url": pg.url, "retrieved_utc": datetime.now(timezone.utc).isoformat()}


def summarise(pg):
    t = pg.inner_text("body")
    m = re.search(r"Displaying items\s+([\d-]+)\s+of\s+([\d,]+)", t)
    return {"displaying": m.group(0) if m else None,
            "total": m.group(2) if m else None,
            "released_through": (re.search(r"Released through date:\s*([\d/]+)", t) or [None, None])[1]}


def run(kind, fields, tag):
    path = {"bookpage": "search/SearchTypeBookPage",
            "name": "search/SearchTypeName",
            "legal": "search/SearchTypeLegalSearch",
            "doc": "search/SearchTypeDocType",
            "instr": "search/SearchTypeInstrumentNumber",
            "simple": "search/SearchTypeSimpleSearch"}[kind]
    with sync_playwright() as pw:
        b, ctx, pg = boot(pw)
        open_search(pg, path)
        for k, v in fields.items():
            if k in ("Both", "Direct", "Reverse"):
                try:
                    pg.click(f"#{k}")
                    continue
                except Exception:
                    pass
            set_val(pg, k, v)
        pg.wait_for_timeout(600)
        submit(pg)
        pg.wait_for_timeout(9000)
        # page through all result pages
        allrows, seen = [], set()
        for page in range(1, 12):
            for r in collect_rows(pg):
                key = tuple(r)
                if key not in seen:
                    seen.add(key)
                    allrows.append(r)
            nxt = None
            for a in pg.query_selector_all("a,span,li,input"):
                try:
                    t = ((a.inner_text() or "") + (a.get_attribute("value") or "")).strip().lower()
                except Exception:
                    continue
                if t == "next" and a.is_visible():
                    nxt = a
                    break
            if not nxt or page > 10:
                break
            nxt.click()
            pg.wait_for_timeout(5000)
        meta = save(tag, pg)
        meta.update(summarise(pg))
        meta["query"] = fields
        meta["rows"] = allrows
        ctx.storage_state(path="acclaim_state.json")
        ctx.close()
        b.close()
    return meta


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "name":
        nm = sys.argv[2]
        tag = re.sub(r"[^A-Za-z0-9]+", "_", nm)
        res = run("name", {"SearchOnName": nm, "Both": "Both"}, f"name_{tag}")
    elif cmd == "bookpage":
        res = run("bookpage", {"BookNumber": sys.argv[2],
                               "PageNumber": sys.argv[3]},
                  f"bookpage_{sys.argv[2]}_{sys.argv[3]}")
    elif cmd == "legal":
        res = run("legal", {"SearchOnName": sys.argv[2]},
                  f"legal_{re.sub(r'[^A-Za-z0-9]+','_',sys.argv[2])}")
    else:
        raise SystemExit("usage: name|bookpage|legal ...")
    print("META:", json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))
    print(f"ROWS: {len(res['rows'])}")
    hdr = ["row", "consideration", "direct", "indirect", "record_date",
           "book_type", "book_page", "instrument", "doc_type", "doc_link",
           "case", "legal"]
    w = csv.writer(sys.stdout)
    w.writerow(hdr)
    for r in res["rows"]:
        w.writerow(r[:12])
    (OUT / f"acclaim_{res['path'].split('/')[-1][:-5]}.json").write_text(
        json.dumps(res, indent=1))