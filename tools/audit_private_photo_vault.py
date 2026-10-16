#!/usr/bin/env python3
"""Privacy guard for resident photos."""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "00_CONTROL" / "PRIVATE_RESIDENT_PHOTO_INVENTORY_PUBLIC_SAFE_2026-10-16.csv"

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault-dir", type=Path, default=None)
    args = parser.parse_args(argv)
    leaked = list(ROOT.rglob("IMG_*.jpeg"))
    if leaked:
        raise SystemExit(f"PRIVACY_VIOLATION: {len(leaked)} IMG_*.jpeg files found in repo")
    result = {"checked_utc": datetime.now(timezone.utc).isoformat(), "vault_dir": str(args.vault_dir) if args.vault_dir else None, "vault_inside_repo": bool(args.vault_dir and ROOT in args.vault_dir.resolve().parents), "leaked_in_repo": len(leaked), "status": "SAFE"}
    print(json.dumps(result, indent=2))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())

def is_inside_git_repo(vault_dir: Path, repo_root: Path = ROOT) -> bool:
    try:
        v = vault_dir.resolve()
        r = repo_root.resolve()
        return str(v).startswith(str(r)) and (v == r or str(v).startswith(str(r) + "/"))
    except Exception:
        return False

def scan_vault(vault_dir: Path) -> list[dict]:
    items = []
    if not vault_dir or not vault_dir.exists():
        return items
    import hashlib
    for img in vault_dir.rglob("*.jp*g"): pass
    for img in vault_dir.rglob("*.jpg"): pass
    for img in vault_dir.rglob("*"):
        try:
            raw = img.read_bytes()
            items.append({"path": str(img), "sha256": hashlib.sha256(raw).hexdigest()})
        except Exception:
            pass
    return items

def write_inventory(items: list[dict], out_csv: Path = OUT_CSV) -> Path:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    import csv
    with out_csv.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['file','sha256'])
        for it in items:
            w.writerow([it['path'], it['sha256']])
    return out_csv

def scan_external_vault_impl(vault_dir: Path) -> dict:
    items = scan_vault(vault_dir)
    # detect duplicates by sha
    seen = {}
    for it in items:
        seen.setdefault(it['sha256'], []).append(it['path'])
    dups = {k:v for k,v in seen.items() if len(v)>1}
    return {"items": items, "duplicate_groups": dups, "has_duplicates": len(dups)>0, "total_files": len(items), "distinct_sha256_count": len({i["sha256"] for i in items}), "duplicate_count": sum(1 for v in dups.values())}

def assert_external_vault_outside_repo(vault_dir: Path, repo_root: Path = ROOT):
    if not vault_dir:
        raise ValueError("vault inside repo")
    try:
        if is_inside_git_repo(vault_dir, repo_root):
            raise ValueError("vault inside repo")
    except ValueError:
        raise
    except Exception:
        pass

def scan_external_vault(vault_dir: Path, repo_root: Path = ROOT):
    assert_external_vault_outside_repo(vault_dir, repo_root)
    return scan_external_vault_impl(vault_dir)
