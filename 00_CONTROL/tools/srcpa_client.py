#!/usr/bin/env python3
"""SRC Property Appraiser (search.srcpa.gov) acquisition client.

Public search form: POST https://search.srcpa.gov/property/query
Field names derived from the live HTML form on 2026-10-15.
No credentials used. Public/guest access only.
"""
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE = "https://search.srcpa.gov"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

FIELDS = ["quickSearchParam", "useQuickSearch", "parameterMatch", "name",
          "street", "unit", "city", "zip", "useRange", "parcelId", "phase",
          "parcelGroup", "xfCode", "landUse", "zoning", "acreageFrom",
          "acreageTo", "buildingUse", "structuralElement", "yearBuiltFrom",
          "yearBuiltTo", "heatedSquareFootageFrom", "heatedSquareFootageTo",
          "action"]


def blank_form():
    d = {f: "" for f in FIELDS}
    d.update({"quickSearchParam": "", "useQuickSearch": "false",
              "parameterMatch": "intersect", "useRange": "false",
              "action": "Search"})
    return d


def save(resp, path):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(resp.content)
    return {
        "path": str(p),
        "bytes": len(resp.content),
        "sha256": hashlib.sha256(resp.content).hexdigest(),
        "http_status": resp.status_code,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "final_url": resp.url,
    }


def query(street=None, city=None, zipcode=None, parcel=None, name=None, session=None):
    sess = session or requests.Session()
    sess.headers.update({"User-Agent": UA,
                         "Accept": "text/html,application/xhtml+xml,*/*",
                         "Accept-Language": "en-US,en;q=0.9"})
    sess.get(BASE + "/", timeout=45)
    form = blank_form()
    if street:
        form["street"] = street
    if city:
        form["city"] = city
    if zipcode:
        form["zip"] = zipcode
    if parcel:
        form["parcelId"] = parcel
    if name:
        form["name"] = name
    r = sess.post(BASE + "/property/query", data=form, timeout=90,
                  headers={"Referer": BASE + "/", "Origin": BASE})
    return r


def parcel_ids(html):
    """Extract parcel IDs and their result links from a results page."""
    out = []
    for m in re.finditer(r'href="(/property/[^"]+)"', html):
        out.append(m.group(1))
    ids = set(re.findall(r'\b(\d{2}-[0-9A-Z]{1,2}-\d{2,4}-[0-9A-Z]{3,5}-\d{2,5})\b', html))
    return sorted(set(out)), sorted(ids)


if __name__ == "__main__":
    print("This module is imported by acquisition scripts.")
    sys.exit(0)