#!/usr/bin/env python3
"""Check the neighbor-facing documentation and publication metadata.

This is a mechanical *gate*, not human sign-off, engineering verification or
a claim that all public records have been acquired. No network connections.
"""
from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def check(label: str, condition: bool) -> None:
    print(("PASS " if condition else "FAIL ") + label)
    if not condition:
        errors.append(label)


def text(path: str) -> str:
    target = ROOT / path
    check("exists: " + path, target.is_file())
    return target.read_text(encoding="utf-8") if target.is_file() else ""


public_paths = [
    "README.md",
    "PUBLIC_EVIDENCE_GUIDE.md",
    "PUBLICATION_AND_VERSIONING.md",
    "15_RECONCILED_DRAFTS/README.md",
    "15_RECONCILED_DRAFTS/01_HOMEOWNER_BRIEF.md",
    "15_RECONCILED_DRAFTS/02_COUNTY_LETTER_DRAFT.md",
    "15_RECONCILED_DRAFTS/03_PROXY_MEETING_NOTES.md",
    "15_RECONCILED_DRAFTS/05_RECORDS_STATUS_AND_FOLLOW_UP.md",
    "15_RECONCILED_DRAFTS/06_COMMISSIONER_COVER_LETTER_DRAFT.md",
    "18_NEIGHBOR_TOOLKIT/README.md",
    "18_NEIGHBOR_TOOLKIT/01_DOCUMENT_AN_OBSERVATION.md",
    "18_NEIGHBOR_TOOLKIT/02_REQUESTS_AND_RESPONSES.md",
    "18_NEIGHBOR_TOOLKIT/03_MEETING_GUIDE.md",
    "18_NEIGHBOR_TOOLKIT/04_PRIVACY_AND_SHARING.md",
    "18_NEIGHBOR_TOOLKIT/templates/MEETING_NOTES.md",
    "18_NEIGHBOR_TOOLKIT/templates/CHANGE_AND_CORRECTION.md",
    "11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/README.md",
    "tools/reviewed_question_report.md",
]
for rel in public_paths:
    content = text(rel)
    if not content:
        continue
    # Do not treat web, fragment, or mail links as local files.
    for raw in re.findall(r"!?(?:\[[^\]]*\])\(([^)]+)\)", content):
        link = raw.split(" #", 1)[0].split(" \"", 1)[0].strip()
        if not link or link.startswith(("#", "http:", "https:", "mailto:", "data:")):
            continue
        destination = link.split("#", 1)[0].split("?", 1)[0]
        try:
            target = (ROOT / rel).parent.joinpath(destination).resolve()
            ok = target.is_relative_to(ROOT.resolve()) and target.exists()
        except (OSError, ValueError):
            ok = False
        check("local link: " + rel + " -> " + destination, ok)

# In claims that are intended to be current, the unsent request count must
# distinguish eight draft files from their nine agency/service templates.
current_claim_paths = [
    "README.md",
    "00_CONTROL/ACTIVE_ASSERTION_CONSISTENCY_2026-10-15.md",
    "00_CONTROL/READING_ORDER_AND_SNAPSHOT_STATUS.md",
    "00_CONTROL/OPEN_QUESTIONS.md",
    "15_RECONCILED_DRAFTS/05_PRIMARY_SOURCE_EXTRACTS.md",
    "15_RECONCILED_DRAFTS/05_RECORDS_STATUS_AND_FOLLOW_UP.md",
    "17_CURRENT_RESEARCH/FIVE_QUESTION_FINDINGS_2026-10-16.md",
]
obsolete = [
    r"five foundational.{0,80}two supplemental",
    r"seven request drafts",
    r"any of the seven",
    r"four explicitly named public-safe markdown drafts",
]
for rel in current_claim_paths:
    value = text(rel)
    for expression in obsolete:
        check("no stale count: " + rel + " / " + expression,
              re.search(expression, value, flags=re.I | re.S) is None)

letters = (
    "15_RECONCILED_DRAFTS/06_COMMISSIONER_COVER_LETTER_DRAFT.md",
    "15_RECONCILED_DRAFTS/02_COUNTY_LETTER_DRAFT.md",
)
for rel in letters:
    value = text(rel)
    check("homeowner attribution: " + rel,
          "Dylan Thompson" in value and "2265 Tom Street" in value and
          "DRAFT" in value and "BP-2026-1621" in value and
          "BP-2026-1612" in value)
    check("no blank name placeholder: " + rel,
          not re.search(r"(?i)(?:name|residential address):\s*_{3,}", value))

track = ROOT / "13_PUBLIC_RECORDS_REQUESTS"
drafts = list(track.glob("*.md"))
check("eight agency request draft files", len(drafts) == 8)
check("all agency request drafts explicitly unsent",
      all("DRAFTED_NOT_SUBMITTED" in p.read_text(encoding="utf-8")[:500]
          for p in drafts))

for name in ("OBSERVATION_LOG.csv", "REQUEST_TRACKER.csv"):
    p = ROOT / "18_NEIGHBOR_TOOLKIT" / "templates" / name
    check("blank template exists: " + name, p.is_file() and len(p.read_text().splitlines()) == 1)

# Must be a current *machine-generated triage inventory*, not an unupdated
# spreadsheet that incorrectly suggests an older repository was checked.
report = ROOT / "00_CONTROL/RELEASE_PRIVACY_CLASSIFICATION.csv"
if report.is_file():
    with report.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    by_name = {r["path"]: r for r in rows}
    check("unique privacy classification paths", len(by_name) == len(rows))
    expected = set()
    for file in ROOT.rglob("*"):
        if not file.is_file():
            continue
        rel = file.relative_to(ROOT).as_posix()
        if rel == "00_CONTROL/RELEASE_PRIVACY_CLASSIFICATION.csv":
            continue
        if any(part in {".git", ".evidence_vault", "__pycache__"} for part in file.parts):
            continue
        expected.add(rel)
    check("privacy inventory covers current worktree", set(by_name) == expected)
    incorrect = []
    for rel in expected & by_name.keys():
        file = ROOT / rel
        row = by_name[rel]
        if row["sha256"] != hashlib.sha256(file.read_bytes()).hexdigest() or row["bytes"] != str(file.stat().st_size):
            incorrect.append(rel)
    check("privacy inventory hashes and sizes are current", not incorrect)
else:
    check("privacy inventory present", False)

# Control the scope of readable public-facing templates. Personal originals
# must never be saved alongside these blank public toolkit files.
allowed = {".md", ".csv"}
unsafe = [p.relative_to(ROOT).as_posix()
          for p in (ROOT / "18_NEIGHBOR_TOOLKIT").rglob("*")
          if p.is_file() and p.suffix.lower() not in allowed]
check("no original resident media in public neighbor toolkit", not unsafe)

for rel in ("14_MEETING_PACKET/README.md", "releases/2026-10-15/README.md"):
    value = text(rel).upper()
    check("legacy archive marked superseded: " + rel, "SUPERSEDED" in value)

print("NEIGHBOR PUBLICATION GATE: " + str(len(errors)) + " failure(s)")
raise SystemExit(bool(errors))
