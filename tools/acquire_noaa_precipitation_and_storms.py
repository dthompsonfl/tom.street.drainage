#!/usr/bin/env python3
"""Autonomously acquire NOAA Atlas 14 PFDS and NWS Weather API metadata."""
from __future__ import annotations
import argparse, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "11_HYDROLOGY_AND_HAZARD" / "NOAA_ATLAS14_AND_NWS"
ALLOWED_HOSTS = {"hdsc.nws.noaa.gov", "api.weather.gov"}
LAT, LON = 30.4152, -86.8147
MAX_BYTES = 12*1024*1024
USER_AGENT = "TomStreetPublicEvidence/2.0 (Precipitation-Audit)"

def check_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS or parsed.username or parsed.password or parsed.port not in (None,443):
        raise ValueError(f"Unapproved precipitation URL: {url}")
    return url

class CheckedRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def save_immutable(dest: Path, raw: bytes) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(raw).hexdigest()
    if dest.exists():
        old = hashlib.sha256(dest.read_bytes()).hexdigest()
        if old == digest:
            return {"storage_status":"UNCHANGED_EXISTING","path":dest.relative_to(ROOT).as_posix(),"sha256":digest,"bytes":len(raw)}
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        v = dest.with_name(f"{dest.stem}_{ts}{dest.suffix}")
        with NamedTemporaryFile(dir=dest.parent, delete=False) as f:
            f.write(raw); tmp=Path(f.name)
        os.replace(tmp,v)
        return {"storage_status":"UPSTREAM_CHANGED_VERSIONED_COPY_SAVED","path":v.relative_to(ROOT).as_posix(),"baseline_path":dest.relative_to(ROOT).as_posix(),"previous_sha256":old,"sha256":digest,"bytes":len(raw)}
    with NamedTemporaryFile(dir=dest.parent, delete=False) as f:
        f.write(raw); tmp=Path(f.name)
    os.replace(tmp,dest)
    return {"storage_status":"SAVED_NEW","path":dest.relative_to(ROOT).as_posix(),"sha256":digest,"bytes":len(raw)}

def fetch_json(label: str, url: str, dest: Path) -> dict:
    check_url(url)
    rec = {"source_id":label,"requested_url":url,"retrieved_utc":datetime.now(timezone.utc).isoformat(),"status":"NOT_ACQUIRED"}
    try:
        headers={"User-Agent":USER_AGENT,"Accept":"application/json"}
        req=Request(url, headers=headers)
        with build_opener(CheckedRedirectHandler()).open(req, timeout=60) as resp:
            check_url(resp.url)
            raw=resp.read(MAX_BYTES+1)
            if len(raw)>MAX_BYTES: raise ValueError("Response exceeds 12 MB cap")
            rec["http_status"]=resp.status; rec["final_url"]=resp.url
            json.loads(raw)
            saved=save_immutable(dest, raw)
            rec.update({"status":"PUBLIC_PRECIP_VALIDATED",**saved})
    except Exception as exc:
        rec["failure"]=f"{type(exc).__name__}:{exc}"[:350]
    return rec

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__); parser.parse_args(argv)
    OUT_DIR.mkdir(parents=True,exist_ok=True)
    results=[]
    atlas_url="https://hdsc.nws.noaa.gov/cgi-bin/hdsc/new/fe_text_mean.csv?lat="+str(LAT)+"&lon="+str(LON)+"&data=depth&units=english"
    results.append(fetch_json("NOAA_ATLAS14_PFDS_POINT", atlas_url, OUT_DIR/"noaa_atlas14_pfds_point.csv"))
    nws_pts=f"https://api.weather.gov/points/{LAT},{LON}"
    results.append(fetch_json("NWS_POINT_METADATA", nws_pts, OUT_DIR/"nws_point_metadata.json"))
    results.sort(key=lambda r:r["source_id"])
    manifest={"captured_utc":datetime.now(timezone.utc).isoformat(),"tool":Path(__file__).name,"point":{"lat":LAT,"lon":LON},"captured_count":sum(1 for r in results if r["status"]=="PUBLIC_PRECIP_VALIDATED"),"requested_count":len(results),"records":results,"limitations":["PFDS reflects NOAA Atlas 14; local drainage capacity separate."]}
    p=OUT_DIR/"ACQUISITION_MANIFEST.json"; p.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"manifest":p.relative_to(ROOT).as_posix(),"captured_count":manifest["captured_count"]}))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
