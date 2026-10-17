#!/usr/bin/env python3
"""Read-only, byte-exact independent audit of Tom Street LABINS originals.

PASS verifies source custody and bounded mapping only. It does not certify
historical drainage, parcel title, elevation differences or a legal violation.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=Path("11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-17/LABINS_SANTA_ROSA")
YEAR_DIR=BASE/"ORIGINAL_IMAGERY_CELL_648138"
YEARS=(2007,2010,2013,2016,2019)
count=0
size=0
failures=[]
reported_files=set()

def fail(msg):failures.append(msg)
def read(relative):return json.loads((ROOT/relative).read_text(encoding="utf-8"))
def md5less(path):
    h=hashlib.sha256()
    with path.open("rb") as stream:
        while part:=stream.read(1024*1024):h.update(part)
    return h.hexdigest()
def verify(info,where):
    global count,size
    rel=Path(info["path"])
    if rel.is_absolute() or ".." in rel.parts:
        return fail(where+": path escape")
    full=ROOT/rel
    if not full.is_file():
        return fail(where+": original source not in repo "+str(rel))
    if full.stat().st_size!=int(info["bytes"]) or md5less(full)!=info["sha256"]:
        return fail(where+": source hash/size mismatch "+str(rel))
    count+=1
    size+=full.stat().st_size
    reported_files.add(rel.as_posix())
    return full

def rows(name,key):
    with (ROOT/"00_CONTROL"/name).open(newline="",encoding="utf-8-sig") as f:
        out=list(csv.DictReader(f))
    by={r[key]:r for r in out}
    # The historical ledgers may legitimately contain multiple archived versions
    # of one path. Claim-source links intentionally have repeated claim IDs.
    # Validate new original entries individually by digest rather than
    # imposing a global uniqueness constraint on old records.
    return by

reg=rows("SOURCE_REGISTER.csv","local_relative_path")
exhibits=rows("EXHIBIT_INDEX.csv","source_file")
claim_links=rows("CLAIM_SOURCE_LINKS.csv","claim_id") # Multiple rows per claim intentionally: inspect complete records below.
with (ROOT/"00_CONTROL/CLAIM_SOURCE_LINKS.csv").open(newline="",encoding="utf-8") as f:
    source_links=list(csv.DictReader(f))
claims=rows("EVIDENCE_LEDGER.csv","claim_id")

grid=read(BASE/"ACQUISITION_MANIFEST.json")
pdf=grid["official_grid_index"]
if pdf["status"]!="ORIGINAL_GRID_PDF_SAVED_AND_HASHED":fail("original LABINS PDF not acquired")
verify(pdf,"original LABINS grid PDF")

north=read(BASE/"LABINS_NORTH_GRID_POINT_LOOKUP_MANIFEST.json")
if north["status"]!="ALL_SOURCE_PROBES_CAPTURED":fail("FREAC north grid query incomplete")
if len(north["captures"])!=6:fail("FREAC six original captures not present")
for source in north["captures"]:
    full=verify(source,"FREAC original grid source")
    if full and "POINT" in source["name"] or full and "SAMPLE" in source["name"]:
        feat=json.loads(full.read_bytes()).get("features",[])
        if len(feat)!=1 or feat[0].get("attributes",{}).get("spn_id")!=648138:
            fail("FREAC grid ID unexpectedly changed")
if len(north["point_intersections"])!=4 or any(r["grid_ids"]!=[648138] for r in north["point_intersections"]):
    fail("Original four location checks do not match 648138")

html=read(BASE/"LABINS_648138_IMAGE_DOWNLOAD_DISCOVERY_MANIFEST.json")
if html["exact_verified_grid_id"]!="648138":fail("LABINS search grid identity differs")
for item in html["source_documents"]:
    verify(item,"LABINS public search form original")
for item in html["search_results"]:
    if "source_capture" in item:verify(item["source_capture"],"LABINS public exact-cell results")
if len(html["search_results"][0]["candidate_download_links"])!=20:
    fail("Expected 20 file links from original LABINS download result")

mismatch=read("02_PROPERTY_AND_PARCELS/CLERK_LOT_QQ_DISCOVERY_2026-10-17/INDEX_DISCOVERY_REPORT_20261017T171827Z.json")
pa=mismatch["srpa_plat"]["queries"][1]["original_source"]
path=verify(pa,"SRCPA nonmatching phase query")
if path:
    data=json.loads(path.read_text())
    if not(len(data.get("results",[]))==1 and
           data["results"][0].get("subdivisionName")=="SENTINEL RIDGE PHASE 1" and
           data["results"][0].get("subdivisionCode")=="04933"):
        fail("Misrouted plat source cannot serve as negative control")

originals=0
missing=[]
for year in YEARS:
    m=read(YEAR_DIR/f"ACQUISITION_MANIFEST_{year}.json")
    if m["year"]!=year or m["official_grid_identifier"]!="648138":
        fail(f"Manifest {year} not linked to verified grid")
    if len(m["files"])!=m["published_file_count"]:
        fail(f"Published file count wrong: {year}")
    archived=0
    for info in m["files"]:
        if info["status"]!="ORIGINAL_OFFICIAL_BYTES_ARCHIVED_AND_VALIDATED" and info["status"]!="ORIGINAL_ALREADY_ARCHIVED_IDENTICAL":
            missing.append((year,info["name"],info["status"],info.get("error","")))
            continue
        path=verify(info,f"LABINS {year} original")
        if not path:continue
        originals+=1;archived+=1
        ext=path.suffix.lower()
        if ext==".sid" and path.open("rb").read(4).lower()!=b"msid":
            fail(f"Not a real MrSID header: {path.name}")
        if ext==".sdw":
            try:
                coords=path.read_text(encoding="ascii").split()
                if len(coords)!=6 or any(not math.isfinite(float(n)) for n in coords):
                    fail(f"Worldfile invalid: {path.name}")
            except Exception as err:fail(f"Cannot read worldfile {path.name}: {err}")
        if ext==".xml":
            doc=ET.parse(path).getroot()
            begin=doc.findtext(".//begdate");end=doc.findtext(".//enddate")
            expected={2016:("20151207","20160206"),2019:("20190125","20190306")}
            if year in expected and (begin,end)!=expected[year]:
                fail(f"Project-wide flight dates differ for {year}: {begin}, {end}")
    if archived!=m["archived_file_count"]:
        fail(f"Year {year} archived count mismatch")
if originals!=19:fail(f"Expected 19 validated imagery/sidecar originals, got {originals}")
if len(missing)!=1 or missing[0][0]!=2016 or not missing[0][1].endswith(".aux") or "HTTP 404" not in missing[0][3]:
    fail(f"Missing-source exceptions differ from documented 2016 .aux HTTP 404: {missing}")

for rel in sorted(reported_files):
    source=reg.get(rel)
    ex=exhibits.get(rel)
    if not source:fail("Source register missing "+rel)
    if not ex:fail("Exhibit index missing "+rel)
    if not source or not ex:continue
    digest=md5less(ROOT/rel)
    if source["sha256_hash"]!=digest or ex["sha256"]!=digest:
        fail("Registry integrity diverges for "+rel)
    if int(source["file_size_bytes"])!=(ROOT/rel).stat().st_size or int(ex["bytes"])!=(ROOT/rel).stat().st_size:
        fail("Registry byte size differs for "+rel)
    if not any(x["source_file"]==rel and x["source_sha256"]==digest and
               x["claim_id"] in {f"CLM-{n:03d}" for n in range(44,53)}
               for x in source_links):
        fail("Original has no SHA-256 linked bounded claim "+rel)
for i in range(44,53):
    row=claims.get(f"CLM-{i:03d}")
    if not row:fail(f"CLM-{i} missing from ledger")
    elif not row.get("limitation"):fail(f"CLM-{i} missing evidence limitation")

report={
    "status":"PASS" if not failures else "FAIL",
    "verified_file_count":count,"verified_total_bytes":size,
    "source_original_count":originals,
    "missing_published_files":missing,
    "checked_claim_range":"CLM-044..CLM-052",
    "integrity_errors":failures,
    "scope":"Actual original source files and all new mappings; not flood causation, permit compliance or title completeness.",
}
print(json.dumps(report,indent=2))
if failures:raise SystemExit(1)
