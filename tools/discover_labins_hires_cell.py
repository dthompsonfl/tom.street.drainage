#!/usr/bin/env python3
"""Discover original LABINS high-resolution aerial files covering cell 648138.

Bounded public web form access only. Preserve original official query HTML
and source URLs if they include the verified six-digit cell. Never fabricate
imagery from the imagery grid or save login/session information.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urljoin,urlsplit
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-17/LABINS_SANTA_ROSA"
PAGE="https://www.labins.org/mapping_data/aerials/hi-resolution_images.cfm"
CELL="648138"
MAX_BYTES=3_000_000
UA="TomStreetPublicEvidence/2.0 (source archive, public LABINS cell 648138)"

def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,b):
    f=OUT/name
    if f.exists() and f.read_bytes()!=b:raise RuntimeError("Existing official source mismatch")
    if not f.exists():f.write_bytes(b)
    return {"path":f.relative_to(ROOT).as_posix(),"bytes":len(b),"sha256":sha(b)}

def response(r):
    r.raise_for_status()
    if urlsplit(r.url).hostname not in ("www.labins.org","ftp.labins.org"):
        raise RuntimeError("Unexpected cross-host response")
    if len(r.content)>MAX_BYTES or len(r.content)<80:raise RuntimeError("Unbounded or empty response")
    if "html" not in r.headers.get("Content-Type","").lower():raise RuntimeError("Not a public HTML source")
    return r.content

def bounded_links(soup,url):
    links=[]
    for link in soup.find_all("a",href=True):
        u=urljoin(url,link["href"])
        if urlsplit(u).scheme!="https" or urlsplit(u).hostname not in ("www.labins.org","ftp.labins.org"):
            continue
        txt=" ".join(link.stripped_strings)[:90]
        if (CELL in u or CELL in txt or any(ext in u.lower() for ext in (".sid",".jp2",".zip",".tif",".sdw",".txt"))):
            links.append({"official_url":u,"label":txt})
    return links[:120]

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    session=requests.Session()
    session.headers.update({"User-Agent":UA,"Accept":"text/html"})
    result={"timestamp_utc":datetime.now(timezone.utc).isoformat(),"exact_verified_grid_id":CELL,
        "authoritative_id_source":"https://maps.freac.fsu.edu/arcgis/rest/services/LABINS/LABINS_Data_ccr_relate/MapServer/14",
        "query_page":PAGE,
        "status":"NOT_OBTAINED","source_documents":[],"form_schema":[],"search_results":[],
        "limits":["Aerial availability varies by collection year even when grid ID is correct.",
          "Link to a file is not source-file acquisition; download and independently validate actual bytes and map metadata before claiming imagery obtained.",
          "Zero links may reflect dynamic site UI, inventory omissions or inaccessible public download rather than absence of imagery."]}
    try:
        r=session.get(PAGE,timeout=60)
        b=response(r)
        # Public unpersonalized GET page can be archived.
        result["source_documents"].append(save("ORIGINAL_LABINS_HIRES_CELL_DOWNLOAD_SEARCH_FORM.html",b)|{"official_url":r.url})
        soup=BeautifulSoup(b,"html.parser")
        for form in soup.find_all("form"):
            inputs=[]
            hidden={}
            for el in form.select("input"):
                f={"type":el.get("type","text").lower(),"name":el.get("name"),"value":(el.get("value","") or "")[:30]}
                inputs.append(f)
                if f["type"]=="hidden" and f["name"]:hidden[f["name"]]=el.get("value","")
            method=(form.get("method") or "GET").upper()
            url=urljoin(r.url,form.get("action") or PAGE)
            descriptor={"method":method,"official_action":url,"fields":inputs[:30]}
            result["form_schema"].append(descriptor)
            if urlsplit(url).hostname!="www.labins.org":continue
            candidate=[v for v in inputs if v["type"] in ("text","search","number") and v["name"]]
            if len(candidate)!=1:continue
            data={**hidden,candidate[0]["name"]:CELL}
            item={"method":method,"url":url,"field_name":candidate[0]["name"],"status":"NOT_QUERIED"}
            try:
                res=session.post(url,data=data,timeout=70,allow_redirects=False) if method=="POST" else session.get(url,params=data,timeout=70,allow_redirects=False)
                if 300<=res.status_code<400:
                    nxt=urljoin(url,res.headers.get("Location",""))
                    if urlsplit(nxt).hostname!="www.labins.org":raise RuntimeError("Unexpected redirect")
                    res=session.get(nxt,timeout=70,allow_redirects=False)
                raw=response(res)
                if CELL not in raw.decode("utf-8",errors="ignore"):
                    item["validation"]="No grid identifier echoed in result; links might be generic"
                else:item["validation"]="Grid identifier echoed in official response"
                original="ORIGINAL_LABINS_CELL_648138_SEARCH_RESULT.html"
                item["source_capture"]=save(original,raw)|{"official_url":res.url}
                sub=BeautifulSoup(raw,"html.parser")
                item["candidate_download_links"]=bounded_links(sub,res.url)
                item["search_title"]=sub.title.get_text(" ",strip=True)[:130] if sub.title else ""
                item["status"]="OFFICIAL_PUBLIC_CELL_FORM_RESPONSE_ARCHIVED"
            except Exception as exc:
                item["status"]="PUBLIC_CELL_QUERY_UNAVAILABLE"
                item["failure"]=type(exc).__name__+": "+str(exc)[:230]
            result["search_results"].append(item)
        result["status"]="CELL_QUERY_COMPLETED" if any(x["status"].startswith("OFFICIAL") for x in result["search_results"]) else "FORM_DISCOVERED_BUT_NO_CONFIRMED_CELL_RECORDS"
    except Exception as exc:
        result["status"]="PUBLIC_LABINS_PAGE_ACCESS_FAILED"
        result["failure"]=type(exc).__name__+": "+str(exc)[:230]
    (OUT/"LABINS_648138_IMAGE_DOWNLOAD_DISCOVERY_MANIFEST.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"forms":result["form_schema"],
            "results":[{"status":x["status"],"links":x.get("candidate_download_links",[]),"validation":x.get("validation")} for x in result["search_results"]]},indent=2))
if __name__=="__main__":main()
