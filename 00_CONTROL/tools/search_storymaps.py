#!/usr/bin/env python3
"""Search the Santa Rosa County 'Approved Land Development Projects' StoryMaps

for the development that contains the Tom Street lots (Crescent Shores /
Hadleigh Hills).  Public ArcGIS item data, no login."""

import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:  # noqa: E402
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT  # noqa: E402
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = _ROOT
OUT = ROOT / "04_ENGINEERING_AND_DRAINAGE/Tom_Street_Shared_System"

STORYMAPS = {
    "2026": "63da6c68c2da44b7b0068d91424e2bf1",
    "2025": "3ce6a90e76744e35958b7e0f4852a9e9",
    "2024": "7aa471170df24578bbc244044c116205",
    "2023": "f792cb0954504f0da672fbdd0848c9a5",
    "2022": "7cacf164fbf94245ab6d383122fbef96",
    "2021": "76b720554c0f4f9fbedc0e3a92b01cb8",
    "2020": "258fb6aa23ad4995a0fccb8c66c9a656",
}

TERMS = ["Crescent Shores", "Hadleigh Hills", "Hadleigh", "Crescent",
         "Tom St", "Tom Street", "Pope Sub", "Navarre"]

S = requests.Session()
S.headers.update({"User-Agent": "Tom-Street-Drainage-Investigation/1.0"})

def plain_text(item):
    try:
        d = S.get(f"https://www.arcgis.com/sharing/rest/content/items/{item}/data",
                  params={"f": "json"}, timeout=90).json()
    except Exception as e:
        return None, str(e)
    txt = json.dumps(d)
    txt = html.unescape(txt).replace("\\n", " ").replace('\\"', '"')
    txt = re.sub(r"<[^>]+>", " ", txt)
    return re.sub(r"\s+", " ", txt), None

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    report = {"retrieved_utc": datetime.now(timezone.utc).isoformat(),
              "source": "Santa Rosa County Approved Land Development Projects "
                        "(ArcGIS StoryMaps)", "years": {}}
    for year, item in STORYMAPS.items():
        t, err = plain_text(item)
        if err:
            report["years"][year] = {"item": item, "error": err}
            print(year, "ERROR", err)
            continue
        hits = {}
        for term in TERMS:
            idxs = [m.start() for m in re.finditer(re.escape(term), t, re.I)]
            if idxs:
                hits[term] = [t[max(0, i - 220): i + 320] for i in idxs[:4]]
        report["years"][year] = {"item": item, "chars": len(t), "hits": hits}
        print(f"{year}: {len(t)} chars, terms hit: {list(hits.keys()) or 'NONE'}")
        for term in ("Crescent Shores", "Hadleigh Hills"):
            for h in hits.get(term, []):
                print("    >>", h[:300])
    fp = OUT / "approved_subdivision_storymaps_search.json"
    fp.write_text(json.dumps(report, indent=1))
    print("saved", fp)