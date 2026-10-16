#!/usr/bin/env python3
"""Redact account identity from portal screenshots, producing a DERIVATIVE for
public release while the unredacted original stays in the restricted vault.

The redaction is a solid opaque box over the account region of the MGO header,
not a soft blur, so no pixels of the identifying text survive.

Run:  python3 00_CONTROL/tools/redact_captures.py
"""
import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT, rel, sha256_file  # noqa: E402

from PIL import Image, ImageDraw
from pathlib import Path

# Region of the MGO header carrying the account display name and e-mail.
# Measured from the captured screenshots (1700px viewport).
HEADER_BOX = (1160, 20, 1700, 100)
BANNER = "#1b2f4e"


def redact(src: Path, dst: Path, label: str = "[account identity redacted]") -> dict:
    img = Image.open(src).convert("RGB")
    w, h = img.size
    box = (int(HEADER_BOX[0] * w / 1700), int(HEADER_BOX[1] * h / 1180),
           int(HEADER_BOX[2] * w / 1700), int(HEADER_BOX[3] * h / 1180))
    d = ImageDraw.Draw(img)
    d.rectangle(box, fill=BANNER)
    d.text((box[0] + 12, box[1] + 26), label, fill="#d8dee9")
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, "PNG", optimize=True)
    return {"source": rel(src), "derivative": rel(dst),
            "source_sha256": sha256_file(src),
            "derivative_sha256": sha256_file(dst),
            "derivative_bytes": dst.stat().st_size}


if __name__ == "__main__":
    from PIL import ImageFont
    out = []
    for src in sorted((_ROOT / ".evidence_vault" / "restricted").rglob("*.png")):
        rel_p = src.relative_to(_ROOT / ".evidence_vault" / "restricted")
        dst = _ROOT / "14_MEETING_PACKET" / "exhibits" / "derived_redacted" / rel_p
        out.append(redact(src, dst))
        print("redacted:", out[-1]["source"], "->", out[-1]["derivative"])
    # also redact any still-tracked png in the working tree
    for src in sorted(_ROOT.rglob("*.png")):
        if ".evidence_vault" in rel(src) or "14_MEETING_PACKET" in rel(src):
            continue
        if not src.exists():
            continue
        dst = _ROOT / "14_MEETING_PACKET" / "exhibits" / "derived_redacted" / \
            src.relative_to(_ROOT)
        out.append(redact(src, dst))
        print("redacted:", out[-1]["source"], "->", out[-1]["derivative"])
    import json
    (_ROOT / "14_MEETING_PACKET" / "exhibits" /
     "derived_redacted" / "REDACTION_INDEX.json").write_text(
        json.dumps(out, indent=1))
    print("wrote redaction index")