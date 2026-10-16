#!/usr/bin/env python3
"""Visually inspect and preserve nonauthoritative image derivatives of the official
Crescent Shores recorded Plat Book A, Page 70. Never modify the recorded PDF.
The rendered images are display aids only; any handwritten measurements or
easement labels require independent survey/Clerk document interpretation.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from io import BytesIO

import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"02_PROPERTY_AND_PARCELS/PRE_REQUEST_OCT16_PRIMARY_LOOKUPS/ORIGINAL_CLERK_PLAT_BOOK_A_PAGE_70.pdf"
ACQ=ROOT/"02_PROPERTY_AND_PARCELS/PRE_REQUEST_OCT16_PRIMARY_LOOKUPS/ACQUISITION_REPORT.json"
OUT=ROOT/"02_PROPERTY_AND_PARCELS/PRE_REQUEST_OCT16_PRIMARY_LOOKUPS/PLAT_A_70_DISPLAY_DERIVATIVES"
REPORT=OUT/"INSPECTION_AND_RENDER_MANIFEST.json"

def digest(b):return hashlib.sha256(b).hexdigest()

def main():
    j=json.loads(ACQ.read_text())
    match=j["clerk_plat_search"]["queries"][0]["exact_plat_index_matches"]
    assert len(match)==1 and match[0]["book_page"]=="A/70" and match[0]["legal_region"]=="CRESCENT SHORES"
    source=SOURCE.read_bytes()
    assert source.startswith(b"%PDF-"),"Not original Clerk PDF"
    assert digest(source)==match[0]["original"]["sha256"],"Primary PDF SHA256 differs from acquisition"
    assert len(source)==match[0]["original"]["bytes"]
    doc=fitz.open(stream=source,filetype="pdf")
    assert len(doc)==2,"Archived original page count unexpectedly changed"
    OUT.mkdir(parents=True,exist_ok=True)
    records=[]
    for idx,page in enumerate(doc):
        rect=page.rect
        text=page.get_text("text") or ""
        images=page.get_images(full=True)
        # Source is scanned historic map; preserve one clear full-sheet preview.
        scale=min(2.0,1800/max(rect.width,rect.height))
        pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
        im=Image.frombytes("RGB",(pix.width,pix.height),pix.samples)
        file=OUT/f"DERIVED_CRESCENT_SHORES_PLAT_A_70_PAGE_{idx+1}_PREVIEW.jpg"
        buf=BytesIO();im.save(buf,format="JPEG",quality=90,optimize=True)
        raw=buf.getvalue()
        if file.exists() and digest(file.read_bytes())!=digest(raw):
            raise RuntimeError("Source render changed; do not overwrite derived evidence: "+file.name)
        if not file.exists():file.write_bytes(raw)
        records.append({"source_page":idx+1,"pdf_page_width_pt":round(rect.width,2),
                        "pdf_page_height_pt":round(rect.height,2),
                        "text_chars":len(text.strip()),"image_xobjects":len(images),
                        "preview":file.relative_to(ROOT).as_posix(),
                        "preview_bytes":len(raw),"preview_sha256":digest(raw),
                        "preview_dimensions_px":[im.width,im.height],
                        "text_excerpt":text.strip()[:600] if text.strip() else "",
                        "note":"Display derivative. Do not use to determine survey distances or drainage rights."})
    payload={
        "rendered_utc":datetime.now(timezone.utc).isoformat(),
        "source_authority":"Santa Rosa County Clerk of the Circuit Court",
        "source_document_id":"875693","source_plat_book_page":"A/70",
        "source_sha256":digest(source),"source_bytes":len(source),
        "source_official_url":"https://acclaim.srccol.com/AcclaimWeb/Image/DocumentPdfAllPages/875693",
        "records":records,
        "limitations":["Source PDF is immutable, previews are lossy JPEG derivatives.",
          "No legal boundary, survey, plat dedication, drainage easement or lot split may be inferred solely from the previews.",
          "Page text extraction count is not an OCR review or certified transcription.",
          "Separate Lot QQ chain of title and 2026 approved grading plans remain necessary.",
          "Public GitHub remains a disclosure surface; do not add private neighbor media or contact data."],
    }
    REPORT.write_text(json.dumps(payload,indent=2)+"\n")
    print(json.dumps({"original_bytes":len(source),
      "source_sha256":digest(source),"page_count":len(records),
      "page_previews":[{"path":r["preview"],"size":r["preview_bytes"],
       "dimensions":r["preview_dimensions_px"],"text_chars":r["text_chars"]} for r in records]},indent=2))

if __name__=="__main__":main()
