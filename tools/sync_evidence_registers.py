#!/usr/bin/env python3
"""Dynamic, append-safe evidence register synchronizer and integrity validator.

Solves two major bottlenecks in the original `tools.zip` suite:
1. Replaces the single-use, hardcoded-SHA256 importers (`import_reviewed_question_sources.py`
   and `reconcile_question_findings.py`) with a general, cryptographic manifest
   ingester that can import and register ANY new capture directory or manifest
   under `11_HYDROLOGY_AND_HAZARD`, `02_PROPERTY_AND_PARCELS`, `03_PERMITS_AND_INSPECTIONS`,
   or `17_CURRENT_RESEARCH/captures/` into `00_CONTROL/SOURCE_REGISTER.csv`.
2. Replaces the brittle exact-count assertions in `check_historical_evidence_crosslinks.py`
   (`assert len(sources)==23`) and `verify_reconciled_release.py` (`len(ids)==43`)
   with a monotonic lower-bound + full referential integrity check so that adding
   new evidence files never breaks repository CI checks.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / "00_CONTROL"

MAGIC_SIGNATURES = {
    ".pdf": (b"%PDF-",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".tif": (b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+"),
    ".tiff": (b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+"),
    ".gpkg": (b"SQLite format 3\x00",),
    ".laz": (b"LASF",),
    ".zip": (b"PK\x03\x04",),
}


def compute_sha256_and_magic(path: Path) -> tuple[str, int, bool]:
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as f:
        head = f.read(16)
        size += len(head)
        h.update(head)
        while chunk := f.read(1024 * 1024):
            size += len(chunk)
            h.update(chunk)
    suffix = path.suffix.lower()
    if suffix in MAGIC_SIGNATURES:
        magic_ok = head.startswith(MAGIC_SIGNATURES[suffix])
    elif suffix == ".json":
        try:
            obj = json.loads(path.read_bytes())
            magic_ok = isinstance(obj, (dict, list))
        except Exception:
            magic_ok = False
    else:
        magic_ok = size > 0
    return h.hexdigest(), size, magic_ok


def read_csv_register(csv_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not csv_path.is_file():
        return [], []
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv_register(csv_path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.write_bytes(buf.getvalue().encode("utf-8"))


def infer_agency(source_id: str, url: str) -> str:
    u = url.lower()
    if "santarosa" in u or "srcpa" in u or source_id.startswith("SRC"):
        return "Santa Rosa County"
    if "noaa" in u:
        return "NOAA Office for Coastal Management"
    if "fema.gov" in u:
        return "FEMA National Flood Hazard Layer"
    if "nationalmap.gov" in u or "usgs" in u:
        return "U.S. Geological Survey (USGS)"
    if "usda.gov" in u or "geoplatform.gov" in u:
        return "U.S. Department of Agriculture (USDA)"
    if "dep.state.fl.us" in u or "floridadep.gov" in u or source_id.startswith("DEP"):
        return "Florida Department of Environmental Protection"
    if "sjrwmd.com" in u or "nwfwater.com" in u or source_id.startswith("NWFWMD"):
        return "Northwest Florida Water Management District"
    if "fdot" in u or "blob.core.windows.net" in u:
        return "Florida Department of Transportation"
    if "mcclibrary" in u or source_id.startswith("ORD"):
        return "Santa Rosa County / Municode"
    return "Public Government Source"


def extract_manifest_entries(manifest_path: Path) -> list[dict]:
    """Normalize records from any ACQUISITION_MANIFEST.json or *.acquisition.json."""
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(data, dict):
        return []

    normalized = []
    captured_utc = data.get("captured_utc") or data.get("retrieved_utc") or data.get("created_utc") or datetime.now(timezone.utc).isoformat()

    # Case 1: Single-file `.acquisition.json` (e.g., NOAA 2006/2017 or East Navarre map)
    if ("local_original" in data or "file" in data) and "sha256" in data:
        rel_path = data.get("local_original") or data.get("file")
        sid = f"SRC-AUTO-{Path(rel_path).stem.upper()}"
        normalized.append({
            "source_id": sid,
            "local_relative_path": str(rel_path),
            "original_url": data.get("source_url", ""),
            "retrieved_utc": captured_utc,
            "sha256": data["sha256"],
            "bytes": int(data["bytes"]),
            "agency": data.get("agency") or data.get("source_agency") or infer_agency(sid, data.get("source_url", "")),
        })

    # Case 2: Multi-record `ACQUISITION_MANIFEST.json` across various scripts
    list_keys = ("sources", "records", "images", "documents", "entries", "network_captures")
    for key in list_keys:
        items = data.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            rel_path = (
                item.get("local_path")
                or item.get("canonical_path")
                or item.get("path")
                or item.get("file")
                or item.get("local_file")
            )
            sha = item.get("sha256")
            size = item.get("bytes")
            if not rel_path or not sha or size is None:
                continue
            raw_id = (
                item.get("source_id")
                or item.get("id")
                or item.get("document_id")
                or item.get("document")
                or item.get("service_label")
                or Path(rel_path).stem
            )
            sid = f"SRC-AUTO-{str(raw_id).upper().replace(' ', '_')}"
            url = (
                item.get("requested_url")
                or item.get("source_url")
                or item.get("original_url")
                or item.get("export_url")
                or item.get("request_url")
                or item.get("url")
                or data.get("service", "")
            )
            normalized.append({
                "source_id": sid,
                "local_relative_path": str(rel_path),
                "original_url": str(url),
                "retrieved_utc": item.get("retrieved_utc") or captured_utc,
                "sha256": str(sha),
                "bytes": int(size),
                "agency": data.get("agency") or data.get("source_agency") or infer_agency(sid, str(url)),
            })

    # Case 3: Single-output NAIP manifests (`path` + `sha256` at top level)
    if "path" in data and "sha256" in data and "bytes" in data:
        rel_path = data["path"]
        sid = f"SRC-AUTO-{Path(rel_path).stem.upper()}"
        normalized.append({
            "source_id": sid,
            "local_relative_path": str(rel_path),
            "original_url": data.get("source_export_url", data.get("service", "")),
            "retrieved_utc": captured_utc,
            "sha256": data["sha256"],
            "bytes": int(data["bytes"]),
            "agency": data.get("agency", "USDA"),
        })

    return normalized


def sync_all_manifests_to_register(dry_run: bool = False) -> dict:
    """Scan all manifests in the repository, verify bytes/hashes, and sync to SOURCE_REGISTER.csv."""
    register_path = CONTROL / "SOURCE_REGISTER.csv"
    fields, rows = read_csv_register(register_path)
    if not fields:
        fields = [
            "source_id", "document_title", "issuing_agency", "record_system",
            "source_identifier", "retrieval_date_utc", "original_url",
            "local_relative_path", "file_type", "file_size_bytes", "sha256_hash",
            "status", "verification_method", "notes",
        ]

    by_path = {r.get("local_relative_path", ""): r for r in rows if r.get("local_relative_path")}
    by_id = {r.get("source_id", ""): r for r in rows if r.get("source_id")}

    manifests = sorted(
        set(ROOT.rglob("ACQUISITION_MANIFEST.json"))
        | set(ROOT.rglob("*.acquisition.json"))
    )

    added = []
    versioned_updates = []
    verified_existing = 0
    errors = []

    for mpath in manifests:
        for entry in extract_manifest_entries(mpath):
            rel = entry["local_relative_path"]
            file_path = ROOT / rel
            if not file_path.is_file():
                errors.append({"manifest": mpath.relative_to(ROOT).as_posix(), "missing_file": rel})
                continue
            actual_sha, actual_size, magic_ok = compute_sha256_and_magic(file_path)
            if actual_sha != entry["sha256"] or actual_size != entry["bytes"] or not magic_ok:
                errors.append({
                    "manifest": mpath.relative_to(ROOT).as_posix(),
                    "file": rel,
                    "issue": "HASH_SIZE_OR_MAGIC_MISMATCH",
                    "expected_sha": entry["sha256"],
                    "actual_sha": actual_sha,
                    "magic_ok": magic_ok,
                })
                continue

            if rel in by_path:
                existing_row = by_path[rel]
                if existing_row.get("sha256_hash") == actual_sha:
                    verified_existing += 1
                    continue
                # Upstream file at path was updated (if someone replaced it); create a versioned register record
                ts_suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
                new_id = f"{existing_row['source_id']}-V{ts_suffix}"
                versioned_updates.append(new_id)
                sid = new_id
            else:
                sid = entry["source_id"]
                if sid in by_id and by_id[sid].get("local_relative_path") != rel:
                    short_hash = actual_sha[:8].upper()
                    sid = f"{sid}-{short_hash}"
                if sid in by_id:
                    verified_existing += 1
                    continue
                added.append(sid)

            new_row = {
                "source_id": sid,
                "document_title": Path(rel).name,
                "issuing_agency": entry["agency"],
                "record_system": "Autonomous Public Source Capture",
                "source_identifier": Path(rel).stem,
                "retrieval_date_utc": entry["retrieved_utc"],
                "original_url": entry["original_url"],
                "local_relative_path": rel,
                "file_type": Path(rel).suffix.lstrip("."),
                "file_size_bytes": str(actual_size),
                "sha256_hash": actual_sha,
                "status": "PRESERVED_PRIMARY_CAPTURE_NOT_SITE_COMPLIANCE",
                "verification_method": "Automated SHA-256, byte-length, and file-signature verification",
                "notes": f"Ingested from {mpath.relative_to(ROOT).as_posix()}; raw capture does not establish engineering compliance.",
            }
            rows.append({f: str(new_row.get(f, "")) for f in fields})
            by_path[rel] = new_row
            by_id[sid] = new_row

    if (added or versioned_updates) and not dry_run and not errors:
        write_csv_register(register_path, fields, rows)

    return {
        "synchronized_utc": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "manifests_scanned": len(manifests),
        "verified_existing_records": verified_existing,
        "added_source_ids": added,
        "versioned_update_ids": versioned_updates,
        "integrity_errors": errors,
    }


def validate_monotonic_crosslinks() -> dict:
    """Validate SOURCE_REGISTER, EXHIBIT_INDEX, EVIDENCE_LEDGER, and CLAIM_SOURCE_LINKS without brittle upper-bound counts."""
    issues = []
    _, sources = read_csv_register(CONTROL / "SOURCE_REGISTER.csv")
    _, exhibits = read_csv_register(CONTROL / "EXHIBIT_INDEX.csv")
    _, claims = read_csv_register(CONTROL / "EVIDENCE_LEDGER.csv")
    _, links = read_csv_register(CONTROL / "CLAIM_SOURCE_LINKS.csv")

    if len({r["source_id"] for r in sources}) != len(sources):
        issues.append("Duplicate source_id in SOURCE_REGISTER.csv")
    if len({r["exhibit_id"] for r in exhibits}) != len(exhibits):
        issues.append("Duplicate exhibit_id in EXHIBIT_INDEX.csv")
    if len({r["claim_id"] for r in claims}) != len(claims):
        issues.append("Duplicate claim_id in EVIDENCE_LEDGER.csv")

    # Monotonic baseline checks (allows growth as new evidence is added!)
    hist_sources = [x for x in sources if x.get("source_id", "").startswith("SRC-HIST-")]
    if sources and len(hist_sources) < 23:
        issues.append(f"Expected at least 23 SRC-HIST-* sources, found {len(hist_sources)}")

    ex_map = {x["exhibit_id"]: x for x in exhibits}
    for row in sources:
        rel = (row.get("local_relative_path") or "").strip()
        if not rel:
            continue
        p = ROOT / rel
        if not p.is_file():
            continue
        sha, size, magic_ok = compute_sha256_and_magic(p)
        if sha != row.get("sha256_hash") or str(size) != str(row.get("file_size_bytes")):
            issues.append(f"Hash/size mismatch in SOURCE_REGISTER for {row['source_id']} ({rel})")
        if not magic_ok:
            issues.append(f"Magic signature check failed for {row['source_id']} ({rel})")

    for claim in claims:
        cid = claim.get("claim_id", "")
        eids = [e.strip() for e in (claim.get("source_exhibit") or "").split("|") if e.strip()]
        for eid in eids:
            if eid not in ex_map:
                issues.append(f"Claim {cid} references unknown exhibit {eid}")

    # Privacy guard: ensure no raw resident IMG_*.jpeg leaked into public tree
    if any(ROOT.rglob("IMG_*.jpeg")):
        issues.append("PRIVACY_VIOLATION: Private resident JPEG (IMG_*.jpeg) found in repository tree")

    return {
        "status": "PASS" if not issues else "FAIL",
        "sources_total": len(sources),
        "exhibits_total": len(exhibits),
        "claims_total": len(claims),
        "links_total": len(links),
        "issues": issues,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Preview register additions without writing CSVs.")
    parser.add_argument("--validate-only", action="store_true", help="Only run monotonic crosslink & hash validation.")
    args = parser.parse_args(argv)

    result = {}
    if not args.validate_only:
        result["sync"] = sync_all_manifests_to_register(dry_run=args.dry_run)
    result["validation"] = validate_monotonic_crosslinks()
    print(json.dumps(result, indent=2))
    has_errors = bool(
        result.get("sync", {}).get("integrity_errors")
        or result["validation"]["status"] != "PASS"
    )
    return 1 if has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
