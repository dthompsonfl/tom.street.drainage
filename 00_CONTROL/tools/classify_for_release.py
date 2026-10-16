#!/usr/bin/env python3
"""Privacy triage for Tom Street public evidence (no embedded account identifiers).

This is an automated *screen*, never permission for public release. No real
personal identifiers, session values, hashes of sensitive values or cookies may
be added to this tracked source. Keep project-specific sensitive patterns in
an ignored local file and obtain a human privacy sign-off outside Git.

Run: python3 00_CONTROL/tools/classify_for_release.py [--write] [--check]
"""
from __future__ import annotations
import csv
import hashlib
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from paths import ROOT  # noqa: E402

# Generic signature patterns only. Never store literal actual secrets here.
GENERIC_SECRETS = [
    ("private-key-header", re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("auth-header", re.compile(rb"(?im)^\s*(?:authorization|proxy-authorization)\s*[:=]\s*(?:bearer|basic)\s+[A-Za-z0-9._+/-]{12,}")),
    ("set-cookie", re.compile(rb"(?im)^\s*(?:set-cookie|cookie)\s*:\s*[^\r\n]{20,}")),
    ("environment-secret", re.compile(rb"(?im)^\s*[A-Za-z_]*(?:SECRET|TOKEN|PASSWORD|API_KEY)\s*=\s*[^\r\n\s#]{12,}\s*$")),
]
NAME_RISK = re.compile(r"(?:^|/)(?:\.env(?:\..*)?|credentials[^/]*|.*(?:auth|session)[^/]*state[^/]*\.json)$", re.I)
AUTH_CAPTURE_RE = re.compile(r"(?:^|/)(?:SYSTEM_RAW/.*\.(?:html|png)|[^/]*_record_page\.html|[^/]*_project\.html|[^/]*_api_calls\.json)$", re.I)

# This public scanner intentionally doesn't know actual homeowner/account names.
# Use a local, ignored `private_patterns.txt` when a reviewer can safely run it.
def local_markers():
    path = ROOT / ".evidence_vault" / "private_patterns.txt"
    if not path.exists():
        return []
    return [x.strip().encode("utf-8") for x in path.read_text().splitlines()
            if x.strip() and not x.lstrip().startswith("#")]


def classify(path: str, data: bytes, additional=()):
    if path.endswith(".pyc") or "/__pycache__/" in path:
        return "BUILD_ARTIFACT", "compiled output; not distributable"
    if path.startswith(".evidence_vault/") or NAME_RISK.search(path):
        return "RESTRICTED", "restricted pathname"
    for label, pattern in GENERIC_SECRETS:
        if pattern.search(data):
            return "RESTRICTED", label  # never echo a matched secret
    if any(m in data for m in additional):
        return "RESTRICTED", "local-private-pattern"
    if path.startswith("03_PERMITS_AND_INSPECTIONS/") and path.endswith(("_contacts.json", "_project_by_uid.json", "_api.json", "_payments.json")):
        return "REVIEW_REQUIRED", "agency response can contain personal or private third-party contact fields"
    if AUTH_CAPTURE_RE.search(path):
        return "REVIEW_REQUIRED", "portal/raw capture; human provenance and redaction required"
    if path.lower().endswith((".pdf", ".zip", ".png", ".jpg", ".jpeg")):
        return "REVIEW_REQUIRED", "binary/media: inspect metadata and extracted contents"
    return "PUBLIC_CANDIDATE", "mechanical screen only, not release approval"


def scan(include_release=True):
    # Any stale path absent from this fresh walk is never silently classified.
    rows=[]
    marks=local_markers()
    for root, dirs, files in os.walk(ROOT):
        dirs[:]=sorted(d for d in dirs if d not in {".git", ".evidence_vault", "__pycache__"}
                           and (include_release or d != "releases"))
        for name in sorted(files):
            path=Path(root)/name
            rel=path.relative_to(ROOT).as_posix()
            if rel=="00_CONTROL/RELEASE_PRIVACY_CLASSIFICATION.csv":
                continue  # generated output cannot self-hash
            data=path.read_bytes()
            cls, reason=classify(rel,data,marks)
            rows.append(dict(path=rel,bytes=str(len(data)),sha256=hashlib.sha256(data).hexdigest(),privacy_class=cls,reason=reason))
    return sorted(rows,key=lambda row:row["path"])


def main():
    rows=scan()
    if "--write" in sys.argv:
        out=ROOT/"00_CONTROL/RELEASE_PRIVACY_CLASSIFICATION.csv"
        with out.open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=["path","bytes","sha256","privacy_class","reason"])
            w.writeheader();w.writerows(rows)
        print("wrote",out.relative_to(ROOT),len(rows),"rows (self excluded)")
    counts={x:sum(r["privacy_class"]==x for r in rows) for x in {r["privacy_class"] for r in rows}}
    print("classification counts",counts)
    for row in rows:
        if row["privacy_class"] in ("RESTRICTED","BUILD_ARTIFACT"):
            print(row["privacy_class"],row["path"])
    # --check is a mechanical gate. It cannot approve media/third-party disclosure.
    if "--check" in sys.argv:
        forbidden=[r for r in rows if r["privacy_class"] in ("RESTRICTED","BUILD_ARTIFACT")]
        if forbidden:
            print("FAIL: restricted/build artifacts still in public worktree")
            return 1
    return 0

if __name__=="__main__":
    raise SystemExit(main())
