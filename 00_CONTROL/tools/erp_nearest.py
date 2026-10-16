#!/usr/bin/env python3
"""Acquire ERP evidence for the Tom Street parcels from the official NWFWMD /
FDEP / other-WMD public ArcGIS services, and record the distance from each
parcel to the nearest Environmental Resource Permit boundary."""
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path("/home/dylan/Tom-Street-Drainage-Investigation")
OUT = ROOT / "09_ENVIRONMENTAL_PERMITS/SYSTEM_RAW"
SVC = ("https://permitting.sjrwmd.com/arcgis02/rest/services/NWFWMD/"
       "EPermit_ERP/MapServer")

POINTS = {
    "2264_Tom_St": {"address": "2264 Tom St, Navarre, FL 32566",
                    "lon": -86.814654128074, "lat": 30.415261890933,
                    "parcel": "21-2S-26-0780-0QQ00-1020"},
    "2268_Tom_St": {"address": "2268 Tom St, Navarre, FL 32566",
                    "lon": -86.814732079774, "lat": 30.415812456243,
                    "parcel": "21-2S-26-0780-0QQ00-1490"},
    "2265_Tom_St": {"address": "2265 Tom St, Navarre, FL 32566",
                    "lon": -86.815198029771, "lat": 30.415138383589,
                    "parcel": "21-2S-26-0780-0QQ00-1180"},
}
S = requests.Session()
S.headers.update({"User-Agent": "Tom-Street-Drainage-Investigation/1.0 "
                               "(public-records research)"})


def nearest_permits(pt, radii=(150, 500, 1000, 2000)):
    found = {}
    for dist in radii:
        for lid in (0, 1):
            r = S.get(f"{SVC}/{lid}/query", timeout=120, params={
                "where": "1=1", "geometry": f"{pt['lon']},{pt['lat']}",
                "geometryType": "esriGeometryPoint", "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects", "distance": dist,
                "units": "esriSRUnit_Foot", "outFields": "*",
                "returnGeometry": "true", "outSR": "4326", "f": "json"}).json()
            for f in r.get("features", []):
                a = f["attributes"]
                key = (a.get("OFFCL_PRMT_ID"), a.get("SEQ_NO"))
                rec = found.setdefault(key, {"attributes": a, "radius_ft": dist})
                rec["radius_ft"] = min(rec["radius_ft"], dist)
                g = (f.get("geometry") or {})
                if g:
                    rec.setdefault("geometry_wgs84", g)
    return list(found.values())


def ring_distance_ft(pt, geom):
    """Approximate distance from point to nearest vertex of the permit polygon."""
    if not geom:
        return None
    rings = geom.get("rings") or []
    best = None
    for ring in rings:
        for x, y in ring:
            dx = (x - pt["lon"]) * 111320 * math.cos(math.radians(pt["lat"]))
            dy = (y - pt["lat"]) * 110574
            d = math.hypot(dx, dy)
            best = d if best is None else min(best, d)
    return round(best, 1) if best else None


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    rep = {"retrieved_utc": datetime.now(timezone.utc).isoformat(),
           "service": SVC, "sites": {}}
    for slug, pt in POINTS.items():
        recs = nearest_permits(pt)
        for r in recs:
            r["vertex_distance_ft"] = ring_distance_ft(pt, r.get("geometry_wgs84"))
            r.pop("geometry_wgs84", None)
        rep["sites"][slug] = recs
        print(f"{slug} ({pt['parcel']}): {len(recs)} ERP permit(s) within 2000 ft")
        for r in recs:
            a = r["attributes"]
            print(f"   P{a.get('OFFCL_PRMT_ID')}-{a.get('SEQ_NO')} "
                  f"{a.get('SITE_NM')} | {a.get('RULE_TYPE_DESC')} | "
                  f"{a.get('PRMT_STTS')} | {a.get('COUNTY')} | "
                  f"~{r['vertex_distance_ft']} ft to nearest boundary vertex")
    fp = OUT / "erp_nearest_permits_tom_street.json"
    fp.write_text(json.dumps(rep, indent=1))
    print("\nsaved", fp, fp.stat().st_size, "bytes")
    print("sha256", hashlib.sha256(fp.read_bytes()).hexdigest())