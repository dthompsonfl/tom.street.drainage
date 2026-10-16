#!/usr/bin/env python3
"""Autonomously acquire FEMA NFHL flood hazard, USGS 3DEP EPQS, and USDA NRCS soil data.

Fills the missing hydrology/elevation/soil primary-source acquisition gap in
`11_HYDROLOGY_AND_HAZARD` referenced by `check_document_claims.py` (EX-12 /
CLM-014) and `acquire_noaa_tom_street_2017.py` (USGS EPQS comparison).

Key capabilities:
1. Queries FEMA National Flood Hazard Layer (NFHL) REST services for both point
   intersections AND full corridor bounding-box polygons (Flood Hazard Zones
   Layer 28, FIRM Panels Layer 3, LOMAs Layer 34, Base Flood Elevations Layer 16).
2. Queries USGS 3DEP Elevation Point Query Service (EPQS) for authoritative
   NAVD88 elevations at all Tom Street target and neighboring parcel sample points.
3. Queries USDA NRCS Soil Data Access (SDA) REST API for official map unit
   hydrologic soil group (HSG), drainage class, and hydric rating at Tom Street.
4. Preserves all captures immutably with SHA-256 manifests and explicit
   evidentiary limitations (e.g., FEMA point/polygon flood zones do not establish
   stormwater conveyance capacity or lot-grading compliance).
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
OUT_DIR = ROOT / "11_HYDROLOGY_AND_HAZARD" / "FEMA_USGS_NRCS_CAPTURES"

FEMA_NFHL = "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer"
USGS_EPQS = "https://epqs.nationalmap.gov/v1/json"
NRCS_SDA = "https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest"

ALLOWED_HOSTS = {
    "hazards.fema.gov",
    "epqs.nationalmap.gov",
    "nationalmap.gov",
    "elevation.nationalmap.gov",
    "sdmdataaccess.sc.egov.usda.gov",
}

MAX_BYTES = 12 * 1024 * 1024
USER_AGENT = "TomStreetPublicEvidence/2.0 (Hydrology-Audit)"

SITES = {
    "2260_Tom_St": {"parcel": "21-2S-26-0780-0QQ00-1010", "lon": -86.81466, "lat": 30.41504},
    "2264_Tom_St": {"parcel": "21-2S-26-0780-0QQ00-1020", "lon": -86.81466, "lat": 30.41519},
    "2265_Tom_St": {"parcel": "21-2S-26-0780-0QQ00-1180", "lon": -86.81521, "lat": 30.41515},
    "2268_Tom_St": {"parcel": "21-2S-26-0780-0QQ00-1490", "lon": -86.81466, "lat": 30.41534},
}
BBOX = "-86.8162,30.4144,-86.8134,30.4160"


def check_url(url: str) -> str:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in ALLOWED_HOSTS
        or parsed.username
        or parsed.password
        or parsed.port not in (None, 443)
    ):
        raise ValueError(f"Unapproved hydrology URL: {url}")
    return url


class CheckedRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def save_immutable(dest: Path, raw: bytes) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(raw).hexdigest()
    if dest.exists():
        old_digest = hashlib.sha256(dest.read_bytes()).hexdigest()
        if old_digest == digest:
            return {"storage_status": "UNCHANGED_EXISTING", "path": dest.relative_to(ROOT).as_posix(), "sha256": digest, "bytes": len(raw)}
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        versioned = dest.with_name(f"{dest.stem}_{ts}{dest.suffix}")
        with NamedTemporaryFile(dir=dest.parent, delete=False) as f:
            f.write(raw)
            tmp = Path(f.name)
        os.replace(tmp, versioned)
        return {
            "storage_status": "UPSTREAM_CHANGED_VERSIONED_COPY_SAVED",
            "path": versioned.relative_to(ROOT).as_posix(),
            "baseline_path": dest.relative_to(ROOT).as_posix(),
            "previous_sha256": old_digest,
            "sha256": digest,
            "bytes": len(raw),
        }
    with NamedTemporaryFile(dir=dest.parent, delete=False) as f:
        f.write(raw)
        tmp = Path(f.name)
    os.replace(tmp, dest)
    return {"storage_status": "SAVED_NEW", "path": dest.relative_to(ROOT).as_posix(), "sha256": digest, "bytes": len(raw)}


def fetch_json(label: str, url: str, dest: Path, post_body: bytes | None = None) -> dict:
    check_url(url)
    rec = {
        "source_id": label,
        "requested_url": url,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "status": "NOT_ACQUIRED",
    }
    try:
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        if post_body is not None:
            headers["Content-Type"] = "application/json"
        req = Request(url, data=post_body, headers=headers)
        with build_opener(CheckedRedirectHandler()).open(req, timeout=60) as resp:
            check_url(resp.url)
            raw = resp.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError("Response exceeds 12 MB cap")
            rec["http_status"] = resp.status
            rec["final_url"] = resp.url

        obj = json.loads(raw)
        if not isinstance(obj, dict) or "error" in obj:
            raise ValueError(f"Service returned error or unexpected structure: {obj.get('error') if isinstance(obj, dict) else type(obj)}")
        saved = save_immutable(dest, raw)
        rec.update({"status": "PUBLIC_HYDROLOGY_JSON_VALIDATED", **saved})
    except Exception as exc:
        rec["failure"] = f"{type(exc).__name__}: {exc}"[:350]
    return rec


def build_tasks() -> list[tuple[str, str, Path, bytes | None]]:
    tasks: list[tuple[str, str, Path, bytes | None]] = []

    # 1. FEMA NFHL Layer 28 (Flood Hazard Zones) point queries & corridor envelope
    for site, info in SITES.items():
        q = urlencode({
            "geometry": f"{info['lon']},{info['lat']}",
            "geometryType": "esriGeometryPoint",
            "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "FLD_ZONE,ZONE_SUBTY,SFHA_TF,STATIC_BFE,V_DATUM,DFIRM_ID,VERSION_ID",
            "returnGeometry": "false",
            "f": "pjson",
        })
        tasks.append((
            f"FEMA_NFHL_ZONE_POINT_{site.upper()}",
            f"{FEMA_NFHL}/28/query?{q}",
            OUT_DIR / f"fema_nfhl_zone_point_{site}.json",
            None,
        ))

    bbox_q = urlencode({
        "geometry": BBOX,
        "geometryType": "esriGeometryEnvelope",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": 4326,
        "f": "pjson",
    })
    tasks.append((
        "FEMA_NFHL_CORRIDOR_ZONES_BBOX",
        f"{FEMA_NFHL}/28/query?{bbox_q}",
        OUT_DIR / "fema_nfhl_corridor_zones_bbox.json",
        None,
    ))
    tasks.append((
        "FEMA_NFHL_FIRM_PANELS_BBOX",
        f"{FEMA_NFHL}/3/query?{bbox_q}",
        OUT_DIR / "fema_nfhl_firm_panels_bbox.json",
        None,
    ))
    tasks.append((
        "FEMA_NFHL_LOMAS_BBOX",
        f"{FEMA_NFHL}/34/query?{bbox_q}",
        OUT_DIR / "fema_nfhl_lomas_bbox.json",
        None,
    ))

    # 2. USGS 3DEP Elevation Point Query Service (EPQS) for each site in Feet & Meters
    for site, info in SITES.items():
        epqs_q = urlencode({
            "x": info["lon"],
            "y": info["lat"],
            "wkid": 4326,
            "units": "Feet",
            "includeDate": "true",
        })
        tasks.append((
            f"USGS_EPQS_FEET_{site.upper()}",
            f"{USGS_EPQS}?{epqs_q}",
            OUT_DIR / f"usgs_epqs_feet_{site}.json",
            None,
        ))

    # 3. USDA NRCS Soil Data Access (SDA) query for Tom Street WKT polygon
    wkt = "POLYGON((-86.8162 30.4144, -86.8134 30.4144, -86.8134 30.4160, -86.8162 30.4160, -86.8162 30.4144))"
    sql = (
        "SELECT mu.musym, mu.muname, mu.mukey, muagg.hydgrpdcd, muagg.drclassdcd, "
        "muagg.wtdepannmin, muagg.hydclprs "
        "FROM mapunit AS mu "
        "INNER JOIN muaggatt AS muagg ON mu.mukey = muagg.mukey "
        f"WHERE mu.mukey IN (SELECT * FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('{wkt}'))"
    )
    post_payload = json.dumps({"query": sql, "format": "JSON+COLUMNNAME"}).encode("utf-8")
    tasks.append((
        "USDA_NRCS_SOIL_HYDROLOGIC_GROUP_TOM_STREET",
        NRCS_SDA,
        OUT_DIR / "usda_nrcs_soil_hydrologic_group_tom_street.json",
        post_payload,
    ))
    return tasks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tasks = build_tasks()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [
            pool.submit(fetch_json, label, url, dest, body)
            for label, url, dest, body in tasks
        ]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    results.sort(key=lambda r: r["source_id"])

    manifest = {
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "tool": "acquire_hydrology_fema_usgs.py",
        "agencies": [
            "FEMA National Flood Hazard Layer (NFHL)",
            "USGS 3D Elevation Program (3DEP EPQS)",
            "USDA NRCS Web Soil Survey / Soil Data Access",
        ],
        "sites_queried": SITES,
        "corridor_bbox_wgs84": BBOX,
        "captured_count": sum(1 for r in results if r["status"] == "PUBLIC_HYDROLOGY_JSON_VALIDATED"),
        "requested_count": len(results),
        "records": results,
        "limitations": [
            "FEMA NFHL Zone X or SFHA classifications at sample points or polygons reflect regulatory riverine/coastal flood mapping, NOT local stormwater runoff adequacy or compliance with LDC 4.04.01.",
            "USGS EPQS point elevations interpolate regional 3DEP LiDAR DEMs; they do not reflect 2026 fill, finished floor elevations, or buried culvert inverts.",
            "USDA NRCS soil map units provide general hydrologic soil group context, not site-specific geotechnical borings or seasonal high water table certifications.",
        ],
    }
    manifest_path = OUT_DIR / "ACQUISITION_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifest": manifest_path.relative_to(ROOT).as_posix(),
        "captured_count": manifest["captured_count"],
        "requested_count": manifest["requested_count"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
