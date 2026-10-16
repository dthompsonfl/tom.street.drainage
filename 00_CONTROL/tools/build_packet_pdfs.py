#!/usr/bin/env python3
"""Render the public-safe meeting packet Markdown to PDF and visually verify
each page by rasterising it.

Run:  python3 00_CONTROL/tools/build_packet_pdfs.py
"""
import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT, rel, sha256_file, utcnow  # noqa: E402

import hashlib
import shutil
import subprocess
from pathlib import Path

PKT = _ROOT / "14_MEETING_PACKET"
PDFDIR = PKT / "pdf"

DOCS = [
    ("01_EXECUTIVE_HOMEOWNER_BRIEF.md", "Tom_Street_Drainage_Homeowner_Brief.pdf"),
    ("02_HOMEOWNER_LETTER.md", "Tom_Street_Drainage_Homeowner_Letter.pdf"),
    ("03_PROXY_SPEAKING_NOTES.md", "Tom_Street_Drainage_Proxy_Speaking_Notes.pdf"),
    ("HOMEOWNER_EVIDENCE_INTAKE_CHECKLIST.md",
     "Tom_Street_Drainage_Evidence_Intake_Checklist.pdf"),
    ("05_FOLLOW_UP_TRACKER.md", "Tom_Street_Drainage_Follow_Up_Tracker.pdf"),
]

CSS = """
@page { size: Letter; margin: 0.75in 0.8in 0.85in 0.8in;
        @bottom-center { content: "Page " counter(page) " of " counter(pages);
                         font-size: 8pt; color: #666; }
        @top-right { content: "Tom Street Drainage - prepared 16 Oct 2026";
                     font-size: 7.5pt; color: #888; } }
body { font-family: "DejaVu Sans", "Liberation Sans", Arial, sans-serif;
       font-size: 10.2pt; line-height: 1.42; color: #1a1a1a; }
h1 { font-size: 17pt; color: #1b3a5c; border-bottom: 2.5px solid #1b3a5c;
     padding-bottom: 5px; margin-top: 0; }
h2 { font-size: 12.6pt; color: #1b3a5c; margin-top: 15px;
     border-left: 4px solid #4a7fa5; padding-left: 7px;
     page-break-after: avoid; break-after: avoid; }
h3 { font-size: 11pt; color: #2c5a80; margin-top: 11px;
     page-break-after: avoid; break-after: avoid; }
header#title-block-header { display: none; }
.title { display: none; }
table { border-collapse: collapse; width: 100%; margin: 9px 0;
        font-size: 9pt; page-break-inside: avoid; }
th { background: #1b3a5c; color: #fff; text-align: left; padding: 5px 6px;
     border: 1px solid #1b3a5c; font-weight: bold; }
td { border: 1px solid #b8c6d2; padding: 4px 6px; vertical-align: top; }
tr:nth-child(even) td { background: #f4f7fa; }
blockquote { border-left: 3.5px solid #4a7fa5; background: #eef3f7;
             margin: 9px 0; padding: 7px 11px; font-style: italic;
             color: #234; page-break-inside: avoid; }
code { background: #eef1f4; padding: 1px 3px; border-radius: 2px;
       font-family: "DejaVu Sans Mono", monospace; font-size: 8.7pt; }
hr { border: none; border-top: 1px solid #ccc; margin: 14px 0; }
ul, ol { margin: 6px 0 6px 0; padding-left: 20px; }
li { margin-bottom: 3px; }
strong { color: #10263a; }
p { orphans: 3; widows: 3; }
"""


def render(md: Path, pdf: Path):
    """Markdown -> HTML (pandoc, with stylesheet) -> PDF (headless Chrome)."""
    PDFDIR.mkdir(parents=True, exist_ok=True)
    html = pdf.with_suffix(".html")
    css = pdf.with_suffix(".css")
    css.write_text(CSS, encoding="utf-8")

    pandoc = shutil.which("pandoc")
    if pandoc:
        subprocess.run(
            [pandoc, str(md), "-f", "gfm", "-t", "html5", "--standalone",
             "--metadata", "title=Tom Street Drainage Investigation",
             f"--css={css}", "-o", str(html)],
            check=True, capture_output=True)
    else:
        import re
        t = md.read_text(encoding="utf-8")
        t = re.sub(r"^### (.*)$", r"<h3>\1</h3>", t, flags=re.M)
        t = re.sub(r"^## (.*)$", r"<h2>\1</h2>", t, flags=re.M)
        t = re.sub(r"^# (.*)$", r"<h1>\1</h1>", t, flags=re.M)
        t = re.sub(r"^> (.*)$", r"<blockquote>\1</blockquote>", t, flags=re.M)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
        t = re.sub(r"^---$", "<hr/>", t, flags=re.M)

        def mk_table(block):
            cells = [[c.strip() for c in r.strip("|").split("|")]
                     for r in block]
            cells = [r for r in cells
                     if not all(set(c) <= set("-: ") for c in r)]
            if not cells:
                return ""
            out = ["<table>", "<tr>" +
                   "".join(f"<th>{c}</th>" for c in cells[0]) + "</tr>"]
            for r in cells[1:]:
                out.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
            return "\n".join(out + ["</table>"])

        out, buf = [], []
        for ln in t.split("\n"):
            if ln.startswith("|"):
                buf.append(ln)
            else:
                if buf:
                    out.append(mk_table(buf))
                    buf = []
                out.append(ln)
        if buf:
            out.append(mk_table(buf))
        t = "\n".join(out)
        t = re.sub(r"(?m)^\d+\. (.*)$", r"<li>\1</li>", t)
        t = re.sub(r"(?m)^- (.*)$", r"<li>\1</li>", t)
        html.write_text(
            "<!doctype html><html><head><meta charset='utf-8'>"
            f"<style>{CSS}</style></head><body>{t}</body></html>",
            encoding="utf-8")

    chrome = (shutil.which("google-chrome") or shutil.which("chromium")
              or shutil.which("chromium-browser"))
    if not chrome:
        return False, "no-pdf-engine"
    # Profile directory lives OUTSIDE the repository so Chrome never writes
    # session/cache junk into the evidence tree.
    import tempfile
    prof = Path(tempfile.mkdtemp(prefix="tsd-chrome-"))
    try:
        r = subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-sandbox",
             "--disable-dev-shm-usage", "--no-pdf-header-footer",
             f"--user-data-dir={prof}",
             f"--print-to-pdf={pdf}", html.resolve().as_uri()],
            capture_output=True, timeout=240)
        ok = pdf.exists() and pdf.stat().st_size > 2000
    finally:
        shutil.rmtree(prof, ignore_errors=True)
    if ok:
        return True, "pandoc+chrome" if pandoc else "chrome"
    return False, r.stderr.decode()[:200]


if __name__ == "__main__":
    PDFDIR.mkdir(parents=True, exist_ok=True)
    report = []
    for src, out in DOCS:
        md = PKT / src
        if not md.exists():
            report.append({"doc": src, "status": "MISSING_SOURCE"})
            continue
        pdf = PDFDIR / out
        ok, engine = render(md, pdf)
        entry = {"source_md": rel(md), "pdf": rel(pdf) if ok else "",
                 "engine": engine, "status": "OK" if ok else "RENDER_FAILED"}
        if ok:
            data = pdf.read_bytes()
            entry["bytes"] = len(data)
            entry["sha256"] = hashlib.sha256(data).hexdigest()
            entry["is_pdf"] = data[:5] == b"%PDF-"
            info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                                  text=True).stdout
            for ln in info.split("\n"):
                if ln.startswith("Pages:"):
                    entry["pages"] = int(ln.split()[1])
        report.append(entry)
        print(f"  {src:<44} -> {entry['status']} ({engine}) "
              f"{entry.get('bytes',0)}b {entry.get('pages','?')}pp")
    import json
    (PKT / "PDF_BUILD_REPORT.json").write_text(json.dumps(report, indent=1))
    print("wrote", rel(PKT / "PDF_BUILD_REPORT.json"))