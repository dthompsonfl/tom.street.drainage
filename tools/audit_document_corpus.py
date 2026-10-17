#!/usr/bin/env python3
"""Read-only inventory and automated line/page screening of tracked documents.

IMPORTANT: this is a reproducible *screen*, not independent semantic, visual,
engineering, legal, privacy or publication review. A clean run NEVER approves
a source or homeowner letter for distribution.

Output is a private-to-the-runner report artifact, not a Git commit:
  document_inventory.csv, document_findings.csv, document_audit_summary.json

No PDF or captured HTML text is copied into results. The immutable originals
and superseded packets are never changed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {".md", ".html", ".txt"}
DOC_EXTENSIONS = TEXT_EXTENSIONS | {".pdf"}
LINK = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
RISK_PATTERNS = {
    "POSSIBLE_OBSOLETE_PARCEL": re.compile(
        r"\b(?:2264\s+Tom(?:\s+Street|\s+St)?\b.{0,75}(?:0QQ00-1490|\b-1490\b)"
        r"|2268\s+Tom(?:\s+Street|\s+St)?\b.{0,75}(?:0QQ00-1060|\b-1060\b))",
        re.IGNORECASE,
    ),
    "POSSIBLE_UNDATED_ACTIVE_STATUS": re.compile(
        r"\b(?:both permits are active|permit status:\s*active"
        r"|permits are currently active)\b", re.IGNORECASE
    ),
    "POSSIBLE_UNSUPPORTED_CAUSATION": re.compile(
        r"\b(?:construction caused flooding|builder caused flooding"
        r"|drainage violation (?:is|was) proven"
        r"|no approved plans exist)\b", re.IGNORECASE
    ),
    "POSSIBLE_STALE_ORIGINAL_PLAT_STATUS": re.compile(
        r"\b(?:original|recorded|Crescent Shores)\s+plat\b.{0,110}"
        r"\b(?:unverified|not found|not obtained|not retrieved)\b",
        re.IGNORECASE,
    ),
}
CAVEAT = re.compile(
    r"\b(?:incorrect|wrong|formerly|historic|historical|superseded|older|"
    r"archived|at capture|when captured|unverified|not proven|"
    r"misattribut|not a current|outdated|quotation)\b", re.IGNORECASE
)

def tracked_paths(root: Path) -> list[Path]:
    data = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
    names = [x.decode("utf-8", "surrogateescape") for x in data.split(b"\0") if x]
    return sorted((root / name for name in names if Path(name).suffix.lower() in DOC_EXTENSIONS),
                  key=lambda p: p.relative_to(root).as_posix())

def role(relpath: str) -> str:
    if (relpath.startswith(("14_MEETING_PACKET/", "releases/"))):
        return "SUPERSEDED_HISTORICAL"
    if ("/SOURCE/" in relpath or "/ORIGINAL_" in relpath or
        "/SYSTEM_RAW/" in relpath or "/captures/" in relpath or
        relpath.startswith("03_PERMITS_AND_INSPECTIONS/BP-2026-")):
        return "SOURCE_OR_ORIGINAL_PRESERVE"
    if relpath.startswith(("13_PUBLIC_RECORDS_REQUESTS/", "15_RECONCILED_DRAFTS/")):
        return "CURRENT_DRAFT_NOT_APPROVED"
    return "WORKING_OR_HISTORICAL_RESEARCH"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def local_target(base: Path, raw: str) -> Path | None:
    raw = raw.strip().strip("<>")
    if not raw or raw.startswith("#") or raw.lower().startswith(("mailto:", "tel:", "data:")):
        return None
    raw = raw.split(' "', 1)[0].split(" '", 1)[0]
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc:
        return None
    target = unquote(parsed.path)
    if not target:
        return None
    return (ROOT / target.lstrip("/") if target.startswith("/")
            else base.parent / target).resolve()

def check_text(path: Path, findings: list[dict]) -> tuple[int, int, int]:
    rel = path.relative_to(ROOT).as_posix()
    source_role = role(rel)
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    for index, line in enumerate(lines, 1):
        # Only Markdown links are parsed. HTML snapshots are retained as
        # immutable historical capture and not rewritten on heuristic findings.
        if path.suffix.lower() == ".md":
            for m in LINK.finditer(line):
                target = local_target(path, m.group(1))
                if target is not None:
                    try:
                        target.relative_to(ROOT)
                        exists = target.exists()
                    except ValueError:
                        exists = False
                    if not exists:
                        findings.append(dict(
                            path=rel, kind="text", location=f"line:{index}",
                            code="MISSING_LOCAL_LINK_TARGET", priority="REVIEW",
                            review_state="UNVERIFIED", role=source_role
                        ))
        if source_role == "SOURCE_OR_ORIGINAL_PRESERVE":
            continue
        for code, expression in RISK_PATTERNS.items():
            if expression.search(line):
                caveated = bool(CAVEAT.search(line))
                findings.append(dict(
                    path=rel, kind="text", location=f"line:{index}",
                    code=code, priority="CONTEXT_REVIEW" if caveated else "REVIEW",
                    review_state="UNVERIFIED", role=source_role
                ))
    return len(lines), 0, 0

def check_pdf(path: Path, findings: list[dict]) -> tuple[int, int, int]:
    rel = path.relative_to(ROOT).as_posix()
    source_role = role(rel)
    reader = PdfReader(str(path), strict=False)
    n_pages = len(reader.pages)
    with_text = 0
    blank = 0
    for number, page in enumerate(reader.pages, 1):
        try:
            txt = page.extract_text() or ""
        except Exception:
            findings.append(dict(
                path=rel, kind="pdf", location=f"page:{number}",
                code="PDF_TEXT_EXTRACTION_ERROR", priority="REVIEW",
                review_state="UNVERIFIED", role=source_role
            ))
            continue
        if txt.strip():
            with_text += 1
            # Inspect extracted text *line by line* without copying text into
            # report artifacts; PDF lines are an extraction, not visual rows.
            if source_role != "SOURCE_OR_ORIGINAL_PRESERVE":
                for lineno, line in enumerate(txt.splitlines(), 1):
                    for code, expression in RISK_PATTERNS.items():
                        if expression.search(line):
                            findings.append(dict(
                                path=rel, kind="pdf",
                                location=f"page:{number}:text-line:{lineno}",
                                code=code,
                                priority="CONTEXT_REVIEW" if CAVEAT.search(line) else "REVIEW",
                                review_state="UNVERIFIED", role=source_role
                            ))
        else:
            blank += 1
            findings.append(dict(
                path=rel, kind="pdf", location=f"page:{number}",
                code="PAGE_HAS_NO_EXTRACTABLE_TEXT", priority="VISUAL_REVIEW",
                review_state="UNVERIFIED", role=source_role
            ))
    return n_pages, with_text, blank

def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def run(output: Path) -> int:
    output.mkdir(parents=True, exist_ok=True)
    files = tracked_paths(ROOT)
    inventory: list[dict] = []
    findings: list[dict] = []
    for file in files:
        rel = file.relative_to(ROOT).as_posix()
        kind = file.suffix.lower().lstrip(".")
        entry = dict(path=rel, kind=kind, role=role(rel), bytes=file.stat().st_size,
                     sha256=sha256(file), lines_or_pages=0, pdf_text_pages=0,
                     pdf_nontext_pages=0, findings=0, review_state="NOT_SEMANTICALLY_REVIEWED")
        before = len(findings)
        try:
            n, txt, empty = (check_pdf(file, findings) if kind == "pdf"
                             else check_text(file, findings))
            entry.update(lines_or_pages=n, pdf_text_pages=txt, pdf_nontext_pages=empty,
                         review_state="AUTOMATED_LINE_SCAN_ONLY" if kind != "pdf"
                         else "AUTOMATED_PDF_TEXT_EXTRACTION_ONLY")
        except Exception as exc:
            # Do not put exception bodies into public artifacts; file paths and
            # status codes are enough for directed follow-up.
            entry["review_state"] = "UNREADABLE_REQUIRES_HUMAN_CHECK"
            findings.append(dict(path=rel, kind=kind, location="whole-file",
                                 code="DOCUMENT_READ_OR_PARSE_ERROR",
                                 priority="BLOCKER", review_state="UNVERIFIED",
                                 role=role(rel)))
        entry["findings"] = len(findings) - before
        inventory.append(entry)
    cols = ["path", "kind", "role", "bytes", "sha256", "lines_or_pages",
            "pdf_text_pages", "pdf_nontext_pages", "findings", "review_state"]
    fcols = ["path", "kind", "location", "code", "priority", "review_state", "role"]
    write_csv(output / "document_inventory.csv", inventory, cols)
    write_csv(output / "document_findings.csv", findings, fcols)
    counters = Counter(row["kind"] for row in inventory)
    states = Counter(row["review_state"] for row in inventory)
    issue_codes = Counter(row["code"] for row in findings)
    total_pages = sum(x["lines_or_pages"] for x in inventory if x["kind"] == "pdf")
    no_text = sum(x["pdf_nontext_pages"] for x in inventory if x["kind"] == "pdf")
    try:
        commit = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
        ).strip()
    except subprocess.CalledProcessError:
        commit = "UNAVAILABLE"
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": commit, "tracked_document_count": len(inventory),
        "counts_by_extension": dict(sorted(counters.items())),
        "source_bytes": sum(x["bytes"] for x in inventory),
        "text_source_lines": sum(
            x["lines_or_pages"] for x in inventory if x["kind"] != "pdf"),
        "pdf_total_pages": total_pages,
        "pdf_pages_without_extractable_text": no_text,
        "review_states": dict(sorted(states.items())),
        "finding_codes": dict(sorted(issue_codes.items())),
        "document_parse_errors": sum(x["review_state"] ==
                                     "UNREADABLE_REQUIRES_HUMAN_CHECK" for x in inventory),
        "important_limitation": (
            "Every tracked text line was screened by patterns and each PDF page "
            "was passed to an extractor. This is NOT a semantic read of every "
            "sentence, scan-OCR, visual PDF/page review, legal validity check, "
            "engineering opinion, privacy approval, or permission to publish."
        ),
        "required_manual_gates": [
            "Review all flagged lines in source context and classify false positives.",
            "Visually inspect each PDF page, including image-only pages and diagrams.",
            "Verify primary legal source applicability and current county permit status.",
            "Reconcile Markdown-derived PDF parity and legibility before distribution.",
            "Obtain homeowner approval, independent source/privacy review and evidence.",
            "Retain unmodified originals and dated receipt/custody records."
        ],
    }
    (output / "document_audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 1 if summary["document_parse_errors"] else 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".document-audit-output")
    args = parser.parse_args()
    raise SystemExit(run(args.output))
