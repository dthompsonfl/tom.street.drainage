#!/usr/bin/env python3
"""Acquire and independently validate one NOAA public 2017 Tom Street DEM tile.

This preserves original downloaded TIFF bytes unchanged; metadata and limited
historical observations are derived and stored separately. It does not claim
today's elevations, parcel survey accuracy, or drainage engineering adequacy.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import Request, urlopen

import rasterio
from rasterio.warp import transform

SOURCE = (
    "https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/"
    "dem/FL_Escam_St_Rosa_DEM_2017_8683/16reu175645.tif"
)
SOURCE_CATALOG = (
    "https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/"
    "dem/FL_Escam_St_Rosa_DEM_2017_8683/index.html"
)
METADATA = "https://www.fisheries.noaa.gov/inport/item/55909"
DEST = Path(__file__).resolve().parents[1] / (
    "11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/"
    "ORIGINAL_NOAA_2017/16reu175645.tif"
)
MANIFEST = DEST.with_suffix(".acquisition.json")
SITES = {
    "2264_Tom_St": {
        "parcel": "21-2S-26-0780-0QQ00-1020", "lon": -86.81466, "lat": 30.41519
    },
    "2265_Tom_St": {
        "parcel": "21-2S-26-0780-0QQ00-1180", "lon": -86.81521, "lat": 30.41515
    },
    "2268_Tom_St": {
        "parcel": "21-2S-26-0780-0QQ00-1490", "lon": -86.81466, "lat": 30.41534
    },
}


def download() -> bytes:
    request = Request(SOURCE, headers={"User-Agent": "TomStreetPublicEvidence/1.0"})
    with urlopen(request, timeout=120) as response:
        if response.status != 200:
            raise ValueError(f"Unexpected HTTP status: {response.status}")
        raw = response.read(40_000_001)
    if len(raw) > 40_000_000:
        raise ValueError("Unreasonable TIFF size; refusing to archive")
    if len(raw) < 50_000 or raw[:4] not in (b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+"):
        raise ValueError("Response is not a plausible TIFF")
    return raw


def validate(tmp_path: Path) -> dict:
    with rasterio.open(tmp_path) as src:
        if src.crs is None or src.count < 1:
            raise ValueError("Tile has no georeference or image band")
        if not (0.5 <= abs(src.res[0]) <= 3 and 0.5 <= abs(src.res[1]) <= 3):
            raise ValueError(f"Unexpected DEM grid resolution: {src.res}")
        sample_out = {}
        for name, info in SITES.items():
            ex, ny = transform(
                "EPSG:4326", src.crs, [info["lon"]], [info["lat"]]
            )
            x, y = ex[0], ny[0]
            if not (src.bounds.left <= x < src.bounds.right and
                    src.bounds.bottom <= y < src.bounds.top):
                raise ValueError(f"NOAA tile does not cover {name}: {x}, {y}")
            val = next(src.sample([(x, y)], indexes=1, masked=True))[0]
            if bool(getattr(val, "mask", False)) or not math.isfinite(float(val)):
                raise ValueError(f"No valid terrain sample for {name}")
            # Very wide geographic sanity bound, not a survey acceptance test.
            if not -50 <= float(val) <= 200:
                raise ValueError(f"Implausible terrain sample at {name}: {val}")
            sample_out[name] = {
                "parcel": info["parcel"],
                "lon": info["lon"], "lat": info["lat"],
                "raster_x": x, "raster_y": y, "elevation_raster_units": float(val),
                "elevation_units": "U.S. survey feet (EPSG:6360)",
                "elevation_meters_derived": float(val) * (1200.0 / 3937.0),
            }
        return {
            "crs": str(src.crs), "width": src.width, "height": src.height,
            "resolution": [abs(v) for v in src.res],
            "bounds": dict(left=src.bounds.left, bottom=src.bounds.bottom,
                           right=src.bounds.right, top=src.bounds.top),
            "count": src.count, "nodata": src.nodata,
            "raster_samples": sample_out,
        }


def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    raw = download()
    # Validate isolated bytes before replacing an existing previously archived copy.
    with NamedTemporaryFile(suffix=".tif", dir=DEST.parent, delete=False) as f:
        f.write(raw)
        tmp = Path(f.name)
    try:
        details = validate(tmp)
        if DEST.exists() and DEST.read_bytes() != raw:
            raise ValueError("Existing NOAA source differs; preserve both versions before replacing")
        if not DEST.exists():
            os.replace(tmp, DEST)
        else:
            tmp.unlink(missing_ok=True)
    finally:
        tmp.unlink(missing_ok=True)

    manifest = {
        "status": "ORIGINAL_BINARY_DOWNLOADED_AND_GEOMETRY_VALIDATED",
        "agency": "NOAA Office for Coastal Management / Northwest Florida Water Management District",
        "dataset": "2017 NWFWMD Lidar DEM: Escambia Santa Rosa",
        "dataset_id": "NOAA 8683",
        "source_url": SOURCE,
        "source_catalog": SOURCE_CATALOG,
        "dataset_metadata": METADATA,
        "source_acquisition_window": "2017-03-31 to 2017-04-08",
        "source_vertical_reference": "NAVD88 (GEOID12B), U.S. survey feet, as stated in NOAA InPort 55909 process step 12 (vertical EPSG:6360)",
        "horizontal_grid_units": "meters, 1 meter cell size, EPSG:6345",
        "vertical_elevation_units": "U.S. survey feet; derived meters use factor 1200/3937",
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "local_original": str(DEST),
        "validation": details,
        "limitations": [
            "2017 historical hydro-flattened 1 m DEM, not current 2026 surveyed conditions.",
            "Tax parcel display coordinates, not survey control points.",
            "Raster-derived elevations cannot establish pipe-invert levels or compliance.",
            "USGS EPQS responses report rasterId 19247 and a 2017-05-05 acquisition date; equivalence of sources is unverified.",
            "Dataset project-wide vertical accuracy cannot substitute for lot-specific field survey.",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "bytes": len(raw),
                      "sha256": manifest["sha256"], "samples": details["raster_samples"]},
                     indent=2))


if __name__ == "__main__":
    main()
