#!/usr/bin/env python3
"""Archive public County GIS metadata for the historic stormwater-problem layer.

The layer description references April 2006 flooding. It does not date the
individual Tom Street polygon or establish present-day drainage causation.
"""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/COUNTY_STORMWATER_PROVENANCE"
BASE = "https://cloud.santarosa.fl.gov/arcgis/rest/services/santarosa/GoMaps4_0/MapServer/79"
URLS = {
    "ORIGINAL_GOMAPS_STORMWATER_LAYER_79.json": BASE + "?f=pjson",
    "ORIGINAL_GOMAPS_STORMWATER_FEATURE_2068.json": BASE + "/query?" + urlencode({
        "where": "OBJECTID=2068", "outFields": "OBJECTID,DataSource,GlobalID",
        "returnGeometry": "false", "f": "pjson",
    }),
}

def acquire(name: str, url: str) -> dict:
    request = Request(url, headers={"User-Agent": "TomStreetEvidence/1.0", "Accept": "application/json"})
    with urlopen(request, timeout=80) as response:
        if response.status != 200 or urlsplit(response.url).hostname != "cloud.santarosa.fl.gov":
            raise RuntimeError("County source request failed or redirected")
        raw = response.read(750001)
    if not 100 <= len(raw) <= 750000:
        raise RuntimeError(f"Implausible County JSON size for {name}")
    response_json = json.loads(raw)
    if not isinstance(response_json, dict) or response_json.get("error"):
        raise RuntimeError("County source did not return an ArcGIS object")
    if name.endswith("LAYER_79.json"):
        desc = response_json.get("description", "")
        if response_json.get("id") != 79 or response_json.get("name") != "Stormwater Problem Area":
            raise RuntimeError("Unexpected County GIS layer")
        if "April 2006" not in desc or "Road" not in desc:
            raise RuntimeError("Historic layer provenance statement missing")
        verification = "LAYER_ID_79_AND_APRIL_2006_GENERAL_DESCRIPTION_VERIFIED"
    else:
        features = response_json.get("features")
        if not isinstance(features, list) or len(features) != 1:
            raise RuntimeError("Object 2068 not uniquely returned")
        attrs = features[0].get("attributes", {})
        if attrs.get("OBJECTID") != 2068 or attrs.get("DataSource") != "Road & Bridge Maps Marked Up by Foreman":
            raise RuntimeError("Unexpected historical feature attributes")
        verification = "COUNTY_FEATURE_2068_AND_DATA_SOURCE_VERIFIED"
    dst = OUT / name
    if dst.exists():
        if dst.read_bytes() != raw:
            raise RuntimeError("Existing original changed; refuse destructive overwrite: " + name)
    else:
        dst.write_bytes(raw)
    return {"path": dst.relative_to(ROOT).as_posix(), "source_url": url,
            "sha256": sha256(raw).hexdigest(), "bytes": len(raw),
            "type": "OFFICIAL_ORIGINAL_ARCGIS_RESPONSE", "validation": verification}

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    entries = [acquire(name, url) for name, url in URLS.items()]
    path = OUT / "ACQUISITION_MANIFEST.json"
    report = {
        "status": "ORIGINAL_OFFICIAL_RESPONSES_DOWNLOADED_VERIFIED",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "agency": "Santa Rosa County GIS",
        "files": entries,
        "limitations": [
            "Layer-wide April 2006 context does not establish when OBJECTID 2068 was mapped.",
            "Historical polygon coverage is not parcel-level flooding proof or evidence of builder wrongdoing.",
            "No surveyed pipe inverts, current grades, outfall, or hydraulic capacity established.",
        ],
    }
    if path.exists():
        old = json.loads(path.read_text(encoding="utf-8"))
        if old["files"] != entries:
            raise RuntimeError("Acquisition file list changed; preserve and investigate original manifest")
        report = old
    else:
        path.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    for row in entries:
        print("VERIFIED", row["path"], row["bytes"], row["sha256"])

if __name__ == "__main__":
    main()
