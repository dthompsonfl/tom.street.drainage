#!/usr/bin/env python3
"""Chapter 119 ingest helper."""
from __future__ import annotations
import argparse, csv, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "13_PUBLIC_RECORDS_REQUESTS"
CONTROL = ROOT / "00_CONTROL"
ACTIONS_CSV = CONTROL / "MISSING_RECORDS_AND_ACTIONS.csv"
SOURCE_CSV = CONTROL / "SOURCE_REGISTER.csv"

def mark_submitted(gap_id: str | None, receipt_id: str | None) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CONTROL.mkdir(parents=True, exist_ok=True)
    gap_path = CONTROL / "MISSING_RECORDS_AND_ACTIONS.csv"
    if gap_path.exists():
        with gap_path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        changed = False
        for r in rows:
            if gap_id and r.get("gap_id") == gap_id:
                if receipt_id:
                    r["receipt_id"] = receipt_id
                r["status"] = r.get("status", "").replace("DRAFTED_NOT_SUBMITTED", "SUBMITTED") or "SUBMITTED"
                changed = True
        if changed:
            tmp = gap_path.with_suffix(".tmp")
            with tmp.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else ["gap_id","status","receipt_id"])
                w.writeheader(); w.writerows(rows)
            os.replace(tmp, gap_path)
    return {"status":"ok","gap_id":gap_id,"receipt_id":receipt_id,"submitted":"TRUE"}

def ingest_file(src: Path) -> dict:
    if not src or not src.exists():
        return {"status":"error","reason":"file_not_found"}
    raw = src.read_bytes()
    if not raw:
        raise ValueError("empty file")
    h = hashlib.sha256(raw).hexdigest()
    rec = {"ingested_utc":datetime.now(timezone.utc).isoformat(),"source_path":str(src),"size_bytes":len(raw),"sha256":h}
    sidecar = src.with_suffix(src.suffix + ".acquisition.json")
    sidecar.write_text(json.dumps(rec, indent=2)+"\n", encoding="utf-8")
    return rec

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gap-id")
    p.add_argument("--receipt-id")
    p.add_argument("--mark-submitted", action="store_true")
    p.add_argument("--ingest-file", type=Path)
    args = p.parse_args(argv)
    res = {"status":"ok"}
    if args.mark_submitted:
        res["mark"] = mark_submitted(args.gap_id, args.receipt_id)
    if args.ingest_file:
        res["ingest"] = ingest_file(args.ingest_file)
    print(json.dumps(res, indent=2))
    return 0
if __name__=="__main__":
    raise SystemExit(main())

def record_submission_receipt(gap_id: str, receipt_id: str) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CONTROL.mkdir(parents=True, exist_ok=True)
    if not ACTIONS_CSV.exists():
        ACTIONS_CSV.write_text("gap_id,status,submitted,receipt_id\n", encoding="utf-8")
    with ACTIONS_CSV.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    # normalize headers
    if not rows and "gap_id" not in (ACTIONS_CSV.read_text()[:200]):
        pass
    changed = False
    found = False
    for r in rows:
        if r.get("gap_id") == gap_id:
            found = True
            r["status"] = "SUBMITTED"
            r["submitted"] = "TRUE"
            r["receipt_id"] = receipt_id
            changed = True
    if not found:
        row = {"gap_id": gap_id, "status": "SUBMITTED", "submitted": "TRUE", "receipt_id": receipt_id}
        rows.append(row); changed = True
    tmp = ACTIONS_CSV.with_suffix(".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        fields = ["gap_id","status","submitted","receipt_id"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    os.replace(tmp, ACTIONS_CSV)
    return {"status":"ok","submitted":"TRUE","receipt_id": receipt_id}

def ingest_response_attachment(response_path: Path, gap_id: str | None = None, receipt_id: str | None = None) -> dict:
    if not response_path or not response_path.exists():
        raise FileNotFoundError(str(response_path))
    raw = response_path.read_bytes()
    if not raw:
        raise ValueError("empty")
    h = hashlib.sha256(raw).hexdigest()
    CONTROL.mkdir(parents=True, exist_ok=True)
    if not SOURCE_CSV.exists():
        SOURCE_CSV.write_text("source_id,document_title,issuing_agency,record_system,source_identifier,retrieval_date_utc,original_url,local_relative_path,file_type,file_size_bytes,sha256_hash,status,verification_method,notes\n", encoding="utf-8")
    return {"status":"ok","sha256":h,"size_bytes":len(raw)}

def ingest_agency_file(src_file: Path, gap_id: str | None = None, agency: str | None = None, dest_subdir: str | None = None, receipt_id: str | None = None) -> dict:
    if not src_file or not src_file.exists():
        raise FileNotFoundError(str(src_file))
    raw = src_file.read_bytes()
    if not raw.startswith(b"%PDF-"):
        raise ValueError("not plausible pdf")
    h = hashlib.sha256(raw).hexdigest()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target_dir = ROOT
    if dest_subdir:
        target_dir = ROOT / dest_subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    out = target_dir / f"PRR_{receipt_id or 'UNKNOWN'}_{ts}.pdf"
    out.write_bytes(raw)
    side = out.with_suffix(".pdf.acquisition.json")
    side.write_text(json.dumps({"sha256":h,"size_bytes":len(raw),"ingested_utc":datetime.now(timezone.utc).isoformat()}, indent=2)+"\n", encoding="utf-8")
    # append to SOURCE_CSV if exists
    if SOURCE_CSV.exists():
        with SOURCE_CSV.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            sid = f"SRC-PRR-{receipt_id or 'UNK'}-{ts[:8]}"
            w.writerow([sid, "Public Records Production", agency or "", "PRR", receipt_id or "", ts, "", out.relative_to(ROOT).as_posix(), "pdf", len(raw), h, "VERIFIED", "manual", "ingested"])
    return {"status":"ok","destination": out.relative_to(ROOT).as_posix(), "local_relative_path": out.relative_to(ROOT).as_posix(), "sidecar_manifest": side.relative_to(ROOT).as_posix(),"sha256":h,"size_bytes":len(raw)}
