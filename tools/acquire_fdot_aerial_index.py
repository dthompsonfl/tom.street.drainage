#!/usr/bin/env python3
"""Archive FDOT historical aerial-photography availability catalogues.

County-year archive listing is an inventory, not proof that a particular frame
covers Tom Street or can be downloaded without APLUS access.
"""
from __future__ import annotations
import hashlib
import json
import os
from datetime import datetime,timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import Request,urlopen
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1] / ("11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/FDOT_AERIAL_ARCHIVE_INDEX")
BASE="https://fdotwww.blob.core.windows.net/sitefinity/docs/default-source/co-gis/aplus/"
DOCS={
    "FDOT_AVAILABLE_AERIAL_PHOTOGRAPHY_2026_LIST": BASE+"aerial-photography-listecc67b89-a9cc-4abe-9516-b7e8a977c432.pdf?sfvrsn=446ef142_4",
    "FDOT_RECENT_COUNTY_PHOTO_STATUS": BASE+"aerial-status.pdf?sfvrsn=a300ebe_8",
}

def grab(key,url):
    target=ROOT/(key+".pdf")
    record={"document":key,"url":url,"status":"NOT_OBTAINED"}
    try:
        with urlopen(Request(url,headers={"User-Agent":"TomStreetEvidenceArchive/1.0"}),timeout=90) as resp:
            if resp.status!=200: raise ValueError(f"HTTP {resp.status}")
            raw=resp.read(13_000_001)
        if len(raw)>13_000_000 or raw[:5]!=b"%PDF-":
            raise ValueError("Unexpected or oversized PDF")
        with NamedTemporaryFile(suffix=".pdf",dir=ROOT,delete=False) as f:
            f.write(raw)
            tmp=Path(f.name)
        try:
            pdf=PdfReader(tmp,strict=False)
            if pdf.is_encrypted:raise ValueError("Encrypted report")
            if len(pdf.pages)<1 or len(pdf.pages)>200:raise ValueError("Unreasonable number of pages")
            text="\n".join(page.extract_text() or "" for page in pdf.pages)
            digest=hashlib.sha256(raw).hexdigest()
            if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
                raise ValueError("Previously archived original differs")
            if not target.exists():
                os.replace(tmp,target)
            sample=[]
            for line in text.splitlines():
                if "santa rosa" in line.casefold():
                    sample.append(line.strip()[:280])
            record.update({"status":"ORIGINAL_FDOT_COUNTY_INDEX_PDF_SAVED", "path":str(target),
                           "sha256":digest,"bytes":len(raw),"page_count":len(pdf.pages),
                           "visible_text_lines_mentioning_santa_rosa":sample[:10],
                           "has_santa_rosa_visible_text":bool(sample)})
        finally:
            tmp.unlink(missing_ok=True)
    except Exception as e:
        record["error"]=f"{type(e).__name__}: {e}"[:350]
    return record

def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    records=[grab(k,v) for k,v in DOCS.items()]
    out={"retrieved_utc":datetime.now(timezone.utc).isoformat(),
         "agency":"Florida Department of Transportation GIS Aerial Photo Archive",
         "official_portal":"https://www.fdot.gov/gis/aerialproducts.shtm",
         "documents":records,
         "status":"ALL_SOURCE_LISTS_ACQUIRED" if all(r["status"].startswith("ORIGINAL_") for r in records) else "PARTIAL_COUNTY_AERIAL_LIST_ACQUISITION",
         "limitations":[
             "County aerial collection year listing does not establish a photograph for every Tom Street lot and date.",
             "Historic frames may require FDOT APLUS user access and manual geographic index review.",
             "County lists are administrative inventories, not parcel surveys, flight-line GPS metadata or current impervious surface data.",
             "Follow FDOT source restrictions/attribution for distribution of actual photographic frames.",
         ]}
    (ROOT/"ACQUISITION_MANIFEST.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    for rec in records:print(rec["document"],rec["status"],rec.get("bytes"),rec.get("visible_text_lines_mentioning_santa_rosa",[]))
    if not any(rec["status"].startswith("ORIGINAL_") for rec in records):
        raise RuntimeError("No original FDOT aerial availability catalogue obtained")
if __name__=="__main__":
    main()
