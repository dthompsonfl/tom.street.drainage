#!/usr/bin/env python3
"""Acquire Santa Rosa County Property Appraiser evidence for the Tom Street

parcels and write machine-verifiable source files.

Public endpoints, discovered from the live site on 2026-10-15:
  POST https://search.srcpa.gov/property/query        -> JSON result set
  POST https://search.srcpa.gov/property/export/selected -> JSON/CSV record export
  POST https://search.srcpa.gov/property/print/selected -> PDF mailing label
"""

import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:  # noqa: E402
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT  # noqa: E402
import csv
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = _ROOT
BASE = "https://search.srcpa.gov"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

TARGETS = {
    "2264_Tom_St": ("2264 TOM ST", "21-2S-26-0780-0QQ00-1020"),
    "2268_Tom_St": ("2268 TOM ST", "21-2S-26-0780-0QQ00-1490"),
    "2265_Tom_St": ("2265 TOM ST", "21-2S-26-0780-0QQ00-1180"),
}

def session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA,
                      "Accept": "text/html,application/xhtml+xml,*/*",
                      "Accept-Language": "en-US,en;q=0.9"})
    s.get(BASE + "/", timeout=45)
    return s

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    data = content if isinstance(content, bytes) else content.encode()
    p.write_bytes(data)
    return {"relative_path": path, "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "retrieved_utc": datetime.now(timezone.utc).isoformat()}

def search_street(s, street="TOM", city="NAVARRE"):
    r = s.post(BASE + "/property/query", timeout=90,
               headers={"Referer": BASE + "/", "Origin": BASE},
               data={"quickSearchParam": "", "useQuickSearch": "false",
                     "parameterMatch": "intersect", "name": "",
                     "street": street, "unit": "", "city": city, "zip": "",
                     "useRange": "false", "parcelId": "", "phase": "",
                     "parcelGroup": "", "xfCode": "", "landUse": "",
                     "zoning": "", "acreageFrom": "", "acreageTo": "",
                     "buildingUse": "", "structuralElement": "",
                     "yearBuiltFrom": "", "yearBuiltTo": "",
                     "heatedSquareFootageFrom": "", "heatedSquareFootageTo": "",
                     "action": "Search"})
    r.raise_for_status()
    return r.json()

def export(s, parcel_key):
    r = s.post(BASE + "/property/export/selected", timeout=90,
               headers={"Referer": BASE + "/", "Origin": BASE},
               data=[("parcel", str(parcel_key)), ("format", "json")])
    r.raise_for_status()
    return r.content

def search_parcel(s, pid):
    r = s.post(BASE + "/property/query", timeout=90,
               headers={"Referer": BASE + "/", "Origin": BASE},
               data={"quickSearchParam": "", "useQuickSearch": "false",
                     "parameterMatch": "intersect", "name": "", "street": "",
                     "unit": "", "city": "", "zip": "", "useRange": "false",
                     "parcelId": pid, "phase": "", "parcelGroup": "",
                     "xfCode": "", "landUse": "", "zoning": "",
                     "acreageFrom": "", "acreageTo": "", "buildingUse": "",
                     "structuralElement": "", "yearBuiltFrom": "",
                     "yearBuiltTo": "", "heatedSquareFootageFrom": "",
                     "heatedSquareFootageTo": "", "action": "Search"})
    r.raise_for_status()
    return r.json()

def main():
    manifest = []
    s = session()

    # 1. Full Tom Street (Navarre) result set
    data = search_street(s)
    m = write("02_PROPERTY_AND_PARCELS/RAW_HTTP/srcpa_property_query_street_TOM_NAVARRE.json",
              json.dumps(data, indent=1))
    m["source_url"] = BASE + "/property/query"
    m["query"] = "street=TOM city=NAVARRE"
    m["result_count"] = len(data.get("results", []))
    manifest.append(m)
    print("Tom St result set:", m["result_count"], "records")

    # 2. Per-parcel searches and record exports
    for slug, (addr, pid) in TARGETS.items():
        j = search_parcel(s, pid)
        m = write(f"02_PROPERTY_AND_PARCELS/{slug}/srcpa_property_query_parcel_{pid}.json",
                  json.dumps(j, indent=1))
        m["source_url"] = BASE + "/property/query"
        m["query"] = f"parcelId={pid}"
        manifest.append(m)
        key = j["results"][0]["parcelKey"]
        blob = export(s, key)
        m = write(f"02_PROPERTY_AND_PARCELS/{slug}/srcpa_property_record_{pid}.json",
                  json.dumps(json.loads(blob), indent=1))
        m["source_url"] = BASE + "/property/export/selected"
        m["query"] = f"parcel={key} format=json"
        manifest.append(m)
        print(f"{addr}: parcel={pid} key={key} export_bytes={m['bytes']}")
        time.sleep(1.5)

    out = ROOT / "00_CONTROL/SYSTEM_RAW/srcpa_acquisition_manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=1))
    print("wrote", out)

if __name__ == "__main__":
    main()