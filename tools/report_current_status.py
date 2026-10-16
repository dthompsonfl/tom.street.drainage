#!/usr/bin/env python3
"""Report current public administrative counts without modifying source records.

This tool reads only explicitly named public CSVs and repository file existence.
It cannot certify engineering, legal applicability, privacy release or source truth.
By default all output goes to stdout, and no network or file writes occur.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COUNTS = (
    ("sources", "00_CONTROL/SOURCE_REGISTER.csv", "source_id"),
    ("claims", "00_CONTROL/EVIDENCE_LEDGER.csv", "claim_id"),
    ("exhibits", "00_CONTROL/EXHIBIT_INDEX.csv", "exhibit_id"),
    ("permit_inventory", "00_CONTROL/PERMIT_DOCUMENT_INVENTORY.csv", "document_id"),
    ("chronology", "00_CONTROL/CHRONOLOGY.csv", "event_id"),
)
ACCEPTED_CLOSE = frozenset(("CLOSED", "COMPLETE", "RESOLVED", "OBTAINED_VERIFIED", "RECEIVED_VERIFIED"))


class StatusError(ValueError):
    """Public register cannot be interpreted safely."""


def rows_of(root: Path, path: str, required: set[str]) -> list[dict[str, str]]:
    file = root / path
    if not file.is_file():
        raise StatusError(f"required public register is missing: {path}")
    with file.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = set(reader.fieldnames or ())
        missing = sorted(required - columns)
        if missing:
            raise StatusError(f"missing required columns in {path}: {', '.join(missing)}")
        output = list(reader)
    if not output:
        raise StatusError(f"required public register has no records: {path}")
    if any(None in entry for entry in output):
        raise StatusError(f"malformed row in {path}")
    return output


def verify_unique(rows: list[dict[str, str]], path: str, identifier: str):
    all_ids = [r[identifier].strip() for r in rows]
    if not all(all_ids) or len(all_ids) != len(set(all_ids)):
        raise StatusError(f"blank or duplicate {identifier} in {path}")


def collect(root: Path) -> dict:
    root = root.resolve()
    counters: dict[str, int] = {}
    for title, path, identifier in COUNTS:
        entries = rows_of(root, path, {identifier})
        verify_unique(entries, path, identifier)
        counters[title] = len(entries)

    gap_path = "00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv"
    gaps = rows_of(root, gap_path, {"gap_id", "status", "submitted", "submission_date", "receipt_id", "closure_evidence"})
    verify_unique(gaps, gap_path, "gap_id")
    gap_stats: Counter[str] = Counter()
    sent_with_receipt = 0
    unresolved = 0
    for r in gaps:
        gap = r["gap_id"].strip()
        status = r["status"].strip().upper() or "UNCLASSIFIED"
        sent = r["submitted"].strip().upper()
        if sent not in ("TRUE", "FALSE"):
            raise StatusError(f"{gap}: submitted must be TRUE or FALSE")
        if sent == "TRUE":
            if not r["receipt_id"].strip() or not r["submission_date"].strip():
                raise StatusError(f"{gap}: submitted requires a dated receipt reference")
            sent_with_receipt += 1
        elif r["receipt_id"].strip() or r["submission_date"].strip():
            raise StatusError(f"{gap}: unsent request has a receipt or transmission date")
        if status in ACCEPTED_CLOSE and not r["closure_evidence"].strip():
            raise StatusError(f"{gap}: closed without source-linked closure evidence")
        if status not in ACCEPTED_CLOSE:
            unresolved += 1
        gap_stats[status] += 1

    design_path = "00_CONTROL/DESIGN_VS_FIELD_MATRIX.csv"
    design = rows_of(root, design_path, {"item_id", "status"})
    verify_unique(design, design_path, "item_id")
    designs = dict(sorted(Counter(r["status"].strip().upper() or "UNCLASSIFIED" for r in design).items()))

    old = rows_of(root, "00_CONTROL/INDEPENDENT_REMEDIATION_REGISTER.csv", {"id", "status"})
    verify_unique(old, "00_CONTROL/INDEPENDENT_REMEDIATION_REGISTER.csv", "id")

    return {
        "release_status": "RESEARCH_AND_HOMEOWNER_DRAFTS; NOT_ENGINEERING_OR_PUBLICATION_APPROVED",
        "source": "current local public repository registers; captured permit status is not live",
        "register_counts": counters,
        "record_requests": {"gap_rows": len(gaps), "unresolved": unresolved,
                            "sent_with_dated_receipt": sent_with_receipt,
                            "statuses": dict(sorted(gap_stats.items()))},
        "design_vs_field": {"rows": len(design), "statuses": designs},
        "historical_audit": {"findings": len(old), "status": "FROZEN_AUDIT_NOT_CURRENT_DEFECT_COUNT"},
        "autonomous_pipeline": {"full_operation_verified": False,
             "note": "See dry-run diagnostic, operator opt-in, and automation decisions for unimplemented modules"},
        "verification_limit": "File and tracker bookkeeping only; not an agency receipt audit, independent field measurement, privacy consent, or hydro-engineering conclusion",
    }


def markdown(report: dict) -> str:
    req = report["record_requests"]
    d = report["design_vs_field"]
    rc = report["register_counts"]
    lines = ["# Tom Street: live administrative snapshot", "",
             "**Status: investigation records incomplete; letters remain unsigned drafts.**", "",
             "This report is derived from the current public CSV registers at execution time. It does not read private originals or use live government APIs.", "",
             "## Current tracked counts", "",
             f"- External evidence gap rows: **{req['gap_rows']}**; unresolved or partial: **{req['unresolved']}**.",
             f"- Gaps with a recorded dated submission and receipt: **{req['sent_with_dated_receipt']}**. This reflects tracker entries, not independent verification of outgoing emails.",
             f"- Design-versus-field comparison rows: **{d['rows']}**.",
             f"- Source records: **{rc['sources']}**; claims: **{rc['claims']}**; exhibits: **{rc['exhibits']}**; inventory rows: **{rc['permit_inventory']}**; chronology events: **{rc['chronology']}**.", "",
             "## Tracked gap statuses", ""]
    lines += [f"- `{key}`: {value}" for key, value in req["statuses"].items()]
    lines += ["", "## Design-versus-field statuses", ""]
    lines += [f"- `{key}`: {value}" for key, value in d["statuses"].items()]
    lines += ["", f"**Historical 51-item baseline:** {report['historical_audit']['findings']} entries, deliberately not treated as today's defect count.",
              "", "**External dependencies:** approved plans, accepted asset/ROW records, contemporary comparable survey/outfall measurements, agency written responses, homeowner original-file permissions.",
              "", "**Integrity limit:** matching filenames, hashes or tracker states never prove a drainage cause, a permit violation or homeowner release approval.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="public repository checkout root; for offline tests")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args(argv)
    try:
        result = collect(args.root)
    except (StatusError, OSError, UnicodeError) as error:
        print(f"CURRENT STATUS UNAVAILABLE: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True) if args.format == "json" else markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
