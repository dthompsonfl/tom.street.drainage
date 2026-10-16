#!/usr/bin/env python3
"""Import only the exact public GIS captures reviewed on 2026-10-16.

This is an offline, one-capture importer, not a downloader or a general ZIP
extractor. The source snapshot and any other archive members are never copied.
The entire artifact hash binds filenames, original bytes and source manifest.
"""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ARTIFACT_SHA256 = '5640c8af5587384737a7b3a6b7f8266ef2702d832cd25ed52536776b59b012bb'
CAPTURE = '20261016T054716Z'
EXPECTED = {
    'SRC_STREET_APP', 'SRC_STREET_APP_DATA', 'SRC_STREET_WEBMAP',
    'SRC_STREET_METADATA', 'SRC_TOM_STREET', 'SRC_TOM_FID_2006',
    'SRC_STREET_SPATIAL', 'SRC_GOMAPS_METADATA', 'SRC_GOMAPS_TOM',
    'NWFWMD_ERP_METADATA', 'NWFWMD_ERP_SPATIAL',
}

def import_capture(artifact: Path, root: Path) -> int:
    raw = artifact.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ARTIFACT_SHA256:
        raise ValueError('Artifact does not match the independently reviewed bytes')
    with zipfile.ZipFile(artifact) as z:
        prefix = 'captures/' + CAPTURE + '/'
        manifest_raw = z.read(prefix + 'ACQUISITION_MANIFEST.json')
        manifest = json.loads(manifest_raw)
        rows = manifest['sources']
        if len(rows) != len(EXPECTED) or {r['source_id'] for r in rows} != EXPECTED:
            raise ValueError('Unexpected source inventory')
        pending = {'ACQUISITION_MANIFEST.json': manifest_raw}
        for row in rows:
            name = row['source_id'] + '.json'
            data = z.read(prefix + name)
            if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
                raise ValueError('Capture does not match manifest: ' + name)
            obj = json.loads(data)
            if not isinstance(obj, dict) or 'error' in obj:
                raise ValueError('Unreviewed error response: ' + name)
            pending[name] = data
    destination = root / '17_CURRENT_RESEARCH' / 'captures' / CAPTURE
    # Preflight all destinations before any writes; never replace evidence.
    for name, data in pending.items():
        target = destination / name
        if target.exists() and target.read_bytes() != data:
            raise FileExistsError('Refusing to replace existing evidence: ' + name)
    destination.mkdir(parents=True, exist_ok=True)
    for name, data in pending.items():
        target = destination / name
        if not target.exists():
            with target.open('xb') as f:
                f.write(data)
    return len(pending)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: import_reviewed_question_sources.py artifact.zip')
    print('Preserved public files:', import_capture(Path(sys.argv[1]), Path(__file__).resolve().parents[1]))
