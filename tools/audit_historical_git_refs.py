#!/usr/bin/env python3
"""Public-safe technical scan of Git refs/history for historical exposure indicators.

Scans ALL locally reachable refs. A full checkout (non-shallow) is mandatory.
Does not print historical blob identifiers, paths, emails, passwords or tokens.
It cannot determine credential validity or visually inspect images/PDFs.
An optional PRIVATE report containing path/blob pointers is written only
outside the public repository with restrictive local permissions.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_FULL_BYTES = 6 * 1024 * 1024
EDGE_BYTES = 128 * 1024
DEFAULT_OUT = ROOT / "00_CONTROL" / "HISTORICAL_GIT_TECHNICAL_SCREEN_2026-10-16.json"
EMAIL = re.compile(rb"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
AUTH = re.compile(rb"(?i)\b(?:authorization|set-cookie|cookie|sessionid|csrf[_-]?token|access_token|refresh_token|id_token)\b")
SECRET = [
    ("POSSIBLE_PRIVATE_KEY", re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("POSSIBLE_HTTP_BEARER", re.compile(rb"(?i)\bauthorization\s*[:=]\s*['\"]?(?:bearer|basic)\s+[a-z0-9._~+/-]{18,}")),
    ("POSSIBLE_ENV_SECRET", re.compile(rb"(?im)^\s*[a-z_]*(?:SECRET|TOKEN|PASSWORD|API_KEY)\s*=\s*[^\r\n\s#]{16,}\s*$")),
    ("POSSIBLE_TOKEN_FIELD", re.compile(rb"(?i)['\"](?:access_token|refresh_token|id_token|session_token)['\"]\s*:\s*['\"][^'\"\s]{18,}")),
]
PORTAL_PATH = re.compile(r"(?i)(?:_project\.html|_record_page\.html|_api_calls\.json|mgo_search_page_authenticated|/SYSTEM_RAW/.*(?:mgo_|session))")
BINARY_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".zip", ".laz", ".sid", ".gpkg", ".geotiff", ".pyc", ".gz", ".webp"}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT, stderr=subprocess.DEVNULL)


def verify_full_checkout():
    if git("rev-parse", "--is-shallow-repository").strip() != b"false":
        raise RuntimeError("Refusing to mark partial history scan complete: checkout is shallow")
    if not (ROOT / ".git").exists():
        raise RuntimeError("Git checkout with full history required")


def inventory():
    lines = git("rev-list", "--objects", "--all").decode("utf-8", "replace").splitlines()
    objects = {}
    for line in lines:
        sha, _, path = line.partition(" ")
        if re.fullmatch("[0-9a-f]{40}", sha):
            objects.setdefault(sha, path)
    if not objects:
        raise RuntimeError("No reachable objects")
    p = subprocess.run(
        ["git", "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
        input=("\n".join(objects) + "\n").encode(), cwd=ROOT, capture_output=True, check=True,
    )
    blobs = []
    for line in p.stdout.decode().splitlines():
        items = line.split(" ")
        if len(items) == 3 and items[1] == "blob":
            sha, _kind, size = items
            blobs.append((sha, int(size), objects[sha]))
    if not blobs:
        raise RuntimeError("No reachable blobs")
    return blobs, len(objects)


def private_path_check(path: Path):
    resolved = path.resolve()
    if resolved == ROOT or resolved.is_relative_to(ROOT.resolve()):
        raise ValueError("PRIVATE report destination must be outside the public Git checkout")
    if path.exists() and path.is_symlink():
        raise ValueError("Refusing to follow a private report symlink")
    return resolved


def review(out: Path, private_report: Path | None = None):
    verify_full_checkout()
    blobs, objcount = inventory()
    reference_names = git("for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes", "refs/tags").decode().splitlines()
    if not reference_names:
        raise RuntimeError("No references to review")
    current = git("rev-parse", "HEAD").decode().strip()
    seen = collections.Counter()
    risk = collections.Counter()
    disclosures = []
    read_total = 0
    cmd = subprocess.Popen(
        ["git", "cat-file", "--batch"], cwd=ROOT,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        bufsize=0,
    )
    try:
        assert cmd.stdin is not None and cmd.stdout is not None
        for sha, expected_size, path in blobs:
            cmd.stdin.write((sha + "\n").encode("ascii"))
            cmd.stdin.flush()
            header = cmd.stdout.readline().decode("ascii", "replace").split()
            if len(header) != 3 or header[0] != sha or header[1] != "blob" or int(header[2]) != expected_size:
                raise RuntimeError("Git blob stream / inventory mismatch")
            remained = expected_size
            data = bytearray()
            tail = bytearray()
            scan_full = expected_size <= MAX_FULL_BYTES
            while remained:
                chunk = cmd.stdout.read(min(remained, 1024 * 1024))
                if not chunk:
                    raise RuntimeError("Truncated git object stream")
                remained -= len(chunk)
                if scan_full:
                    data.extend(chunk)
                else:
                    if len(data) < EDGE_BYTES:
                        data.extend(chunk[: max(0, EDGE_BYTES - len(data))])
                    tail.extend(chunk)
                    if len(tail) > EDGE_BYTES:
                        del tail[:-EDGE_BYTES]
            ending = cmd.stdout.read(1)
            if ending != b"\n":
                raise RuntimeError("Git cat-file record delimiter missing")
            inspected = bytes(data) if scan_full else bytes(data + tail)
            read_total += len(inspected)
            seen["reachable_blobs"] += 1
            seen["whole_blob_byte_screened" if scan_full else "oversized_blob_partial_byte_screened"] += 1
            suffix = Path(path).suffix.lower()
            if suffix in BINARY_EXT:
                seen["binary_or_compressed_blob_not_semantically_parsed"] += 1
            else:
                seen["text_or_untyped_blob_byte_screened"] += 1
            flags = []
            if PORTAL_PATH.search(path):
                flags.append("HISTORIC_PORTAL_OR_SESSION_CONTEXT_PATH")
            if EMAIL.search(inspected):
                flags.append("EMAIL_LIKE_CONTENT_PRESENT")
            if AUTH.search(inspected):
                flags.append("AUTH_CONTEXT_TEXT_PRESENT")
            for label, signature in SECRET:
                if signature.search(inspected):
                    flags.append(label)
            for flag in flags:
                risk[flag] += 1
            if flags:
                disclosures.append({
                    "blob_sha": sha,
                    "path": path,
                    "size_bytes": expected_size,
                    "flags": flags,
                    "raw_bytes_coverage": "FULL" if scan_full else "PARTIAL",
                })
    finally:
        if cmd.stdin:
            cmd.stdin.close()
        if cmd.stdout:
            cmd.stdout.close()
        try:
            cmd.wait(timeout=10)
        except subprocess.TimeoutExpired:
            cmd.kill()
            cmd.wait()
    if cmd.returncode not in (0, -13):
        raise RuntimeError("git cat-file process exited abnormally")
    summary = {
        "review_type": "AUTOMATED_FULL_REACHABLE_REF_BYTE_SCREEN_NOT_INDEPENDENT_HUMAN_PRIVACY_CLEARANCE",
        "source_git_head": current,
        "git_checkout_shallow": False,
        "git_refs_examined": len(reference_names),
        "all_refs_blob_objects_enumerated": objcount,
        "source_bytes_modified": 0,
        "scan_counts": dict(sorted(seen.items())),
        "indicators": dict(sorted(risk.items())),
        "potential_credential_like_blobs": sum(
            1 for item in disclosures if any(flag.startswith("POSSIBLE_") for flag in item["flags"])
        ),
        "known_historic_authenticated_capture_path_hits": risk["HISTORIC_PORTAL_OR_SESSION_CONTEXT_PATH"],
        "outside_git_forks_and_expired_or_unreachable_objects": "NOT_EXAMINED",
        "binary_pdf_and_image_embedded_contents": "NOT_SEMANTICALLY_SCREENED",
        "original_source_availability_or_redistribution_rights": "NOT_ESTABLISHED_BY_THIS_SCREEN",
        "session_validity_or_revocation": "NOT_EXAMINED",
        "independent_human_security_review": "PENDING",
        "history_rewrite_authorization": "NOT_GRANTED",
        "source_capture_deletion_or_history_rewrite_performed": False,
        "next_action": "Authorized account-holder security reviewer must privately inspect historic suspect blobs; invalidate any active credentials, maintain preservation/rollback plan; do not publish private values.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if private_report:
        path = private_path_check(private_report)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"reviewed_head": current, "suspect_blob_paths": disclosures}, f, indent=2)
            f.write("\n")
    print("HISTORICAL_SCAN_SUMMARY_JSON=" + json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--private-report", type=Path, default=None,
                    help="Optional owner-only report with blob/path pointers, outside checkout, new file only")
    args = ap.parse_args()
    review(args.out, args.private_report)


if __name__ == "__main__":
    main()
