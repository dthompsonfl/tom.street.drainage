#!/usr/bin/env python3
"""Preserve public County ArcGIS exports of historical Tom Street imagery.

These images are *derived map exports*, not original aerial negatives/orthos or
property surveys. The source servers and export parameters are preserved for
replay, and any missing year is explicitly represented in the manifest.
"""
from __future__ import annotations

import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from PIL import Image

DEST = Path(
    "11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/"
    "COUNTY_HISTORICAL_AERIAL_EXPORTS"
)
ROOT = "https://cloud.santarosa.fl.gov/arcgis/rest/services"
SOURCES = {
    2001: "GoSpatial/Aerials2001",
    2005: "GoSpatial/Aerials2005",
    2006: "GoSpatial/Aerials2006",
    2010: "GoSpatial/Aerials2010",
    2012: "GoSpatial/Aerials2012",
    2016: "GoSpatial/Aerials2016",
    2019: "santarosa/Aerials2019",
    2022: "santarosa/Aerials2022",
}
BBOX = [-86.8162, 30.4144, -86.8134, 30.4160]
PIXELS = [1600, 1000]
PARAMS = {
    "bbox": ",".join(str(x) for x in BBOX),
    "bboxSR": "4326", "imageSR": "4326",
    "size": ",".join(str(x) for x in PIXELS),
    "format": "jpg",
    "dpi": "96", "f": "image",
    "transparent": "false",
}
SOURCE_DISCLAIMER = "https://www.santarosa.fl.gov/470/Mapping-GIS"


def retrieve(url):
    with urlopen(
        Request(url, headers={"User-Agent": "TomStreetPublicEvidence/1.0"}),
        timeout=120,
    ) as response:
        if response.status != 200:
            raise ValueError(f"Non-200 HTTP response: {response.status}")
        content_type = response.headers.get("Content-Type", "")
        raw = response.read(8_000_001)
    if not 15_000 <= len(raw) <= 8_000_000:
        raise ValueError("Response too small or too large for expected image")
    if not raw.startswith(b"\xff\xd8\xff"):
        raise ValueError("Response is not a JPEG; do not archive error as imagery")
    with Image.open(io.BytesIO(raw)) as img:
        img.load()
        if img.size != tuple(PIXELS):
            raise ValueError(f"Unexpected image size: {img.size}")
        if img.convert("L").entropy() < 1.0:
            raise ValueError("Image is almost blank; data coverage is not proven")
    return raw, content_type


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    entries = []
    succeeded = 0
    for year, service in SOURCES.items():
        service_url = f"{ROOT}/{service}/MapServer"
        url = f"{service_url}/export?{urlencode(PARAMS)}"
        filename = f"santa_rosa_{year}_tom_street_export.jpg"
        path = DEST / filename
        record = {
            "service_year_label": year,
            "map_service": service_url,
            "request_url": url,
            "status": "NOT_DOWNLOADED",
        }
        try:
            raw, content_type = retrieve(url)
            if path.exists() and path.read_bytes() != raw:
                raise ValueError("An earlier captured image has different bytes; preserve both")
            if not path.exists():
                path.write_bytes(raw)
            record.update({
                "status": "COUNTY_IMAGE_EXPORT_SAVED_AND_VALIDATED",
                "content_type": content_type,
                "local_file": str(path),
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "width": PIXELS[0], "height": PIXELS[1],
            })
            succeeded += 1
        except Exception as exc:
            record.update({
                "status": "NOT_ACQUIRED",
                "failure_type": type(exc).__name__,
                "failure_details": str(exc)[:250],
            })
        entries.append(record)
        print(f"{year}: {record['status']}")
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": (
            "EIGHT_COUNTY_DERIVED_IMAGE_EXPORTS_SAVED"
            if succeeded == len(SOURCES)
            else "PARTIAL_HISTORICAL_IMAGERY_ACQUISITION"
        ),
        "success_count": succeeded,
        "attempt_count": len(SOURCES),
        "source_agency": "Santa Rosa County Geographic Information Systems",
        "source_disclaimer": SOURCE_DISCLAIMER,
        "bounding_box_wgs84_west_south_east_north": BBOX,
        "image_size_pixels": PIXELS,
        "entries": entries,
        "limitations": [
            "Derived county MapServer JPEG exports, not original survey-grade aerial imagery or originals from acquisition.",
            "Service year labels do not establish exact aerial flight date of every pixel; underlying orthophoto metadata is required.",
            "Map export bbox uses WGS84 and fixed pixel size, and individual years may have different ground sampling distance and georegistration.",
            "Raster exports do not prove a land elevation or lawful runoff drainage path.",
            "Imagery from 2022 or earlier does not establish what grading exists in 2026.",
            "County GIS metadata/distribution liability and source URL must accompany redistributed extracts.",
            "No resident private photographs or metadata are included.",
        ],
    }
    (DEST / "ACQUISITION_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": manifest["status"],
                      "saved": succeeded, "requested": len(SOURCES)}, indent=2))
    if not succeeded:
        raise RuntimeError("No images acquired: inspect source server responses")


if __name__ == "__main__":
    main()
