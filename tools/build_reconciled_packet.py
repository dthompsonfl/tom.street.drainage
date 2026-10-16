#!/usr/bin/env python3
"""Build PUBLIC-SAFE Tom Street homeowner draft PDFs, never resident photographs.

Only the five explicitly listed Markdown files are eligible release inputs.
Each PDF remains DRAFT, with its own footer and an evidence-scope manifest.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate
from reportlab.pdfgen import canvas as pdf_canvas
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "15_RECONCILED_DRAFTS"
OUT = SOURCE / "pdf"
SELECTED = (
    ("01_HOMEOWNER_BRIEF.md", "Tom_Street_Homeowner_Brief.pdf"),
    ("06_COMMISSIONER_COVER_LETTER_DRAFT.md", "Tom_Street_Commissioner_Cover_Letter_Draft.pdf"),
    ("02_COUNTY_LETTER_DRAFT.md", "Tom_Street_County_Letter_Draft.pdf"),
    ("03_PROXY_MEETING_NOTES.md", "Tom_Street_Proxy_Meeting_Notes.pdf"),
    ("05_RECORDS_STATUS_AND_FOLLOW_UP.md", "Tom_Street_Records_Status_and_Follow_Up.pdf"),
)
COMBINED = "Tom_Street_Reconciled_Public_Meeting_Draft.pdf"
ZIP_NAME = "Tom_Street_Reconciled_Public_Drafts.zip"

STYLE = {
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=17.5, leading=21, textColor=colors.HexColor("#142D3B"), spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=12, leading=15.5, textColor=colors.HexColor("#183C4E"), spaceBefore=9, spaceAfter=4, keepWithNext=True),
    "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=11, leading=14.5, textColor=colors.HexColor("#183C4E"), spaceBefore=8, spaceAfter=4, keepWithNext=True),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=11.25, leading=15.3, spaceAfter=7, allowWidows=0, allowOrphans=0),
    "item": ParagraphStyle("item", fontName="Helvetica", fontSize=11.1, leading=15.2, leftIndent=18, firstLineIndent=-12, spaceAfter=5, allowWidows=0, allowOrphans=0),
    "fine": ParagraphStyle("fine", fontName="Helvetica-Oblique", fontSize=9.6, leading=13.2, textColor=colors.HexColor("#52656E"), spaceAfter=7),
}

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def markup(line: str) -> str:
    line = html.escape(line, quote=False)
    line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
    line = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", line)
    return re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="#1B5973">\1</link>', line)

def read_markdown(source: str):
    flow = []
    para = []
    def flush():
        if para:
            flow.append(Paragraph(markup(" ".join(para)), STYLE["body"]))
            para.clear()
    for raw in source.splitlines():
        hard_break = raw.endswith("  ")  # Markdown: two trailing spaces start a new line
        line = raw.strip()
        if not line:
            flush()
            continue
        if set(line) == {"-"}:
            flush()
            flow.append(HRFlowable(width="100%", thickness=.4, color=colors.HexColor("#C9D3D9"), spaceBefore=6, spaceAfter=10))
            continue
        if line.startswith("# "):
            flush()
            flow.append(Paragraph(markup(line[2:]), STYLE["title"]))
            continue
        if line.startswith("## "):
            flush()
            flow.append(Paragraph(markup(line[3:]), STYLE["h2"]))
            continue
        if line.startswith("### "):
            flush()
            flow.append(Paragraph(markup(line[4:]), STYLE["h3"]))
            continue
        if line.startswith(">"):
            flush()
            flow.append(Paragraph(markup(line.lstrip("> ").strip()), STYLE["fine"]))
            continue
        item = re.match(r"^(-|\*|\d+[.)])\s+(.*)$", line)
        if item:
            flush()
            bullet = "\u2022" if item.group(1) in ("-", "*") else item.group(1)
            flow.append(Paragraph(markup(bullet + "  " + item.group(2)), STYLE["item"]))
            continue
        if line.startswith("|"):
            raise ValueError("Public packet source cannot contain a Markdown table")
        para.append(line)
        if hard_break:
            flush()
    flush()
    return flow

def footer(canvas, doc):
    canvas.saveState()
    width, _ = letter
    canvas.setStrokeColor(colors.HexColor("#CBD6DB"))
    canvas.line(.76 * inch, .59 * inch, width - .76 * inch, .59 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#586971"))
    canvas.drawString(.76 * inch, .42 * inch, "TOM STREET | Evidence-based homeowner DRAFT | Not a legal or engineering conclusion")
    canvas.restoreState()

def create_pdf(source: str, path: Path) -> int:
    doc = SimpleDocTemplate(str(path), pagesize=letter, leftMargin=.79*inch, rightMargin=.79*inch,
                            topMargin=.7*inch, bottomMargin=.72*inch,
                            title=path.stem, author="Tom Street homeowner research draft", pageCompression=1)
    doc.build(read_markdown(source), onFirstPage=footer, onLaterPages=footer)
    reader = PdfReader(str(path))
    pages = len(reader.pages)
    if pages < 1 or pages > 12:
        raise AssertionError("Unexpected page count in " + str(path))
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    if len(extracted) < min(400, len(source)//3):
        raise AssertionError("PDF text extraction coverage too low: " + str(path))
    if "DRAFT" not in extracted:
        raise AssertionError("Draft watermark/footer missing in " + str(path))
    return pages

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()
    outputs = []
    for md_name, pdf_name in SELECTED:
        markdown = SOURCE / md_name
        text = markdown.read_text(encoding="utf-8")
        if "draft" not in text.lower():
            raise AssertionError("Missing draft status in " + md_name)
        if "|" in text and any(line.startswith("|") for line in text.splitlines()):
            raise AssertionError("Unsupported table in " + md_name)
        pdf = OUT / pdf_name
        pages = create_pdf(text, pdf)
        for page in PdfReader(str(pdf)).pages:
            writer.add_page(page)
        outputs.append({"source_md": md_name, "source_sha256": sha(markdown.read_bytes()), "pdf": pdf_name,
                        "bytes": pdf.stat().st_size, "sha256": sha(pdf.read_bytes()), "pages": pages,
                        "page_text_lengths": [len(re.sub(r"TOM STREET \| Evidence-based homeowner DRAFT \| Not a legal or engineering conclusion|Page \d+", "", page.extract_text() or "").strip()) for page in PdfReader(str(pdf)).pages]})
    # Number only the combined handout so printed copies have meaningful
    # sequential pagination, without an underlying duplicate "Page 1" layer.
    packet_pages = len(writer.pages)
    for page_number, page in enumerate(writer.pages, start=1):
        buffer = BytesIO()
        canvas = pdf_canvas.Canvas(buffer, pagesize=letter)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#586971"))
        canvas.drawRightString(letter[0] - .76 * inch, .42 * inch,
                               f"Packet page {page_number} of {packet_pages}")
        canvas.save()
        buffer.seek(0)
        page.merge_page(PdfReader(buffer).pages[0])
    combined = OUT / COMBINED
    with combined.open("wb") as stream:
        writer.write(stream)
    outputs.append({"source_md": "merge of approved-scope source drafts", "pdf": COMBINED,
                    "bytes": combined.stat().st_size, "sha256": sha(combined.read_bytes()),
                    "pages": len(PdfReader(str(combined)).pages)})
    manifest = {
        "release_status": "DRAFT_NOT_APPROVED_FOR_EXTERNAL_DISTRIBUTION",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "photo_originals_included": False,
        "file_scope": "Five explicitly named public-safe Markdown drafts",
        "unresolved": ["Approved signed engineering and surveys not acquired",
                       "Current official permit/CO status not refreshed",
                       "Photo original provenance/permission not verified",
                       "Homeowner release sign-off outstanding"],
        "outputs": outputs,
    }
    (OUT / "RELEASE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUT / "SHA256SUMS.txt").write_text(
        "".join(item["sha256"] + "  " + item["pdf"] + "\n" for item in outputs), encoding="ascii")
    with zipfile.ZipFile(OUT / ZIP_NAME, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as archive:
        for output in outputs:
            archive.write(OUT / output["pdf"], arcname=output["pdf"])
        for md_name, _ in SELECTED:
            archive.write(SOURCE / md_name, arcname="editable/" + md_name)
        archive.write(OUT / "RELEASE_MANIFEST.json", arcname="RELEASE_MANIFEST.json")
        archive.write(OUT / "SHA256SUMS.txt", arcname="SHA256SUMS.txt")
    print(json.dumps({"status": manifest["release_status"], "pages": [v["pages"] for v in outputs]}, indent=2))

if __name__ == "__main__":
    main()
