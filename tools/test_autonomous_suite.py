#!/usr/bin/env python3
"""HISTORICAL integration expectations; not a verified complete autonomous suite.

Some referenced modules remain unavailable. Running this full historical suite
may fail before executing tests; it is not part of the supported release checks.
Use read-only administration-quality CI and the pipeline --dry-run dependency
preflight for current supported functionality. Do not report it as passing.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image


def load_module(name: str, filename: str):
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class AutonomousSuiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.permits = load_module("permits", "acquire_live_permits_and_parcels.py")
        cls.hydro = load_module("hydro", "acquire_hydrology_fema_usgs.py")
        cls.precip = load_module("precip", "acquire_noaa_precipitation_and_storms.py")
        cls.discover = load_module("discover", "discover_agency_updates.py")
        cls.sync = load_module("sync", "sync_evidence_registers.py")
        cls.lidar = load_module("lidar", "analyze_lidar_terrain_change.py")
        cls.prr = load_module("prr", "ingest_records_request_response.py")
        cls.photo = load_module("photo", "audit_private_photo_vault.py")
        cls.patch = load_module("patch", "patch_legacy_checks_for_autonomy.py")
        cls.pipeline = load_module("pipeline", "autonomous_evidence_pipeline.py")

    def test_url_allowlists_reject_unapproved_hosts_and_http(self):
        for mod in (self.permits, self.hydro, self.precip, self.discover):
            for bad_url in (
                "http://cloud.santarosa.fl.gov/arcgis",
                "https://evil.example.com/arcgis",
                "https://user:pass@cloud.santarosa.fl.gov/arcgis",
                "https://cloud.santarosa.fl.gov:8443/arcgis",
            ):
                with self.assertRaises(ValueError):
                    mod.check_url(bad_url)

    def test_atomic_write_versioned_preserves_prior_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            orig_root = self.permits.ROOT
            self.permits.ROOT = root
            try:
                dest = root / "02_PROPERTY_AND_PARCELS" / "parcel.json"
                snap1 = root / "captures" / "t1"
                snap2 = root / "captures" / "t2"
                raw1 = b'{"status": "Active", "version": 1}'
                raw2 = b'{"status": "Closed", "version": 2}'

                r1 = self.permits.atomic_write_versioned(dest, raw1, snap1)
                self.assertEqual(r1["write_status"], "INITIAL_BASELINE_SAVED")
                self.assertEqual(dest.read_bytes(), raw1)

                r_same = self.permits.atomic_write_versioned(dest, raw1, snap1)
                self.assertEqual(r_same["write_status"], "UNCHANGED_MATCHES_BASELINE")

                r2 = self.permits.atomic_write_versioned(dest, raw2, snap2)
                self.assertEqual(r2["write_status"], "UPSTREAM_CHANGED_BASELINE_PRESERVED")
                self.assertEqual(dest.read_bytes(), raw1)
                self.assertEqual((root / r2["snapshot_path"]).read_bytes(), raw2)
            finally:
                self.permits.ROOT = orig_root

    def test_sync_register_ingests_manifests_and_verifies_magic_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            orig_root, orig_control = self.sync.ROOT, self.sync.CONTROL
            self.sync.ROOT = root
            self.sync.CONTROL = root / "00_CONTROL"
            try:
                cap_dir = root / "17_CURRENT_RESEARCH" / "captures" / "20261016T120000Z"
                cap_dir.mkdir(parents=True, exist_ok=True)
                pdf_bytes = b"%PDF-1.7\nTom Street test ordinance bytes"
                pdf_path = cap_dir / "ORD_TEST.pdf"
                pdf_path.write_bytes(pdf_bytes)
                digest = hashlib.sha256(pdf_bytes).hexdigest()

                manifest = {
                    "captured_utc": "2026-10-16T12:00:00Z",
                    "sources": [
                        {
                            "source_id": "ORD_TEST",
                            "requested_url": "https://mcclibraryfunctions.azurewebsites.us/api/ordinanceDownload/1",
                            "local_path": pdf_path.relative_to(root).as_posix(),
                            "bytes": len(pdf_bytes),
                            "sha256": digest,
                        }
                    ],
                }
                (cap_dir / "ACQUISITION_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")

                res = self.sync.sync_all_manifests_to_register(dry_run=False)
                self.assertEqual(res["integrity_errors"], [])
                self.assertEqual(res["added_source_ids"], ["SRC-AUTO-ORD_TEST"])

                res2 = self.sync.sync_all_manifests_to_register(dry_run=False)
                self.assertEqual(res2["added_source_ids"], [])
                self.assertEqual(res2["verified_existing_records"], 1)
            finally:
                self.sync.ROOT = orig_root
                self.sync.CONTROL = orig_control

    def test_public_records_ingestion_and_receipt_tracking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            orig_root, orig_ctrl, orig_act, orig_src = (
                self.prr.ROOT, self.prr.CONTROL, self.prr.ACTIONS_CSV, self.prr.SOURCE_CSV
            )
            self.prr.ROOT = root
            self.prr.CONTROL = root / "00_CONTROL"
            self.prr.ACTIONS_CSV = self.prr.CONTROL / "MISSING_RECORDS_AND_ACTIONS.csv"
            self.prr.SOURCE_CSV = self.prr.CONTROL / "SOURCE_REGISTER.csv"
            try:
                self.prr.CONTROL.mkdir(parents=True, exist_ok=True)
                self.prr.ACTIONS_CSV.write_text(
                    "gap_id,status,submitted,receipt_id\nGAP-01,DRAFTED_NOT_SUBMITTED,FALSE,\n",
                    encoding="utf-8",
                )
                self.prr.SOURCE_CSV.write_text(
                    "source_id,document_title,issuing_agency,record_system,source_identifier,retrieval_date_utc,original_url,local_relative_path,file_type,file_size_bytes,sha256_hash,status,verification_method,notes\n",
                    encoding="utf-8",
                )
                sub = self.prr.record_submission_receipt("GAP-01", "PRR-2026-991")
                self.assertEqual(sub["submitted"], "TRUE")
                self.assertEqual(sub["receipt_id"], "PRR-2026-991")

                sample_pdf = root / "incoming_grading_plan.pdf"
                sample_pdf.write_bytes(b"%PDF-1.7\nApproved Grading Plan Sheet 1")
                ing = self.prr.ingest_agency_file(
                    src_file=sample_pdf,
                    gap_id="GAP-01",
                    agency="Santa Rosa County Engineering",
                    dest_subdir="03_PERMITS_AND_INSPECTIONS/PUBLIC_RECORDS_PRODUCTIONS",
                    receipt_id="PRR-2026-991",
                )
                self.assertTrue((root / ing["local_relative_path"]).is_file())
                self.assertTrue((root / ing["sidecar_manifest"]).is_file())
            finally:
                self.prr.ROOT, self.prr.CONTROL, self.prr.ACTIONS_CSV, self.prr.SOURCE_CSV = (
                    orig_root, orig_ctrl, orig_act, orig_src
                )

    def test_private_photo_vault_rejects_in_repo_path_and_detects_duplicates(self):
        with tempfile.TemporaryDirectory() as vault_tmp:
            vault = Path(vault_tmp)
            img1 = vault / "photo_a.jpg"
            img2 = vault / "photo_b_dup.jpg"
            im = Image.new("RGB", (64, 64), color=(20, 40, 60))
            im.save(img1, format="JPEG")
            img2.write_bytes(img1.read_bytes())

            scan = self.photo.scan_external_vault(vault)
            self.assertEqual(scan["total_files"], 2)
            self.assertEqual(scan["distinct_sha256_count"], 1)
            self.assertEqual(scan["duplicate_count"], 1)

            with self.assertRaises(ValueError):
                self.photo.scan_external_vault(self.photo.ROOT)

    def test_patch_legacy_checks_idempotent_and_verified(self):
        crosslinks_file = Path(__file__).with_name("check_historical_evidence_crosslinks.py")
        if crosslinks_file.is_file():
            content = crosslinks_file.read_text(encoding="utf-8")
            self.assertTrue("assert len(sources)>=23," in content or "assert len(sources)==23," in content)

    def test_pipeline_dry_run_succeeds(self):
        rc = self.pipeline.main(["--mode", "full", "--dry-run"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
