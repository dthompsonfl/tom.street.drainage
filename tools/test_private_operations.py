#!/usr/bin/env python3
"""Synthetic permission/path/receipt safeguards; never uses actual resident data."""
from __future__ import annotations

import csv
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path


def module(filename):
    p=Path(__file__).with_name(filename)
    spec=importlib.util.spec_from_file_location(filename.replace('.', '_'), p)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

private = module('private_evidence_audit.py')
receipts = module('record_submission_receipt.py')


class PrivateEvidenceTests(unittest.TestCase):
    def test_private_audit_detects_exact_duplicates_without_disclosing_names(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            vault=Path(a); repo=Path(b)
            (vault/'camera_01.jpg').write_bytes(b'\xff\xd8\xff\xe0demo')
            (vault/'camera_02.jpg').write_bytes(b'\xff\xd8\xff\xe0demo')
            report=private.scan_external_vault(vault,root=repo)
            self.assertEqual(report['total_files'],2)
            self.assertEqual(report['duplicate_count'],1)
            self.assertNotIn('camera_01',str(report))
            self.assertFalse(report['private_manifest_written'])

    def test_private_manifest_is_private_and_not_in_repo(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            vault=Path(a); repo=Path(b)
            (vault/'test.pdf').write_bytes(b'%PDF-1.7\nfixture')
            path=vault/'custody.json'
            report=private.scan_external_vault(vault,root=repo,private_manifest=path)
            self.assertTrue(report['private_manifest_written'])
            self.assertTrue(path.is_file())
            self.assertEqual(os.stat(path).st_mode & 0o777,0o600)
            with self.assertRaises(ValueError):
                private.scan_external_vault(vault,root=repo,private_manifest=repo/'wrong.json')

    def test_repo_and_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            repo=Path(a); vault=Path(b)
            with self.assertRaises(ValueError):
                private.scan_external_vault(repo,root=repo)
            (vault/'escape.jpg').symlink_to(repo/'absent.jpg')
            with self.assertRaises(ValueError):
                private.scan_external_vault(vault,root=repo)


class ReceiptTests(unittest.TestCase):
    def setup_fixture(self,repo):
        p=repo/'00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv'
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text('gap_id,gap,submitted,submission_date,receipt_id,status,closure_evidence\n'
                     'GAP-01,Approved design,FALSE,,,REQUEST_DRAFTED,\n',encoding='utf-8')
        return p

    def arguments(self,repo,proof,audit,**override):
        result=dict(root=repo,gap_id='GAP-01',date_sent='2026-10-16',public_reference='REF-001',
                    private_proof=proof,private_audit=audit,expected_sha256=None,
                    apply=False,confirmed_proof_reviewed=False)
        result.update(override)
        return result

    def test_preview_never_changes_register_or_copies_proof(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            repo=Path(a); private_vault=Path(b)
            register=self.setup_fixture(repo)
            proof=private_vault/'private_outgoing.eml';proof.write_bytes(b'Synthetic proof with PRIVATE fixture data')
            audit=private_vault/'receipt.json'
            original=register.read_bytes()
            result=receipts.record_submission_receipt(**self.arguments(repo,proof,audit))
            self.assertEqual(result['status'],'PREVIEW_NOT_APPLIED')
            self.assertEqual(original,register.read_bytes())
            self.assertFalse(audit.exists())
            self.assertNotIn('PRIVATE fixture',str(result))

    def test_apply_requires_acknowledgment_and_sha_and_writes_private_audit(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            repo=Path(a); vault=Path(b); reg=self.setup_fixture(repo)
            proof=vault/'receipt.eml';proof.write_bytes(b'Locally checked synthetic sent confirmation')
            audit=vault/'private_receipt.json'
            preview=receipts.record_submission_receipt(**self.arguments(repo,proof,audit))
            sha=preview['register_sha256']
            with self.assertRaises(ValueError):
                receipts.record_submission_receipt(**self.arguments(repo,proof,audit,
                    apply=True,expected_sha256=sha))
            with self.assertRaises(ValueError):
                receipts.record_submission_receipt(**self.arguments(repo,proof,audit,
                    apply=True,confirmed_proof_reviewed=True,expected_sha256='0'*64))
            result=receipts.record_submission_receipt(**self.arguments(repo,proof,audit,
                apply=True,confirmed_proof_reviewed=True,expected_sha256=sha))
            self.assertEqual(result['status'],'APPLIED_AFTER_OPERATOR_CONFIRMATION')
            self.assertEqual(os.stat(audit).st_mode & 0o777,0o600)
            text=reg.read_text()
            self.assertIn('TRUE,2026-10-16,REF-001,SUBMITTED_AWAITING_RECORDS',text)
            self.assertNotIn('Locally checked',text)

    def test_reject_public_proof_or_duplicate_change(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            repo=Path(a);vault=Path(b);self.setup_fixture(repo)
            inside=repo/'resident.eml';inside.write_bytes(b'private content')
            proof=vault/'receipt.eml';proof.write_bytes(b'sent synthetic')
            audit=vault/'new.json'
            with self.assertRaises(ValueError):
                receipts.record_submission_receipt(**self.arguments(repo,inside,audit))
            with self.assertRaises(ValueError):
                receipts.record_submission_receipt(**self.arguments(repo,proof,repo/'public.json'))
            with self.assertRaises(ValueError):
                receipts.record_submission_receipt(**self.arguments(repo,proof,audit,public_reference='phone1234567890'))


if __name__=='__main__':
    unittest.main()
