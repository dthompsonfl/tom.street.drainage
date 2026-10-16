#!/usr/bin/env python3
"""Check the public blank neighbor toolkit and printable derivatives.

This is a mechanical layout/source/privacy gate, not authorization to share
completed household records or a determination about drainage conditions.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
TOOLKIT = ROOT / '18_NEIGHBOR_TOOLKIT'
PRINT = TOOLKIT / 'print'

MASTER = 'Tom_Street_Neighbor_Documentation_Forms.pdf'
SINGLES = {
    '03_Event_Observation.pdf': 3,
    '04_Photo_and_Video_Index.pdf': 4,
    '10_Request_and_Response.pdf': 10,
    '11_Meeting_and_Inspection_Notes.pdf': 11,
    '13_Documented_Roles.pdf': 13,
    '14_Original_Files_and_Handoff.pdf': 14,
    '16_Missing_Records_Checklist.pdf': 16,
    '18_Continuation_Page.pdf': 18,
}
REQUIRED_GUIDES = {
    'README.md', '01_DOCUMENT_AN_OBSERVATION.md', '02_REQUESTS_AND_RESPONSES.md',
    '03_MEETING_GUIDE.md', '04_PRIVACY_AND_SHARING.md',
    '05_ORIGINALS_AND_IDS.md', '06_DOCUMENTED_ROLES.md',
    '07_SOURCE_AND_MEASUREMENT_GUIDE.md', '08_COORDINATOR_CHECKLIST.md',
    '09_WHERE_TO_REQUEST_AND_REPORT.md',
    'print/README.md', 'templates/README.md',
}
REQUIRED_TEMPLATES = {
    'OBSERVATION_LOG.csv', 'REQUEST_TRACKER.csv', 'PHOTO_VIDEO_INDEX.csv',
    'SOURCE_DOCUMENT_LOG.csv', 'DOCUMENTED_ROLE_TRACKER.csv',
    'DRAINAGE_FEATURE_LOG.csv', 'WORK_AND_CONDITION_LOG.csv',
    'ORIGINAL_FILE_AND_TRANSFER_LOG.csv', 'WEATHER_AND_COMPARISON_LOG.csv',
    'PROPERTY_CONDITION_AND_EXPENSE_LOG.csv',
}
errors = []


def check(name, valid):
    print(('PASS ' if valid else 'FAIL ') + name)
    if not valid:
        errors.append(name)


def text(value):
    return value.read_text(encoding='utf-8')


for name in sorted(REQUIRED_GUIDES):
    check('guide exists: ' + name, (TOOLKIT/name).is_file())
for name in sorted(REQUIRED_TEMPLATES):
    path = TOOLKIT/'templates'/name
    check('blank CSV: ' + name,
          path.is_file() and len(text(path).splitlines()) == 1 and
          len(next(csv.reader(text(path).splitlines()))) >= 7)
for name in ('MEETING_NOTES.md', 'CHANGE_AND_CORRECTION.md'):
    check('editable text template: ' + name, (TOOLKIT/'templates'/name).is_file())

# Restrict binary material to exact generated PDF names. Never accept resident
# originals, photographs, completed CSV logs or arbitrary source archives.
allowed_pdf_paths = {'print/'+MASTER} | {'print/'+x for x in SINGLES}
for path in sorted(TOOLKIT.rglob('*')):
    if not path.is_file():
        continue
    relative = path.relative_to(TOOLKIT).as_posix()
    check('allowed toolkit file: '+relative,
          path.suffix in ('.md', '.csv') or relative in allowed_pdf_paths)

if (PRINT/MASTER).is_file():
    master = PdfReader(str(PRINT/MASTER))
    check('full packet has 18 pages', len(master.pages) == 18)
    for i, page in enumerate(master.pages, 1):
        box = page.mediabox
        check(f'US Letter page {i:02}', abs(float(box.width)-612)<0.1 and abs(float(box.height)-792)<0.1)
        content = page.extract_text() or ''
        check(f'extractable content page {i:02}', len(content)>220 and 'TOM STREET' in content)
        check(f'blank master footer page {i:02}', 'BLANK MASTER' in content)
    for name, number in SINGLES.items():
        pdfpath = PRINT/name
        if not pdfpath.is_file():
            check('standalone present: '+name, False)
            continue
        parsed = PdfReader(str(pdfpath))
        check('standalone one page: '+name, len(parsed.pages)==1)
        if parsed.pages:
            from_master = master.pages[number-1].extract_text() or ''
            as_single = parsed.pages[0].extract_text() or ''
            check('standalone matches master: '+name, from_master==as_single)
else:
    check('full packet exists', False)

# All locally referenced file targets must exist in a full checkout.
for p in sorted(TOOLKIT.rglob('*.md')):
    value = text(p)
    for target in re.findall(r'(?<!!)(?:\[[^\]]*\])\(([^)]+)\)', value):
        if target.startswith(('https://', 'http://', 'mailto:', '#')):
            continue
        dest = target.split('#', 1)[0].split('?', 1)[0]
        resolved = (p.parent / dest).resolve()
        # In a partial patch test, parent repo references are not available.
        if '--partial' in sys.argv and not resolved.is_relative_to(TOOLKIT.resolve()):
            continue
        check('link: '+p.relative_to(TOOLKIT).as_posix()+' -> '+dest,
              resolved.is_relative_to(ROOT.resolve()) and resolved.exists())

# High-level invariants: every core activity has a printable action path.
index = text(TOOLKIT/'README.md')
for name in (MASTER,*SINGLES):
    check('index points to PDF: '+name, name in index)
check('private handling explicit', 'private' in index.lower() and 'public' in index.lower())
check('roles require dated sources', 'dated source' in index.lower())
check('primary form available', '03_Event_Observation.pdf' in index)

print('NEIGHBOR TOOLKIT: '+str(len(errors))+' failure(s)')
raise SystemExit(bool(errors))
