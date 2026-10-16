#!/usr/bin/env python3
"""Preserve the independently indexed original NOAA 2006 Tom Street COPC LAZ.

The selected tile URL comes from the already preserved original NOAA GeoPackage,
not guessed from an address. It must index all three properties, be LAS-format,
and fit within a conservative GitHub file-size limit. LAS header checks do NOT
substitute for a ground-point classification or professional terrain survey.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import struct
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import Request, urlopen

NAME = "20060228_sr1369_ld_p17.copc.laz"
SOURCE = ("https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/"
          "laz/geoid18/57/" + NAME)
BASE = Path(__file__).resolve().parents[1] / (
    "11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/"
    "ORIGINAL_NOAA_2006"
)
INDEX_MANIFEST = BASE / "tileindex_2006_FL_Panhandle_m57.acquisition.json"
DEST = BASE / NAME
MANIFEST = BASE / "2006_tom_street_copc_acquisition.json"
MAX_BYTES = 80_000_000
SITES = ["2264_Tom_St", "2265_Tom_St", "2268_Tom_St"]


def check_index():
    index = json.loads(INDEX_MANIFEST.read_text(encoding="utf-8"))
    assert index["status"] == "ORIGINAL_GPKG_PRESERVED_AND_TILES_IDENTIFIED"
    assert len(index["layers"]) > 0
    projected = {}
    for site in SITES:
        matches = [
            match for layer in index["layers"]
            for match in layer["site_tile_intersections"][site]
        ]
        if len(matches) != 1:
            raise ValueError(f"Expected one authoritative 2006 tile for {site}")
        attrs = matches[0]["properties"]
        if attrs.get("filename") != NAME or attrs.get("url") != SOURCE:
            raise ValueError(f"Public tile index source does not match {site}")
        projected[site] = index["layers"][0]["site_projected_points"][site]
    return projected


def download_to_temp():
    BASE.mkdir(parents=True, exist_ok=True)
    request = Request(SOURCE, headers={"User-Agent": "TomStreetPublicEvidence/1.0"})
    with urlopen(request, timeout=180) as response:
        if response.status != 200:
            raise ValueError(f"Unexpected HTTP {response.status}")
        announced = response.headers.get("Content-Length")
        if announced and int(announced) > MAX_BYTES:
            raise ValueError(f"Public 2006 source too large for standard GitHub: {announced}")
        f = NamedTemporaryFile(dir=BASE, suffix=".copc.laz", delete=False)
        path = Path(f.name)
        digest = hashlib.sha256()
        total = 0
        try:
            with f:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_BYTES:
                        raise ValueError("Public 2006 source exceeded 80 MB repository limit")
                    digest.update(chunk)
                    f.write(chunk)
        except Exception:
            path.unlink(missing_ok=True)
            raise
    if total < 1024:
        path.unlink(missing_ok=True)
        raise ValueError("Downloaded file unexpectedly small")
    return path, total, digest.hexdigest()


def read_las_header(path, projected):
    with path.open("rb") as f:
        head = f.read(375)
    if len(head) < 227 or head[:4] != b"LASF":
        raise ValueError("Source file fails LAS file-header signature check")
    major, minor = head[24], head[25]
    if major != 1 or minor < 2 or minor > 4:
        raise ValueError(f"Unexpected LAS header version {major}.{minor}")
    scale = list(struct.unpack_from("<ddd", head, 131))
    offset = list(struct.unpack_from("<ddd", head, 155))
    maxx, minx, maxy, miny, maxz, minz = struct.unpack_from("<dddddd", head, 179)
    if not all(math.isfinite(v) for v in
               scale + offset + [maxx, minx, maxy, miny, maxz, minz]):
        raise ValueError("Invalid non-finite LAS coordinate bounds")
    if not (minx < maxx and miny < maxy and minz < maxz):
        raise ValueError("Invalid LAS bounds")
    if not (1_000_000 > maxx > minx > 0 and 4_000_000 > maxy > miny > 2_000_000):
        raise ValueError("LAS XY ranges do not appear to use the expected Florida UTM coordinates")
    inside = {}
    for site, (x, y) in projected.items():
        inside[site] = (minx <= x <= maxx and miny <= y <= maxy)
    if not all(inside.values()):
        raise ValueError(f"LAS point-cloud bounds do not cover all sites: {inside}")
    return {
        "LAS_version": f"{major}.{minor}", "point_data_format": head[104] & 0x3F,
        "legacy_point_count": struct.unpack_from("<I", head, 107)[0],
        "horizontal_bounds": {
            "minx": minx, "maxx": maxx, "miny": miny, "maxy": maxy,
        },
        "vertical_bounds_source_units": {"minz": minz, "maxz": maxz},
        "point_scale": scale, "point_offset": offset,
        "representative_site_inside_LAS_bounds": inside,
    }


def main():
    projected = check_index()
    tmp, size, sha256 = download_to_temp()
    try:
        inspection = read_las_header(tmp, projected)
        if DEST.exists() and hashlib.sha256(DEST.read_bytes()).hexdigest() != sha256:
            raise ValueError("Original file differs from previously preserved evidence")
        if DEST.exists():
            tmp.unlink(missing_ok=True)
        else:
            os.replace(tmp, DEST)
    finally:
        tmp.unlink(missing_ok=True)

    manifest = {
        "status": "2006_ORIGINAL_PUBLIC_COPC_LAZ_PRESERVED_HEADER_AND_EXTENT_CHECKED",
        "dataset": "2006 NWFWMD Lidar: Escambia, Santa Rosa and Walton Counties",
        "source_agency": "NOAA Office for Coastal Management / NWFWMD",
        "source_url": SOURCE,
        "index_source": str(INDEX_MANIFEST),
        "metadata_source": "https://www.fisheries.noaa.gov/inport/item/48209",
        "source_date_in_filename": "2006-02-28",
        "published_product_vertical_reference": "NAVD88 using GEOID18 per NOAA public geoid18 index. Verify site-specific vertical units and LAS VLR metadata before numeric comparison.",
        "local_original": str(DEST),
        "bytes": size, "sha256": sha256,
        "header": inspection,
        "limitations": [
            "A preserved 2006 original point cloud; site ground points and their classifications have NOT been analyzed.",
            "No 2006 lot elevation or changes to 2017/2026 inferred.",
            "Published GEOID18 product not automatically interchangeable with 2017 NOAA GEOID12B raster.",
            "Public parcel polygons and sample points are approximate, not surveys.",
            "LAS header coverage does not establish adequacy or cause of drainage condition.",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "file": str(DEST),
                      "bytes": size, "sha256": sha256,
                      "bounds": inspection["horizontal_bounds"]}, indent=2))


if __name__ == "__main__":
    main()
