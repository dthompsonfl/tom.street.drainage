#!/usr/bin/env python3
"""Release safety controller: do not recreate withdrawn 2026-10-15 packet.

This work requires independently approved/public-safe exhibits and signer
release authorization. `python build_release.py` verifies readiness and
blocks publication; --skip-tests intentionally cannot bypass this gate.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path
from paths import ROOT

def main():
    if '--skip-tests' in sys.argv or '--force' in sys.argv:
        print('BLOCKED: safety checks cannot be bypassed to publish public material')
        return 2
    result=subprocess.run([sys.executable,str(ROOT/'00_CONTROL/tools/strict_release_gate.py')],cwd=ROOT)
    if result.returncode:
        print('BLOCKED: evidence control gate failed; no archive was generated')
        return result.returncode
    print('DRAFT QUALITY CHECK PASS; FINAL RELEASE STILL BLOCKED')
    print('Required: documented privacy review, approval of all exhibits, fact-checked PDF regeneration, signed release decision and proof of county-held source records when relevant.')
    print('Work from 15_RECONCILED_DRAFTS. Legacy packet under releases/2026-10-15 is WITHDRAWN.')
    return 3
if __name__=='__main__':raise SystemExit(main())
