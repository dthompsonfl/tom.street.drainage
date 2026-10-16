#!/usr/bin/env python3
"""Archive official 2021 USDA NAIP orthophoto export at Tom Street.

Provenance: USDA Farm Production and Conservation, federal GeoPlatform NAIP
2021 CONUS ImageServer. This is a WGS84 image-service JPEG export (derivative),
not original JP2 camera/ortho source. Source timestamp/footprint metadata is
queried separately and preserved; never treat the label 2021 as precise date.
"""
from __future__ import annotations
import hashlib
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from PIL import Image, ImageStat

ROOT = Path("11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/USDA_NAIP_2021")
SERVICE = "https://imagery.geoplatform.gov/iipp/rest/services/NAIP/NAIP2021_CONUS/ImageServer"
BBOX = [-86.8162, 30.4144, -86.8134, 30.4160]
SIZE = [1800, 1028]
MAX_BYTES = 10_000_000
OUTPUT = ROOT / "Tom_Street_USDA_NAIP_2021_WGS84_Export.jpg"
MANIFEST = ROOT / "ACQUISITION_MANIFEST.json"

def fetch(url):
    with urlopen(Request(url, headers={"User-Agent": "TomStreetPublicEvidence/1.0"}),
                 timeout=130) as r:
        if r.status != 200:
            raise RuntimeError(f"HTTP {r.status}")
        raw = r.read(MAX_BYTES + 1)
        mime = r.headers.get("Content-Type", "")
    if len(raw) > MAX_BYTES:
        raise RuntimeError("Response exceeds bounded image limit")
    return raw, mime

def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    args = {"bbox": ",".join(str(x) for x in BBOX), "bboxSR": 4326,
            "imageSR": 4326, "size": ",".join(str(x) for x in SIZE),
            "format": "jpg", "compressionQuality": 94, "f": "image"}
    url = SERVICE + "/exportImage?" + urlencode(args)
    query_args = {
        "geometry": json.dumps({"x":-86.81466,"y":30.41519,"spatialReference":{"wkid":4326}}),
        "geometryType": "esriGeometryPoint", "spatialRel": "esriSpatialRelIntersects",
        "outFields": "objectid,name,year,state,metadata,resolution",
        "returnGeometry":"false", "f":"pjson"
    }
    qurl = SERVICE + "/query?" + urlencode(query_args)
    report = {"retrieved_utc": datetime.now(timezone.utc).isoformat(),
              "dataset": "USDA NAIP 2021 CONUS",
              "agency": "USDA FPAC via US Forest Service and Federal GeoPlatform IIPP",
              "service": SERVICE, "source_export_url": url,
              "source_catalog_query_url": qurl, "bbox_wgs84": BBOX,
              "dimensions": SIZE, "image_status": "NOT_ACQUIRED",
              "catalog_status": "NOT_ACQUIRED"}
    try:
        raw, mimetype = fetch(qurl)
        catalog = json.loads(raw)
        if catalog.get("error"):
            raise ValueError(f"ArcGIS ImageServer returned {catalog['error']}")
        features = catalog.get("features")
        if not isinstance(features, list):
            raise ValueError("No ArcGIS catalog features array")
        report.update({"catalog_status": "POINT_INTERSECTION_RETRIEVED",
                       "catalog_intersecting_features": features})
    except Exception as exc:
        report["catalog_failure"] = f"{type(exc).__name__}: {exc}"[:300]
    try:
        raw, mimetype = fetch(url)
        if not (len(raw)>15000 and raw[:3]==b"\xff\xd8\xff"):
            raise ValueError("No authentic JPEG response returned")
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
            if image.format != "JPEG" or image.size != tuple(SIZE):
                raise ValueError(f"Unexpected JPEG format or dimensions {image.format}, {image.size}")
            gray = image.convert("L")
            w,h=gray.size
            sd=ImageStat.Stat(gray.crop((w//4,h//4,3*w//4,3*h//4))).stddev[0]
            if sd < 7:
                raise ValueError(f"Image center likely blank or no coverage; SD {sd}")
        checksum = hashlib.sha256(raw).hexdigest()
        if OUTPUT.exists():
            if hashlib.sha256(OUTPUT.read_bytes()).hexdigest() != checksum:
                raise ValueError("Archived original export differs from new bytes; do not overwrite")
        else:
            tmp = OUTPUT.with_suffix(".tmp")
            try:
                tmp.write_bytes(raw)
                os.replace(tmp, OUTPUT)
            finally:
                tmp.unlink(missing_ok=True)
        report.update({"image_status": "PUBLIC_NAIP_2021_EXPORT_BYTES_SAVED_AND_VALIDATED",
                       "source_content_type": mimetype, "path":str(OUTPUT), "bytes":len(raw),
                       "sha256":checksum, "center_pixel_intensity_sd":round(sd,3)})
    except Exception as exc:
        report["image_failure"]=f"{type(exc).__name__}: {exc}"[:300]
    report["limitations"]=[
        "2021 refers to dataset acquisition year; individual tile date must be verified from official catalog metadata.",
        "Service-rendered JPEG crop, not underlying original JP2 orthophoto tile.",
        "This shows pre-2026 visible terrain appearance, not height measurements or drain capacity.",
        "Image service mosaics and geographic resampling may affect direct comparisons across years.",
        "No private resident photographs are saved in this public archive.",
    ]
    MANIFEST.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("NAIP2021",report["image_status"],report["catalog_status"],
          report.get("image_failure"),report.get("catalog_failure"))
    if report["image_status"] != "PUBLIC_NAIP_2021_EXPORT_BYTES_SAVED_AND_VALIDATED":
        raise RuntimeError(report.get("image_failure","NAIP2021 source could not be acquired"))

if __name__ == "__main__":
    main()
