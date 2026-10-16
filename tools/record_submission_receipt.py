#!/usr/bin/env python3
"""Safely record a CONFIRMED sent agency request; never publish private proof.

Dry-run by default. --apply requires a human review acknowledgment, an existing
private outgoing/receipt file OUTSIDE the public repo, and exact expected
SHA-256 of the current gap register. No email or agency contact is sent.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_REL = '00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv'
RECEIPT_RE = re.compile(r'^[A-Za-z][A-Za-z0-9._-]{2,63}$')


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_records(root: Path):
    file = root / CSV_REL
    raw = file.read_bytes()
    text = raw.decode('utf-8-sig')
    reader = csv.DictReader(text.splitlines())
    headers = reader.fieldnames or []
    needed = {'gap_id', 'submitted', 'submission_date', 'receipt_id', 'status'}
    if not needed.issubset(headers):
        raise ValueError('gap register is missing required fields')
    rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError('malformed register rows')
    return file, headers, rows, hash_bytes(raw)


def record_submission_receipt(*, root: Path, gap_id: str, date_sent: str, public_reference: str,
                              private_proof: Path, private_audit: Path, expected_sha256: str | None,
                              apply: bool, confirmed_proof_reviewed: bool) -> dict:
    repo = root.resolve()
    file, headers, rows, current_sha = read_records(repo)
    if not gap_id.startswith('GAP-'):
        raise ValueError('gap ID must match an existing GAP-* item')
    if not RECEIPT_RE.fullmatch(public_reference) or re.search(r'\d{10,}', public_reference):
        raise ValueError('public reference must be a non-identifying opaque code (no phone/email)')
    try:
        date.fromisoformat(date_sent)
    except ValueError as exc:
        raise ValueError('sent date must be YYYY-MM-DD') from exc
    proof = private_proof.expanduser().resolve(strict=True)
    audit = private_audit.expanduser().resolve()
    if not proof.is_file() or not proof.stat().st_size:
        raise ValueError('actual outgoing/acknowledgment proof file required')
    if proof.is_relative_to(repo) or audit.is_relative_to(repo) or audit == proof:
        raise ValueError('private proof and audit must remain outside public repository')
    if audit.is_relative_to(proof):
        raise ValueError('cannot write an audit inside proof file')
    matches = [r for r in rows if r['gap_id'] == gap_id]
    if len(matches) != 1:
        raise ValueError('gap ID missing or duplicated')
    row = matches[0]
    if row['submitted'].upper() == 'TRUE':
        if row['receipt_id'] == public_reference and row['submission_date'] == date_sent:
            return {'status': 'ALREADY_RECORDED', 'gap_id': gap_id, 'register_sha256': current_sha}
        raise ValueError('gap already submitted with a different receipt/date; reconcile manually')
    if row['submitted'].upper() != 'FALSE':
        raise ValueError('gap submission state ambiguous')
    result = {'status': 'PREVIEW_NOT_APPLIED', 'gap_id': gap_id, 'register_sha256': current_sha,
              'will_set': {'submitted': 'TRUE', 'submission_date': date_sent, 'receipt_id': public_reference,
                           'status': 'SUBMITTED_AWAITING_RECORDS'},
              'private_proof_verified_as_existing_bytes': True,
              'proof_content_authenticity': 'REQUIRES_HUMAN_CONFIRMATION'}
    if not apply:
        return result
    if not confirmed_proof_reviewed:
        raise ValueError('--apply requires human confirmation that the proof demonstrates actual sending')
    if expected_sha256 != current_sha:
        raise ValueError('register changed since preview; rerun preview and reconcile before applying')
    # The proof is never copied or printed. This is a private custody record.
    audit.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if audit.exists():
        raise ValueError('private audit path exists; refuse to overwrite prior custody record')
    h = hashlib.sha256()
    with proof.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    private_data = {'gap_id': gap_id, 'sent_date': date_sent, 'public_reference': public_reference,
                    'proof_file_private': str(proof), 'proof_size_bytes': proof.stat().st_size,
                    'proof_sha256': h.hexdigest(), 'reviewed_by_operator': True,
                    'note': 'Hash proves retained bytes, not agency acknowledgement or actual message delivery'}
    fd, tmp = tempfile.mkstemp(dir=str(audit.parent), prefix='.receipt-audit-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            os.fchmod(f.fileno(), 0o600)
            json.dump(private_data, f, indent=2)
            f.write('\n')
        os.replace(tmp, audit)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    row['submitted'] = 'TRUE'
    row['submission_date'] = date_sent
    row['receipt_id'] = public_reference
    row['status'] = 'SUBMITTED_AWAITING_RECORDS'
    fd, tmp = tempfile.mkstemp(dir=str(file.parent), prefix='.gap-records-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
        # Verify the public register remains at the previewed version.
        if hash_bytes(file.read_bytes()) != current_sha:
            raise ValueError('concurrent public register update detected; private audit retained for reconciliation')
        os.replace(tmp, file)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    result['status'] = 'APPLIED_AFTER_OPERATOR_CONFIRMATION'
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--gap-id', required=True)
    p.add_argument('--sent-date', required=True, help='YYYY-MM-DD, actual transmission day')
    p.add_argument('--public-reference', required=True, help='nonsensitive tracking code, not personal information')
    p.add_argument('--private-proof', required=True, type=Path, help='actual outgoing or acknowledgment file, private')
    p.add_argument('--private-audit', required=True, type=Path, help='new custody JSON path outside Git')
    p.add_argument('--expect-sha256', help='required with --apply, from dry-run preview')
    p.add_argument('--apply', action='store_true', help='make changes, otherwise preview only')
    p.add_argument('--confirmed-proof-reviewed', action='store_true', help='operator actually examined proof of sending')
    args = p.parse_args(argv)
    try:
        result = record_submission_receipt(root=ROOT, gap_id=args.gap_id, date_sent=args.sent_date,
            public_reference=args.public_reference, private_proof=args.private_proof,
            private_audit=args.private_audit, expected_sha256=args.expect_sha256,
            apply=args.apply, confirmed_proof_reviewed=args.confirmed_proof_reviewed)
    except (ValueError, OSError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': type(exc).__name__,
                          'note': 'Review proof, repository version, public reference and permissions; no private paths printed'}))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
