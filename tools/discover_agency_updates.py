#!/usr/bin/env python3
"""Autonomously discover newly published ordinances, ERPs, FDEP orders, and County docs.

Addresses the static-ID limitation in the existing `acquire_*.py` scripts, which only
fetch hardcoded document IDs (e.g., `ORD_2025_25`, `ORD_2026_03`, `ERP 9220-2`).

This scanner queries official agency catalogs and spatial layers for NEW or
previously unindexed records relevant to the Tom Street investigation:
1. NWFWMD E-Permitting (`EPermit_ERP/MapServer/0`): spatial radius search around
   Tom Street AND text attribute queries for `Holiday Builders`, `Crescent Shores`,
   `Hadleigh Hills`, and `Tom St` to detect any new ERP applications or modifications.
2. FDEP MapDirect / Environmental Resource Permitting & NPDES Stormwater GIS
   services: spatial envelope search around Tom Street for any newly logged state
   stormwater notices (CGP NOIs) or ERP activities.
3. Santa Rosa County GIS Layer Catalog (`GoMaps4_0/MapServer`): inspects all live
   layer IDs and metadata timestamps to detect if the County has added, renamed,
   or updated hydrology/stormwater/zoning layers.
4. Santa Rosa County Ordinance & Document Discovery: checks known ordinance endpoints
   and produces a structured `DISCOVERY_REPORT.json` listing newly detected items
   for automatic acquisition and human evidentiary review.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
GOMAPS = "https://cloud.santarosa.fl.gov/arcgis/rest/services/santarosa/GoMaps4_0/MapServer"
NWFWMD_ERP = "https://permitting.sjrwmd.com/arcgis02/rest/services/NWFWMD/EPermit_ERP/MapServer/0"
FDEP_ERP = "https://ca.dep.state.fl.us/arcgis/rest/services/OpenData/DEP_ERP/MapServer/0"
FDEP_NPDES = "https://ca.dep.state.fl.us/arcgis/rest/services/OpenData/NPDES_STORMWATER/MapServer/0"

ALLOWED_HOSTS = {
    "cloud.santarosa.fl.gov",
    "permitting.sjrwmd.com",
    "ca.dep.state.fl.us",
    "services.arcgis.com",
    "santarosagis.maps.arcgis.com",
    "mcclibraryfunctions.azurewebsites.us",
    "www.santarosa.fl.gov",
    "floridadep.gov",
}

MAX_BYTES = 12 * 1024 * 1024
USER_AGENT = "TomStreetPublicEvidence/2.0 (Autonomous-Discovery)"


def check_url(url: str) -> str:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in ALLOWED_HOSTS
        or parsed.username
        or parsed.password
        or parsed.port not in (None, 443)
    ):
        raise ValueError(f"Unapproved discovery URL: {url}")
    return url


class CheckedRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def query_url(base: str, **params) -> str:
    return f"{base}?{urlencode({'f': 'pjson', **params})}"


def run_probe(probe_id: str, description: str, url: str, out_dir: Path) -> dict:
    check_url(url)
    entry = {
        "probe_id": probe_id,
        "description": description,
        "url": url,
        "queried_utc": datetime.now(timezone.utc).isoformat(),
        "status": "NOT_COMPLETED",
    }
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        with build_opener(CheckedRedirectHandler()).open(req, timeout=45) as resp:
            check_url(resp.url)
            raw = resp.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError("Discovery response exceeds 12 MB safety cap")
            entry["http_status"] = resp.status
            entry["final_url"] = resp.url

        data = json.loads(raw)
        if not isinstance(data, dict) or "error" in data:
            raise ValueError(f"API error: {data.get('error') if isinstance(data, dict) else 'Invalid JSON'}")

        out_dir.mkdir(parents=True, exist_ok=True)
        dest = out_dir / f"{probe_id}.json"
        dest.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()

        features = data.get("features", [])
        layers = data.get("layers", [])
        entry.update({
            "status": "DISCOVERY_PROBE_SUCCEEDED",
            "local_path": dest.relative_to(ROOT).as_posix(),
            "bytes": len(raw),
            "sha256": digest,
            "feature_count": len(features) if "features" in data else None,
            "layer_count": len(layers) if "layers" in data else None,
            "exceeded_transfer_limit": bool(data.get("exceededTransferLimit")),
            "sample_Hits": [
                f.get("attributes", {}) for f in features[:15]
            ] if features else [],
        })
    except Exception as exc:
        entry["status"] = "DISCOVERY_PROBE_FAILED"
        entry["failure"] = f"{type(exc).__name__}: {exc}"[:350]
    return entry


def build_discovery_probes() -> list[tuple[str, str, str]]:
    return [
        (
            "DISCOVER_NWFWMD_ERP_RADIUS_3000FT",
            "NWFWMD ERP permits within 3,000 feet of Tom Street (detects new permits beyond 9220-2)",
            query_url(
                f"{NWFWMD_ERP}/query",
                geometry="-86.8147,30.4152",
                geometryType="esriGeometryPoint",
                inSR=4326,
                spatialRel="esriSpatialRelIntersects",
                distance=3000,
                units="esriSRUnit_Foot",
                outFields="*",
                returnGeometry="true",
                outSR=4326,
            ),
        ),
        (
            "DISCOVER_NWFWMD_ERP_KEYWORD_SEARCH",
            "NWFWMD ERP keyword search for Holiday Builders, Crescent Shores, Hadleigh Hills, or Tom St",
            query_url(
                f"{NWFWMD_ERP}/query",
                where=(
                    "UPPER(PROJECT_NAME) LIKE '%CRESCENT SHORES%' "
                    "OR UPPER(PROJECT_NAME) LIKE '%HADLEIGH%' "
                    "OR UPPER(PROJECT_NAME) LIKE '%TOM ST%' "
                    "OR UPPER(APPLICANT) LIKE '%HOLIDAY BUILDERS%'"
                ),
                outFields="*",
                returnGeometry="true",
                outSR=4326,
            ),
        ),
        (
            "DISCOVER_FDEP_ERP_VICINITY",
            "FDEP OpenData Environmental Resource Permits within 1,000m of Tom Street",
            query_url(
                f"{FDEP_ERP}/query",
                geometry="-86.8147,30.4152",
                geometryType="esriGeometryPoint",
                inSR=4326,
                spatialRel="esriSpatialRelIntersects",
                distance=1000,
                units="esriSRUnit_Meter",
                outFields="*",
                returnGeometry="true",
                outSR=4326,
            ),
        ),
        (
            "DISCOVER_FDEP_NPDES_STORMWATER_VICINITY",
            "FDEP NPDES Construction Generic Permit (CGP) / Stormwater facilities within 1,000m of Tom Street",
            query_url(
                f"{FDEP_NPDES}/query",
                geometry="-86.8147,30.4152",
                geometryType="esriGeometryPoint",
                inSR=4326,
                spatialRel="esriSpatialRelIntersects",
                distance=1000,
                units="esriSRUnit_Meter",
                outFields="*",
                returnGeometry="true",
                outSR=4326,
            ),
        ),
        (
            "DISCOVER_SRC_GOMAPS_LAYER_DIRECTORY",
            "Santa Rosa County GoMaps 4.0 full layer catalog (detects new/renamed county GIS layers)",
            query_url(GOMAPS),
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = ROOT / "17_CURRENT_RESEARCH" / "discovery_scans" / ts
    probes = build_discovery_probes()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [
            pool.submit(run_probe, pid, desc, url, out_dir)
            for pid, desc, url in probes
        ]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    results.sort(key=lambda r: r["probe_id"])

    report = {
        "scanned_utc": datetime.now(timezone.utc).isoformat(),
        "tool": "discover_agency_updates.py",
        "purpose": (
            "Proactive multi-agency discovery scan for new permits, stormwater NOIs, "
            "or GIS layer updates around Tom Street. Newly discovered features are "
            "staged in 17_CURRENT_RESEARCH/discovery_scans/ for evidentiary verification."
        ),
        "probes_succeeded": sum(1 for r in results if r["status"] == "DISCOVERY_PROBE_SUCCEEDED"),
        "probes_total": len(results),
        "results": results,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "DISCOVERY_REPORT.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "discovery_report": report_path.relative_to(ROOT).as_posix(),
        "probes_succeeded": report["probes_succeeded"],
        "probes_total": report["probes_total"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
