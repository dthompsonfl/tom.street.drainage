#!/usr/bin/env python3
"""Automated structural verification; never substitutes for visual or human review."""
from __future__ import annotations

import hashlib
import json
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from pypdf import PdfReader
import build_neighborhood_reference_map as site_map

ROOT = Path(__file__).resolve().parents[1]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class NeighborhoodReferenceTests(unittest.TestCase):
    def test_gis_features_are_official_identified_records(self):
        data, caps, parcels, road = site_map.extract()
        self.assertEqual(set(parcels), {"2264", "2265", "2268"})
        self.assertEqual(road["attributes"]["OBJECTID"], 2036)
        self.assertEqual(road["attributes"]["MAINTAINER"], "County Maintained")
        self.assertIn("verified_parcel_shapes", caps)
        self.assertGreater(len(data), 10000)

    def test_map_rendered_with_source_checksum_and_text_labels(self):
        manifest_file = ROOT / "19_NEIGHBOR_REVIEW/map/MAP_MANIFEST.json"
        self.assertTrue(manifest_file.is_file(), "Generate map using canonical generator")
        manifest = json.loads(manifest_file.read_text())
        self.assertEqual(manifest["status"], "SOURCE_LINKED_GIS_CONTEXT_NOT_CERTIFIED_SURVEY")
        self.assertEqual(manifest["independent_visual_review"], "PENDING")
        self.assertEqual(manifest["human_publication_approval"], "PENDING")
        self.assertEqual(manifest["source_sha256"], sha(site_map.SOURCE.read_bytes()))
        self.assertEqual(set(manifest["verified_feature_ids"]["parcels"]), {"2264", "2265", "2268"})
        for item in manifest["outputs"]:
            p = ROOT / item["path"]
            self.assertTrue(p.is_file())
            self.assertEqual(sha(p.read_bytes()), item["sha256"])
            self.assertEqual(p.stat().st_size, item["bytes"])
        svg = (ROOT / "19_NEIGHBOR_REVIEW/map/Tom_Street_GIS_Reference_2026-10-16.svg").read_text()
        svgroot = ET.fromstring(svg)
        self.assertEqual(svgroot.tag, "{http://www.w3.org/2000/svg}svg")
        for text in ("2264", "2265", "2268", "County Maintained", "NOT a survey", "No pipes"):
            self.assertIn(text, svg)
        pages = PdfReader(str(ROOT / "19_NEIGHBOR_REVIEW/map/Tom_Street_GIS_Reference_2026-10-16.pdf")).pages
        self.assertEqual(len(pages), 1)
        self.assertAlmostEqual(float(pages[0].mediabox.width), 612)
        self.assertAlmostEqual(float(pages[0].mediabox.height), 792)
        actual_text = pages[0].extract_text()
        self.assertIn("2026-10-16", actual_text)
        self.assertIn("UNVERIFIED", actual_text)
        self.assertIn("Tom Street", actual_text)

    def test_candidate_is_pinned_readable_and_unapproved(self):
        dest = ROOT / "19_NEIGHBOR_REVIEW/candidates"
        files = list(dest.glob("*_CANDIDATE.zip"))
        self.assertEqual(len(files), 1, "Build exactly one candidate for this checkout")
        with zipfile.ZipFile(files[0]) as z:
            names = z.namelist()
            self.assertEqual(len(names), len(set(names)))
            m = json.loads(z.read("EDITION_MANIFEST.json"))
            self.assertEqual(m["edition_status"], "CANDIDATE_NOT_AUTHORIZED_FOR_PUBLIC_DISTRIBUTION")
            self.assertEqual(m["publication_decision"], "AWAITING_HUMAN_APPROVAL")
            self.assertEqual(m["two_real_neighbor_usability_tests"], "PENDING")
            self.assertFalse(m["resident_private_originals_included"])
            self.assertFalse(m["government_originals_included"])
            self.assertIn(m["source_commit"][:12], files[0].name)
            self.assertIn(m["source_commit"], z.read("START_HERE.txt").decode())
            self.assertEqual(len(m["included_files"]), len(names) - 2)
            self.assertIn("19_NEIGHBOR_REVIEW/map/Tom_Street_GIS_Reference_2026-10-16.pdf", names)
            self.assertIn("18_NEIGHBOR_TOOLKIT/print/03_Event_Observation.pdf", names)
            for row in m["included_files"]:
                content = z.read(row["path"])
                self.assertEqual(row["bytes"], len(content), row["path"])
                self.assertEqual(row["sha256"], sha(content), row["path"])
            sums = z.read("SHA256SUMS.txt").decode().splitlines()
            self.assertEqual(len(sums), len(names) - 1)
            for entry in sums:
                check, name = entry.split("  ", 1)
                self.assertEqual(check, sha(z.read(name)), name)


if __name__ == "__main__":
    unittest.main()
