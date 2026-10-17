#!/usr/bin/env python3
"""Build one pinned, DRAFT-ONLY Tom Street neighborhood review candidate.

No submission, approval, publication or collection of resident records occurs.
Run from a checkout of the exact intended source commit after regenerating PDFs.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import zipfile
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT_TIMEZONE = "America/Chicago"
OUT = ROOT / "19_NEIGHBOR_REVIEW" / "candidates"
SELECTED = [
    ("NEIGHBOR_REVIEW_GUIDE.md", "Navigation, audience and feedback instructions"),
    ("15_RECONCILED_DRAFTS/01_HOMEOWNER_BRIEF.md", "Plain-language current concern"),
    ("15_RECONCILED_DRAFTS/pdf/Tom_Street_Reconciled_Public_Meeting_Draft.pdf", "Unsigned five-page meeting draft"),
    ("18_NEIGHBOR_TOOLKIT/print/03_Event_Observation.pdf", "Blank one-page observation worksheet"),
    ("18_NEIGHBOR_TOOLKIT/print/Tom_Street_Neighbor_Documentation_Forms.pdf", "Complete blank 18-page resident worksheet set"),
    ("19_NEIGHBOR_REVIEW/map/Tom_Street_GIS_Reference_2026-10-16.svg", "Accessible County GIS reference image"),
    ("19_NEIGHBOR_REVIEW/map/Tom_Street_GIS_Reference_2026-10-16.pdf", "Print-friendly County GIS reference"),
    ("PUBLIC_EVIDENCE_GUIDE.md", "Short source index and proof limits"),
    ("00_CONTROL/OPEN_QUESTIONS.md", "Unresolved engineering and agency records questions"),
    ("15_RECONCILED_DRAFTS/05_RECORDS_STATUS_AND_FOLLOW_UP.md", "Blank follow-up tracking draft"),
    ("CONTRIBUTING.md", "Correction reporting and private-submission warning"),
]
READ_ME = """TOM STREET | NEIGHBORHOOD REVIEW CANDIDATE
============================================
STATUS: UNAPPROVED CANDIDATE - FOR TECHNICAL / OWNER REVIEW ONLY
This is NOT a signed letter, sent request, engineer survey, County approval,
confirmed resident consent or public-release authorization.

Reading order
-------------
1. NEIGHBOR_REVIEW_GUIDE.md
2. 15_RECONCILED_DRAFTS/01_HOMEOWNER_BRIEF.md
3. 19_NEIGHBOR_REVIEW/map/Tom_Street_GIS_Reference_2026-10-16.pdf
4. 15_RECONCILED_DRAFTS/pdf/Tom_Street_Reconciled_Public_Meeting_Draft.pdf
5. PUBLIC_EVIDENCE_GUIDE.md and 00_CONTROL/OPEN_QUESTIONS.md
6. 18_NEIGHBOR_TOOLKIT/print/03_Event_Observation.pdf (blank practice form)

Use the exact version and source commit recorded in the included manifest.
The map is County GIS reference only, not a surveyed design or proof of cause.
Keep your original photos, completed forms, private records, device metadata,
permissions and authenticated portal captures OUT of this public repository.
For factual corrections use CONTRIBUTING.md. Private material must be handled
through a coordinator-arranged restricted transfer, never public GitHub issues.

No distribution as an approved neighborhood edition until the exact package
passes real-neighbor tests, independent source/privacy review, specific author
consents and a recorded human publication decision.
"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def candidate_date(source_commit_timestamp: str) -> str:
    """Use the pinned commit's local calendar date, never a hardcoded release date."""
    instant = datetime.fromisoformat(source_commit_timestamp.replace("Z", "+00:00"))
    if instant.tzinfo is None:
        raise ValueError("Git commit timestamp must contain a timezone")
    return instant.astimezone(ZoneInfo(SOURCE_COMMIT_TIMEZONE)).date().isoformat()


def check_source_parity():
    from pypdf import PdfReader
    draft_manifest = json.loads((ROOT / "15_RECONCILED_DRAFTS/pdf/RELEASE_MANIFEST.json").read_text())
    if draft_manifest.get("release_status") != "DRAFT_NOT_APPROVED_FOR_EXTERNAL_DISTRIBUTION":
        raise ValueError("Expected existing meeting packet to remain an unsigned draft")
    for item in draft_manifest["outputs"]:
        p = ROOT / "15_RECONCILED_DRAFTS/pdf" / item["pdf"]
        if not p.is_file() or sha(p.read_bytes()) != item["sha256"]:
            raise ValueError("Meeting packet PDF manifest mismatch: " + item["pdf"])
        if item["source_md"] in {"merge of approved-scope source drafts", None}:
            continue
        original = ROOT / "15_RECONCILED_DRAFTS" / item["source_md"]
        if sha(original.read_bytes()) != item["source_sha256"]:
            raise ValueError("Stale generated PDF source: " + item["source_md"])
    for p, expected in [
        ("15_RECONCILED_DRAFTS/pdf/Tom_Street_Reconciled_Public_Meeting_Draft.pdf", 5),
        ("18_NEIGHBOR_TOOLKIT/print/Tom_Street_Neighbor_Documentation_Forms.pdf", 18),
        ("19_NEIGHBOR_REVIEW/map/Tom_Street_GIS_Reference_2026-10-16.pdf", 1),
    ]:
        pages = PdfReader(str(ROOT / p)).pages
        if len(pages) != expected:
            raise ValueError(f"{p}: expected {expected} pages, got {len(pages)}")
        if any(not page.extract_text().strip() for page in pages):
            raise ValueError(p + " contains an unextractable/blank page")
    map_manifest = json.loads((ROOT / "19_NEIGHBOR_REVIEW/map/MAP_MANIFEST.json").read_text())
    for item in map_manifest["outputs"]:
        p = ROOT / item["path"]
        if sha(p.read_bytes()) != item["sha256"] or len(p.read_bytes()) != item["bytes"]:
            raise ValueError("Map output differs from source-linked map manifest")
    if map_manifest["independent_visual_review"] != "PENDING":
        raise ValueError("Do not invent completed visual review")


def build():
    source_commit = git("rev-parse", "HEAD")
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise RuntimeError("Unable to pin checkout source commit")
    timestamp = git("show", "-s", "--format=%cI", "HEAD")
    dated_source = candidate_date(timestamp)
    check_source_parity()
    contents = {}
    manifest_entries = []
    for path, purpose in SELECTED:
        p = ROOT / path
        if not p.is_file():
            raise FileNotFoundError(path)
        data = p.read_bytes()
        contents[path] = data
        manifest_entries.append({
            "path": path, "bytes": len(data), "sha256": sha(data),
            "purpose": purpose, "status": "DRAFT_OR_BLANK_MATERIAL",
        })
    fingerprint_lines = [f"{name}  {sha(data)}" for name, data in sorted(contents.items())]
    input_fingerprint = sha(("\n".join(fingerprint_lines) + "\n").encode("utf-8"))[:12]
    edition = f"Tom_Street_Neighborhood_Review_{dated_source}_v1_{source_commit[:12]}_{input_fingerprint}_CANDIDATE"
    intro = READ_ME.replace("STATUS: UNAPPROVED", f"VERSION: {edition}\nSOURCE COMMIT: {source_commit}\nSTATUS: UNAPPROVED")
    contents["START_HERE.txt"] = intro.encode("utf-8")
    manifest_entries.insert(0, {
        "path": "START_HERE.txt", "bytes": len(contents["START_HERE.txt"]),
        "sha256": sha(contents["START_HERE.txt"]),
        "purpose": "Status, version and reading order", "status": "UNAPPROVED_CANDIDATE",
    })
    manifest = {
        "edition_id": edition,
        "source_commit": source_commit,
        "source_commit_timestamp": timestamp,
        "candidate_date": dated_source,
        "candidate_date_basis": "America/Chicago calendar date of pinned source commit; not a public release date",
        "input_fingerprint": input_fingerprint,
        "build_timestamp_basis": "source-commit timestamp for versioning; actual build UTC is in separate summary",
        "edition_status": "CANDIDATE_NOT_AUTHORIZED_FOR_PUBLIC_DISTRIBUTION",
        "publication_decision": "AWAITING_HUMAN_APPROVAL",
        "author_and_speaker_approval": "PENDING",
        "independent_privacy_and_source_review": "PENDING",
        "two_real_neighbor_usability_tests": "PENDING",
        "visual_pdf_review": "PENDING",
        "government_originals_included": False,
        "resident_private_originals_included": False,
        "no_claim_of_engineering_causation": True,
        "supersedes": None,
        "distribution_notes": "Technical review only; do not describe as personally approved or officially submitted.",
        "included_files": manifest_entries,
    }
    contents["EDITION_MANIFEST.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    checksums = "".join(f"{sha(contents[p])}  {p}\n" for p in sorted(contents))
    contents["SHA256SUMS.txt"] = checksums.encode("ascii")
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / (edition + ".zip")
    data_path = OUT / (edition + ".summary.json")
    import io
    memory = io.BytesIO()
    zip_day = tuple(int(component) for component in dated_source.split("-"))
    with zipfile.ZipFile(memory, "w") as archive:
        for path in sorted(contents):
            info = zipfile.ZipInfo(path, date_time=(*zip_day, 12, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, contents[path], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    data = memory.getvalue()
    if target.exists() and target.read_bytes() != data:
        raise RuntimeError("Refusing to replace an existing different candidate with the same edition ID")
    target.write_bytes(data)
    summary = {"status": manifest["edition_status"], "edition_id": edition,
               "source_commit": source_commit, "zip_sha256": sha(data),
               "zip_bytes": len(data), "included_file_count": len(contents),
               "build_timestamp_utc": datetime.now(timezone.utc).isoformat(),
               "human_approval": "PENDING"}
    data_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    build()
