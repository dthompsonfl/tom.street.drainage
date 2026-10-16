#!/usr/bin/env python3
"""Read-only regression checks for the five-question research update."""
from pathlib import Path
import csv,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def run():
    errors=[]
    def check(label,ok):
        print(('PASS ' if ok else 'FAIL ')+label)
        if not ok:errors.append(label)
    for p in sorted((ROOT/'17_CURRENT_RESEARCH/captures').glob('*/ACQUISITION_MANIFEST.json')):
        for r in json.loads(p.read_text())['sources']:
            path=r.get('local_path')
            if path:
                f=ROOT/path
                check('original bytes '+r['source_id'],f.is_file() and len(f.read_bytes())==r['bytes'] and hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'])
    old=ROOT/'17_CURRENT_RESEARCH/captures/20261016T054716Z'
    road=json.loads((old/'SRC_TOM_FID_2006.json').read_text())['features'][0]['attributes']
    check('target road range and maintainer',road['FID']==2006 and road['SEGMENTID']==2036 and road['MAINTAINER']=='County Maintained' and road['RANGELOW']<=2264<=2268<=road['RANGEHIGH'])
    check('map zeros not silently interpreted as survey',all(road[x]==0 for x in ['From_Elev','To_Elev','ROWWIDTH']))
    for name in ['README.md','00_CONTROL/JURISDICTION_AND_AUTHORITY_SCOPE_2026-10-15.md','15_RECONCILED_DRAFTS/01_HOMEOWNER_BRIEF.md','13_PUBLIC_RECORDS_REQUESTS/COUNTY_PUBLIC_WORKS_DRAINAGE_WORK_REQUEST_DRAFT.md']:
        text=(ROOT/name).read_text()
        check('current road classification '+name,'County Maintained' in text)
    f=ROOT/'17_CURRENT_RESEARCH/FIVE_QUESTION_FINDINGS_2026-10-16.md'
    check('findings document exists',f.is_file())
    if f.is_file():
        text=f.read_text()
        for value in ['NOT_OBTAINED','ASSET_RESPONSIBILITY_UNRESOLVED','2021-11-21','2025-25','2026-03','transmission','NOT a site-specific']:
            check('evidence boundary '+value,value in text)
    claims=list(csv.DictReader((ROOT/'00_CONTROL/EVIDENCE_LEDGER.csv').open()))
    check('new road claim registered',any(x['claim_id']=='CLM-024' and 'County Maintained' in x['claim'] for x in claims))
    joins=list(csv.DictReader((ROOT/'00_CONTROL/CLAIM_SOURCE_LINKS.csv').open()))
    check('road has two direct agency-source joins',len([x for x in joins if x['claim_id']=='CLM-024'])==2)
    check('no request marked sent',all(r['submitted']=='FALSE' for r in csv.DictReader((ROOT/'00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv').open())))
    print('QUESTION FINDINGS:',len(errors),'failures')
    return errors
if __name__=='__main__':raise SystemExit(bool(run()))
