#!/usr/bin/env python3
"""Read-only audit for an off-repository private evidence directory.

No native photos, GPS, names, paths or hashes are printed to the public console.
Optional detailed inventory goes to an explicitly chosen PRIVATE path.
File hashes indicate byte identity, not when/where a photo was taken.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def external_folder(folder: Path, root: Path = ROOT) -> Path:
    target = folder.expanduser().resolve(strict=True)
    repo = root.resolve()
    if not target.is_dir():
        raise ValueError('private vault must be a directory')
    if target == repo or target.is_relative_to(repo) or repo.is_relative_to(target):
        raise ValueError('private vault cannot be within, or contain, the public repository')
    return target


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def detected_type(path: Path) -> str:
    with path.open('rb') as handle:
        b = handle.read(16)
    if b.startswith(b'\xff\xd8\xff'):
        return 'jpeg'
    if b.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    if b.startswith(b'%PDF-'):
        return 'pdf'
    if len(b) > 12 and b[4:8] == b'ftyp':
        return 'heic_or_video_container'
    if b.lstrip().startswith(b'<?xml'):
        return 'xml_sidecar'
    return 'unknown_or_unsupported'


def scan_external_vault(folder: Path, *, root: Path = ROOT, private_manifest: Path | None = None) -> dict:
    vault = external_folder(folder, root)
    if private_manifest is not None:
        manifest = private_manifest.expanduser().resolve()
        repo = root.resolve()
        if manifest == repo or manifest.is_relative_to(repo):
            raise ValueError('private manifest must not be written into the public repository')
        if not manifest.is_relative_to(vault):
            raise ValueError('private manifest must be contained within the supplied private vault')
    else:
        manifest = None
    rows = []
    for entry in sorted(vault.rglob('*')):
        if entry.is_symlink():
            raise ValueError('symlink encountered; refuse to follow unreviewed private-vault links')
        if not entry.is_file():
            continue
        if manifest is not None and entry == manifest:
            continue
        if not entry.resolve().is_relative_to(vault):
            raise ValueError('a private file resolves outside its vault')
        info = entry.stat()
        rows.append({
            'private_relative_path': entry.relative_to(vault).as_posix(),
            'bytes': info.st_size,
            'sha256': sha_file(entry),
            'detected_type': detected_type(entry),
        })
    hashes = Counter(r['sha256'] for r in rows)
    result = {
        'total_files': len(rows),
        'distinct_sha256_count': len(hashes),
        'duplicate_count': sum(n - 1 for n in hashes.values()),
        'unknown_file_type_count': sum(r['detected_type'] == 'unknown_or_unsupported' for r in rows),
        'audit_scope': 'byte integrity and file-type triage only; provenance and rights unverified',
    }
    if manifest is not None:
        manifest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        data = {'audited_utc': datetime.now(timezone.utc).isoformat(), 'summary': result, 'private_file_rows': rows}
        fd, tempname = tempfile.mkstemp(prefix='.private-evidence-audit-', dir=str(manifest.parent))
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as h:
                os.fchmod(h.fileno(), 0o600)
                json.dump(data, h, indent=2)
                h.write('\n')
            os.replace(tempname, manifest)
        finally:
            if os.path.exists(tempname):
                os.unlink(tempname)
        result['private_manifest_written'] = True
    else:
        result['private_manifest_written'] = False
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vault', type=Path, required=True, help='explicit external private folder; never inside this repository')
    p.add_argument('--private-manifest', type=Path, help='optional PRIVATE JSON output, must reside inside vault')
    args = p.parse_args(argv)
    try:
        result = scan_external_vault(args.vault, private_manifest=args.private_manifest)
    except (ValueError, OSError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': type(exc).__name__, 'note': 'Check private folder, symlinks and permissions; path omitted'}))
        return 2
    print(json.dumps({'status': 'AUDITED', **result}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
