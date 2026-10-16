#!/usr/bin/env python3
"""Query the official Florida ERP MapServer services (FDEP + 5 water management

districts) for Environmental Resource Permit records near the Tom Street
parcels in Navarre, Santa Rosa County, Florida.

Official public ArcGIS REST endpoints published by each agency:
  FDEP   https://ca.dep.state.fl.us/arcgis/rest/services/External_Services/FDEP_ERP/MapServer
  NWFWMD https://permitting.sjrwmd.com/arcgis02/rest/services/NWFWMD/EPermit_ERP/MapServer
  SFWMD  https://geoweb.sfwmd.gov/agsext1/rest/services/RegulationApplicationPermitsApp/RegulationFloridaPermitsERP/MapServer
  SRWMD  https://permitting.sjrwmd.com/arcgis02/rest/services/SRWMD/EPermit_ERP/MapServer
  SJRWMD https://permitting.sjrwmd.com/arcgis02/rest/services/SJRWMD/EPermit_ERP/MapServer
  SWFWMD https://www25.swfwmd.state.fl.us/arcgis11/rest/services/prjFLPermitPortal/EPermitERP/MapServer
"""

import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:  # noqa: E402
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT  # noqa: E402
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = _ROOT
OUT = ROOT / "09_ENVIRONMENTAL_PERMITS/SYSTEM_RAW"

SITES = {
    "FDEP_ERP": "https://ca.dep.state.fl.us/arcgis/rest/services/External_Services/FDEP_ERP/MapServer",
    "NWFWMD_EPermit_ERP": "https://permitting.sjrwmd.com/arcgis02/rest/services/NWFWMD/EPermit_ERP/MapServer",
    "SFWMD_ERP": "https://geoweb.sfwmd.gov/agsext1/rest/services/RegulationApplicationPermitsApp/RegulationFloridaPermitsERP/MapServer",
    "SRWMD_EPermit_ERP": "https://permitting.sjrwmd.com/arcgis02/rest/services/SRWMD/EPermit_ERP/MapServer",
    "SJRWMD_EPermit_ERP": "https://permitting.sjrwmd.com/arcgis02/rest/services/SJRWMD/EPermit_ERP/MapServer",
    "SWFWMD_EPermitERP": "https://www25.swfwmd.state.fl.us/arcgis11/rest/services/prjFLPermitPortal/EPermitERP/MapServer",
}

POINTS = {
    "2264_Tom_St": (-86.814654128074, 30.415261890933),
    "2268_Tom_St": (-86.814732079774, 30.415812456243),
    "2265_Tom_St": (-86.815198029771, 30.415138383589),
}

S = requests.Session()
S.headers.update({"User-Agent": "Tom-Street-Drainage-Investigation/1.0 "
                               "(public-records research)"})

def layers(svc):
    try:
        d = S.get(svc, params={"f": "json"}, timeout=60).json()
        return [(l["id"], l["name"]) for l in d.get("layers", [])
                if l.get("geometryType")]
    except Exception as e:
        print("   layer discovery failed:", e)
        return []

def query(svc, lid, pt, dist=150):
    """ArcGIS REST spatial query in WGS84 (inSR=4326) around a lon/lat point."""
    url = f"{svc}/{lid}/query"
    params = {
        "where": "1=1",
        "geometry": f"{pt[0]},{pt[1]}",
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "distance": str(dist),
        "units": "esriSRUnit_Foot",
        "outFields": "*",
        "returnGeometry": "false",
        "resultRecordCount": "2000",
        "f": "json",
    }
    try:
        r = S.get(url, params=params, timeout=120)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {"retrieved_utc": datetime.now(timezone.utc).isoformat(),
              "points": POINTS, "services": {}, "results": {}}
    for name, svc in SITES.items():
        print("==", name, svc)
        ls = layers(svc)
        print("   layers:", ls)
        report["services"][name] = {"service": svc, "layers": ls}
        for slug, pt in POINTS.items():
            hits = []
            for lid, lname in ls:
                d = query(svc, lid, pt)
                if "error" in d:
                    print(f"   ERR {name}/{slug}/{lid}: {d['error']}")
                    continue
                if d.get("exceededTransferLimit"):
                    print(f"   note: {name}/{slug}/{lid} exceeded transfer limit")
                fs = d.get("features", [])
                if fs:
                    print(f"   HIT {name}/{slug} layer {lid} ({lname}): {len(fs)}")
                    for f in fs:
                        hits.append({"service": name, "layer_id": lid,
                                     "layer_name": lname,
                                     "attributes": f.get("attributes")})
                time.sleep(0.4)
            report["results"].setdefault(slug, []).extend(hits)
    for slug in POINTS:
        n = len(report["results"].get(slug, []))
        print(f"TOTAL {slug}: {n} ERP features within 120 ft")
    fp = OUT / "erp_mapserver_query_results.json"
    fp.write_text(json.dumps(report, indent=1))
    print("saved", fp, fp.stat().st_size, "bytes")
    print("sha256", hashlib.sha256(fp.read_bytes()).hexdigest())

if __name__ == "__main__":
    main()