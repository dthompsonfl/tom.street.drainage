#!/usr/bin/env python3
"""Fetch exact original LABINS MrSID image and world/aux/xml sidecars, grid 648138.

Only official links parsed from preserved LABINS lookup are allowed. Bytes remain
unmodified. A source exceeding safety caps is reported as missing, not forged.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
import requests

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-17/LABINS_SANTA_ROSA"
SOURCE=BASE/"LABINS_648138_IMAGE_DOWNLOAD_DISCOVERY_MANIFEST.json"
OUT=BASE/"ORIGINAL_IMAGERY_CELL_648138"
MAX_FILE=78*1024*1024
MAX_RUN=220*1024*1024
CHUNK=1024*1024

def check_url(url,year):
    p=urlsplit(url)
    if p.scheme!="https" or p.hostname not in ("www.labins.org","ftp.labins.org"):
        raise ValueError("Not official LABINS source")
    ext=Path(p.path).suffix.lower()
    if ext not in (".sid",".sdw",".aux",".xml"):raise ValueError("Unexpected media type")
    if f"/Imagery/{year}/" not in p.path or "_648138_24" not in Path(p.path).name or p.query:
        raise ValueError("URL not for the verified grid and year")
    return Path(p.path).name,ext

def validate(path,ext):
    if path.stat().st_size<16:raise ValueError("Empty/implausibly small source")
    with path.open("rb") as file:head=file.read(512)
    if b"<html" in head.lower() or b"<!doctype" in head.lower():raise ValueError("HTML masquerading as media")
    if ext==".sid" and head[:4].lower()!=b"msid":
        raise ValueError("Missing genuine MrSID file header: "+head[:12].hex())
    if ext==".sdw":
        nums=path.read_text(encoding="ascii").split()
        if len(nums)!=6 or any(not math.isfinite(float(n)) for n in nums):
            raise ValueError("Invalid georeferencing world file")
    if ext==".xml":ET.parse(path)

def download(session,url,year,remaining):
    fname,ext=check_url(url,year)
    target=OUT/str(year)/fname
    item={"year":year,"source_url":url,"name":fname,"status":"NOT_OBTAINED"}
    tmp=None
    try:
        with session.get(url,stream=True,timeout=(25,150),allow_redirects=False) as r:
            if r.status_code!=200:raise RuntimeError(f"HTTP {r.status_code}")
            declared=int(r.headers.get("Content-Length","0") or 0)
            cap=MAX_FILE if ext==".sid" else 3*1024*1024
            item["declared_bytes"]=declared
            item["content_type"]=r.headers.get("Content-Type","")
            if declared and declared>min(cap,remaining):
                raise ValueError("Source exceeds safe public-Git preservation size")
            target.parent.mkdir(parents=True,exist_ok=True)
            with NamedTemporaryFile(dir=target.parent,prefix=".source_",delete=False) as f:
                tmp=Path(f.name);n=0;h=hashlib.sha256()
                for chunk in r.iter_content(CHUNK):
                    if not chunk:continue
                    n+=len(chunk)
                    if n>min(cap,remaining):raise ValueError("Stream exceeded safe preservation size")
                    f.write(chunk);h.update(chunk)
            validate(tmp,ext)
            item.update(bytes=n,sha256=h.hexdigest(),path=target.relative_to(ROOT).as_posix())
            if target.exists():
                with target.open("rb") as f:
                    old=hashlib.file_digest(f,"sha256").hexdigest()
                if target.stat().st_size!=n or old!=h.hexdigest():
                    raise ValueError("Prior original has different bytes: no overwrite")
                item["status"]="ORIGINAL_ALREADY_ARCHIVED_IDENTICAL"
                tmp.unlink()
            else:
                os.replace(tmp,target)
                item["status"]="ORIGINAL_OFFICIAL_BYTES_ARCHIVED_AND_VALIDATED"
            tmp=None
    except Exception as exc:
        item["status"]="SOURCE_DOWNLOAD_FAILED_OR_TOO_LARGE"
        item["error"]=type(exc).__name__+": "+str(exc)[:220]
    finally:
        if tmp and tmp.exists():tmp.unlink()
    return item

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--year",type=int,choices=[2007,2010,2013,2016,2019],required=True)
    year=ap.parse_args().year
    source=json.loads(SOURCE.read_text(encoding="utf-8"))
    if source.get("exact_verified_grid_id")!="648138" or source.get("status")!="CELL_QUERY_COMPLETED":
        raise RuntimeError("No verified official LABINS grid source")
    urls=[p["official_url"] for query in source.get("search_results",[])
          for p in query.get("candidate_download_links",[])
          if f"/Imagery/{year}/" in p["official_url"]]
    if not 1<=len(urls)<=7:raise RuntimeError("Unexpected number of official year sources")
    s=requests.Session()
    s.headers.update({"User-Agent":"TomStreetPublicEvidence/2.0","Accept":"application/octet-stream,*/*"})
    files=[];remaining=MAX_RUN
    for url in urls:
        info=download(s,url,year,remaining)
        files.append(info)
        if info["status"].startswith("ORIGINAL_"):remaining-=info["bytes"]
    OUT.mkdir(parents=True,exist_ok=True)
    manifest={"retrieved_utc":datetime.now(timezone.utc).isoformat(),"year":year,
        "official_grid_identifier":"648138",
        "exact_download_index":SOURCE.relative_to(ROOT).as_posix(),
        "published_file_count":len(urls),
        "archived_file_count":sum(v["status"].startswith("ORIGINAL_") for v in files),
        "files":files,
        "limitations":[
            "MrSID and sidecar bytes are original official material; no image transformation.",
            "Source collection year is not precise photographic flight date.",
            "Orthoimagery does not measure vertical lot grades or establish builder stormwater responsibility.",
            "Oversized or inaccessible source files are explicitly excluded, not reported as saved.",
            "Missing world/aux/xml sidecars prevent complete georeferenced image reuse."]}
    (OUT/f"ACQUISITION_MANIFEST_{year}.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"year":year,"published":len(urls),"archived":manifest["archived_file_count"],
       "results":[{"name":x["name"],"status":x["status"],"bytes":x.get("bytes"),"error":x.get("error")} for x in files]},indent=2))
if __name__=="__main__":main()
