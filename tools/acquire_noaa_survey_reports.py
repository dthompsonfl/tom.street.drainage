#!/usr/bin/env python3
"""Preserve first-party historical LiDAR survey QA and acquisition reports.

These describe 2017/2018 regional survey methods and vertical accuracy. They
do not contain signed 2026 site grading, lot survey, or drainage designs.
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

ROOT = Path(__file__).resolve().parents[1] / ("11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/NOAA_SURVEY_REPORTS")
BASE17 = "https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/8680/supplemental/"
BASE18 = "https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/8945/supplemental/"
REPORTS = [
    ("2017_NWFWMD_Project_Report", BASE17 + "FL_Escambia_Santa_Rosa_NWFWMD_Lidar_Project_Report_20180301.pdf", "2017 NWFWMD Escambia/Santa Rosa project report"),
    ("2018_Panhandle_Acquisition_Report", BASE18 + "3143_NWFWMD_FL_PanHandle_Aquisition_Report.pdf", "2018 project flight acquisition report"),
    ("2018_Panhandle_Control_Report", BASE18 + "FL_PanHandle_Aquisition_Control_Report.pdf", "2018 acquisition/control report"),
    ("2018_Panhandle_Checkpoint_Survey_Report", BASE18 + "FL_PanHandle_Checkpoints_Survey_Report.pdf", "2018 independent survey checkpoint report"),
    ("2018_Panhandle_Project_Report", BASE18 + "FL_Panhandle_Lidar_Project_Report_20190601.pdf", "2018 overall project report"),
]
MAX_SIZE = 35_000_000


def fetch(url, dest):
    with urlopen(Request(url, headers={"User-Agent": "TomStreetPublicEvidence/1.0"}), timeout=140) as res:
        if res.status != 200:
            raise ValueError(f"HTTP {res.status}")
        if res.headers.get("Content-Length") and int(res.headers["Content-Length"]) > MAX_SIZE:
            raise ValueError("Original PDF exceeds archival cap; request separately")
        with NamedTemporaryFile(dir=ROOT, suffix=".pdf", delete=False) as stream:
            tmp = Path(stream.name)
            digest = hashlib.sha256()
            size = 0
            try:
                while blob := res.read(1_048_576):
                    size += len(blob)
                    if size > MAX_SIZE:
                        raise ValueError("Source PDF exceeds 35MB, not saved as truncated")
                    digest.update(blob)
                    stream.write(blob)
            except Exception:
                tmp.unlink(missing_ok=True)
                raise
    try:
        with tmp.open("rb") as stream:
            if stream.read(5) != b"%PDF-":
                raise ValueError("Source is not a PDF")
        pages = len(PdfReader(tmp, strict=False).pages)
        if pages < 1 or pages > 2000:
            raise ValueError(f"Unexpected document page count {pages}")
        old = dest.exists()
        if old and hashlib.sha256(dest.read_bytes()).hexdigest() != digest.hexdigest():
            raise ValueError("Already-archived official PDF differs: preserve both versions manually")
        if not old:
            os.replace(tmp, dest)
        return {"file": str(dest), "sha256": digest.hexdigest(), "bytes": size, "pages": pages}
    finally:
        tmp.unlink(missing_ok=True)


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    records = []
    for key, url, title in REPORTS:
        item = {"id": key, "title": title, "source_url": url, "status": "NOT_ACQUIRED"}
        try:
            saved = fetch(url, ROOT / f"{key}.pdf")
            item.update({"status": "ORIGINAL_NOAA_PDF_SAVED_STRUCTURALLY_VALIDATED", **saved})
        except Exception as exc:
            item["reason"] = f"{type(exc).__name__}: {exc}"[:300]
        records.append(item)
        print(key, item["status"], item.get("pages"), item.get("reason"))
    manifest = {
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "agency": "NOAA Office for Coastal Management / NWFWMD / USGS",
        "source_metadata": [
            "https://www.fisheries.noaa.gov/inport/item/55909",
            "https://www.fisheries.noaa.gov/inport/item/58332",
        ],
        "retrieved_count": sum("ORIGINAL" in x["status"] for x in records),
        "requested_count": len(records),
        "records": records,
        "limitations": [
            "Regional LiDAR QA reports, not surveyed elevations for individual Tom Street lot corners.",
            "Preserved PDF bytes and page count do not equal comprehensive technical audit of each report.",
            "2018 coverage of the target sites must be established by 2018 index intersections; broader dataset bounds are not proof.",
            "Vertical datums/units/geoid models vary across products and need engineer/surveyor reconciliation.",
        ],
    }
    (ROOT / "ACQUISITION_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if not manifest["retrieved_count"]:
        raise RuntimeError("No first-party LiDAR reports acquired")


if __name__ == "__main__":
    main()
