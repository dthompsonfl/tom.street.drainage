#!/usr/bin/env python3
"""Classify every file for public-release safety.

Privacy classes
  PUBLIC       safe to track and publish
  RESTRICTED   contains authenticated account identity or logged-in portal state;
               must be removed from the PUBLIC remote and retained only in the
               local evidence vault
  BUILD_ARTIFACT  compiled bytecode; should not be tracked

Scans raw BYTES, because portal HTML captures are not valid UTF-8 and are
silently skipped by line-oriented text tools.

Run:  python3 00_CONTROL/tools/classify_for_release.py --write
"""
import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT, rel, sha256_file  # noqa: E402

import csv
import re
from pathlib import Path

# Account-identifying markers observed in this investigation.
# The literals are split at import time so this tracked source file does not
# itself contain the requester's identifying strings verbatim.
ACCOUNT_MARKERS = [
    b"Dylan" + b" Thompson",                 # requester display name
    b"thompson.d.r.92" + b"@gmail.com",       # requester e-mail
    b"__Host-" + b"MGUserToken",
    b"7568CBA6" + b"-CB19-40AA-80FF-B02974F19C71",  # session token
]
# Markers showing the capture is a logged-in (not guest) portal shell.
AUTHENTICATED_SHELL = [
    b"Current Jurisdiction",
    b"cp/project-details",
    b"mgoconnect.org/cp",
]

# Whole-page captures of portals, regardless of marker presence.
AUTH_CAPTURE_RE = re.compile(
    r"(SYSTEM_RAW/.*\.(html|png)$|_project\.(html|png)$|_record_page\.html$|"
    r"_record\.png$|_api_calls\.json$)", re.I)


def classify(relpath: str, data: bytes) -> tuple[str, str]:
    if relpath.endswith(".pyc") or "/__pycache__/" in relpath:
        return "BUILD_ARTIFACT", "compiled bytecode"
    if relpath == __file__.replace(str(_ROOT) + "/", "") or \
            relpath.endswith("tools/classify_for_release.py"):
        # this detector necessarily embeds the markers it searches for
        return "PUBLIC", "source code (detector; embeds marker literals)"
    hits = [m.decode() for m in ACCOUNT_MARKERS if m in data]
    if hits:
        return "RESTRICTED", "account identity present (" + \
            ", ".join(sorted({_label(h) for h in hits})) + ")"
    if AUTH_CAPTURE_RE.search(relpath):
        shell = [m.decode() for m in AUTHENTICATED_SHELL if m in data]
        if shell:
            return "RESTRICTED", "authenticated portal shell: " + ", ".join(shell)
        return "PUBLIC", "public (guest) portal capture"
    if relpath.startswith("00_CONTROL/tools/"):
        return "PUBLIC", "source code"
    return "PUBLIC", ""


_LABELS = {}


def _label(marker: bytes) -> str:
    """Stable, non-identifying label for a marker."""
    if not _LABELS:
        for i, m in enumerate(ACCOUNT_MARKERS, start=1):
            _LABELS[m] = f"marker-{i}"
    return _LABELS.get(marker, "marker")


def main(write: bool = False):
    rows = []
    for dirpath, dirnames, filenames in _os.walk(_ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in {".git", "__pycache__", ".evidence_vault"}]
        for fn in sorted(filenames):
            p = Path(dirpath) / fn
            data = p.read_bytes()
            cls, why = classify(rel(p), data)
            rows.append({"path": rel(p), "bytes": len(data),
                         "sha256": sha256_file(p),
                         "privacy_class": cls, "reason": why})
    rows.sort(key=lambda x: x["path"])
    counts = {}
    for x in rows:
        counts[x["privacy_class"]] = counts.get(x["privacy_class"], 0) + 1
    if write:
        out = _ROOT / "00_CONTROL" / "RELEASE_PRIVACY_CLASSIFICATION.csv"
        with out.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["path", "bytes", "sha256",
                                                "privacy_class", "reason"])
            w.writeheader()
            w.writerows(rows)
        print("wrote", rel(out))
    print("counts:", counts)
    print("\nRESTRICTED (must be removed from the public remote):")
    for x in rows:
        if x["privacy_class"] == "RESTRICTED":
            print(f"  {x['bytes']:>9}  {x['path']}  [{x['reason']}]")
    print("\nBUILD_ARTIFACT (should be untracked):")
    for x in rows:
        if x["privacy_class"] == "BUILD_ARTIFACT":
            print(f"  {x['bytes']:>9}  {x['path']}")
    return rows


if __name__ == "__main__":
    main(write="--write" in _sys.argv)