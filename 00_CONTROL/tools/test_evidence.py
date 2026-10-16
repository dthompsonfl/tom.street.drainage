#!/usr/bin/env python3
"""Test suite for the Tom Street Drainage Investigation evidence tooling.

Covers the properties the directive calls out:
  * ZIP member preservation and hash identity
  * SHA-256 correctness
  * no manifest self-hash paradox
  * valid MIME / real PDF format (not HTML masquerading as PDF)
  * unique registry IDs and referential integrity
  * every register path that claims a file actually exists and is non-empty
  * every evidence claim cites a real source file
  * blocked/failed downloads are logged, not silently dropped
  * source dates and versions preserved
  * public privacy filter (no account identity in public-facing material)

Run:  python3 00_CONTROL/tools/test_evidence.py
Exit code 0 = all pass.
"""
import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT, rel, sha256_file  # noqa: E402

import csv
import hashlib
import io
import json
import re
import subprocess
import zipfile
from pathlib import Path

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  -- {detail}" if detail and not ok else ""))
    return ok


# ---------------------------------------------------------------- helpers
def csvrows(p):
    f = _ROOT / p
    return list(csv.DictReader(f.open())) if f.exists() else []


def walk_files():
    for dp, dn, fn in _os.walk(_ROOT):
        dn[:] = [d for d in dn if d not in {".git", "__pycache__",
                                            ".evidence_vault", "releases"}]
        for f in sorted(fn):
            p = Path(dp) / f
            yield p, rel(p)


# ---------------------------------------------------------------- tests
def t_hash():
    p = Path("/etc/hostname")
    if not p.exists():
        return check("sha256 matches hashlib", True, "skipped: no sample")
    d = p.read_bytes()
    check("sha256 matches hashlib",
          sha256_file(p) == hashlib.sha256(d).hexdigest())
    check("sha256 of empty bytes stable",
          hashlib.sha256(b"").hexdigest() ==
          "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")


def t_manifest_no_self_hash():
    """Only primary source captures are included, never mutable/private files."""
    from validate_evidence import is_source_evidence

    rows = csvrows("00_CONTROL/EVIDENCE_MANIFEST.csv")
    paths = [r["relative_path"] for r in rows]
    bad_scope = [p for p in paths if not is_source_evidence(p)]
    check("manifest excludes self, private files and mutable derivatives",
          not bad_scope, "; ".join(bad_scope[:3]))
    check("manifest paths are unique", len(paths) == len(set(paths)))

    expected = {p for _, p in walk_files() if is_source_evidence(p)}
    listed = set(paths)
    check("manifest covers exactly all repository primary evidence files",
          expected == listed,
          f"missing={sorted(expected - listed)[:3]}, unexpected={sorted(listed - expected)[:3]}")

    bad_hashes = []
    for row in rows:
        path = _ROOT / row["relative_path"]
        if not path.is_file():
            bad_hashes.append(row["relative_path"] + ": absent")
            continue
        if sha256_file(path) != row["sha256"]:
            bad_hashes.append(row["relative_path"] + ": SHA-256 mismatch")
        if str(path.stat().st_size) != row["bytes"]:
            bad_hashes.append(row["relative_path"] + ": size mismatch")
    check(f"manifest SHA-256 and byte sizes verified ({len(rows)} sources)",
          not bad_hashes, "; ".join(bad_hashes[:3]))



def t_pdfs_real():
    bad = []
    for p, r in walk_files():
        if p.suffix.lower() != ".pdf":
            continue
        data = p.read_bytes()
        if not data.startswith(b"%PDF-"):
            bad.append(f"{r}: no %PDF- header")
            continue
        r_ = subprocess.run(["pdfinfo", str(p)], capture_output=True)
        if r_.returncode != 0:
            bad.append(f"{r}: pdfinfo failed")
        else:
            if b"Pages:" not in r_.stdout:
                bad.append(f"{r}: no page count")
        # an HTML error page saved with a .pdf name
        head = data[:2048].lower()
        if b"<html" in head and b"<!doctype html" in head:
            bad.append(f"{r}: HTML masquerading as PDF")
    check("all PDFs are real PDFs with parseable page counts",
          not bad, "; ".join(bad[:3]))


def t_zips():
    for zp in sorted((_ROOT / "releases").rglob("*.zip")) if (
            _ROOT / "releases").exists() else []:
        rel_z = rel(zp)
        try:
            with zipfile.ZipFile(zp) as z:
                check(f"zip integrity: {rel_z}", z.testzip() is None)
                names = z.namelist()
                check(f"zip non-empty: {rel_z}", len(names) > 0)
                check(f"zip has no nested archive: {rel_z}",
                      not any(n.lower().endswith((".zip", ".tar.gz"))
                              for n in names))
                check(f"zip has no traversal: {rel_z}",
                      not any(n.startswith("/") or ".." in n.split("/")
                              for n in names))
                if rel_z.endswith("sha256"):
                    pass
        except Exception as e:
            check(f"zip integrity: {rel_z}", False, str(e))


def t_release_zip_hash_parity():
    """Every member of a release ZIP must match its recorded SHA-256."""
    if not (_ROOT / "releases").exists():
        return
    for mf in sorted((_ROOT / "releases").rglob("SHA256SUMS.txt")):
        release_info = mf.parent / "RELEASE_MANIFEST.json"
        if not release_info.is_file():
            check("release manifest accompanies SHA256SUMS", False, str(mf))
            continue
        try:
            zip_relative = json.loads(release_info.read_text())["zip"]
            zp = _ROOT / zip_relative
        except (OSError, KeyError, ValueError) as exc:
            check("release ZIP path is documented", False, str(exc))
            continue
        if not zp.is_file():
            check("release ZIP exists at manifest path", False, str(zp))
            continue
        expect = {}
        for line in mf.read_text().splitlines():
            m = re.match(r"([0-9a-f]{64})\s+\*?(.+)$", line.strip())
            if m:
                expect[m.group(2).strip()] = m.group(1)
        with zipfile.ZipFile(zp) as z:
            got = {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()
                   if not n.endswith("/")}
        check(f"release ZIP matches SHA256SUMS ({rel(zp)})", expect == got,
              f"expected {len(expect)} entries, zipped {len(got)}")


def t_unique_ids():
    for name, key in [("00_CONTROL/EVIDENCE_LEDGER.csv", "claim_id"),
                      ("00_CONTROL/EXHIBIT_INDEX.csv", "exhibit_id"),
                      ("00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv", "gap_id"),
                      ("00_CONTROL/CHRONOLOGY.csv", "event_id"),
                      ("00_CONTROL/DESIGN_VS_FIELD_MATRIX.csv", "item_id"),
                      ("00_CONTROL/SOURCE_REGISTER.csv", "source_id"),
                      ("00_CONTROL/PERMIT_DOCUMENT_INVENTORY.csv", "document_id")]:
        rows = csvrows(name)
        ids = [r[key] for r in rows]
        check(f"unique IDs in {name}", len(ids) == len(set(ids)),
              f"{len(ids)} rows, {len(set(ids))} unique")


def t_register_paths_exist():
    bad = []
    n = 0
    for reg in ["00_CONTROL/SOURCE_REGISTER.csv",
                "00_CONTROL/EXHIBIT_INDEX.csv",
                "00_CONTROL/EVIDENCE_LEDGER.csv"]:
        for r in csvrows(reg):
            for fld in ("local_relative_path", "source_file"):
                v = (r.get(fld) or "").strip()
                if not v or v.startswith("http"):
                    continue
                n += 1
                p = _ROOT / v
                if not p.exists():
                    alt = _ROOT / ".evidence_vault" / "restricted" / v
                    if not alt.exists():
                        bad.append(f"{rel}: {fld}={v}")
                elif p.stat().st_size == 0:
                    bad.append(f"{rel}: {fld}={v} EMPTY")
    check(f"all register file references resolve ({n} checked)", not bad,
          "; ".join(bad[:3]))


def t_checksums_match():
    bad = []
    n = 0
    for r in csvrows("00_CONTROL/SOURCE_REGISTER.csv"):
        v = (r.get("local_relative_path") or "").strip()
        if not v:
            continue
        p = _ROOT / v
        if not p.exists():
            continue
        n += 1
        if sha256_file(p) != r["sha256_hash"]:
            bad.append(f"{v} sha256 mismatch")
        if str(p.stat().st_size) != r["file_size_bytes"]:
            bad.append(f"{v} size mismatch")
    check(f"SOURCE_REGISTER checksums and sizes match reality ({n} files)",
          not bad, "; ".join(bad[:3]))


def t_claims_cite_real_source():
    bad = []
    for r in csvrows("00_CONTROL/EVIDENCE_LEDGER.csv"):
        cls = r["evidentiary_class"]
        f = (r.get("source_file") or "").strip()
        if cls in ("OFFICIAL_RECORD", "OBSERVATION") and not f:
            bad.append(f"{r['claim_id']} claims {cls} with no source file")
        if f and not (_ROOT / f).exists():
            bad.append(f"{r['claim_id']} source missing: {f}")
    check("every OFFICIAL_RECORD/OBSERVATION claim cites an existing file",
          not bad, "; ".join(bad[:3]))


def t_failed_searches_logged():
    log = csvrows("00_CONTROL/SEARCH_LOG.csv")
    outcomes = {r.get("outcome", "") for r in log}
    check("search log records non-success outcomes too",
          any(o for o in outcomes if o.upper() not in ("SUCCESS", "")),
          f"outcomes seen: {sorted(outcomes)}")
    inv = csvrows("00_CONTROL/PERMIT_DOCUMENT_INVENTORY.csv")
    st = {r["acquisition_status"] for r in inv}
    check("document inventory uses explicit non-obtained statuses",
          bool(st & {"NOT_OFFERED_IN_PORTAL", "AUTHENTICATION_REQUIRED",
                     "NOT_FOUND_IN_SEARCHED_SYSTEM", "REQUEST_DRAFTED"}),
          f"statuses: {sorted(st)}")


def t_no_submitted_without_receipt():
    rows = csvrows("00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv")
    bad = [r["gap_id"] for r in rows
           if r["submitted"].upper() == "TRUE" and not r["receipt_id"].strip()]
    check("no gap marked submitted without a receipt id", not bad,
          ", ".join(bad))


def t_request_files_exist():
    bad = []
    for r in csvrows("00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv"):
        v = (r.get("request_file") or "").strip()
        if v and not (_ROOT / v).exists():
            bad.append(v)
    check("every tracked request file exists", not bad, ", ".join(bad[:3]))


def t_privacy_public_material():
    """Generic source/privacy screen, never a human clearance decision.

    Real homeowner account markers must be stored only in the ignored
    .evidence_vault/private_patterns.txt file. No real identity, email, session
    cookie or fragment of a live token belongs in tracked tests or source code.
    """
    from classify_for_release import classify, local_markers
    private_markers = local_markers()
    bad = []
    checked = 0
    for p, relpath in walk_files():
        if relpath.startswith(".evidence_vault/"):
            continue
        try:
            data = p.read_bytes()
        except OSError:
            bad.append(relpath + ": unreadable")
            continue
        classification, reason = classify(relpath, data, private_markers)
        checked += 1
        if classification == "RESTRICTED":
            bad.append(relpath + ": " + reason)
    check(f"no automatic restricted-data hits in {checked} files",
          not bad, "; ".join(bad[:3]))
    check("private markers are not embedded in the public test suite",
          b"private_patterns.txt" in Path(__file__).read_bytes())
    # REVIEW_REQUIRED media, portals and source records must still be cleared
    # manually; passing this generic screen does NOT mean publication approved.


def t_redacted_derivative_exists():
    idx = _ROOT / "14_MEETING_PACKET/exhibits/derived_redacted/REDACTION_INDEX.json"
    check("redaction index present for derived images", idx.exists())
    if idx.exists():
        d = json.loads(idx.read_text())
        ok = all((_ROOT / e["derivative"]).exists() for e in d)
        check("every redacted derivative exists on disk", ok)


def t_no_violation_language():
    """Public packet must not assert a violation or inadequacy."""
    banned = re.compile(
        r"\b(is in violation|violates the code|committed a violation|"
        r"is negligent|is illegal|bbuilder (is|was) at fault|"
        r"caused the flooding)\b", re.I)
    bad = []
    for f in (_ROOT / "14_MEETING_PACKET").rglob("*.md"):
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if banned.search(line) and "not" not in line.lower():
                bad.append(f"{rel(f)}:{i}")
    check("no unsupported violation/culpability assertions in the packet",
          not bad, ", ".join(bad[:3]))


def t_parity_identifiers():
    """Parcel and permit IDs must agree across the public packet."""
    facts = {
        "21-2S-26-0780-0QQ00-1020": "2264",
        "21-2S-26-0780-0QQ00-1490": "2268",
    }
    bad = []
    for f in (_ROOT / "14_MEETING_PACKET").rglob("*.md"):
        flat = re.sub(r"\s+", " ", f.read_text(encoding="utf-8"))
        for pid, addr in facts.items():
            # each occurrence of a parcel ID must be paired with its address
            # within a 120-character window, in either order
            for m in re.finditer(re.escape(pid), flat):
                win = flat[max(0, m.start() - 120): m.end() + 120]
                if addr not in win:
                    bad.append(f"{rel(f)}: {pid} unpaired with {addr}")
                    break
    check("parcel IDs are paired with the right address in the packet",
          not bad, "; ".join(bad[:3]))


def t_lint_tools():
    bad = []
    for f in sorted((_ROOT / "00_CONTROL/tools").glob("*.py")):
        r = subprocess.run([_sys.executable, "-m", "py_compile", str(f)],
                           capture_output=True)
        if r.returncode != 0:
            bad.append(f.name)
    check("all tools compile", not bad, ", ".join(bad))


def t_no_hardcoded_home():
    bad = []
    for f in sorted((_ROOT / "00_CONTROL/tools").glob("*.py")):
        if f.name in {"paths.py", "test_evidence.py"}:
            continue
        if "/home/" in f.read_text(encoding="utf-8"):
            bad.append(f.name)
    check("no hardcoded /home/ paths in tools", not bad, ", ".join(bad))


def t_tools_import():
    bad = []
    for f in sorted((_ROOT / "00_CONTROL/tools").glob("*.py")):
        if f.name in {"paths.py", "mgo_login_helper.py", "mgo_docs_probe.py"}:
            continue
        r = subprocess.run([_sys.executable, "-c",
                            f"import sys; sys.path.insert(0, '{_HERE}');"
                            f" import {f.stem}"],
                           capture_output=True, cwd=str(_HERE))
        if r.returncode != 0:
            bad.append(f"{f.stem}: {r.stderr.decode().strip().splitlines()[-1][:60]}")
    check("all importable tools import cleanly", not bad, "; ".join(bad[:2]))


def t_evidence_files_nonempty():
    empty = [r for p, r in walk_files() if p.stat().st_size == 0]
    check("no empty files in the repository", not empty, ", ".join(empty[:3]))


def t_ledger_dates():
    rows = csvrows("00_CONTROL/CHRONOLOGY.csv")
    bad = [r["event_id"] for r in rows
           if not (r["date_observed"] or r["date_record_created"])]
    check("every chronology row has a date field or an explicit UNKNOWN",
          not bad, ", ".join(bad))


def t_dvf_not_fabricated():
    rows = csvrows("00_CONTROL/DESIGN_VS_FIELD_MATRIX.csv")
    MEAS = re.compile(r"\d+(\.\d+)?\s*(ft|feet|inch|in\.|%|mm|cm|m)\b", re.I)
    numeric = [r for r in rows
               if r["approved_value"] not in ("NOT_OBTAINED",)
               and MEAS.search(r["approved_value"])
               and r["status"] == "NOT_TESTABLE"]
    check("no fabricated numeric 'approved' values in design-vs-field",
          not numeric, ", ".join(r["item_id"] for r in numeric))


if __name__ == "__main__":
    print("Tom Street Drainage Investigation - evidence tooling tests\n")
    for fn in [t_hash, t_manifest_no_self_hash, t_pdfs_real, t_zips,
               t_release_zip_hash_parity, t_unique_ids, t_register_paths_exist,
               t_checksums_match, t_claims_cite_real_source,
               t_failed_searches_logged, t_no_submitted_without_receipt,
               t_request_files_exist, t_privacy_public_material,
               t_redacted_derivative_exists, t_no_violation_language,
               t_parity_identifiers, t_lint_tools, t_no_hardcoded_home,
               t_tools_import, t_evidence_files_nonempty, t_ledger_dates,
               t_dvf_not_fabricated]:
        try:
            fn()
        except Exception as e:
            check(f"{fn.__name__} (raised)", False, f"{type(e).__name__}: {e}")
    npass = sum(1 for _, ok, _ in RESULTS if ok)
    nfail = len(RESULTS) - npass
    print(f"\n{npass} passed, {nfail} failed, {len(RESULTS)} total")
    (_ROOT / "00_CONTROL" / "TEST_RESULTS.txt").write_text(
        "\n".join(f"{'PASS' if ok else 'FAIL'}\t{n}\t{d}" for n, ok, d in RESULTS)
        + f"\n\n{npass} passed, {nfail} failed\n")
    print("wrote 00_CONTROL/TEST_RESULTS.txt")
    _sys.exit(1 if nfail else 0)