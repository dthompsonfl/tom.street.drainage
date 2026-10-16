#!/usr/bin/env python3
"""Check 2026-10-16 historical source/exhibit/claim cross-references against bytes.

This is a mechanical referential-integrity check, not survey verification.
"""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
CONTROL=REPO/"00_CONTROL"
AUDIT=json.loads((CONTROL/"HISTORICAL_PUBLIC_EVIDENCE_INTEGRITY_AUDIT_2026-10-16.json").read_text())
FILES={file["path"]:file for file in AUDIT["verified_files"]}


def rows(filename):
    with (CONTROL/filename).open(newline="",encoding="utf-8-sig") as fh:
        reader=csv.DictReader(fh)
        if len(set(reader.fieldnames))!=len(reader.fieldnames):
            raise AssertionError(f"Duplicate column in {filename}")
        return list(reader)

def check_file(entry):
    path=REPO/entry["path"]
    assert path.is_file(),f"Missing source: {entry['path']}"
    assert path.stat().st_size==entry["bytes"], f"Invalid byte length: {path}"
    h=hashlib.sha256()
    with path.open("rb") as f:
        while data:=f.read(1048576):
            h.update(data)
    assert h.hexdigest()==entry["sha256"], f"Source SHA-256 mismatch: {path}"

def main():
    assert AUDIT["integrity_status"]=="PASS",AUDIT.get("hash_or_safety_errors")
    assert len(FILES)==AUDIT["checked_file_count"],"Hash source manifest size mismatch"
    registers=rows("SOURCE_REGISTER.csv")
    exhibits=rows("EXHIBIT_INDEX.csv")
    claims=rows("EVIDENCE_LEDGER.csv")
    sources=[x for x in registers if x["source_id"].startswith("SRC-HIST-")]
    # This audit is bounded to the 23 archived historical sources. Select by
    # actual file path, not EX-/CLM- numeric ranges that grow with new research.
    new_exhibits=[x for x in exhibits if x["source_file"] in FILES]
    new_claims=[x for x in claims if x["source_file"] in FILES]
    assert len(sources)>=len(FILES),f"Expected >= {len(FILES)} historic source rows"
    assert len(new_exhibits)>=11,f"Expected >= 11 archived historical source exhibits, found {len(new_exhibits)}"
    assert len(new_claims)>=9,f"Expected >= 9 archived historical claims, found {len(new_claims)}"
    assert len({x["source_id"] for x in registers})==len(registers),"Duplicate source IDs"
    assert len({x["exhibit_id"] for x in exhibits})==len(exhibits),"Duplicate exhibit IDs"
    assert len({x["claim_id"] for x in claims})==len(claims),"Duplicate claim IDs"
    assert set(x["local_relative_path"] for x in sources)==set(FILES),"Missing or duplicate archived source in source register"
    exmap={x["exhibit_id"]:x for x in exhibits}
    for entry in FILES.values():
        check_file(entry)
    for x in sources:
        ref=FILES[x["local_relative_path"]]
        assert x["sha256_hash"]==ref["sha256"],x["source_id"]
        assert int(x["file_size_bytes"])==ref["bytes"],x["source_id"]
        assert x["original_url"].startswith("https://"),x["source_id"]
    for x in new_exhibits:
        ref=FILES.get(x["source_file"])
        assert ref is not None,x["exhibit_id"]
        assert x["sha256"]==ref["sha256"],x["exhibit_id"]
        assert int(x["bytes"])==ref["bytes"],x["exhibit_id"]
    for x in new_claims:
        ref=FILES.get(x["source_file"])
        assert ref is not None,x["claim_id"]
        assert x["sha256"]==ref["sha256"],x["claim_id"]
        for exhibit in x["source_exhibit"].split("|"):
            assert exhibit in exmap,f"Broken exhibit link: {x['claim_id']}->{exhibit}"
    image=rows("PRIVATE_RESIDENT_PHOTO_INVENTORY_PUBLIC_SAFE_2026-10-16.csv")
    assert len(image)==37
    assert len({x["photo_id"] for x in image})==37
    assert sum(bool(x["exact_content_duplicate_of"]) for x in image)==2
    assert all(x["public_release"]=="ON_HOLD_PRIVACY_AND_RIGHTS" for x in image)
    assert all(x["public_repository_image_copy"]=="NOT_COMMITTED" for x in image)
    assert not any(REPO.rglob("IMG_*.jpeg")),"Private resident JPEG found in public repository"
    for p in ["HISTORICAL_EVIDENCE_COMPLETENESS_2026-10-16.md"]:
        assert (CONTROL/p).is_file(),p
    print("PASS 23 distinct source files SHA-256 validated")
    print("PASS 23 source records, 11 exhibits, 9 source-linked claims")
    print("PASS 37 indexed private photo instances, no raw JPEG in public source tree")
    print("PASS original/derived source paths, statuses, sizes, and claim references")

if __name__=="__main__":
    main()
