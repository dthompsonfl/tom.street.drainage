#!/usr/bin/env python3
"""Validate every file in the evidence archive and (re)build

00_CONTROL/EVIDENCE_MANIFEST.csv directly from what is actually on disk.

No entry is marked verified unless the file exists, is non-empty, its type was
identified, and (for PDFs) it parses locally.
"""

import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:  # noqa: E402
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT  # noqa: E402
import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = _ROOT
MANIFEST = ROOT / "00_CONTROL/EVIDENCE_MANIFEST.csv"
SKIP_DIRS = {".git", "00_CONTROL/tools", "__pycache__"}

EXCLUDE = re.compile(r"(^\.git/)|(^\.evidence_vault/)|(^private-)|(^\.env(?:\.|$))|(tools/)|(__pycache__)|(^00_CONTROL/EVIDENCE_MANIFEST\.csv$)")

def filetype(p: Path) -> str:
    try:
        out = subprocess.run(["file", "-b", "--mime-type", str(p)],
                             capture_output=True, text=True, timeout=30)
        return out.stdout.strip()
    except Exception:
        return "unknown"

def file_desc(p: Path) -> str:
    try:
        out = subprocess.run(["file", "-b", str(p)], capture_output=True,
                             text=True, timeout=30)
        return out.stdout.strip()[:160]
    except Exception:
        return ""

def validate_pdf(p: Path):
    """Return (ok, note, pages), using pypdf rather than a host PDF binary."""
    head = p.open("rb").read(2048)
    if not head.startswith(b"%PDF-"):
        return False, "NOT_A_PDF_HEADER (possible HTML error page)", None
    try:
        from pypdf import PdfReader
        with p.open("rb") as source:
            document = PdfReader(source, strict=False)
            pages = len(document.pages)
        if pages <= 0:
            return False, "PDF_HAS_NO_PAGES", None
        return True, "pypdf_ok", pages
    except ImportError:
        return False, "PYPDF_NOT_INSTALLED: install requirements-release.txt", None
    except Exception as exc:
        return False, "PDF_PARSE_FAILED: " + str(exc)[:120], None

# Only immutable original-source captures belong in this hash manifest.
# Drafts, public releases and control CSVs change while being generated.
SOURCE_PREFIXES = (
    "00_CONTROL/SYSTEM_RAW/",
    "02_PROPERTY_AND_PARCELS/",
    "03_PERMITS_AND_INSPECTIONS/",
    "04_ENGINEERING_AND_DRAINAGE/",
    "08_LEGAL_AND_REGULATORY/",
    "09_ENVIRONMENTAL_PERMITS/",
    "11_HYDROLOGY_AND_HAZARD/",
)
SOURCE_EXTENSIONS = frozenset({
    ".pdf", ".json", ".html", ".geojson", ".xml", ".jpg", ".jpeg",
    ".png", ".tif", ".tiff", ".dwg", ".dxf", ".shp", ".dbf",
    ".prj", ".gpkg", ".gdb", ".kml", ".kmz", ".xls", ".xlsx",
})


def is_source_evidence(relative_path: str) -> bool:
    """True only for source evidence, never private vault or mutable outputs."""
    return (
        relative_path.startswith(SOURCE_PREFIXES)
        and Path(relative_path).suffix.lower() in SOURCE_EXTENSIONS
    )


def walk():
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if EXCLUDE.search(rel) or not is_source_evidence(rel):
            continue
        yield p, rel

def main():
    rows = []
    n_pass = n_fail = 0
    for p, rel in walk():
        data = p.read_bytes()
        size = len(data)
        sha = hashlib.sha256(data).hexdigest()
        mime = "text/markdown" if p.suffix.lower() == ".md" else filetype(p)
        integrity = "PASS"
        note = ""
        pages = ""
        if size == 0:
            integrity = "FAIL"
            note = "EMPTY_FILE"
        elif p.suffix.lower() == ".pdf":
            ok, n, pg = validate_pdf(p)
            if not ok:
                integrity = "FAIL"
                note = n
            else:
                pages = pg
        elif mime in ("text/html", "application/xhtml+xml"):
            head = data[:400].lower()
            if b"<html" in head and b"service temporarily unavailable" in head:
                integrity = "FAIL"
                note = "PORTAL_ERROR_PAGE"
        if integrity == "PASS":
            n_pass += 1
        else:
            n_fail += 1
        rows.append({
            "relative_path": rel,
            "file_name": p.name,
            "bytes": size,
            "sha256": sha,
            "file_type_mime": mime,
            "file_description": file_desc(p),
            "pdf_pages": pages,
            "integrity_validation": integrity,
            "integrity_note": note,
            "validated_utc": datetime.now(timezone.utc).isoformat(),
        })
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"files={len(rows)} pass={n_pass} fail={n_fail}")
    for r in rows:
        if r["integrity_validation"] != "PASS":
            print("  FAIL", r["relative_path"], r["integrity_note"])
    print("wrote", MANIFEST)
    if n_fail:
        raise SystemExit(1)

if __name__ == "__main__":
    main()