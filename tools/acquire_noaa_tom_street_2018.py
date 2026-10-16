#!/usr/bin/env python3
"""Preserve the original 2018 NOAA/USGS Florida Panhandle DEM tile for Tom Street.

Use the original NOAA geospatial tile index to choose the tile that intersects
all 3 parcel-interior sample points. Keep index ZIP and selected GeoTIFF
unaltered and checksum both. Never download the region-wide 44GB collection.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import fiona
import rasterio
from pyproj import Transformer
from shapely.geometry import Point, shape
from rasterio.warp import transform

DEST = Path("11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/ORIGINAL_NOAA_2018")
INDEX_URL = ("https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/dem/"
             "FL_Panhandle_DEM_2018_8942/tileindex_FL_Panhandle_DEM_2018.zip")
BASE_URL = "https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/dem/FL_Panhandle_DEM_2018_8942/"
DATASET = "https://www.fisheries.noaa.gov/inport/item/58332"
POINTS = {
    "2264_Tom_St": (-86.81466, 30.41519),
    "2265_Tom_St": (-86.81521, 30.41515),
    "2268_Tom_St": (-86.81466, 30.41534),
}
MAX = 75_000_000


def download(url: str, destination: Path, max_bytes=MAX):
    with urlopen(Request(url, headers={"User-Agent": "TomStreetEvidence/1.0"}), timeout=160) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Unexpected response status {resp.status}")
        if resp.headers.get("Content-Length") and int(resp.headers["Content-Length"]) > max_bytes:
            raise RuntimeError("Source exceeds bounded acquisition size")
        with tempfile.NamedTemporaryFile(dir=DEST, delete=False) as f:
            temp = Path(f.name)
            sha = hashlib.sha256()
            size = 0
            while part := resp.read(1024 * 1024):
                size += len(part)
                if size > max_bytes:
                    temp.unlink(missing_ok=True)
                    raise RuntimeError("Source exceeded bounded acquisition size")
                sha.update(part)
                f.write(part)
    if destination.exists():
        if hashlib.sha256(destination.read_bytes()).hexdigest() != sha.hexdigest():
            temp.unlink(missing_ok=True)
            raise RuntimeError("Source bytes changed; immutable prior copy retained")
        temp.unlink(missing_ok=True)
    else:
        os.replace(temp, destination)
    return {"path": str(destination), "bytes": size, "sha256": sha.hexdigest(), "url": url}


def select_tiles(index: Path):
    with tempfile.TemporaryDirectory(prefix="noaa_2018_index_") as tmp:
        folder = Path(tmp)
        with zipfile.ZipFile(index) as z:
            if z.testzip():
                raise ValueError("NOAA index ZIP CRC verification failed")
            items = z.infolist()
            if len(items) > 30 or sum(i.file_size for i in items) > 120_000_000:
                raise ValueError("Unexpected ZIP contents")
            for item in items:
                if item.is_dir():
                    continue
                suffix = Path(item.filename).suffix.lower()
                if suffix not in (".shp", ".shx", ".dbf", ".prj", ".cpg"):
                    continue
                if "/" in item.filename.strip("/") and len(Path(item.filename).parts) > 3:
                    raise ValueError("Unexpected nested path in tile-index ZIP")
                target = folder / Path(item.filename).name
                with target.open("wb") as out:
                    out.write(z.read(item))
        files = list(folder.glob("*.shp"))
        if len(files) != 1:
            raise ValueError(f"Expected one shapefile layer, got {len(files)}")
        with fiona.open(files[0]) as src:
            if not src.crs:
                raise ValueError("Index lacks CRS")
            xy = {}
            transf = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
            for key, (lon, lat) in POINTS.items():
                x, y = transf.transform(lon, lat)
                xy[key] = Point(x, y)
            sites = {key: [] for key in POINTS}
            n = 0
            for feature in src:
                n += 1
                if not feature.geometry:
                    continue
                geom = shape(feature.geometry)
                if geom.is_empty:
                    continue
                record = {
                    "feature_id": str(feature.id),
                    "properties": dict(feature.properties),
                    "bounds": list(geom.bounds),
                }
                for key, point in xy.items():
                    if geom.intersects(point):
                        sites[key].append(record)
            return str(src.crs), n, sites


def choose_url(sites):
    url_counts = {}
    for items in sites.values():
        for item in items:
            attrs = item["properties"]
            value = next((v for k, v in attrs.items() if k.lower() in ("url", "download", "downloadurl")), None)
            if isinstance(value, str) and value.startswith(BASE_URL):
                url_counts[value] = url_counts.get(value, 0) + 1
    choices = [url for url, count in url_counts.items() if count >= len(POINTS)]
    if len(choices) != 1:
        raise ValueError(f"Could not uniquely identify common Tom Street source tile: {url_counts}")
    return choices[0]


def inspect_raster(path):
    with rasterio.open(path) as src:
        if not src.crs or src.count != 1:
            raise ValueError("Missing CRS or not one-band bare-earth DEM")
        values = {}
        for name, (lon, lat) in POINTS.items():
            x, y = transform("EPSG:4326", src.crs, [lon], [lat])
            if not (src.bounds.left <= x[0] <= src.bounds.right
                    and src.bounds.bottom <= y[0] <= src.bounds.top):
                raise ValueError(f"Raster extent does not cover {name}")
            v = next(src.sample([(x[0], y[0])], indexes=1, masked=True))[0]
            if bool(getattr(v, "mask", False)) or not math.isfinite(float(v)):
                raise ValueError(f"No valid raster surface at {name}")
            if not -30 <= float(v) <= 200:
                raise ValueError(f"Invalid bare-earth sample at {name}")
            values[name] = {
                "lon": lon, "lat": lat,
                "raster_x": x[0], "raster_y": y[0],
                "source_elevation": float(v),
            }
        return {
            "crs": str(src.crs), "resolution": list(src.res),
            "width": src.width, "height": src.height,
            "bounds": {"left": src.bounds.left, "bottom": src.bounds.bottom,
                       "right": src.bounds.right, "top": src.bounds.top},
            "nodata": src.nodata, "sample_values": values,
            "source_vertical_reference": "NAVD88 GEOID12B, meters as reported by NOAA InPort 58332; verify per-tile metadata for engineering use",
        }


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    idx = download(INDEX_URL, DEST / "tileindex_FL_Panhandle_DEM_2018.zip", max_bytes=25_000_000)
    crs, features, sites = select_tiles(Path(idx["path"]))
    manifest = {
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "source_agency": "NOAA / USGS / NWFWMD", "dataset": DATASET,
        "source_window": "2018-03-31 to 2018-05-10",
        "index": idx, "index_crs": crs,
        "index_feature_count": features, "parcel_point_matches": sites,
        "status": "INDEX_OBTAINED_SOURCE_TILE_PENDING",
    }
    try:
        tile_url = choose_url(sites)
        base = Path(urlparse(tile_url).path).name
        if not base.endswith((".tif", ".tiff")):
            raise ValueError(f"Unexpected indexed source filename {base}")
        tile = download(tile_url, DEST / base)
        with Path(tile["path"]).open("rb") as fh:
            if fh.read(4) not in (b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+"):
                raise ValueError("Not a TIFF")
        validation = inspect_raster(Path(tile["path"]))
        manifest.update({
            "source_tile": tile, "raster_validation": validation,
            "status": "ORIGINAL_2018_DEM_TILE_AND_INDEX_PRESERVED_AND_CHECKED",
        })
    except Exception as exc:
        manifest.update({
            "status": "INDEX_PRESERVED_TILE_FAILED",
            "error": f"{type(exc).__name__}: {exc}"[:400],
        })
    manifest["limitations"] = [
        "Each timestamp/year identifies a regional acquisition window rather than the exact site flight date.",
        "Original 2018 DEM has distinct horizontal projection from 2017 NOAA and must be coregistered before comparing heights.",
        "Only indexed tiles covering the 3 site sample points are acquired, not the whole regional 44GB source.",
        "Grid elevations are 2018 terrain, not 2026 grading or a certified cadastral survey.",
        "Hydro-flattened DEM cannot measure buried culvert inverts or impervious-construction outfall capacity.",
    ]
    (DEST / "ACQUISITION_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("NOAA 2018:", manifest["status"], manifest.get("source_tile", {}).get("path", ""))
    if manifest["status"] != "ORIGINAL_2018_DEM_TILE_AND_INDEX_PRESERVED_AND_CHECKED":
        raise RuntimeError(manifest.get("error", "2018 source not fully acquired"))


if __name__ == "__main__":
    main()
