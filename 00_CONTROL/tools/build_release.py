#!/usr/bin/env python3
"""Single validate -> test -> package entry point for the Tom Street Drainage
Investigation.

Builds `releases/<version>/` containing ONLY privacy-reviewed public material,
plus a SHA256SUMS file and a manifest. Restricted evidence stays in the local
vault and is never packaged.

Run:  python3 00_CONTROL/tools/build_release.py [--skip-tests]
"""
import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT, rel, sha256_file, utcnow  # noqa: E402

import hashlib
import json
import subprocess
import zipfile
from datetime import date
from pathlib import Path

VERSION = date.today().isoformat()
RELDIR = _ROOT / "releases" / VERSION
ZIPNAME = f"Tom_Street_Public_Meeting_Packet_{VERSION}.zip"

# Public-safe material only. Nothing here may contain authenticated portal
# state, account identity, or private homeowner media.
PUBLIC_ITEMS = [
    "14_MEETING_PACKET/01_EXECUTIVE_HOMEOWNER_BRIEF.md",
    "14_MEETING_PACKET/02_HOMEOWNER_LETTER.md",
    "14_MEETING_PACKET/03_PROXY_SPEAKING_NOTES.md",
    "14_MEETING_PACKET/05_FOLLOW_UP_TRACKER.md",
    "14_MEETING_PACKET/HOMEOWNER_EVIDENCE_INTAKE_CHECKLIST.md",
    "14_MEETING_PACKET/pdf/Tom_Street_Drainage_Homeowner_Brief.pdf",
    "14_MEETING_PACKET/pdf/Tom_Street_Drainage_Homeowner_Letter.pdf",
    "14_MEETING_PACKET/pdf/Tom_Street_Drainage_Proxy_Speaking_Notes.pdf",
    "14_MEETING_PACKET/pdf/Tom_Street_Drainage_Follow_Up_Tracker.pdf",
    "14_MEETING_PACKET/pdf/Tom_Street_Drainage_Evidence_Intake_Checklist.pdf",
    "14_MEETING_PACKET/exhibits/derived_redacted/03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_project.png",
    "14_MEETING_PACKET/RELEASE_README.md",
    "README.md",
    "00_CONTROL/EVIDENCE_LEDGER.csv",
    "00_CONTROL/EXHIBIT_INDEX.csv",
    "00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv",
    "00_CONTROL/CHRONOLOGY.csv",
    "00_CONTROL/DESIGN_VS_FIELD_MATRIX.csv",
    "00_CONTROL/CONTRADICTION_LOG.csv",
    "00_CONTROL/RESPONSIBILITY_MATRIX.csv",
    "00_CONTROL/REGULATORY_AND_CASELAW_MATRIX.md",
    "00_CONTROL/ACQUISITION_RESULTS.md",
]

# Never packaged, under any circumstance.
FORBIDDEN = (".evidence_vault", ".git", "__pycache__",
             "mgo_auth.json", "acclaim_state.json", "SYSTEM_RAW")


def run(cmd):
    print(f"\n$ {' '.join(str(c) for c in cmd)}")
    r = subprocess.run([str(c) for c in cmd], cwd=str(_ROOT),
                       capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    print("\n".join(out.strip().splitlines()[-12:]))
    return r.returncode


def main(skip_tests=False):
    steps = []
    rc = run([_sys.executable, "00_CONTROL/tools/validate_evidence.py"])
    steps.append(("validate_evidence", rc))
    rc = run([_sys.executable, "00_CONTROL/tools/classify_for_release.py",
              "--write"])
    steps.append(("classify_for_release", rc))
    if not skip_tests:
        rc = run([_sys.executable, "00_CONTROL/tools/test_evidence.py"])
        steps.append(("test_evidence", rc))
        if rc != 0:
            print("\nBUILD HALTED: tests failed; nothing packaged.")
            return rc
    else:
        steps.append(("test_evidence", "SKIPPED (--skip-tests)"))
        print("\nWARNING: tests skipped - release NOT verified.")

    RELDIR.mkdir(parents=True, exist_ok=True)
    missing = [i for i in PUBLIC_ITEMS if not (_ROOT / i).exists()]
    if missing:
        print("MISSING PUBLIC ITEMS:")
        for m in missing:
            print("   ", m)
        return 2

    zp = RELDIR / ZIPNAME
    sums = []
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for item in PUBLIC_ITEMS:
            if any(f in item for f in FORBIDDEN):
                print("REFUSING to package forbidden path:", item)
                return 3
            data = (_ROOT / item).read_bytes()
            z.writestr(item, data)
            sums.append(f"{hashlib.sha256(data).hexdigest()}  {item}")
    (RELDIR / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n")

    manifest = {
        "version": VERSION,
        "built_utc": utcnow(),
        "zip": rel(zp),
        "zip_bytes": zp.stat().st_size,
        "zip_sha256": sha256_file(zp),
        "members": len(PUBLIC_ITEMS),
        "privacy_review": "PUBLIC-SAFE. No authenticated portal captures, no "
                          "account identity, no private homeowner media, no "
                          "session material. Screenshots are redacted "
                          "derivatives and labelled as such.",
        "excluded": list(FORBIDDEN),
        "restricted_evidence_location": ".evidence_vault/ (local only, not packaged)",
        "validation_steps": [{"step": s, "rc": str(rc_)} for s, rc_ in steps],
    }
    (RELDIR / "RELEASE_MANIFEST.json").write_text(json.dumps(manifest, indent=1))

    print("\n" + "=" * 66)
    print(f"RELEASE {VERSION}")
    print(f"  ZIP      {rel(zp)}")
    print(f"  bytes    {zp.stat().st_size}")
    print(f"  sha256   {manifest['zip_sha256']}")
    print(f"  members  {len(PUBLIC_ITEMS)}")
    print(f"  sums     {rel(RELDIR / 'SHA256SUMS.txt')}")
    print(f"  manifest {rel(RELDIR / 'RELEASE_MANIFEST.json')}")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    _sys.exit(main(skip_tests="--skip-tests" in _sys.argv))