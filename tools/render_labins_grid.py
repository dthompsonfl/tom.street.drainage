#!/usr/bin/env python3
"""Render official LABINS Santa Rosa county imagery grid as review-only image.

No attempt to infer the Tom Street tile without geographic cross-reference.
Preserve original PDF unchanged, derive one 2400-pixel long-side preview,
and provide page dimensions and text-layer status.
"""
import hashlib
import io
import json
from pathlib import Path
import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-17/LABINS_SANTA_ROSA"
SRC=DIR/"ORIGINAL_LABINS_SANTA_ROSA_HIRES_GRID_MAP.pdf"
OUT=DIR/"DERIVED_LABINS_SANTA_ROSA_GRID_PREVIEW.jpg"
MAN=DIR/"DERIVED_GRID_RENDER.json"

def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    manifest=json.loads((DIR/"ACQUISITION_MANIFEST.json").read_text())
    expected=manifest["official_grid_index"]
    assert expected["status"]=="ORIGINAL_GRID_PDF_SAVED_AND_HASHED"
    data=SRC.read_bytes()
    assert len(data)==expected["bytes"] and sha(data)==expected["sha256"]
    doc=fitz.open(stream=data,filetype="pdf")
    assert len(doc)==1
    page=doc[0]
    rect=page.rect
    scale=min(2.5,2400.0/max(rect.width,rect.height))
    pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
    img=Image.frombytes("RGB",(pix.width,pix.height),pix.samples)
    buf=io.BytesIO();img.save(buf,format="JPEG",quality=88,optimize=True)
    raw=buf.getvalue()
    if OUT.exists() and sha(OUT.read_bytes())!=sha(raw):
        raise RuntimeError("Render differs from earlier immutable preview")
    if not OUT.exists():OUT.write_bytes(raw)
    parsed=page.get_text("text")
    out={
      "source":SRC.relative_to(ROOT).as_posix(),
      "source_sha256":sha(data),
      "original_page_count":1,
      "original_page_points":[rect.width,rect.height],
      "page_text_layer_characters":len(parsed),
      "page_text_excerpt":parsed[:400],
      "preview":OUT.relative_to(ROOT).as_posix(),
      "preview_sha256":sha(raw),
      "preview_bytes":len(raw),
      "preview_dimensions_px":img.size,
      "classification":"VISUAL_DERIVATIVE_NOT_AUTHORITATIVE_GRID_BOUNDARY_SURVEY",
      "limitation":"Image must be geographically interpreted against original printed cells; do not infer Tom Street cell from this PDF alone."
    }
    MAN.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))

if __name__=="__main__":main()
