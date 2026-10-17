#!/usr/bin/env python3
"""Render a source-verified overview of three Tom Street parcels and County road.

This is a contextual GIS map, NOT a site survey, legal boundary, finished grade,
outfall determination, permit approval or drainage engineering interpretation.
No internet calls and no modifications to original source files.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/SANTA_ROSA_COUNTY_PRIMARY_GEOMETRIES.json"
OUT = ROOT / "19_NEIGHBOR_REVIEW/map"
DATE = "2026-10-16"
EXPECTED = {
    "2264": ("212S2607800QQ001020", "Construction-permit site", "#cfe7ef", "#216c82"),
    "2265": ("212S2607800QQ001180", "Existing neighboring home", "#f2e2c7", "#986631"),
    "2268": ("212S2607800QQ001490", "Construction-permit site", "#cfe7ef", "#216c82"),
}
LON0, LON1 = -86.81556, -86.81429
LAT0, LAT1 = 30.41498, 30.41551
LIMITS = [
    "County parcel polygons are GIS approximations, not legal surveys.",
    "The County Maintained road classification does not establish pipe, swale or culvert responsibility.",
    "The historic mapped stormwater problem area is background context, not proof of 2026 flooding.",
    "No measured runoff direction, 2026 grades, culvert inverts, positive outfall or design adequacy is shown.",
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract():
    original = SOURCE.read_bytes()
    data = json.loads(original)
    captures = {c["key"]: c for c in data["captures"]}
    parcel_features = captures["verified_parcel_shapes"]["response"]["features"]
    features = {}
    for address, (number, _role, _fill, _stroke) in EXPECTED.items():
        matches = [
            f for f in parcel_features
            if f.get("attributes", {}).get("PAR_NUM") == number
            and str(f.get("attributes", {}).get("StrNum")) == address
            and f.get("attributes", {}).get("StrName") == "TOM"
        ]
        if len(matches) != 1:
            raise ValueError(f"Cannot uniquely verify County GIS parcel {address}")
        if not matches[0].get("geometry", {}).get("rings"):
            raise ValueError("Missing parcel polygon for " + address)
        features[address] = matches[0]
    road_matches = [
        f for f in captures["tom_street_sections"]["response"]["features"]
        if f["attributes"].get("OBJECTID") == 2036
        and f["attributes"].get("STREETNAME") == "TOM ST"
        and f["attributes"].get("MAINTAINER") == "County Maintained"
    ]
    if len(road_matches) != 1 or not road_matches[0]["geometry"].get("paths"):
        raise ValueError("County maintained road segment not independently identifiable")
    old = captures["historical_stormwater_problem_area_2068"]["response"]["features"]
    if len(old) != 1 or old[0]["attributes"].get("OBJECTID") != 2068:
        raise ValueError("Historical stormwater mapped feature 2068 not verified")
    if "Foreman" not in old[0]["attributes"].get("DataSource", ""):
        raise ValueError("Historical stormwater source context changed")
    return original, captures, features, road_matches[0]


def points_for(feature):
    return feature["geometry"]["rings"][0]


def x_svg(lon):
    return 75 + (lon - LON0) / (LON1 - LON0) * 915


def y_svg(lat):
    return 170 + (LAT1 - lat) / (LAT1 - LAT0) * 350


def point_str(ring):
    return " ".join(f"{x_svg(p[0]):.1f},{y_svg(p[1]):.1f}" for p in ring)


def label_center(ring):
    unique = ring[:-1] if ring[0] == ring[-1] else ring
    return (sum(p[0] for p in unique) / len(unique),
            sum(p[1] for p in unique) / len(unique))


def build_svg(features, road) -> str:
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="800" viewBox="0 0 1080 800" role="img" aria-labelledby="title desc">',
        '<title id="title">Tom Street: three County GIS parcel outlines, road centerline and historic drainage context, October 16 2026</title>',
        '<desc id="desc">2265 Tom Street is an existing home west of the County GIS Tom Street road line. 2264 and 2268 are construction-permit sites east of the line. County maintains the mapped road segment but the ownership of individual drainage assets is unverified. No runoff arrows or elevation data appear.</desc>',
        '<rect width="1080" height="800" fill="white"/>',
        '<text x="75" y="65" font-family="Arial,sans-serif" font-size="32" font-weight="bold" fill="#152e39">Tom Street | location reference</text>',
        '<text x="75" y="100" font-family="Arial,sans-serif" font-size="18" fill="#344c58">Santa Rosa County GIS snapshot - 2026-10-16 - NOT a survey or drainage conclusion</text>',
        '<rect x="74" y="169" width="918" height="352" fill="#fafbfd" stroke="#889aa3" stroke-width="1.5"/>',
        '<defs><clipPath id="map-clip"><rect x="75" y="170" width="915" height="350"/></clipPath></defs>',
        '<g clip-path="url(#map-clip)">',
    ]
    paths = road["geometry"]["paths"]
    for line in paths:
        pts = " ".join(f"{x_svg(p[0]):.1f},{y_svg(p[1]):.1f}" for p in line)
        parts.append(f'<polyline points="{pts}" fill="none" stroke="#677680" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>')
    for addr, feature in sorted(features.items()):
        _parcel, _role, fill, stroke = EXPECTED[addr]
        parts.append(f'<polygon points="{point_str(points_for(feature))}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>')
    parts.append('</g>')
    for addr, feature in sorted(features.items()):
        center = label_center(points_for(feature))
        tx, ty = x_svg(center[0]), y_svg(center[1])
        parts.append(f'<text x="{tx:.1f}" y="{ty-3:.1f}" font-family="Arial,sans-serif" font-size="22" text-anchor="middle" font-weight="bold" fill="#1c2b33">{addr}</text>')
        parts.append(f'<text x="{tx:.1f}" y="{ty+18:.1f}" font-family="Arial,sans-serif" font-size="13" text-anchor="middle" fill="#273b45">Tom St</text>')
    parts += [
        '<text x="1012" y="180" font-family="Arial,sans-serif" font-size="22" font-weight="bold">N</text>',
        '<path d="M1020 193 L1020 228 M1013 205 L1020 192 L1027 205" fill="none" stroke="#1c2b33" stroke-width="3"/>',
        '<text x="425" y="546" font-family="Arial,sans-serif" font-size="18" fill="#566872">Tom Street centerline: County Maintained (GIS ID 2036)</text>',
        '<rect x="76" y="574" width="18" height="16" fill="#cfe7ef" stroke="#216c82"/>',
        '<text x="102" y="588" font-family="Arial,sans-serif" font-size="17">2264 / 2268: construction-permit properties</text>',
        '<rect x="565" y="574" width="18" height="16" fill="#f2e2c7" stroke="#986631"/>',
        '<text x="591" y="588" font-family="Arial,sans-serif" font-size="17">2265: existing neighboring home</text>',
        '<text x="76" y="628" font-family="Arial,sans-serif" font-size="17" font-weight="bold">Historical context (not current drainage evidence)</text>',
        '<text x="76" y="653" font-family="Arial,sans-serif" font-size="15">County GIS stormwater problem-area object 2068 intersects site sample points;</text>',
        '<text x="76" y="674" font-family="Arial,sans-serif" font-size="15">its broader boundary is outside this local view. No pipes, elevations or runoff arrows mapped.</text>',
        '<text x="76" y="713" font-family="Arial,sans-serif" font-size="14">Sources: Santa Rosa County GoMaps layers 8 (parcel IDs), 5 (road ID 2036), 79 (historic area ID 2068).</text>',
        '<text x="76" y="734" font-family="Arial,sans-serif" font-size="14">GIS original capture: 2026-10-16. Boundaries approximate; road ownership of specific assets unknown.</text>',
        '<text x="76" y="760" font-family="Arial,sans-serif" font-size="14" font-weight="bold">Unverified: legal boundaries, finished elevations, pipe inverts, outfalls and water direction.</text>',
        '</svg>',
    ]
    return "\n".join(parts) + "\n"


def build_pdf(outpath: Path, features, road, src_sha: str):
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor

    pdf = canvas.Canvas(str(outpath), pagesize=(612, 792), invariant=1, pageCompression=1)
    pdf.setTitle("Tom Street County GIS reference | 2026-10-16 | NOT A SURVEY")
    pdf.setAuthor("Tom Street drainage evidence project - compiled from Santa Rosa County GIS")
    pdf.setFillColor(HexColor("#152e39"))
    pdf.setFont("Helvetica-Bold", 17)
    pdf.drawString(50, 742, "Tom Street | GIS location reference")
    pdf.setFont("Helvetica", 9.3)
    pdf.drawString(50, 723, "Santa Rosa County, FL | captured 2026-10-16 | not a survey or drainage assessment")
    pdf.setLineWidth(.8)
    pdf.setStrokeColor(HexColor("#889aa3"))
    pdf.setFillColor(HexColor("#fafbfd"))
    pdf.rect(50, 388, 512, 310, fill=1, stroke=1)

    def xp(lon): return 62 + (lon - LON0) / (LON1 - LON0) * 490
    def yp(lat): return 402 + (lat - LAT0) / (LAT1 - LAT0) * 280

    pdf.saveState()
    clipping = pdf.beginPath()
    clipping.rect(51, 389, 510, 308)
    pdf.clipPath(clipping, stroke=0)
    pdf.setStrokeColor(HexColor("#677680"))
    pdf.setLineWidth(4)
    for line in road["geometry"]["paths"]:
        p = pdf.beginPath()
        for i, coord in enumerate(line):
            (p.moveTo if i == 0 else p.lineTo)(xp(coord[0]), yp(coord[1]))
        pdf.drawPath(p, fill=0, stroke=1)
    for addr, feature in sorted(features.items()):
        _n, _role, fill, stroke = EXPECTED[addr]
        pdf.setFillColor(HexColor(fill))
        pdf.setStrokeColor(HexColor(stroke))
        pdf.setLineWidth(1.6)
        p = pdf.beginPath()
        for i, coord in enumerate(points_for(feature)):
            (p.moveTo if i == 0 else p.lineTo)(xp(coord[0]), yp(coord[1]))
        p.close()
        pdf.drawPath(p, fill=1, stroke=1)
    pdf.restoreState()
    for addr, feature in sorted(features.items()):
        lon, lat = label_center(points_for(feature))
        pdf.setFillColor(HexColor("#172a34"))
        pdf.setFont("Helvetica-Bold", 10.5)
        pdf.drawCentredString(xp(lon), yp(lat) + 2, addr)
        pdf.setFont("Helvetica", 7.4)
        pdf.drawCentredString(xp(lon), yp(lat) - 9, "Tom St")

    pdf.setFillColor(HexColor("#324550"))
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(50, 368, "Legend")
    pdf.setFillColor(HexColor("#cfe7ef"));pdf.setStrokeColor(HexColor("#216c82"))
    pdf.rect(50, 344, 12, 11, fill=1, stroke=1)
    pdf.setFillColor(HexColor("#20313a"));pdf.setFont("Helvetica", 8.2)
    pdf.drawString(68, 347, "2264 / 2268: construction-permit sites")
    pdf.setFillColor(HexColor("#f2e2c7"));pdf.setStrokeColor(HexColor("#986631"))
    pdf.rect(320, 344, 12, 11, fill=1, stroke=1)
    pdf.setFillColor(HexColor("#20313a"))
    pdf.drawString(339, 347, "2265: existing neighboring home")
    pdf.setFont("Helvetica", 8.2)
    pdf.drawString(50, 328, "Gray centerline: County-maintained Tom Street segment 2036 (not a right-of-way survey).")
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(50, 301, "Historical mapped stormwater area: County GIS object 2068")
    pdf.setFont("Helvetica", 8.4)
    pdf.drawString(50, 287, "The historic polygon intersects the three site samples; its edge is outside this zoom.")
    pdf.drawString(50, 273, "This is not evidence of a 2026 construction-related drainage failure.")
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(50, 246, "What this map DOES NOT show")
    pdf.setFont("Helvetica", 8.3)
    for i, line in enumerate(LIMITS):
        pdf.drawString(56, 230 - i * 15, "- " + line)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(50, 145, "Official source: Santa Rosa County GoMaps 4.0, layers 8, 5 and 79.")
    pdf.drawString(50, 131, "Saved primary GIS response: SANTA_ROSA_COUNTY_PRIMARY_GEOMETRIES.json")
    pdf.drawString(50, 117, "Source SHA-256: " + src_sha)
    pdf.setFont("Helvetica-Bold", 8.8)
    pdf.drawString(50, 85, "Field-survey grades, pipes, outfalls and runoff direction remain UNVERIFIED.")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(50, 52, "Tom Street neighborhood review candidate | 2026-10-16 | Page 1 of 1")
    pdf.showPage()
    pdf.save()


def build(output: Path = OUT):
    original, captures, parcels, road = extract()
    output.mkdir(parents=True, exist_ok=True)
    svg = output / f"Tom_Street_GIS_Reference_{DATE}.svg"
    pdf = output / f"Tom_Street_GIS_Reference_{DATE}.pdf"
    svg.write_text(build_svg(parcels, road), encoding="utf-8")
    build_pdf(pdf, parcels, road, sha(original))
    manifest = {
        "status": "SOURCE_LINKED_GIS_CONTEXT_NOT_CERTIFIED_SURVEY",
        "version_date": DATE,
        "source_path": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": sha(original),
        "source_acquisition_utc": captures["verified_parcel_shapes"].get("retrieved_utc", "See source parent retrieved_utc"),
        "source_layers": {"parcels": 8, "road": 5, "historic_stormwater": 79},
        "verified_feature_ids": {
            "parcels": {key: f["attributes"]["OBJECTID"] for key, f in parcels.items()},
            "road": 2036, "historic_area": 2068,
        },
        "outputs": [
            {"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}
            for p in (svg, pdf)
        ],
        "limitations": LIMITS,
        "independent_visual_review": "PENDING",
        "human_publication_approval": "PENDING",
    }
    (output / "MAP_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "outputs": manifest["outputs"]}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=OUT)
    args = ap.parse_args()
    build(args.output)
