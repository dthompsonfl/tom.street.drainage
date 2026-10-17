#!/usr/bin/env python3
"""Acquire public LABINS Santa Rosa imagery map and dated inventory leads.

All sources are public HTTPS records. One original County grid PDF may be saved
if the bytes parse as a PDF. Any inventory entries are derived excerpts with
source URLs, not original imagery or proof of Tom Street tile coverage.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-17/LABINS_SANTA_ROSA"
INVENTORY="https://www.labins.org/mapping_data/aerials/image_inventory.cfm"
GRID="https://ftp.labins.org/CountyGridMaps/SantaRosa.pdf"
MAX=15_000_000
UA="TomStreetPublicEvidence/2.0 (public LABINS geospatial inventory)"

def utc():return datetime.now(timezone.utc).isoformat()
def save_original(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and sha256(path.read_bytes()).digest()!=sha256(raw).digest():
        raise RuntimeError("Existing source bytes changed: preserve a dated version separately")
    if not path.exists():path.write_bytes(raw)
    return {"path":path.relative_to(ROOT).as_posix(),"sha256":sha256(raw).hexdigest(),"bytes":len(raw)}

def get(session,url):
    p=urlparse(url)
    if p.scheme!="https" or p.hostname not in {"www.labins.org","ftp.labins.org"}:
        raise RuntimeError("Unexpected public source host")
    r=session.get(url,timeout=65,allow_redirects=False)
    if r.status_code in (301,302,303,307,308):
        next_url=urljoin(url,r.headers.get("Location",""))
        if urlparse(next_url).hostname not in {"www.labins.org","ftp.labins.org"}:
            raise RuntimeError("LABINS cross-domain redirect")
        r=session.get(next_url,timeout=65)
    r.raise_for_status()
    if not(100<=len(r.content)<=MAX):raise RuntimeError("Source empty or oversized")
    return r

def inventory(session):
    summary={"index_url":INVENTORY,"status":"NOT_OBTAINED","search_attempts":[]}
    try:
        response=get(session,INVENTORY)
        soup=BeautifulSoup(response.text,"html.parser")
        summaries=[]
        for form in soup.select("form"):
            controls=[]
            for select in form.select("select"):
                opts=[(o.get("value","")," ".join(o.stripped_strings)[:70]) for o in select.select("option")]
                controls.append({"name":select.get("name"),"id":select.get("id"),
                                 "options_count":len(opts),
                                 "santa_rosa_options":[o for o in opts if "SANTA ROSA" in o[1].upper()],
                                 "years_present":sorted({o[1] for o in opts if re.fullmatch(r"20(?:1[0-9]|2[0-9])",o[1].strip())})})
            summaries.append({"method":form.get("method"),"action":form.get("action"),"controls":controls})
            fields={}
            for sel in form.select("select"):
                opt=next((o for o in sel.select("option") if "SANTA ROSA" in " ".join(o.stripped_strings).upper()),None)
                if opt and sel.get("name"):fields[sel.get("name")]=opt.get("value","")
            if not fields:continue
            for year in ("2022","2025"):
                data=dict(fields)
                for sel in form.select("select"):
                    option=next((o for o in sel.select("option") if " ".join(o.stripped_strings).strip()==year),None)
                    if option and sel.get("name"):data[sel.get("name")]=option.get("value","")
                q={"year":year,"selected_fields":list(data.keys()),"status":"NOT_QUERIED"}
                try:
                    url=urljoin(INVENTORY,form.get("action") or INVENTORY)
                    if urlparse(url).hostname!="www.labins.org":
                        raise RuntimeError("Search form target not official LABINS domain")
                    method=(form.get("method") or "GET").upper()
                    resp=session.post(url,data=data,timeout=50) if method=="POST" else session.get(url,params=data,timeout=50)
                    resp.raise_for_status()
                    doc=BeautifulSoup(resp.text,"html.parser")
                    rows=[]
                    for tr in doc.select("tr"):
                        cols=[" ".join(c.stripped_strings)[:100] for c in tr.select("td")]
                        label=" ".join(cols)
                        if "SANTA ROSA" in label.upper() and (year in label or len(cols)>=4):
                            rows.append({"columns":cols[:10]})
                    q.update({"status":"RESULT_PAGE_RETURNED_RECORDS_NEED_INTERPRETATION",
                              "final_url":resp.url.split("?")[0],
                              "county_rows":rows[:25],
                              "matching_row_count":len(rows)})
                except Exception as exc:
                    q["status"]="PUBLIC_INVENTORY_FILTER_FAILED"
                    q["reason"]=type(exc).__name__+": "+str(exc)[:200]
                summary["search_attempts"].append(q)
        summary["published_form_schema"]=summaries[:10]
        summary["status"]="PUBLIC_SOURCE_PAGE_ACCESSED" if summaries else "NO_DISCERNIBLE_FILTER_FORM"
    except Exception as exc:
        summary["status"]="INVENTORY_WEB_SOURCE_UNAVAILABLE"
        summary["reason"]=type(exc).__name__+": "+str(exc)[:200]
    return summary

def gridmap(session):
    a={"source_url":GRID,"status":"NOT_OBTAINED"}
    try:
        r=get(session,GRID)
        b=r.content
        if not b.startswith(b"%PDF-"):raise RuntimeError("Grid reference did not return PDF bytes")
        pdf=PdfReader(BytesIO(b),strict=False)
        if not 1<=len(pdf.pages)<=30:raise RuntimeError("Implausible LABINS grid PDF pages")
        a.update(save_original(OUT/"ORIGINAL_LABINS_SANTA_ROSA_HIRES_GRID_MAP.pdf",b))
        a.update({"page_count":len(pdf.pages),"status":"ORIGINAL_GRID_PDF_SAVED_AND_HASHED",
                  "meaning":"Official imagery tile index map, not actual 2022 or 2025 image"})
    except Exception as exc:
        a["status"]="LABINS_PUBLIC_GRID_PDF_UNAVAILABLE"
        a["reason"]=type(exc).__name__+": "+str(exc)[:220]
    return a

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    s=requests.Session();s.headers["User-Agent"]=UA
    report={"captured_utc":utc(),"location_query":"Santa Rosa County, Florida",
            "official_grid_index":gridmap(s),
            "inventory":inventory(s),
            "limitations":[
                "No individual Tom Street frame/tile is identified solely by county dataset availability.",
                "The official 2022/2025 inventory years do not prove particular photographic flight dates or local coverage.",
                "A grid PDF is an index, not original photographic evidence.",
                "The public inventory's derived search rows may be incomplete due to Javascript/session filtering.",
            ]}
    (OUT/"ACQUISITION_MANIFEST.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"grid":report["official_grid_index"]["status"],
      "inventory":report["inventory"]["status"],
      "query_results":[{"year":r["year"],"status":r["status"],
                        "county_rows":r.get("matching_row_count")} for r in report["inventory"].get("search_attempts",[])]},indent=2))

if __name__=="__main__":main()
