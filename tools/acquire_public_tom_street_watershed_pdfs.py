#!/usr/bin/env python3
"""Preserve published Santa Rosa County watershed PDF records.

These are regional county publications, NOT reviewed/approved grading plans for
either Tom Street building permit and NOT certification of application to the
three target parcels. HTTP responses and original PDF bytes are preserved.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import Request, urlopen

from pypdf import PdfReader

BASE = Path("11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/WATERSHED_DOCUMENTS")
REPORTS = {
    "SANTA_ROSA_WATERSHED_MASTER_PLAN_PUBLIC_DRAFT": {
        "url": "https://www.santarosa.fl.gov/DocumentCenter/View/9834/Santa_Rosa_County_Watershed_Master_Plan_Final_Draft",
        "filename": "Santa_Rosa_County_Watershed_Master_Plan_Public_Draft.pdf",
        "note": "Public draft document; its publication and county adoption/final status must be distinguished.",
    },
    "EAST_NAVARRE_WATERSHED_STUDY_AREA_MAP": {
        "url": "https://www.santarosa.fl.gov/DocumentCenter/View/8573/Overall-Study-Area-East-Navarre-Watershed",
        "filename": "East_Navarre_Watershed_Study_Area_Map.pdf",
        "note": "Official study-area map; not the hydrologic/hydraulic model or final report.",
    },
}
MAX_BYTES = 55_000_000


def fetch_pdf(url, tmpdir):
    request = Request(url, headers={"User-Agent": "TomStreetPublicEvidence/1.0"})
    with urlopen(request, timeout=120) as response:
        if response.status != 200:
            raise ValueError(f"Unexpected source HTTP status {response.status}")
        if (s := response.headers.get("Content-Length")) and int(s) > MAX_BYTES:
            raise ValueError("Published PDF exceeds conservative 55MB acquisition limit")
        with NamedTemporaryFile(dir=tmpdir, suffix=".pdf", delete=False) as stream:
            path = Path(stream.name)
            h = hashlib.sha256()
            size = 0
            try:
                while True:
                    data = response.read(1024 * 1024)
                    if not data:
                        break
                    size += len(data)
                    if size > MAX_BYTES:
                        raise ValueError("Published PDF exceeds conservative 55MB acquisition limit")
                    h.update(data)
                    stream.write(data)
            except Exception:
                path.unlink(missing_ok=True)
                raise
    try:
        with path.open("rb") as f:
            assert f.read(5) == b"%PDF-"
        doc = PdfReader(str(path), strict=False)
        if doc.is_encrypted:
            raise ValueError("Published PDF encrypted; not interpreted")
        pages = len(doc.pages)
        if pages < 1 or pages > 3000:
            raise ValueError(f"Unexpected PDF pages {pages}")
        return path, h.hexdigest(), size, pages
    except Exception:
        path.unlink(missing_ok=True)
        raise


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    entries = []
    for name, spec in REPORTS.items():
        record = { "document_id": name, "original_url": spec["url"],
                   "original_status": "NOT_ACQUIRED", "notes": spec["note"] }
        try:
            tmp, digest, size, pages = fetch_pdf(spec["url"], BASE)
            final = BASE / spec["filename"]
            try:
                if final.exists() and hashlib.sha256(final.read_bytes()).hexdigest() != digest:
                    raise ValueError("Published source changed; prior preserved copy must not be replaced")
                if final.exists():
                    tmp.unlink(missing_ok=True)
                else:
                    os.replace(tmp, final)
            finally:
                tmp.unlink(missing_ok=True)
            record.update({
                "original_status": "ORIGINAL_COUNTY_PDF_CAPTURED_AND_STRUCTURALLY_VERIFIED",
                "path": str(final), "sha256": digest, "bytes": size, "pages": pages,
            })
        except Exception as e:
            record.update({
                "original_status": "NOT_OBTAINED",
                "error": f"{type(e).__name__}: {e}"[:250],
            })
        entries.append(record)
        print(f"{name}: {record['original_status']} {record.get('pages', '')}")
    report = {
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "custodian": "Santa Rosa County Florida",
        "acquisition_status": (
            "ALL_PUBLIC_PDFS_SAVED"
            if all(e["original_status"].startswith("ORIGINAL_") for e in entries)
            else "PARTIAL_OR_NONE_PUBLIC_PDF_ACQUISITION"
        ),
        "documents": entries,
        "limitations": [
            "Study-area mapping cannot establish site-specific hydrologic model inclusion without geospatial verification.",
            "Watershed master plan may be a draft; adopted status is not established by file title.",
            "Regional studies are not an approved lot-grading plan or pipe as-built.",
            "Document structural validation does not prove the contents were fully reviewed.",
        ],
    }
    (BASE / "ACQUISITION_MANIFEST.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    if not any(e["original_status"].startswith("ORIGINAL_") for e in entries):
        raise RuntimeError("No requested County watershed PDF obtained")


if __name__ == "__main__":
    main()
