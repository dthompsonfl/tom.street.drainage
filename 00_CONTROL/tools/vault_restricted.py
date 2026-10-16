#!/usr/bin/env python3
"""Move RESTRICTED files out of the repository working tree into the local
evidence vault, preserving original bytes and recording a deterministic
filename map so every reference remains resolvable.

Nothing is deleted. Every moved file is copied first, verified byte-identical
by SHA-256, then removed from the working tree and untracked from Git.

Run:  python3 00_CONTROL/tools/vault_restricted.py [--apply]
"""
import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT, rel, sha256_file  # noqa: E402

import csv
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timezone

VAULT = _ROOT / ".evidence_vault" / "restricted"
SELF = "00_CONTROL/tools/classify_for_release.py"
# The classifier itself holds the marker strings as detection patterns.
ALLOW = {SELF}


def restricted_paths():
    rows = list(csv.DictReader(
        (_ROOT / "00_CONTROL" / "RELEASE_PRIVACY_CLASSIFICATION.csv").open()))
    return [r for r in rows
            if r["privacy_class"] == "RESTRICTED" and r["path"] not in ALLOW]


def main(apply: bool = False):
    rows = restricted_paths()
    print(f"{len(rows)} restricted files")
    VAULT.mkdir(parents=True, exist_ok=True)
    map_rows = []
    for r in rows:
        src = _ROOT / r["path"]
        if not src.exists():
            print("  MISSING", r["path"])
            continue
        dest = VAULT / r["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not apply:
            print(f"  [dry-run] would vault {r['path']} -> {rel(dest)}")
            map_rows.append({"original_relative_path": r["path"],
                             "vault_relative_path": rel(dest),
                             "bytes": r["bytes"], "sha256": r["sha256"],
                             "action": "DRY_RUN"})
            continue
        shutil.copy2(src, dest)
        got = sha256_file(dest)
        if got != r["sha256"]:
            raise SystemExit(f"hash mismatch on copy of {r['path']}")
        map_rows.append({"original_relative_path": r["path"],
                         "vault_relative_path": rel(dest),
                         "bytes": r["bytes"], "sha256": got,
                         "action": "VAULTED_AND_UNTRACKED"})
        print(f"  vaulted {r['path']}")
    out = _ROOT / "00_CONTROL" / "RESTRICTED_EVIDENCE_INDEX.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["original_relative_path",
                                           "vault_relative_path", "bytes",
                                           "sha256", "action"])
        w.writeheader()
        w.writerows(map_rows)
    print("wrote", rel(out))
    if apply:
        subprocess.run(["git", "rm", "--cached", "-q", "--"] +
                       [r["original_relative_path"] for r in map_rows],
                       cwd=_ROOT, check=True)
        for r in map_rows:
            p = _ROOT / r["original_relative_path"]
            if p.exists():
                p.unlink()
        print("untracked and removed from working tree (bytes preserved in vault)")
    print("dry-run" if not apply else "APPLIED",
          datetime.now(timezone.utc).isoformat())


if __name__ == "__main__":
    main(apply="--apply" in _sys.argv)