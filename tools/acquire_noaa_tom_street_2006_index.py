#!/usr/bin/env python3
"""Acquire the original NOAA 2006 Panhandle lidar GeoPackage tile index.

Identify source tiles whose official polygons intersect the three Tom Street
representative points. Keep original GeoPackage unmodified and record checksums.
No 2006 elevation values or geographic coverage are inferred before validation.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import Request, urlopen

import fiona
from pyproj import Transformer
from shapely.geometry import Point, shape

URL = (
    "https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/57/"
    "tileindex_2006_FL_Panhandle_m57.gpkg"
)
METADATA_URL = "https://www.fisheries.noaa.gov/inport/item/48209"
DEST = Path(__file__).resolve().parents[1] / (
    "11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/"
    "ORIGINAL_NOAA_2006/tileindex_2006_FL_Panhandle_m57.gpkg"
)
MANIFEST = DEST.with_suffix(".acquisition.json")
SITES = {
    "2264_Tom_St": {"parcel": "21-2S-26-0780-0QQ00-1020",
                    "lon": -86.81466, "lat": 30.41519},
    "2265_Tom_St": {"parcel": "21-2S-26-0780-0QQ00-1180",
                    "lon": -86.81521, "lat": 30.41515},
    "2268_Tom_St": {"parcel": "21-2S-26-0780-0QQ00-1490",
                    "lon": -86.81466, "lat": 30.41534},
}


def get_bytes():
    with urlopen(Request(URL, headers={"User-Agent": "TomStreetPublicEvidence/1.0"}),
                 timeout=120) as response:
        if response.status != 200:
            raise ValueError(f"HTTP {response.status}")
        raw = response.read(30_000_001)
    if len(raw) < 1024 or len(raw) > 30_000_000:
        raise ValueError(f"Unexpected tile index size: {len(raw)}")
    if not raw.startswith(b"SQLite format 3\x00"):
        raise ValueError("The response is not an SQLite GeoPackage")
    return raw


def classify(path: Path):
    layers = []
    for layer in fiona.listlayers(path):
        with fiona.open(path, layer=layer, mode="r") as src:
            crs = src.crs_wkt or src.crs
            if not crs:
                raise ValueError(f"Source layer {layer} lacks an authoritative CRS")
            transform = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
            projected = {}
            for key, site in SITES.items():
                x, y = transform.transform(site["lon"], site["lat"])
                projected[key] = Point(x, y)
            matches = {key: [] for key in SITES}
            count = 0
            for feat in src:
                count += 1
                if not feat.geometry:
                    continue
                geometry = shape(feat.geometry)
                if geometry.is_empty:
                    continue
                for key, pt in projected.items():
                    if geometry.intersects(pt):
                        matches[key].append({
                            "feature_id": str(feat.id),
                            "properties": dict(feat.properties),
                            "bounds": list(geometry.bounds),
                        })
            layers.append({
                "layer_name": layer, "layer_crs": str(crs),
                "feature_count": count,
                "site_projected_points": {
                    key: [round(pt.x, 3), round(pt.y, 3)]
                    for key, pt in projected.items()
                },
                "site_tile_intersections": matches,
            })
    return layers


def main():
    DEST.parent.mkdir(parents=True, exist_ok=True)
    raw = get_bytes()
    with NamedTemporaryFile(suffix=".gpkg", dir=DEST.parent, delete=False) as f:
        f.write(raw)
        tmp = Path(f.name)
    try:
        layers = classify(tmp)
        if DEST.exists() and DEST.read_bytes() != raw:
            raise ValueError("Official previously preserved tile index has different bytes")
        if not DEST.exists():
            os.replace(tmp, DEST)
        else:
            tmp.unlink(missing_ok=True)
    finally:
        tmp.unlink(missing_ok=True)
    site_matches = {
        name: sum(
            len(layer["site_tile_intersections"][name]) for layer in layers
        ) for name in SITES
    }
    result = {
        "status": (
            "ORIGINAL_GPKG_PRESERVED_AND_TILES_IDENTIFIED"
            if all(site_matches.values())
            else "ORIGINAL_GPKG_PRESERVED_INTERSECTION_INCOMPLETE"
        ),
        "agency": "NOAA Office for Coastal Management",
        "data_source": "2006 NWFWMD Lidar: Escambia, Santa Rosa, and Walton Counties",
        "dataset_id": 57,
        "source_url": URL, "metadata_url": METADATA_URL,
        "source_coverage_period_santa_rosa": "2006-01-12 to 2006-02-28",
        "vertical_reference": "Published version NAVD88 GEOID18; original 2006 datum and possible transformation must be verified when comparing years",
        "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
        "local_original": str(DEST), "sites": SITES,
        "layers": layers, "site_intersection_counts": site_matches,
        "limitations": [
            "A polygon index hit does not establish a usable 2006 point cloud or elevation for a site.",
            "Older 2006 vertical accuracy and classifications differ from the 2017 product.",
            "A tax/GIS sample coordinate is not a property survey.",
            "Do not infer modern drainage or construction impacts from a historic data footprint.",
        ],
    }
    MANIFEST.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "bytes": len(raw),
                      "sha256": result["sha256"],
                      "site_intersection_counts": site_matches,
                      "tile_candidates": [
                          {
                              "site": site,
                              "layer": layer["layer_name"],
                              "matches": layer["site_tile_intersections"][site],
                          }
                          for layer in layers for site in SITES
                          if layer["site_tile_intersections"][site]
                      ]}, indent=2))


if __name__ == "__main__":
    main()
