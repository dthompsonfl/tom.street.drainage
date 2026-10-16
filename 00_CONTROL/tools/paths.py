#!/usr/bin/env python3
"""Repository path discovery and safe-write helpers for the Tom Street
Drainage Investigation tooling.

Replaces the developer-specific absolute roots that were hardcoded in the
first-generation scripts. Resolution order:

  1. ``TSD_REPO_ROOT`` environment variable
  2. the first ancestor of this file that contains ``00_CONTROL``
  3. the current working directory, if it looks like the repository

Nothing here deletes, moves or rewrites evidence. Writes are guarded:
``safe_write`` refuses to overwrite an existing evidence file unless the caller
passes ``overwrite=True`` explicitly.
"""
from __future__ import annotations

import hashlib
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

# Files/directories that are evidence or canonical registers and must never be
# silently clobbered by a tool run.
GUARDED = {
    "00_CONTROL/EVIDENCE_MANIFEST.csv",
    "00_CONTROL/SOURCE_REGISTER.csv",
    "00_CONTROL/PERMIT_DOCUMENT_INVENTORY.csv",
    "00_CONTROL/RECORDS_ACQUISITION_MATRIX.csv",
    "00_CONTROL/EVIDENCE_LEDGER.csv",
    "00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv",
}


def _looks_like_repo(p: Path) -> bool:
    return (p / "00_CONTROL").is_dir()


def find_root(start: Path | None = None) -> Path:
    env = os.environ.get("TSD_REPO_ROOT")
    if env:
        p = Path(env).expanduser().resolve()
        if _looks_like_repo(p):
            return p
        raise SystemExit(f"TSD_REPO_ROOT={env!r} is not the repository root")
    here = (start or Path(__file__)).resolve()
    for cand in [here, *here.parents]:
        if _looks_like_repo(cand):
            return cand
    cwd = Path.cwd().resolve()
    if _looks_like_repo(cwd):
        return cwd
    raise SystemExit("Cannot locate repository root (no ancestor contains 00_CONTROL)")


ROOT = find_root()
TOOLS = ROOT / "00_CONTROL" / "tools"
SYSTEM_RAW = ROOT / "00_CONTROL" / "SYSTEM_RAW"


def rel(p: Path | str) -> str:
    """Repository-relative POSIX path, for registers."""
    q = Path(p)
    try:
        return q.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return q.as_posix()


def abs_(p: Path | str) -> Path:
    q = Path(p)
    return q if q.is_absolute() else ROOT / q


def sha256_file(p: Path | str) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_guarded(p: Path | str) -> bool:
    return rel(p) in GUARDED


def safe_write(p: Path | str, data, *, overwrite: bool = False,
               backup: bool = True) -> Path:
    """Write a file without silently destroying evidence or a canonical register.

    Refuses to overwrite a GUARDED register unless ``overwrite=True``.
    Always backs up an existing file before replacing it unless the target is
    itself the intended canonical output being regenerated.
    """
    target = abs_(p)
    if target.exists() and is_guarded(target) and not overwrite:
        raise PermissionError(
            f"refusing to overwrite guarded register {rel(target)} without "
            f"overwrite=True")
    if target.exists() and backup and not is_guarded(target):
        bak = target.with_suffix(target.suffix + ".bak")
        shutil.copy2(target, bak)
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        target.write_bytes(data)
    else:
        target.write_text(data, encoding="utf-8")
    return target


def read_json(p: Path | str):
    import json
    return json.loads(abs_(p).read_text(encoding="utf-8"))