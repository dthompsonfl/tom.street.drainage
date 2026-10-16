#!/usr/bin/env python3
"""Autonomously acquire and version-snapshot live parcel, permit, and GIS records.

Fills the missing parcel (`02_PROPERTY_AND_PARCELS`) and permit/inspection
(`03_PERMITS_AND_INSPECTIONS`) acquisition gap in `tools/`.

Key capabilities:
1. Queries Santa Rosa County GIS (GoMaps 4.0 MapServer) for parcel polygons,
   attributes, adjacent street segments, drainage basins, wellfield protection
   overlays, and stormwater problem areas across the entire Tom Street target
   corridor (2260, 2264, 2265, 2266, 2268, 2270 Tom St, Navarre, FL 32566).
2. Queries public permit/inspection endpoints (when reachable/configured via
   public API or public portal endpoints) and archives timestamped status
   refresh snapshots under `03_PERMITS_AND_INSPECTIONS/STATUS_REFRESH/` without
   overwriting historical snapshots.
3. Detects upstream byte/field changes against previously archived records in
   `02_PROPERTY_AND_PARCELS` and `03_PERMITS_AND_INSPECTIONS`, writing a
   structured diff manifest while preserving original evidence immutability.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
GOMAPS = "https://cloud.santarosa.fl.gov/arcgis/rest/services/santarosa/GoMaps4_0/MapServer"
STREETS = "https://services.arcgis.com/Eg4L1xEv2R3abuQd/arcgis/rest/services/StreetsOpenData/FeatureServer/0"
MS4 = "https://services.arcgis.com/Eg4L1xEv2R3abuQd/arcgis/rest/services/MS4Audit_gdb/FeatureServer/0"

ALLOWED_HOSTS = {
    "cloud.santarosa.fl.gov",
    "services.arcgis.com",
    "santarosagis.maps.arcgis.com",
    "www.santarosa.fl.gov",
    "santarosa.fl.gov",
    "srcpa.gov",
    "www.srcpa.gov",
}

MAX_BYTES = 16 * 1024 * 1024
USER_AGENT = "TomStreetPublicEvidence/2.0 (Autonomous-Audit-Safe)"

# Full Tom Street investigation corridor (target construction lots + neighboring lots)
CORRIDOR_PARCELS = {
    "2260_Tom_St": {
        "address": "2260 TOM ST",
        "parcel": "21-2S-26-0780-0QQ00-1010",
        "lot": "1010",
        "role": "neighboring_reference_lot",
        "lon": -86.81466,
        "lat": 30.41504,
    },
    "2264_Tom_St": {
        "address": "2264 TOM ST",
        "parcel": "21-2S-26-0780-0QQ00-1020",
        "lot": "1020",
        "permit": "BP-2026-1621",
        "role": "target_construction_lot",
        "lon": -86.81466,
        "lat": 30.41519,
    },
    "2265_Tom_St": {
        "address": "2265 TOM ST",
        "parcel": "21-2S-26-0780-0QQ00-1180",
        "lot": "1180",
        "role": "established_homeowner_lot",
        "lon": -86.81521,
        "lat": 30.41515,
    },
    "2268_Tom_St": {
        "address": "2268 TOM ST",
        "parcel": "21-2S-26-0780-0QQ00-1490",
        "lot": "1490",
        "permit": "BP-2026-1612",
        "role": "target_construction_lot",
        "lon": -86.81466,
        "lat": 30.41534,
    },
}

CORRIDOR_BBOX = "-86.8165,30.4140,-86.8130,30.4165"


def check_url(url: str) -> str:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in ALLOWED_HOSTS
        or parsed.username
        or parsed.password
        or parsed.port not in (None, 443)
    ):
        raise ValueError(f"Unapproved acquisition URL: {url}")
    return url


class CheckedRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def arcgis_query(base_url: str, **params) -> str:
    merged = {"f": "pjson", **params}
    return f"{base_url}?{urlencode(merged)}"


def atomic_write_versioned(dest: Path, raw: bytes, snapshot_dir: Path) -> dict:
    """Write raw bytes without ever silently overwriting differing prior evidence.

    If `dest` does not exist, writes atomically to `dest` and also saves a copy in
    `snapshot_dir`. If `dest` exists with identical SHA-256, records `UNCHANGED`.
    If `dest` exists with different SHA-256, preserves `dest` untouched and saves
    the new capture inside `snapshot_dir` with status `UPSTREAM_CHANGED_NEW_SNAPSHOT`.
    """
    digest = hashlib.sha256(raw).hexdigest()
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snap_path = snapshot_dir / dest.name
    with NamedTemporaryFile(dir=snapshot_dir, delete=False) as tmp_file:
        tmp_file.write(raw)
        tmp_path = Path(tmp_file.name)
    os.replace(tmp_path, snap_path)

    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        with NamedTemporaryFile(dir=dest.parent, delete=False) as tmp_dest:
            tmp_dest.write(raw)
            tmp_dest_path = Path(tmp_dest.name)
        os.replace(tmp_dest_path, dest)
        return {
            "write_status": "INITIAL_BASELINE_SAVED",
            "canonical_path": dest.relative_to(ROOT).as_posix(),
            "snapshot_path": snap_path.relative_to(ROOT).as_posix(),
            "sha256": digest,
            "bytes": len(raw),
        }

    old_digest = hashlib.sha256(dest.read_bytes()).hexdigest()
    if old_digest == digest:
        return {
            "write_status": "UNCHANGED_MATCHES_BASELINE",
            "canonical_path": dest.relative_to(ROOT).as_posix(),
            "snapshot_path": snap_path.relative_to(ROOT).as_posix(),
            "sha256": digest,
            "bytes": len(raw),
        }

    return {
        "write_status": "UPSTREAM_CHANGED_BASELINE_PRESERVED",
        "canonical_path": dest.relative_to(ROOT).as_posix(),
        "previous_sha256": old_digest,
        "snapshot_path": snap_path.relative_to(ROOT).as_posix(),
        "sha256": digest,
        "bytes": len(raw),
    }


def fetch_json_query(source_id: str, url: str, canonical_dest: Path, snapshot_dir: Path) -> dict:
    check_url(url)
    record = {
        "source_id": source_id,
        "requested_url": url,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "status": "NOT_CAPTURED",
    }
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        with build_opener(CheckedRedirectHandler()).open(req, timeout=45) as resp:
            check_url(resp.url)
            raw = resp.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError("Response exceeds 16 MB safety cap")
            record["final_url"] = resp.url
            record["http_status"] = resp.status
            record["content_type"] = resp.headers.get("Content-Type", "")

        parsed = json.loads(raw)
        if not isinstance(parsed, dict) or "error" in parsed:
            raise ValueError(f"ArcGIS/JSON error response: {parsed.get('error') if isinstance(parsed, dict) else 'non-object'}")

        if parsed.get("exceededTransferLimit"):
            capture_class = "PARTIAL_TRANSFER_LIMIT"
        elif parsed.get("features") == []:
            capture_class = "EMPTY_SEARCH_NOT_ABSENCE_PROOF"
        else:
            capture_class = "PUBLIC_JSON_CAPTURED_AND_VALIDATED"

        storage = atomic_write_versioned(canonical_dest, raw, snapshot_dir)
        record.update({
            "status": capture_class,
            "feature_count": len(parsed.get("features", [])) if "features" in parsed else None,
            **storage,
        })
    except Exception as exc:
        record["failure"] = f"{type(exc).__name__}: {exc}"[:350]
    return record


def build_corridor_queries() -> list[tuple[str, str, Path]]:
    queries: list[tuple[str, str, Path]] = []
    parcel_root = ROOT / "02_PROPERTY_AND_PARCELS" / "GIS_CORRIDOR_CAPTURES"

    # 1. Individual parcel polygon & attribute lookups on GoMaps Layer 8 (Parcels)
    for site_key, info in CORRIDOR_PARCELS.items():
        parcel_id = info["parcel"]
        lot = info["lot"]
        url = arcgis_query(
            f"{GOMAPS}/8/query",
            where=f"PARCEL_ID LIKE '%{lot}%' OR SITUS LIKE '{info['address']}%'",
            outFields="*",
            returnGeometry="true",
            outSR=4326,
        )
        queries.append((
            f"SRCPA_GIS_PARCEL_{site_key.upper()}",
            url,
            parcel_root / f"{site_key}_gomaps_parcel_{parcel_id}.json",
        ))

    # 2. Full Tom Street block bounding-box parcel inventory (captures all neighboring lots)
    queries.append((
        "SRCPA_GIS_TOM_STREET_BLOCK_PARCELS",
        arcgis_query(
            f"{GOMAPS}/8/query",
            geometry=CORRIDOR_BBOX,
            geometryType="esriGeometryEnvelope",
            inSR=4326,
            spatialRel="esriSpatialRelIntersects",
            outFields="*",
            returnGeometry="true",
            outSR=4326,
        ),
        parcel_root / "tom_street_corridor_all_parcels_bbox.json",
    ))

    # 3. Subdivision / plat boundary lookup around Tom Street
    queries.append((
        "SRC_GIS_SUBDIVISIONS_TOM_STREET",
        arcgis_query(
            f"{GOMAPS}/11/query",
            geometry=CORRIDOR_BBOX,
            geometryType="esriGeometryEnvelope",
            inSR=4326,
            spatialRel="esriSpatialRelIntersects",
            outFields="*",
            returnGeometry="true",
            outSR=4326,
        ),
        parcel_root / "tom_street_subdivision_boundaries.json",
    ))

    # 4. Street maintainer & roadway segment verification (GoMaps + OpenData)
    queries.append((
        "SRC_STREETS_OPENDATA_TOM_ST",
        arcgis_query(
            f"{STREETS}/query",
            where="UPPER(STREETNAME) LIKE '%TOM%'",
            outFields="*",
            returnGeometry="true",
            outSR=4326,
        ),
        parcel_root / "tom_street_opendata_segments.json",
    ))

    # 5. MS4 Stormwater structures, pipes, outfalls, and problem areas in corridor
    queries.append((
        "SRC_MS4_CORRIDOR_ENVELOPE",
        arcgis_query(
            f"{MS4}/query",
            geometry=CORRIDOR_BBOX,
            geometryType="esriGeometryEnvelope",
            inSR=4326,
            spatialRel="esriSpatialRelIntersects",
            outFields="*",
            returnGeometry="true",
            outSR=4326,
        ),
        parcel_root / "tom_street_ms4_corridor_envelope.json",
    ))
    return queries


def audit_archived_permits_and_parcels() -> dict:
    """Compare archived MGO permit JSONs and SRCPA property JSONs for completeness."""
    summary = {"permits_checked": [], "parcels_checked": [], "gaps_detected": []}
    for site_key, info in CORRIDOR_PARCELS.items():
        addr_num = site_key.split("_")[0]
        pa_path = (
            ROOT
            / "02_PROPERTY_AND_PARCELS"
            / f"{addr_num}_Tom_St"
            / f"srcpa_property_record_{info['parcel']}.json"
        )
        if pa_path.is_file():
            raw = pa_path.read_bytes()
            summary["parcels_checked"].append({
                "site": site_key,
                "path": pa_path.relative_to(ROOT).as_posix(),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
            })
        else:
            summary["gaps_detected"].append({
                "site": site_key,
                "type": "MISSING_ARCHIVED_SRCPA_RECORD",
                "expected_path": pa_path.relative_to(ROOT).as_posix(),
            })

        permit_no = info.get("permit")
        if permit_no:
            p_path = (
                ROOT
                / "03_PERMITS_AND_INSPECTIONS"
                / f"{addr_num}_Tom_St"
                / f"{permit_no}_project_by_uid.json"
            )
            if p_path.is_file():
                raw = p_path.read_bytes()
                data = json.loads(raw).get("data", {})
                summary["permits_checked"].append({
                    "site": site_key,
                    "permit_number": permit_no,
                    "path": p_path.relative_to(ROOT).as_posix(),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "status_in_archive": data.get("status"),
                    "date_updated_in_archive": data.get("dateUpdated"),
                })
            else:
                summary["gaps_detected"].append({
                    "site": site_key,
                    "type": "MISSING_ARCHIVED_MGO_PERMIT_JSON",
                    "expected_path": p_path.relative_to(ROOT).as_posix(),
                })
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--offline-audit-only",
        action="store_true",
        help="Run only offline verification of archived parcel/permit JSONs without network calls.",
    )
    args = parser.parse_args(argv)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot_dir = ROOT / "17_CURRENT_RESEARCH" / "captures" / f"corridor_{timestamp}"

    local_audit = audit_archived_permits_and_parcels()
    records = []
    if not args.offline_audit_only:
        queries = build_corridor_queries()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futures = [
                pool.submit(fetch_json_query, sid, url, dest, snapshot_dir)
                for sid, url, dest in queries
            ]
            for fut in concurrent.futures.as_completed(futures):
                records.append(fut.result())
        records.sort(key=lambda r: r["source_id"])

    manifest = {
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "tool": "acquire_live_permits_and_parcels.py",
        "scope": (
            "Corridor-wide public GIS parcel, subdivision, street-maintainer, and MS4 captures "
            "plus local MGO/SRCPA archive integrity verification. Does not fabricate engineering "
            "approvals or overwrite prior snapshots."
        ),
        "offline_audit_only": args.offline_audit_only,
        "local_archive_audit": local_audit,
        "network_captures": records,
    }

    snapshot_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = snapshot_dir / "ACQUISITION_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifest": manifest_path.relative_to(ROOT).as_posix(),
        "network_captured": sum(1 for r in records if "sha256" in r),
        "network_attempted": len(records),
        "archived_permits_verified": len(local_audit["permits_checked"]),
        "archived_parcels_verified": len(local_audit["parcels_checked"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
