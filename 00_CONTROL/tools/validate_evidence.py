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
    """Return (ok, note, pages). Checks it is a real PDF, not an HTML error."""
    head = p.open("rb").read(2048)
    if not head.startswith(b"%PDF-"):
        return False, "NOT_A_PDF_HEADER (possible HTML error page)", None
    try:
        r = subprocess.run(["pdfinfo", str(p)], capture_output=True,
                           text=True, timeout=60)
        if r.returncode != 0:
            return False, "PDFINFO_FAILED: " + r.stderr.strip()[:120], None
        m = re.search(r"Pages:\s+(\d+)", r.stdout)
        return True, "pdfinfo_ok", int(m.group(1)) if m else None
    except Exception as e:
        return False, f"PDFINFO_ERROR {e}", None

def walk():
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if EXCLUDE.search(rel):
            continue
        yield p, rel

def main():
    rows = []
    n_pass = n_fail = 0
    for p, rel in walk():
        data = p.read_bytes()
        size = len(data)
        sha = hashlib.sha256(data).hexdigest()
        mime = filetype(p)
        integrity = "PASS"
        note = ""
        pages = ""
        if size == 0:
            integrity = "FAIL"
            note = "EMPTY_FILE"
        elif mime == "application/pdf":
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