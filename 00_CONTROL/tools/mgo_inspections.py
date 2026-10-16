#!/usr/bin/env python3
"""Render the MGO inspection history for a permit into a readable evidence
document and attempt to download the county's own inspection report."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

AUTH = "/tmp/opencode/mgo_auth.json"
API = "https://api.mgoconnect.org"
ROOT = Path("/home/dylan/Tom-Street-Drainage-Investigation")


def render(pn, slug, ins, types, proj):
    out = ROOT / "03_PERMITS_AND_INSPECTIONS" / slug
    d = proj.get("data") or {}
    L = []
    L.append(f"# Inspection History — {pn}")
    L.append("")
    L.append(f"**Address:** {d.get('projectAddress')} {d.get('projectCity')}, "
             f"{d.get('projectState')} {d.get('projectZip')}")
    L.append(f"**Work type:** {d.get('workType')}")
    L.append(f"**Status:** {d.get('projectStatus')}")
    L.append(f"**Parcel (MGO):** {d.get('parcelNumber')}")
    L.append(f"**Created:** {d.get('dateCreated')}   **Updated:** {d.get('dateUpdated')}")
    L.append(f"**Project UID:** {d.get('projectUID')}")
    L.append("")
    L.append(f"**Source:** Santa Rosa County Development Services — MGO Connect "
             f"(`mgoconnect.org/cp/project-details/{d.get('projectUID')}`), "
             f"endpoint `/api/v3/cp/work-orders/{d.get('projectID')}/inspections`")
    L.append(f"**Retrieved (UTC):** {datetime.now(timezone.utc).isoformat()}")
    L.append("")
    L.append(f"## {len(ins)} recorded inspections")
    L.append("")
    L.append("| # | Date | Status | Inspection type | Inspector | Comments |")
    L.append("|---|---|---|---|---|---|")
    for i, x in enumerate(sorted(ins, key=lambda r: r["inspectionDateTime"]), 1):
        c = (x.get("comments") or "").replace("|", "/").replace("\n", " ")
        L.append(f"| {i} | {x['inspectionDateTime'][:16].replace('T',' ')} | "
                 f"**{x.get('inspectionStatus')}** | {x.get('inspectionType')} | "
                 f"{x.get('inspectorFullName','')} | {c} |")
    L.append("")
    fee_names = sorted({t.get("typeName") or t.get("name")
                        for t in (types or [])
                        if t.get("typeName") or t.get("name")})
    L.append("## Fee lines present on this permit")
    L.append("")
    L.append("These confirm which disciplines the county actually reviewed and")
    L.append("charged for this project.")
    L.append("")
    for n in fee_names:
        L.append(f"- {n}")
    f = out / f"{pn}_INSPECTION_HISTORY.md"
    f.write_text("\n".join(L), encoding="utf-8")
    return f


def try_reports(pn, slug, ins, pid):
    """Attempt the county's SSRS inspection report endpoints."""
    out = ROOT / "03_PERMITS_AND_INSPECTIONS" / slug
    got = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = b.new_context(storage_state=AUTH)
        pg = ctx.new_page()
        pg.goto("https://www.mgoconnect.org/cp/home",
                wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(8000)
        tok = {}
        pg.on("request", lambda r: tok.setdefault("t", r.headers.get("x-csrf-token"))
              if "api.mgoconnect.org" in r.url and r.headers.get("x-csrf-token") else None)
        pg.goto("https://www.mgoconnect.org/cp/search?jid=276&pid=3",
                wait_until="domcontentloaded", timeout=90000)
        pg.wait_for_timeout(9000)
        hdr = {"Accept": "application/json, */*",
               "Referer": "https://www.mgoconnect.org/",
               "SourcePlatform": "MGO Connect Web"}
        if tok.get("t"):
            hdr["x-csrf-token"] = tok["t"]
        first = ins[0]
        iid = first.get("inspectionID")
        cands = [
            f"/api/v3/cp/inspections/{iid}/report",
            f"/api/v3/cp/work-orders/{pid}/inspections/{iid}/report",
            f"/api/v3/cp/inspections/report/{iid}",
        ]
        for c in cands:
            try:
                r = ctx.request.get(API + c, headers=hdr)
                body = r.body()
                ct = r.headers.get("content-type", "")
                print(f"  {c} -> {r.status} {ct} {len(body)}b")
                if r.status == 200 and ("pdf" in ct or body[:4] == b"%PDF"):
                    fn = out / f"{pn}_inspection_{iid}.pdf"
                    fn.write_bytes(body)
                    got.append({"file": str(fn.relative_to(ROOT)), "bytes": len(body),
                                "sha256": hashlib.sha256(body).hexdigest()})
                    print("    SAVED", fn)
            except Exception as e:
                print(f"  {c} -> ERROR {e}")
        ctx.close()
        b.close()
    return got


if __name__ == "__main__":
    pn, slug = sys.argv[1], sys.argv[2]
    base = ROOT / "03_PERMITS_AND_INSPECTIONS" / slug
    ins = json.load(open(base / f"{pn}_inspections.json"))["data"]
    types = json.load(open(base / f"{pn}_types.json"))["data"]
    proj = json.load(open(base / f"{pn}_project_by_uid.json"))
    f = render(pn, slug, ins, types, proj)
    print("wrote", f, f.stat().st_size, "bytes")
    print("---- attempting inspection report downloads ----")
    got = try_reports(pn, slug, ins, (proj.get("data") or {}).get("projectID"))
    print("downloaded:", got)