#!/usr/bin/env python3
"""Verify acquired Tom Street historical evidence against its recorded checksums.

Writes one bounded audit report, never changes an evidence source. Status PASS
means checked ARCHIVED BYTES match published capture-manifest claims, NOT that
the archive contains every public record, that government data are conclusive,
or that any resident image was released with permission.
"""
from __future__ import annotations
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = Path("11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16")
REPORT = Path("00_CONTROL/HISTORICAL_PUBLIC_EVIDENCE_INTEGRITY_AUDIT_2026-10-16.json")
FILES = []
MISSING = []
ERRORS = []
STATUS = []

def parse(relative):
    return json.loads((REPO/relative).read_text(encoding="utf-8"))

def check(source, path, sha, size, classification):
    path = Path(path)
    if path.is_absolute() or ".." in path.parts:
        ERRORS.append({"source":source,"issue":"PATH_ESCAPE","path":str(path)})
        return
    dest = REPO/path
    if not dest.is_file():
        ERRORS.append({"source":source,"issue":"DECLARED_SOURCE_BYTES_MISSING","path":str(path)})
        return
    if dest.stat().st_size != int(size):
        ERRORS.append({"source":source,"issue":"SIZE_MISMATCH","path":str(path),
                       "expected":int(size),"actual":dest.stat().st_size})
        return
    checksum = hashlib.sha256()
    with dest.open("rb") as stream:
        sig=stream.read(16)
        checksum.update(sig)
        while chunk := stream.read(2*1024*1024):
            checksum.update(chunk)
    actual=checksum.hexdigest()
    if actual!=sha:
        ERRORS.append({"source":source,"issue":"SHA256_MISMATCH","path":str(path),
                       "expected":sha,"actual":actual})
        return
    suffix=dest.suffix.lower()
    valid={
        ".pdf": sig.startswith(b"%PDF-"),
        ".jpg": sig.startswith(b"\xff\xd8\xff"),
        ".jpeg": sig.startswith(b"\xff\xd8\xff"),
        ".tif": sig.startswith((b"II*\x00",b"MM\x00*",b"II+\x00",b"MM\x00+")),
        ".gpkg": sig.startswith(b"SQLite format 3\x00"),
        ".laz": sig.startswith(b"LASF"),
        ".zip": sig.startswith(b"PK\x03\x04"),
    }
    if suffix in valid and not valid[suffix]:
        ERRORS.append({"source":source,"issue":"MAGIC_BYTES_MISMATCH","path":str(path)})
        return
    FILES.append({"source":source,"path":str(path),"bytes":int(size),
                  "sha256":actual,"kind":classification,"state":"HASH_VERIFIED"})

def assert_source(source,name,key,expected):
    if expected != key:
        ERRORS.append({"source":source,"issue":name,"actual":key,"expected":expected})

def main():
    p=ROOT/"ORIGINAL_NOAA_2006"
    idx=parse(p/"tileindex_2006_FL_Panhandle_m57.acquisition.json")
    a=parse(p/"2006_tom_street_copc_acquisition.json")
    check("NOAA_2006_SOURCE_INDEX",idx["local_original"],idx["sha256"],idx["bytes"],"official_original_index")
    check("NOAA_2006_COPC",a["local_original"],a["sha256"],a["bytes"],"official_original_lidar")
    assert_source("NOAA_2006_COPC","EXPECTED_PUBLIC_ORIGINAL_HASH",a["sha256"],
                  "d5e83be7740af296db227af9c29e253ccc9c0279ee062c32c1091bb2f4376faa")
    assert_source("NOAA_2006_INDEX","EXPECTED_PUBLIC_INDEX_HASH",idx["sha256"],
                  "33e4e61c7970f99207eb25a584ee4f2b74a3211880564ef28057d3c80fc1d191")
    m17=parse(ROOT/"ORIGINAL_NOAA_2017/16reu175645.acquisition.json")
    check("NOAA_2017_DEM",m17["local_original"],m17["sha256"],m17["bytes"],"official_original_dem")
    assert_source("NOAA_2017_DEM","EXPECTED_PUBLIC_ORIGINAL_HASH",m17["sha256"],
                  "449070da44acbdc23a289bdbfb436ef0eeb75b2cdc5cdee1fda154b263e507e0")
    m18=parse(ROOT/"ORIGINAL_NOAA_2018/ACQUISITION_MANIFEST.json")
    check("NOAA_2018_INDEX_NO_SITE_COVERAGE",m18["index"]["path"],m18["index"]["sha256"],
          m18["index"]["bytes"],"official_index_no_coverage")
    if m18["status"] != "NO_2018_DEM_TILE_AT_ALL_THREE_SAMPLE_POINTS" or any(m18["parcel_point_matches"].values()):
        ERRORS.append({"source":"NOAA_2018_INDEX","issue":"COVERAGE_STATUS_UNEXPECTED","status":m18["status"]})
    STATUS.append({"source":"NOAA_2018_TERRAIN","status":"NO_SITE_COVERAGE","distance_to_nearest_tile_m":
      {k:v[0]["distance_m"] for k,v in m18["closest_index_polygons_by_projected_distance"].items()}})
    m_aerial=parse(ROOT/"FLORIDA_DEP_HISTORICAL_AERIALS/ACQUISITION_MANIFEST.json")
    accepted=0
    for image in m_aerial["images"]:
        if image["status"]=="PUBLIC_IMAGE_EXPORT_BYTES_VALIDATED":
            check("FDEP_"+image["service_label"],image["file"],image["sha256"],
                  image["bytes"],"official_derived_ortho_jpeg")
            accepted+=1
        else:
            MISSING.append({"source":"FDEP_"+image["service_label"],
                            "status":image["status"],"reason":image.get("failure")})
    if accepted != m_aerial["downloaded_validated_count"]:
        ERRORS.append({"source":"FDEP_IMAGERY","issue":"CAPTURE_COUNT_MISMATCH"})
    metadata=parse(ROOT/"FLORIDA_DEP_HISTORICAL_AERIALS/MOSAIC_CATALOG_PROVENANCE.json")
    if metadata["services_queried"] != m_aerial["requested_count"]:
        ERRORS.append({"source":"FDEP_CATALOG","issue":"SERVICE_COUNT_MISMATCH"})
    for image in m_aerial["images"]:
        if image["status"]=="PUBLIC_IMAGE_EXPORT_BYTES_VALIDATED":
            matching=[x for x in metadata["records"] if x["label"]==image["service_label"]]
            if not matching or matching[0]["catalog_status"] != "POINT_CATALOG_FEATURES_RETURNED":
                ERRORS.append({"source":"FDEP_"+image["service_label"],"issue":"NO_SPATIAL_CATALOG_MATCH"})
    naip=parse(ROOT/"USDA_NAIP_2023/ACQUISITION_MANIFEST.json")
    if naip["image_status"]=="PUBLIC_NAIP_2023_EXPORT_BYTES_SAVED_AND_VALIDATED":
        check("USDA_2023_NAIP",naip["path"],naip["sha256"],naip["bytes"],"official_derived_ortho_jpeg")
        assert_source("USDA_2023_NAIP","EXPECTED_SOURCE_HASH",naip["sha256"],
                      "32427d9550ab3ff80caf3ce39e26d9187f86a9a1a4766916e97f57decd6ea169")
        if naip["catalog_status"] != "POINT_INTERSECTION_RETRIEVED" or not any(
            f["attributes"].get("state")=="FL" and f["attributes"].get("resolution")==0.3
            for f in naip["catalog_intersecting_features"]
        ):
            ERRORS.append({"source":"USDA_2023_NAIP","issue":"MISSING_SITE_SPATIAL_CATALOG_VERIFICATION"})
    else:
        MISSING.append({"source":"USDA_2023_NAIP","status":naip["image_status"]})
    naip21=parse(ROOT/"USDA_NAIP_2021/ACQUISITION_MANIFEST.json")
    if naip21["image_status"]=="PUBLIC_NAIP_2021_EXPORT_BYTES_SAVED_AND_VALIDATED":
        check("USDA_2021_NAIP",naip21["path"],naip21["sha256"],naip21["bytes"],
              "official_derived_ortho_jpeg")
    else:
        MISSING.append({"source":"USDA_2021_NAIP",
                        "status":"NO_USEFUL_SITE_IMAGE",
                        "reason":naip21.get("image_failure"),
                        "catalog_primary_tile_status":naip21.get("catalog_status")})
    fdot=parse(ROOT/"FDOT_AERIAL_ARCHIVE_INDEX/ACQUISITION_MANIFEST.json")
    for record in fdot["documents"]:
        if record["status"]=="ORIGINAL_FDOT_COUNTY_INDEX_PDF_SAVED":
            check(record["document"],record["path"],record["sha256"],record["bytes"],
                  "official_public_historical_photo_coverage_index")
        else:
            MISSING.append({"source":record["document"],"status":record["status"],
                            "reason":record.get("error")})
    wat=parse(ROOT/"WATERSHED_DOCUMENTS/ACQUISITION_MANIFEST.json")
    for doc in wat["documents"]:
        if doc["original_status"].startswith("ORIGINAL_"):
            check("COUNTY_"+doc["document_id"],doc["path"],doc["sha256"],doc["bytes"],"official_published_pdf")
        elif doc["document_id"] == "EAST_NAVARRE_WATERSHED_STUDY_AREA_MAP":
            STATUS.append({"source":"COUNTY_EAST_NAVARRE_STUDY_AREA_MAP",
                           "status":"ORIGINAL_JPEG_CAPTURED_SEPARATELY_PDF_REQUEST_WRONG_MEDIA_TYPE"})
        else:
            MISSING.append({"source":"COUNTY_"+doc["document_id"],"status":doc["original_status"]})
    e=parse(ROOT/"WATERSHED_DOCUMENTS/East_Navarre_Watershed_Study_Area_Official.acquisition.json")
    check("COUNTY_EAST_NAVARRE_MAP",e["file"],e["sha256"],e["bytes"],"official_original_published_map")
    reports=parse(ROOT/"NOAA_SURVEY_REPORTS/ACQUISITION_MANIFEST.json")
    for r in reports["records"]:
        if r["status"].startswith("ORIGINAL_"):
            check("NOAA_REPORT_"+r["id"],r["file"],r["sha256"],r["bytes"],"official_regional_survey_report")
        else:
            MISSING.append({"source":"NOAA_REPORT_"+r["id"],"status":r["status"],"reason":r.get("reason")})
    county=parse(ROOT/"COUNTY_HISTORICAL_AERIAL_EXPORTS/ACQUISITION_MANIFEST.json")
    if county["success_count"]!=0:
        STATUS.append({"source":"COUNTY_AERIALS","status":"NEEDS_REVIEW_NEW_MATERIAL","saved":county["success_count"]})
    else:
        MISSING.append({"source":"COUNTY_AERIALS_MAPSERVER","status":"EIGHT_REQUESTS_FAILED_HTTP_500",
                        "reason":"Source historic map services not started; FDEP official aerials separately archived."})
    photo=REPO/"00_CONTROL/PRIVATE_RESIDENT_PHOTO_INVENTORY_PUBLIC_SAFE_2026-10-16.csv"
    with photo.open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=37 or sum(bool(x["exact_content_duplicate_of"]) for x in rows)!=2:
        ERRORS.append({"source":"PRIVATE_PHOTO_INDEX","issue":"INVENTORY_COUNT_MISMATCH","count":len(rows)})
    STATUS.append({"source":"RESIDENT_PHOTOGRAPHS",
                   "status":"PRIVATE_REPORTED_37_INSTANCES_35_DISTINCT_NOT_PUBLISHED_IN_PUBLIC_GITHUB",
                   "native_originals_authenticated":False})
    if any((REPO/"11_HYDROLOGY_AND_HAZARD").rglob("IMG_*.jpeg")):
        ERRORS.append({"source":"PRIVATE_PHOTOS","issue":"RESIDENT_ORIGINAL_VISIBLE_IN_PUBLIC_HYDROLOGY_TREE"})
    report={
        "audited_utc":datetime.now(timezone.utc).isoformat(),
        "repository":"dthompsonfl/tom.street.drainage",
        "branch":"main",
        "scope":"Historical source files and associated manifests named in this audit, not every repository source.",
        "integrity_status":"PASS" if not ERRORS else "FAIL",
        "checked_file_count":len(FILES),
        "checked_bytes":sum(x["bytes"] for x in FILES),
        "verified_files":FILES,
        "available_but_unacquired":MISSING,
        "other_stated_statuses":STATUS,
        "hash_or_safety_errors":ERRORS,
        "completed_definition":"Each checked file exists, matches captured size and SHA-256, and uses expected file signature. Does not verify substantive accuracy, latest agency record, or complete universe of available data.",
        "site_and_legal_open_issues":[
            "2026 approved sealed grading/drainage and subdivision plans and revisions not held",
            "current common-datum licensed survey, pipe invert elevations and positive downstream outfall unavailable",
            "formal County asset/ditch maintenance ownership, acceptance and easements unavailable",
            "actual NWFWMD ERP and FDEP construction-stormwater coverage applicability unresolved",
            "source orthophotos and exact per-year flight dates partly missing",
            "private resident photo originals and publish permissions incomplete; do not upload to public repo",
        ],
    }
    output=REPO/REPORT
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("HISTORICAL ARCHIVE INTEGRITY:",report["integrity_status"],"files",len(FILES),
          "bytes",report["checked_bytes"],"errors",len(ERRORS),"unacquired",len(MISSING))
    if ERRORS:
        raise RuntimeError("Historical archive integrity check failed; inspect emitted audit JSON")

if __name__ == "__main__":
    main()
