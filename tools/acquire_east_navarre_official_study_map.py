#!/usr/bin/env python3
"""Preserve official County East Navarre watershed study-area map image.

The County's DocumentCenter /8573 page serves an IMAGE, not a PDF.
This is a public project outline and does not prove inclusion of Tom Street
parcels in any drainage sub-basin or identify proposed works.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import Request, urlopen

from PIL import Image

URL = "https://www.santarosa.fl.gov/DocumentCenter/View/8573/Overall-Study-Area-East-Navarre-Watershed"
DEST = Path(__file__).resolve().parents[1] / (
    "11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/"
    "WATERSHED_DOCUMENTS/East_Navarre_Watershed_Study_Area_Official.jpg"
)
MANIFEST = DEST.with_suffix(".acquisition.json")


def main():
    with urlopen(Request(URL, headers={"User-Agent": "TomStreetPublicEvidence/1.0"}),
                 timeout=60) as response:
        if response.status != 200:
            raise ValueError(f"Source returned HTTP {response.status}")
        content_type = response.headers.get("Content-Type", "")
        data = response.read(10_000_001)
    if len(data) < 5000 or len(data) > 10_000_000:
        raise ValueError(f"Unexpected official map size: {len(data)}")
    with Image.open(io.BytesIO(data)) as im:
        im.load()
        if im.format != "JPEG":
            raise ValueError(f"Official map file is not expected JPEG: {im.format}")
        width, height = im.size
        if width < 500 or height < 300:
            raise ValueError("Unexpected low-resolution study map")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists() and hashlib.sha256(DEST.read_bytes()).hexdigest() != hashlib.sha256(data).hexdigest():
        raise ValueError("Previously preserved County map changed; do not overwrite")
    if not DEST.exists():
        with NamedTemporaryFile(dir=DEST.parent, delete=False) as f:
            f.write(data)
            tmp = Path(f.name)
        os.replace(tmp, DEST)
    result = {
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "status": "OFFICIAL_STUDY_AREA_IMAGE_PRESERVED",
        "source_url": URL,
        "source_agency": "Santa Rosa County / Baskerville-Donovan, Inc.",
        "source_content_type": content_type,
        "file": str(DEST),
        "image_format": "JPEG",
        "image_width": width,
        "image_height": height,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "limitations": [
            "This is the project's published overall study-area image, not a site-specific drainage plan.",
            "The study's formal geospatial boundary and its inclusion of all Tom Street parcels are not separately checked.",
            "The image does not supply hydrologic calculations, field measurements, or the final study report.",
            "The source is an image, not a PDF. Any previous failed PDF request is a type mismatch, not proof of missing image.",
        ],
    }
    MANIFEST.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"], width, height, len(data), result["sha256"])


if __name__ == "__main__":
    main()
