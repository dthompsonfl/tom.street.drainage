#!/usr/bin/env python3
"""Read-only, content-aware technical screening of every mechanically flagged file.

The output is deliberately public-safe. It NEVER prints text excerpts, contacts,
identifiers, EXIF GPS coordinates, authentication values, or residents' details.
A negative pattern scan is NOT evidence of permission to republish the record.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION = ROOT / "00_CONTROL/RELEASE_PRIVACY_CLASSIFICATION.csv"
OUT = ROOT / "00_CONTROL/PRIVACY_CONTENT_INSPECTION_2026-10-16.csv"
EMAIL = re.compile(r"(?i)(?<![a-z0-9._%+-])[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
ACTUAL_AUTH = re.compile(
    r"(?i)(?:authorization\s*[:=]\s*['\"]?(?:bearer|basic)\s+[a-z0-9._~+/=-]{18,}"
    r"|(?:access_token|refresh_token|session_token|id_token|password)\s*['\"]?\s*[:=]\s*['\"][^'\"\s]{16,})"
)
AUTH_CONTEXT = re.compile(r"(?i)\b(?:Set-Cookie|__RequestVerificationToken|csrfmiddlewaretoken|sessionid)\b")
LIMIT = 3_000_000
FIELDS = [
    "file_path", "source_sha256", "source_bytes", "inspected_git_commit",
    "file_type", "readable_status", "page_or_member_count", "inspected_text_characters",
    "embedded_or_location_metadata", "email_like_pattern_count", "auth_context_pattern",
    "credential_like_pattern", "technical_actual_risk", "limited_inspection_scope",
    "human_disposition", "human_release_approval", "scan_error_category",
]


def digest(path: Path):
    h = hashlib.sha256()
    n = 0
    with path.open("rb") as f:
        for piece in iter(lambda: f.read(1024 * 1024), b""):
            h.update(piece)
            n += len(piece)
    return h.hexdigest(), n


def head_and_tail(path: Path):
    with path.open("rb") as f:
        first = f.read(LIMIT)
        f.seek(0, 2)
        size = f.tell()
        if size <= LIMIT:
            return first, "COMPLETE_RAW_BYTE_WINDOW"
        f.seek(max(0, size - 64 * 1024))
        return first + f.read(64 * 1024), "PARTIAL_RAW_BYTE_WINDOW_FIRST_3MB_LAST_64KB"


def scan(path: Path, original):
    suffix = path.suffix.lower()
    r = {
        "file_type": suffix or "NO_EXTENSION", "readable_status": "FORMAT_UNINSPECTED",
        "page_or_member_count": "", "inspected_text_characters": "0",
        "embedded_or_location_metadata": "NOT_EVALUATED", "email_like_pattern_count": "0",
        "auth_context_pattern": "NO_MATCH_IN_INSPECTED_TEXT",
        "credential_like_pattern": "NO_MATCH_IN_INSPECTED_TEXT",
        "technical_actual_risk": "NO_CONFIRMED_SECURITY_DISCLOSURE_BY_THIS_SCAN",
        "limited_inspection_scope": "CONTENT_NOT_CLEARED_FOR_REUSE",
        "human_disposition": "PENDING_INDEPENDENT_SOURCE_PRIVACY_REVIEW",
        "human_release_approval": "PENDING", "scan_error_category": "",
    }
    raw, coverage = head_and_tail(path)
    text = ""
    try:
        if suffix == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(str(path), strict=False)
            count = len(reader.pages)
            r["page_or_member_count"] = str(count)
            snippets = []
            chars = 0
            scanned_pages = 0
            for page in reader.pages:
                try:
                    extracted = page.extract_text() or ""
                except Exception:
                    extracted = ""
                snippets.append(extracted[: max(0, LIMIT - chars)])
                chars += len(snippets[-1])
                scanned_pages += 1
                if chars >= LIMIT:
                    break
            text = "\n".join(snippets)
            r["readable_status"] = "PDF_PAGES_PARSED"
            r["limited_inspection_scope"] = f"PDF_EXTRACTED_TEXT_{scanned_pages}_OF_{count}_PAGES_AND_PDF_METADATA_ONLY"
            root = reader.trailer.get("/Root", {})
            if hasattr(root, "get_object"):
                root = root.get_object()
            names = root.get("/Names", {}) if hasattr(root, "get") else {}
            if hasattr(names, "get_object"):
                names = names.get_object()
            attachments = bool(names.get("/EmbeddedFiles")) if hasattr(names, "get") else False
            annotations = any(bool(p.get("/Annots")) for p in reader.pages)
            r["embedded_or_location_metadata"] = (
                "PDF_EMBEDDED_FILES_PRESENT" if attachments else
                "PDF_ANNOTATIONS_PRESENT" if annotations else
                "PDF_NO_EMBEDDED_FILES_OR_ANNOTATIONS_DETECTED"
            )
        elif suffix in (".zip",):
            import zipfile
            with zipfile.ZipFile(path) as z:
                filenames = z.namelist()
                r["page_or_member_count"] = str(len(filenames))
                r["readable_status"] = "ZIP_DIRECTORY_INSPECTED_NO_MEMBER_EXTRACTION"
                r["embedded_or_location_metadata"] = "ZIP_CONTAINS_NESTED_FILES"
                r["limited_inspection_scope"] = "ZIP_MEMBER_NAMES_INSPECTED_CONTENT_NOT_OPENED"
                text = "\n".join(filenames)
        elif suffix in (".jpg", ".jpeg", ".png", ".tif", ".tiff"):
            from PIL import Image
            with Image.open(path) as image:
                exif = image.getexif()
                r["readable_status"] = "IMAGE_METADATA_INSPECTED_PIXELS_NOT_INTERPRETED"
                r["page_or_member_count"] = str(getattr(image, "n_frames", 1))
                contains_gps = bool(exif.get(34853))
                r["embedded_or_location_metadata"] = (
                    "IMAGE_LOCATION_METADATA_PRESENT_RESTRICT_DERIVATIVES"
                    if contains_gps else
                    "IMAGE_NO_GPS_EXIF_TAG_DETECTED_OTHER_METADATA_MAY_EXIST"
                )
                r["limited_inspection_scope"] = "EXIF_AND_FILE_HEADER_ONLY; NO_CONTENT_OR_REUSE_APPROVAL"
        elif suffix in (".json", ".html", ".htm", ".md", ".csv", ".txt", ".xml", ".svg"):
            text = raw.decode("utf-8", errors="replace")
            r["readable_status"] = "TEXT_BYTES_SCREENED"
            r["embedded_or_location_metadata"] = "TEXT_FIELDS_UNDER_REVIEW"
            r["limited_inspection_scope"] = coverage + "; TEXT_CLASSIFIER_CANNOT_PROVE_ABSENCE_OF_PRIVATE_FIELDS"
        else:
            r["readable_status"] = "RAW_HEADER_TRAILER_SCREEN_ONLY"
            r["limited_inspection_scope"] = coverage + "; NONDECODABLE_SOURCE_FORMAT_HUMAN_VIEWER_REQUIRED"
    except Exception as exc:
        r["readable_status"] = "CONTENT_PARSER_FAILED"
        r["scan_error_category"] = type(exc).__name__
        r["limited_inspection_scope"] = "PARSER_FAILED_NEEDS_INDEPENDENT_CONTENT_REVIEW"
        r["technical_actual_risk"] = "UNCERTAINTY_PARSER_FAILURE"
    r["inspected_text_characters"] = str(len(text))
    r["email_like_pattern_count"] = str(len(EMAIL.findall(text)))
    if AUTH_CONTEXT.search(text):
        r["auth_context_pattern"] = "AUTH_CONTEXT_TEXT_PRESENT_CONTEXT_REVIEW_REQUIRED"
    if ACTUAL_AUTH.search(text):
        r["credential_like_pattern"] = "CREDENTIAL_LIKE_TEXT_PRESENT_ESCALATE_PRIVATELY"
        r["technical_actual_risk"] = "POTENTIAL_ACTIVE_SECRET_PRIVATE_RESPONSE_REQUIRED"
    elif r["email_like_pattern_count"] != "0":
        r["technical_actual_risk"] = "CONTACT_DETAIL_TEXT_PRESENT_NOT_AUTOMATICALLY_CONFIDENTIAL"
    if "LOCATION_METADATA_PRESENT" in r["embedded_or_location_metadata"]:
        r["technical_actual_risk"] = "LOCATION_METADATA_NEEDS_OWNER_APPROVAL"
    return r


def main(out: Path):
    with CLASSIFICATION.open(newline="", encoding="utf-8") as f:
        items = list(csv.DictReader(f))
    flagged = [x for x in items if x["privacy_class"] == "REVIEW_REQUIRED"]
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    results = []
    for item in flagged:
        path = ROOT / item["path"]
        if not path.is_file() or path.is_symlink():
            raise ValueError("Flagged path does not resolve to an ordinary file: " + item["path"])
        computed, size = digest(path)
        if computed != item["sha256"] or str(size) != item["bytes"]:
            raise ValueError("Source checksum mismatch for " + item["path"])
        r = scan(path, item)
        r.update(file_path=item["path"], source_sha256=computed,
                 source_bytes=str(size), inspected_git_commit=head)
        results.append(r)
    if len(results) != len(flagged):
        raise ValueError("Incomplete flagged-byte inventory")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)
    import collections
    status = collections.Counter(r["readable_status"] for r in results)
    security = sum("POTENTIAL_ACTIVE_SECRET" in r["technical_actual_risk"] for r in results)
    print(json.dumps({"head":head,"flagged_files_screened":len(results),
          "inspection_status_counts":dict(status),"potential_security_findings":security,
          "human_approvals":0,"source_bytes_modified":0},sort_keys=True))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=OUT)
    main(p.parse_args().out)
