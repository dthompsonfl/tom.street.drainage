#!/usr/bin/env python3
"""Archive geographically relevant FDEP/FDOT historic aerial map exports.

ALL saved JPEGs are derived WGS84 exports from official Florida DEP ImageServer
services, not the original camera frame or ortho raster. Source year is a map
service LABEL; exact site capture date and image provenance need agency metadata.
An HTTP success alone is NOT enough: require valid, nonblank image bytes and
write checksums/source links. Failures remain explicit; do not fabricate images.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import io
import json
import math
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from PIL import Image, ImageStat

BASE = Path(__file__).resolve().parents[1] / ("11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/FLORIDA_DEP_HISTORICAL_AERIALS")
API = "https://ca.dep.state.fl.us/image/rest/services"
BBOX = [-86.8162, 30.4144, -86.8134, 30.4160]
SIZE = [1600, 920]
MAX_BYTES = 8_000_000
SERVICES = [
    ("1994_DOQQ", "MISC/DOQQ_1994"),
    ("1999_DOQQ", "MISC/DOQQ_1999"),
    ("2004_DOQQ", "MISC/DOQQ_2004"),
    ("2008_DOQQ", "MISC/DOQQ_2008"),
    ("2010_NAIP", "MISC/NAIP_Imagery_2010"),
    ("2004_FDOT", "FDOT_Yearly_Aerials/Aerial_Imagery_2004"),
    ("2007_FDOT", "FDOT_Yearly_Aerials/Aerial_Imagery_2007"),
    ("2008_FDOT", "FDOT_Yearly_Aerials/Aerial_Imagery_2008"),
    ("2009_FDOT", "FDOT_Yearly_Aerials/Aerial_Imagery_2009"),
    ("2010_FDOT", "FDOT_Yearly_Aerials/Aerial_Imagery_2010"),
    ("2011_FDOT", "FDOT_Yearly_Aerials/Aerial_Imagery_2011"),
    ("2012_FDOT", "FDOT_Yearly_Aerials/Aerial_Imagery_2012"),
    ("2013_FDOT", "FDOT_Yearly_Aerials/Aerial_Imagery_2013"),
    ("2015_FDOT", "FDOT_Yearly_Aerials/Aerial_Imagery_2015"),
    ("2016_FDOT", "FDOT_Yearly_Aerials/Aerial_Imagery_2016"),
    ("2017_FDOT", "FDOT_Yearly_Aerials/Aerial_Imagery_2017"),
    ("2018_FDOT", "FDOT_Yearly_Aerials/Aerial_Imagery_2018"),
    ("2019_FDOT", "FDOT_Yearly_Aerials/Aerial_Imagery_2019"),
    ("2020_FDOT", "FDOT_Yearly_Aerials/Aerial_Imagery_2020"),
    ("2021_FDOT", "FDOT_Yearly_Aerials/Aerial_Imagery_2021"),
]


def get(url: str, maximum: int) -> tuple[bytes, str]:
    request = Request(url, headers={"User-Agent": "TomStreetPublicEvidence/1.0"})
    with urlopen(request, timeout=95) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        mime = response.headers.get("Content-Type", "")
        raw = response.read(maximum + 1)
    if len(raw) > maximum:
        raise ValueError(f"Content exceeds {maximum}-byte cap")
    return raw, mime


def validate_picture(raw: bytes) -> dict:
    if not (len(raw) >= 10_000 and raw.startswith(b"\xff\xd8\xff")):
        raise ValueError("Unexpected image format, error document, or tiny response")
    with Image.open(io.BytesIO(raw)) as image:
        image.load()
        if image.format != "JPEG" or image.size != tuple(SIZE):
            raise ValueError(f"Incorrect JPEG format/dimensions: {image.format} {image.size}")
        rgb = image.convert("RGB")
        w, h = rgb.size
        central = rgb.crop((w // 4, h // 4, 3 * w // 4, 3 * h // 4))
        stats = ImageStat.Stat(central.convert("L"))
        variability = float(stats.stddev[0])
        if not math.isfinite(variability) or variability < 5:
            raise ValueError(f"Near-uniform center suggests no mosaic coverage (stddev {variability:.2f})")
        # Mark pixel variability as a screening indicator, NOT independent proof
        # that correct-year source imagery was used or building features visible.
        return {"width": w, "height": h, "center_luminance_sd": round(variability, 3)}


def attempt(spec: tuple[str, str]) -> dict:
    name, service = spec
    service_url = f"{API}/{service}/ImageServer"
    args = {
        "bbox": ",".join(map(str, BBOX)),
        "bboxSR": "4326", "imageSR": "4326",
        "size": ",".join(map(str, SIZE)),
        "format": "jpg", "f": "image", "compressionQuality": "92",
    }
    url = f"{service_url}/exportImage?{urlencode(args)}"
    filename = f"{name}_Tom_Street_export.jpg"
    path = BASE / filename
    rec = {
        "service_label": name, "official_service": service_url,
        "export_url": url, "status": "NOT_ACQUIRED", "retrieved_utc": datetime.now(timezone.utc).isoformat(),
    }
    try:
        raw, mime = get(url, MAX_BYTES)
        verification = validate_picture(raw)
        digest = hashlib.sha256(raw).hexdigest()
        if path.exists():
            oldhash = hashlib.sha256(path.read_bytes()).hexdigest()
            if oldhash != digest:
                raise ValueError("Existing archived bytes changed: preserve old copy; no silent overwrite")
        else:
            temp = path.with_suffix(".download")
            try:
                temp.write_bytes(raw)
                os.replace(temp, path)
            finally:
                temp.unlink(missing_ok=True)
        rec.update({
            "status": "PUBLIC_IMAGE_EXPORT_BYTES_VALIDATED",
            "source_content_type": mime,
            "file": str(path), "bytes": len(raw), "sha256": digest,
            "validation": verification,
            "worldfile_geometry": {
                "pixel_width_degrees": (BBOX[2] - BBOX[0]) / SIZE[0],
                "pixel_height_degrees": -(BBOX[3] - BBOX[1]) / SIZE[1],
                "top_left_pixel_center_lon": BBOX[0] + (BBOX[2] - BBOX[0]) / SIZE[0] / 2,
                "top_left_pixel_center_lat": BBOX[3] - (BBOX[3] - BBOX[1]) / SIZE[1] / 2,
                "crs": "EPSG:4326",
            },
        })
    except Exception as exc:
        rec.update({
            "status": "NOT_ACQUIRED",
            "failure": f"{type(exc).__name__}: {exc}"[:350],
        })
    return rec


def main() -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(attempt, SERVICES))
    # Public capture must be monotonic. A service failure cannot imply that an
    # earlier successful local capture should be deleted or rewritten.
    report = {
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "source_agency": "Florida Department of Environmental Protection, Florida DOT, USGS/USDA for labelled subcollections",
        "source_catalogs": [
            "https://ca.dep.state.fl.us/image/rest/services/MISC",
            "https://ca.dep.state.fl.us/image/rest/services/FDOT_Yearly_Aerials",
        ],
        "requested_count": len(SERVICES),
        "downloaded_validated_count": sum(r["status"] == "PUBLIC_IMAGE_EXPORT_BYTES_VALIDATED" for r in records),
        "bbox_wgs84": BBOX, "image_dimensions_pixels": SIZE,
        "images": records,
        "limitations": [
            "These are image exports from an official raster mosaic, not full unmodified aerial survey source files. Original camera/ortho files remain to be obtained.",
            "Service name/year does NOT verify photo acquisition date at the Tom Street pixel; request source mosaic catalog item metadata and flight history.",
            "Geographic coverage tested by pixel variance only; metadata must confirm actual mosaic imagery intersects Tom Street, particularly older years.",
            "Images contain variable spatial resolution; overlaid comparisons require registration checks before measuring footprint changes.",
            "The image depicts visible surfaces; it does not directly measure elevation, drainage capacity, fill, infiltration or physical property boundaries.",
            "No resident-supplied private photographs are stored here. They require permission and a separate restricted evidence vault.",
            "Failures and partial coverage do not establish nonexistence of original imagery at the issuing government custodian.",
        ],
    }
    (BASE / "ACQUISITION_MANIFEST.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    for r in records:
        print(r["service_label"], r["status"], r.get("bytes", "-"),
              r.get("failure", ""))
    print("VALIDATED:", report["downloaded_validated_count"], "of", len(SERVICES))
    # Do not fail a whole evidence ledger if a particular public year is offline:
    # zero acquisitions is an operational failure, still tracked in manifest.
    if report["downloaded_validated_count"] == 0:
        raise RuntimeError("No nonblank public historical aerial exports available")


if __name__ == "__main__":
    main()
