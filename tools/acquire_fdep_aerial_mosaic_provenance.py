#!/usr/bin/env python3
"""Acquire official Florida DEP aerial-image mosaic item provenance.

A successful exported image does not establish that a service's year label
matches the date the Tom Street tile was photographed. Preserve the official
ImageServer catalog query and layer-level metadata for direct comparison.
"""
from __future__ import annotations
import concurrent.futures
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = "https://ca.dep.state.fl.us/image/rest/services"
DEST = Path(__file__).resolve().parents[1] / (
    "11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/"
    "FLORIDA_DEP_HISTORICAL_AERIALS/MOSAIC_CATALOG_PROVENANCE.json"
)
SOURCES = [
    ("1994_DOQQ", "MISC/DOQQ_1994"), ("1999_DOQQ", "MISC/DOQQ_1999"),
    ("2004_DOQQ", "MISC/DOQQ_2004"), ("2008_DOQQ", "MISC/DOQQ_2008"),
    ("2010_NAIP", "MISC/NAIP_Imagery_2010"),
    *[(f"{y}_FDOT", f"FDOT_Yearly_Aerials/Aerial_Imagery_{y}") for y in (
        2004, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
        2015, 2016, 2017, 2018, 2019, 2020, 2021
    )]
]
PROBE = {"x": -86.81466, "y": 30.41519, "spatialReference": {"wkid": 4326}}


def read_json(url, cap=700_000):
    with urlopen(
        Request(url, headers={"User-Agent": "TomStreetPublicEvidence/1.0"}),
        timeout=75,
    ) as resp:
        if resp.status != 200:
            raise ValueError(f"HTTP {resp.status}")
        data = resp.read(cap + 1)
    if len(data) > cap:
        raise ValueError("Response too large for bounded catalog request")
    obj = json.loads(data)
    if not isinstance(obj, dict):
        raise ValueError("Unexpected non-object ArcGIS response")
    return obj


def one_source(pair):
    name, service = pair
    service_url = f"{ROOT}/{service}/ImageServer"
    query = urlencode({
        "geometry": json.dumps(PROBE, separators=(",", ":")),
        "geometryType": "esriGeometryPoint",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "OBJECTID,Name,ProductName,GroupName,Category,Tag",
        "returnGeometry": "false", "f": "pjson",
    })
    query_url = f"{service_url}/query?{query}"
    metadata_url = f"{service_url}?f=pjson"
    record = {
        "label": name, "service_url": service_url,
        "catalog_query_url": query_url,
        "service_metadata_url": metadata_url,
        "catalog_status": "NOT_ACQUIRED",
        "metadata_status": "NOT_ACQUIRED",
    }
    try:
        obj = read_json(query_url)
        if obj.get("error"):
            raise ValueError(f"ArcGIS query error {obj['error']}")
        if not isinstance(obj.get("features"), list):
            raise ValueError("ArcGIS query did not return a features array")
        record["catalog_status"] = (
            "POINT_CATALOG_FEATURES_RETURNED" if obj["features"] else
            "NO_POINT_CATALOG_FEATURES_RETURNED"
        )
        record["catalog_response"] = obj
    except Exception as e:
        record["catalog_failure"] = f"{type(e).__name__}: {e}"[:300]
    try:
        meta = read_json(metadata_url)
        if meta.get("error"):
            raise ValueError(f"ArcGIS service error {meta['error']}")
        record["metadata_status"] = "SERVICE_METADATA_CAPTURED"
        record["metadata_response"] = {
            "name": meta.get("name"),
            "serviceDescription": meta.get("serviceDescription"),
            "description": meta.get("description"),
            "copyrightText": meta.get("copyrightText"),
            "pixelSizeX": meta.get("pixelSizeX"),
            "pixelSizeY": meta.get("pixelSizeY"),
            "capabilities": meta.get("capabilities"),
            "extent": meta.get("extent"),
            "spatialReference": meta.get("spatialReference"),
            "objectIdField": meta.get("objectIdField"),
            "fields": meta.get("fields"),
        }
    except Exception as e:
        record["metadata_failure"] = f"{type(e).__name__}: {e}"[:300]
    return record


def main():
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        rows = list(pool.map(one_source, SOURCES))
    report = {
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "agency": "Florida Department of Environmental Protection image REST service; FDOT and USDA imagery",
        "sample_point_wgs84": PROBE,
        "services_queried": len(SOURCES),
        "catalog_features_found": sum(
            x["catalog_status"] == "POINT_CATALOG_FEATURES_RETURNED" for x in rows
        ),
        "records": rows,
        "limitations": [
            "Service query returns mosaic catalog features, not camera exposure metadata authenticated for each pixel.",
            "A source-year label is not proof of precise date that the Tom Street imagery was flown.",
            "Catalog point is within County parcel 2264 GIS polygon, but not a surveyed point.",
            "Image service metadata can describe statewide or multi-year coverage; parcel-specific flights may differ.",
            "No photogrammetric or elevation conclusions may be drawn from catalog records alone.",
        ],
    }
    DEST.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("CATALOG FEATURES:", report["catalog_features_found"], "/", len(SOURCES))
    for r in rows:
        print(r["label"], r["catalog_status"], r.get("catalog_failure", ""))
    if not any(x["catalog_status"] == "POINT_CATALOG_FEATURES_RETURNED" for x in rows):
        raise RuntimeError("No live geolocated imagery catalog features returned")


if __name__ == "__main__":
    main()
