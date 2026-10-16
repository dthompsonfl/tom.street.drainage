#!/usr/bin/env python3
"""Offline, read-only verification for the public Tom Street draft release.

Checks exact permit/parcel records, source hashes, release PDF content and zip
integrity. Never fetches URLs, sends requests, or processes resident photo files.
"""
import csv
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "15_RECONCILED_DRAFTS"
PDF = SOURCE / "pdf"
manifest = json.loads((PDF / "RELEASE_MANIFEST.json").read_text())
errors = []
notes = []
def check(name, ok):
    (notes if ok else errors).append(name)
    print(("PASS " if ok else "FAIL ") + name)
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

check("release remains unsigned DRAFT", manifest["release_status"] == "DRAFT_NOT_APPROVED_FOR_EXTERNAL_DISTRIBUTION")
check("no original photographs in packet scope", manifest["photo_originals_included"] is False)
check("exactly five explicit source PDFs and merged PDF", len(manifest["outputs"]) == 6)

targets = [
    ("2264", "BP-2026-1621", "1020", "21-2S-26-0780-0QQ00-1020", "03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_project_by_uid.json"),
    ("2268", "BP-2026-1612", "1490", "21-2S-26-0780-0QQ00-1490", "03_PERMITS_AND_INSPECTIONS/2268_Tom_St/BP-2026-1612_project_by_uid.json"),
]
brief = (SOURCE / "01_HOMEOWNER_BRIEF.md").read_text()
letter = (SOURCE / "02_COUNTY_LETTER_DRAFT.md").read_text()
commissioner = (SOURCE / "06_COMMISSIONER_COVER_LETTER_DRAFT.md").read_text()
for address, permit, lot, formatted, source in targets:
    obj = json.loads((ROOT / source).read_text())["data"]
    check("archived county record " + address,
          obj.get("projectNumber") == permit and
          obj.get("lot") == lot and
          obj.get("parcelNumber", "").endswith(lot) and
          obj.get("status") == "Active" and
          address in obj.get("projectAddress", ""))
    check("parcel number paired in public brief " + address, formatted in brief and permit in brief)
    check("parcel number paired in county letter " + address, formatted in letter and permit in letter)
    check("parcel number paired in commissioner letter " + address, formatted in commissioner and permit in commissioner)

all_pages = 0
expected_zip = set()
for output in manifest["outputs"]:
    p = PDF / output["pdf"]
    expected_zip.add(output["pdf"])
    check("PDF exists/hash/size " + p.name,
          p.is_file() and p.stat().st_size == output["bytes"] and digest(p) == output["sha256"])
    if not p.is_file():
        continue
    reader = PdfReader(str(p))
    pages = len(reader.pages)
    check("PDF pages match manifest " + p.name, pages == output["pages"])
    if output["pdf"] != "Tom_Street_Reconciled_Public_Meeting_Draft.pdf":
        all_pages += pages
        check("standalone meeting document fits one page " + p.name, pages == 1)
        md = SOURCE / output["source_md"]
        expected_zip.add("editable/" + md.name)
        check("Markdown source hash " + md.name, digest(md) == output["source_sha256"])
        extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
        check("draft footer present in " + p.name, "Evidence-based homeowner DRAFT" in extracted)
    else:
        check("merged packet page count matches five components", pages == all_pages)

sums = {}
for line in (PDF / "SHA256SUMS.txt").read_text().splitlines():
    if line.strip():
        hashval, filename = line.split(None, 1)
        sums[filename.strip()] = hashval
check("SHA256SUMS covers exact PDF set",
      sums == {item["pdf"]: item["sha256"] for item in manifest["outputs"]})
zip_path = PDF / "Tom_Street_Reconciled_Public_Drafts.zip"
with zipfile.ZipFile(zip_path) as z:
    names = set(z.namelist())
    expected_zip |= {"RELEASE_MANIFEST.json", "SHA256SUMS.txt"}
    check("public zip entries explicitly allowlisted", names == expected_zip)
    check("public zip CRC valid", z.testzip() is None)
    check("zip has no photos or nested archives", all(not n.lower().endswith((".jpeg", ".jpg", ".png", ".tif", ".zip", ".eml")) for n in names))
    for filename in sums:
        check("zip PDF bytes match SHA256SUMS " + filename,
              hashlib.sha256(z.read(filename)).hexdigest() == sums[filename])

rows = list(csv.DictReader((ROOT / "00_CONTROL/SOURCE_REGISTER.csv").open(newline="")))
tested = 0
mismatch = []
for row in rows:
    relative = (row.get("local_relative_path") or "").strip()
    if not relative:
        continue
    path = ROOT / relative
    if not path.is_file():
        continue
    tested += 1
    if digest(path) != row["sha256_hash"] or str(path.stat().st_size) != row["file_size_bytes"]:
        mismatch.append(relative)
check("existing official source-file hashes/sizes remain valid (" + str(tested) + " checked)",
      tested >= 30 and not mismatch)
if mismatch:
    print("MISMATCHES " + ", ".join(mismatch[:10]))

inventory = list(csv.DictReader((ROOT / "00_CONTROL/PERMIT_DOCUMENT_INVENTORY.csv").open(newline="")))
ids = [row["document_id"] for row in inventory]
check("permit inventory has 43 unique IDs", len(ids) == 43 and len(ids) == len(set(ids)))
for site, pid in [("2264", "21-2S-26-0780-0QQ00-1020"), ("2268", "21-2S-26-0780-0QQ00-1490")]:
    bad = [row["document_id"] for row in inventory
           if row["document_id"].startswith("DOC-" + site) and row["parcel_id"] != pid]
    check("all inventory rows bind to correct parcel " + site, not bad)
    code = next((row for row in inventory if row["document_id"] == "DOC-" + site + "-0015"), {})
    check("certification recorded as unverified rather than absent " + site,
          "Assigned" in code.get("notes", "") and
          "unverified" in code.get("notes", "").lower())
    plan = next((row for row in inventory if row["document_id"] == "DOC-" + site + "-0011"), {})
    check("fee line does not prove grading plan " + site,
          "not establishing" in plan.get("notes", "").lower())
snapshot = (ROOT / "00_CONTROL/CHRONOLOGY.csv").read_text()
check("2000-era historical lot attribution explicitly unresolved",
      "2000-era MGO historical address/parcel unresolved" in snapshot)
photo_rows = list(csv.DictReader((ROOT / "00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv").open(newline="")))
photo_gap = next((row for row in photo_rows if row["gap_id"] == "GAP-21"), {})
check("photo gap distinguishes copies from native originals",
      photo_gap.get("status") == "PRIVATE_COPIES_HASH_MATCHED_ORIGINALS_UNVERIFIED")
check("records requests have no unsourced sent status",
      all((row.get("submitted") or "").upper() != "TRUE" or bool(row.get("receipt_id"))
          for row in photo_rows))

ledger = (ROOT / "00_CONTROL/EVIDENCE_LEDGER.csv").read_text()
check("ledger status marks verified copies rather than native originals",
      ",PRIVATE_COPY_HASH_MATCHED," in ledger)
check("ledger distinguishes private copies from native originals",
      "15 independently hash-matched JPEG copies" in ledger and
      "native camera originals" in ledger.lower())
claim_rows = list(csv.DictReader((ROOT / "00_CONTROL/EVIDENCE_LEDGER.csv").open(newline="")))
erp_claim = next((item for item in claim_rows if item["claim_id"] == "CLM-013"), {})
check("ledger does not treat nearby ERP as governing authorization",
      "not prove" in erp_claim.get("limitation", "").lower()
      and "applicab" in erp_claim.get("limitation", "").lower()
      and "limited" in erp_claim.get("claim", "").lower())
check("superseded meeting packet clearly marked",
      "SUPERSEDED" in (ROOT / "14_MEETING_PACKET/RELEASE_README.md").read_text().upper())

print("\n" + str(len(notes)) + " passed, " + str(len(errors)) + " failed")
sys.exit(1 if errors else 0)
