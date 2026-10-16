#!/usr/bin/env python3
"""Phase B acquisition: official hydrologic and hazard context for the Tom
Street parcels.

Sources (all public, authoritative, no login):
  FEMA National Flood Hazard Layer (hazards.fema.gov/arcgis/rest/services/public/NFHL)
    - layer 3  FIRM Panels
    - layer 22 Political Jurisdictions
    - layer 28 Flood Hazard Zones
    - layer 27 Flood Hazard Boundaries
  NOAA NCEI access services - GHCN-Daily precipitation and temperature
    (www.ncei.noaa.gov/access/services/data/v1)

Everything is written under 11_HYDROLOGY_AND_HAZARD/ with a sidecar metadata
record. Units, station identity, datum caveats and vintage are preserved.
"""
import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT, rel, sha256_file, utcnow  # noqa: E402

import json
from pathlib import Path

import requests

OUT = _ROOT / "11_HYDROLOGY_AND_HAZARD"
S = requests.Session()
S.headers.update({"User-Agent": "Tom-Street-Drainage-Investigation/1.0 "
                               "(public-records research)"})

NFHL = "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer"
NCEI = "https://www.ncei.noaa.gov/access/services/data/v1"

# Geocoded parcel centroids (USGS/ESRI geocode, score 100)
PARCELS = {
    "2264_Tom_St": {"lon": -86.814654128074, "lat": 30.415261890933,
                    "parcel": "21-2S-26-0780-0QQ00-1020"},
    "2268_Tom_St": {"lon": -86.814732079774, "lat": 30.415812456243,
                    "parcel": "21-2S-26-0780-0QQ00-1490"},
}

# Station USW00012842 = Pensacola Regional Airport, the nearest long-record
# GHCN-Daily station to Navarre, FL. Distance/vintage caveats are recorded in the
# metadata; this is NOT a gauge at the site.
STATION = "USW00012842"
STATION_NAME = "PENSACOLA RGNL AP, FL US"


def nfhl(layer_id, name, key):
    rows = {}
    for slug, p in PARCELS.items():
        r = S.get(f"{NFHL}/{layer_id}/query", timeout=90, params={
            "where": "1=1", "geometry": f"{p['lon']},{p['lat']}",
            "geometryType": "esriGeometryPoint", "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects", "outFields": "*",
            "returnGeometry": "false", "f": "json"}).json()
        rows[slug] = r.get("features", [])
    return {
        "source_agency": "Federal Emergency Management Agency (FEMA)",
        "source_system": "National Flood Hazard Layer (NFHL) ArcGIS REST",
        "source_url": f"{NFHL}/{layer_id}/query",
        "layer_id": layer_id, "layer_name": name,
        "retrieved_utc": utcnow(),
        "crs": "EPSG:4326 (WGS84) input; attributes as published",
        "results": rows,
    }


def ncei(start, end, station=STATION):
    r = S.get(NCEI, timeout=180, params={
        "dataset": "daily-summaries", "stations": station,
        "startDate": start, "endDate": end, "format": "json",
        "units": "metric", "includeAttributes": "true"})
    r.raise_for_status()
    return r.json()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    written = []

    for lid, name, key in [(3, "FIRM Panels", "firm_panels"),
                           (22, "Political Jurisdictions", "jurisdictions"),
                           (28, "Flood Hazard Zones", "flood_hazard_zones"),
                           (27, "Flood Hazard Boundaries", "flood_hazard_boundaries")]:
        blob = nfhl(lid, name, key)
        f = OUT / f"fema_nfhl_{key}.json"
        f.write_text(json.dumps(blob, indent=1))
        n = sum(len(v) for v in blob["results"].values())
        written.append((rel(f), f.stat().st_size, sha256_file(f),
                        f"{name}: {n} feature(s) across 2 parcels"))
        print(f"  {rel(f)}  {name}: {n} features")

    # Rainfall across the full construction window and the preceding season.
    for tag, s, e in [("construction_window", "2026-01-01", "2026-10-15"),
                      ("2025_full_year", "2025-01-01", "2025-12-31")]:
        rows = ncei(s, e)
        f = OUT / f"noaa_ghcndaily_{tag}.json"
        blob = {
            "source_agency": "NOAA National Centers for Environmental Information (NCEI)",
            "source_system": "NCEI Access Data Service - GHCN-Daily",
            "source_url": NCEI,
            "dataset": "daily-summaries", "station": STATION,
            "station_name": STATION_NAME,
            "station_caveat": ("Nearest long-record GHCN-Daily station to the site. "
                               "This is NOT an on-site rain gauge. Values are "
                               "airport observations and do not measure rainfall "
                               "at 2264/2268 Tom Street."),
            "units": "metric (PRCP in mm, TMAX/TMIN in degrees C)",
            "start": s, "end": e, "retrieved_utc": utcnow(),
            "row_count": len(rows), "rows": rows,
        }
        f.write_text(json.dumps(blob, indent=1))
        prcp = [float(x["PRCP"]) for x in rows
                if x.get("PRCP") not in (None, "")]
        tot = round(sum(prcp), 1) if prcp else None
        written.append((rel(f), f.stat().st_size, sha256_file(f),
                        f"{len(rows)} days, total PRCP {tot} mm"))
        print(f"  {rel(f)}  {len(rows)} days, total PRCP {tot} mm")

    meta = OUT / "HYDROLOGY_SOURCE_MANIFEST.csv"
    lines = ["relative_path,bytes,sha256,description"]
    for r, b, h, d in written:
        lines.append(f"{r},{b},{h},\"{d}\"")
    meta.write_text("\n".join(lines) + "\n")
    print("wrote", rel(meta))
    # also add to the repo-wide manifest
    print("done")


if __name__ == "__main__":
    main()