#!/usr/bin/env python3
"""One reviewed research reconciliation; no network or original-evidence edits.

Imports a single independently inspected artifact by its exact SHA-256. Existing
original bytes may not be replaced. Text edits have explicit old/new anchors and
are idempotent; register additions reject duplicate IDs with differing content.
"""
from __future__ import annotations
import csv,hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CAPTURE='20261016T060511Z'
ARTIFACT_SHA='3b5e8d665e6eb05855bd572a13525ea3d7776c9b0e6a2222682f9a85819b93fc'
OLD='17_CURRENT_RESEARCH/captures/20261016T054716Z/'
NEW='17_CURRENT_RESEARCH/captures/'+CAPTURE+'/'
REPORT='17_CURRENT_RESEARCH/FIVE_QUESTION_FINDINGS_2026-10-16.md'
CHANGED=set()

def write(path,data):
    p=ROOT/path
    if p.is_file() and p.read_bytes()==data:return
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);CHANGED.add(path)

def replace(path,old,new):
    p=ROOT/path;t=p.read_text()
    if new in t:return
    if t.count(old)!=1:raise ValueError('Review changed anchor: '+path+' '+old[:70])
    write(path,t.replace(old,new).encode())

def append(path,heading,body):
    p=ROOT/path;t=p.read_text();block='\n\n'+heading+'\n\n'+body+'\n'
    if heading in t:
        if block not in t:raise ValueError('Existing reconciliation differs: '+path)
        return
    write(path,(t.rstrip()+block).encode())

def readcsv(path):
    with (ROOT/path).open(newline='') as f:
        reader=csv.DictReader(f);return reader.fieldnames,list(reader)

def savecsv(path,fields,rows):
    import io
    stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=fields);w.writeheader();w.writerows(rows)
    write(path,stream.getvalue().encode())

def addcsv(path,key,records):
    fields,rows=readcsv(path);existing={r[key]:r for r in rows}
    for row in records:
        row={f:str(row.get(f,'')) for f in fields}
        if row[key] in existing:
            if existing[row[key]]!=row:raise ValueError('Conflicting registry ID '+path+' '+row[key])
        else:rows.append(row);existing[row[key]]=row
    savecsv(path,fields,rows)

def import_reviewed(artifact):
    if hashlib.sha256(artifact.read_bytes()).hexdigest()!=ARTIFACT_SHA:raise ValueError('Unreviewed artifact')
    pending={}
    with zipfile.ZipFile(artifact) as z:
        prefix='captures/'+CAPTURE+'/'
        raw=z.read(prefix+'ACQUISITION_MANIFEST.json');m=json.loads(raw)
        if len(m['sources'])!=22:raise ValueError('Unexpected acquisition inventory')
        pending[NEW+'ACQUISITION_MANIFEST.json']=raw
        for row in m['sources']:
            rel=row.get('local_path')
            if not rel:continue
            path=Path(rel)
            if path.parent.as_posix()!=NEW.rstrip('/') or path.name!=row['source_id']+path.suffix:raise ValueError('Unexpected capture path')
            data=z.read(prefix+path.name)
            if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('Capture integrity mismatch')
            pending[rel]=data
    if len(pending)!=22:raise ValueError('Expected 21 responses and one manifest')
    for rel,data in pending.items():
        p=ROOT/rel
        if p.exists() and p.read_bytes()!=data:raise FileExistsError('Original evidence conflict '+rel)
    for rel,data in pending.items():write(rel,data)

def documents():
    replace('README.md','Research status (October 15, 2026 local)','Research status (updated October 16, 2026 UTC)')
    replace('00_CONTROL/JURISDICTION_AND_AUTHORITY_SCOPE_2026-10-15.md','**Reviewed:** October 15, 2026 (U.S. Central).','**Updated:** October 16, 2026 UTC; original review October 15 local.')
    replace('README.md','**Do not assume Tom Street is county-maintained** without the Street-Maintainer lookup and easement/acceptance documents.',
      '**County GIS now identifies the relevant Tom Street segment as County Maintained** (FID 2006 / segment 2036, range 2100-2299). Individual drainage-asset ownership, acceptance and easements remain unresolved. See the [five-question findings](17_CURRENT_RESEARCH/FIVE_QUESTION_FINDINGS_2026-10-16.md).')
    replace('00_CONTROL/JURISDICTION_AND_AUTHORITY_SCOPE_2026-10-15.md',"**Tom Street's maintainer, ownership, easements and acceptance status are NOT verified.**",
      '**County GIS verifies County Maintained for the target road segment (FID 2006 / segment 2036). Road title, easements and acceptance/maintenance of individual drainage structures are NOT verified.**')
    replace('00_CONTROL/JURISDICTION_AND_AUTHORITY_SCOPE_2026-10-15.md','**Tom Street street-maintainer and public/private right-of-way determination**',
      '**Tom Street right-of-way title and asset acceptance (GIS street-maintainer classification is now County Maintained)**')
    replace('00_CONTROL/REGULATORY_AND_CASELAW_MATRIX.md','**Tom Street maintainer and roadside asset acceptance are unresolved**',
      '**Tom Street road GIS classification is now County Maintained; roadside asset ownership/acceptance remain unresolved**')
    law='00_CONTROL/REGULATORY_AND_CASELAW_MATRIX.md'
    start='- **Why it matters:** sub-paragraph (g) explains, in the county\'s own words, why'
    end='### B4 '
    t=(ROOT/law).read_text()
    if start in t:
        a=t.index(start);b=t.index(end,a)
        revised='- **Workflow limitation:** the code describes a completion-stage certification, but the saved MGO task labels do not prove which legal pathway the County applied or whether a document exists.\n- **Applicability unresolved:** verify lot dimensions, on-file subdivision plan status, the actual approved plan or ERP-letter alternative, and any D.4 exemption. Whether a subdivision plan is on file does not itself choose between the two alternatives. Secondary lot-size estimates are not a certified survey.\n- **No breach determination:** Active is the archived permit status, not a new live check. An assigned task alone proves neither compliance nor noncompliance.\n\n'
        write(law,(t[:a]+revised+t[b:]).encode())
    replace(law,'**"All lots will require a certified as-built prior to issuance of the Certificate of Occupancy."**',
      'a requirement for a certified as-built before issuance of the Certificate of Occupancy (the printed source uses the spelling **as-build**)')
    replace(law,'*Printed pages 249\u2013250 = PDF pages 267\u2013268.*','*General provisions: printed 249-250 / PDF 267-268; D.1 continues on printed 251 / PDF 269.*')
    replace(law,'**Status: NOT_APPLICABLE on current evidence** \u2014 the D.2 band applies to lots\n  of one acre or more.',
      '**Status: LOT-SPECIFIC APPLICABILITY UNRESOLVED**. The D.2 band applies to lots of one acre or more; confirm actual lot dimensions rather than treat secondary size estimates as an official survey.')
    replace(law,'| LDC \u00a7 4.04.01.D.2.b drainage easement | yes, primary PDF | not applicable on current evidence | \u2014 |',
      '| LDC section 4.04.01.D.2.b drainage easement | yes, primary PDF | lot-specific applicability unresolved | certified dimensions and County approval pathway |')
    update='**October 16 follow-up:** the target road is **County Maintained** in County GIS; asset ownership/maintenance remains unresolved. Actual Ordinances 2025-25 and 2026-03 and the generic grading guideline are now preserved. Clerk-certified electronic transmission dates are not separate Department of State filing receipts. No lot-specific approved plan, exemption, surveyed invert/outfall, or matched ERP/CGP authorization was obtained. See ['+REPORT+'](../'+REPORT+') and its source links.'
    for p in ['00_CONTROL/JURISDICTION_AND_AUTHORITY_SCOPE_2026-10-15.md',law,'00_CONTROL/OPEN_QUESTIONS.md','00_CONTROL/NEXT_ACTIONS.md','00_CONTROL/MAIN_BRANCH_REMEDIATION_STATUS.md','00_CONTROL/ACTIVE_ASSERTION_CONSISTENCY_2026-10-15.md','00_CONTROL/READING_ORDER_AND_SNAPSHOT_STATUS.md']:
        append(p,'## October 16: verified road classification and remaining questions',update)
    pub='13_PUBLIC_RECORDS_REQUESTS/COUNTY_PUBLIC_WORKS_DRAINAGE_WORK_REQUEST_DRAFT.md'
    t=(ROOT/pub).read_text();a=t.index('**County-maintenance boundary:**') if '**County-maintenance boundary:**' in t else t.index('**County-maintenance evidence:**');b=t.index('\n\n',a)
    new='**County-maintenance evidence:** the official County street layer identifies TOM ST, FID 2006 / segment 2036, address range 2100-2299, as **County Maintained**. County GoMaps corroborates that classification. Please identify which culverts, inlets and ditches are accepted County assets and which are private, including the supporting acceptance/easement records. A road-maintainer classification is not proof of asset ownership or a legal maintenance obligation for every adjacent facility.'
    if t[a:b]!=new:write(pub,(t[:a]+new+t[b:]).encode())
    replace(pub,'subject to official street-maintainer lookup','based on the verified County GIS road classification')
    brief='15_RECONCILED_DRAFTS/01_HOMEOWNER_BRIEF.md'
    replace(brief,'**October 15, 2026**','**Updated October 16, 2026**')
    replace(brief,'## Documents needed',
      'County GIS identifies this Tom Street segment as **County Maintained**. Ownership and maintenance of each drainage structure remain unverified.\n\n## Documents needed')
    replace(brief,'A separately preserved homeowner package has **15 internally hash-matched JPEG copies**, but native originals, capture times, exact parcel locations and release permissions are not verified. They remain private.',
      'The 15 hash-matched homeowner photo copies remain private; original capture data, parcel attribution and publication permission are unverified.')
    replace(brief,'*Sources: saved Property Appraiser and MGO records.', '*Sources: saved Property Appraiser, MGO and October 16 County GIS records.')
    letter='15_RECONCILED_DRAFTS/02_COUNTY_LETTER_DRAFT.md'
    replace(letter,'We also request a **documented County Engineering inspection** of the shared roadside drainage, a written finding on actual outfalls and potential effects on established homes, and verification of Tom Street\'s road-maintainer and drainage-asset responsibilities.',
      'County GIS lists Tom Street as **County Maintained**. We request a **documented Engineering inspection**, written findings on outfalls and neighboring effects, and identification of each drainage asset\'s owner/maintainer.')
    proxy='15_RECONCILED_DRAFTS/03_PROXY_MEETING_NOTES.md'
    replace(proxy,'3. What are the roadside/driveway pipe and inlet invert elevations and outfalls? Who maintains Tom Street\'s road and drainage structures?',
      '3. County GIS lists Tom Street as County Maintained. Which drainage structures does the County maintain, and where are the surveyed inverts and outfalls?')
    commissioner='15_RECONCILED_DRAFTS/06_COMMISSIONER_COVER_LETTER_DRAFT.md'
    replace(commissioner,'verified road-maintainer and drainage-asset responsibilities',
      'asset-specific responsibilities along the GIS-listed County Maintained road')
    follow='15_RECONCILED_DRAFTS/05_RECORDS_STATUS_AND_FOLLOW_UP.md'
    replace(follow,'**Date:** October 15, 2026.','**Updated:** October 16, 2026.')
    replace(follow,'## Three essential requests for County Engineering',
      '**New evidence:** County GIS classifies the target Tom Street road segment as County Maintained. Individual drainage-asset ownership and maintenance still require records.\n\n## Three essential requests for County Engineering')
    for p in ['13_PUBLIC_RECORDS_REQUESTS/SHARED_TOM_STREET_ROW_AND_DRAINAGE_PLANS.md','13_PUBLIC_RECORDS_REQUESTS/NWFWMD_ERP_9220-2_FILE.md']:
        append(p,'## October 16 research update (request remains unsubmitted)',update)
    replace('00_CONTROL/tools/validate_evidence.py','    "11_HYDROLOGY_AND_HAZARD/",','    "11_HYDROLOGY_AND_HAZARD/",\n    "17_CURRENT_RESEARCH/captures/",')

def registers():
    sources=[]
    for batch in [OLD,NEW]:
        manifest=json.loads((ROOT/batch/'ACQUISITION_MANIFEST.json').read_text())
        for r in manifest['sources']:
            rel=r.get('local_path')
            if not rel:continue
            agency='Santa Rosa County'
            if r['source_id'].startswith(('NWFWMD','DEP','FBC','ORD')):
                agency={'NWFWMD':'Northwest Florida Water Management District','DEP':'Florida DEP','FBC':'Florida Building Commission','ORD':'Santa Rosa County enacted ordinance'}[r['source_id'].split('_')[0]]
            status='PRESERVED_PRIMARY_CAPTURE_NOT_SITE_COMPLIANCE'
            if r['source_id']=='FBC_CURRENT_EDITION':status='PRESERVED_REDIRECT_ONLY_NOT_SUBSTANTIVE_CODE_TEXT'
            sources.append(dict(source_id='SRC-Q-'+r['source_id'],document_title=r['source_id'],issuing_agency=agency,record_system='Official public source; see URL',source_identifier=r['source_id'],retrieval_date_utc=r['retrieved_utc'],original_url=r['requested_url'],local_relative_path=rel,file_type=Path(rel).suffix.lstrip('.'),file_size_bytes=r['bytes'],sha256_hash=r['sha256'],status=status,verification_method='Exact artifact and per-file SHA-256; JSON parsed or PDF rendered; contextual HTML only',notes='See five-question findings. Empty result is not absence proof. GIS points are not permit boundaries; road classification is not asset title.'))
    addcsv('00_CONTROL/SOURCE_REGISTER.csv','source_id',sources)
    records=[
      ('CLM-024','EX-23',OLD+'SRC_TOM_FID_2006.json','County GIS identifies the target TOM ST segment as County Maintained: FID 2006, segment 2036, range 2100-2299. County GoMaps corroborates the same road classification.','features[0].attributes; FID 2006; segment 2036','Road classification only; not right-of-way title, asset acceptance, surveyed elevations or ownership of every inlet/culvert.'),
      ('CLM-025','EX-24',NEW+'ORD_2025_25.pdf','Enacted Ordinance 2025-25 records adoption November 10 2025 and Clerk-certified electronic transmission November 14 2025; effectiveness is on Department of State filing.','PDF pages 1-2; Exhibit A drainage changes pages 4-5','Transmission certificate is not a separate Department of State receipt. No lot-specific exemption or actual plan approval is established.'),
      ('CLM-026','EX-25',NEW+'ORD_2026_03.pdf','Enacted Ordinance 2026-03 concerns the East Milton Wellfield Protection Overlay; adoption January 22 2026 and Clerk-certified transmission January 27 2026 appear in the instrument.','PDF pages 1-4; signed page 2; map page 4','No verified Tom Street grading exemption or site-specific permit applicability follows from this map.'),
      ('CLM-027','EX-26',NEW+'SRC_GIS_PROBLEM_AREA_79.json','The bounded Tom Street vicinity query returned County stormwater problem-area feature OBJECTID 2068, sourced to Road & Bridge Maps Marked Up by Foreman.','features[0].attributes.OBJECTID and DataSource','No date, severity, causation or current flooding condition is established; may be a lead to pre-existing drainage limitations.'),
      ('CLM-028','EX-27',NEW+'SRC_TYPICAL_GRADING.pdf','The County publishes a one-page Typical Yard Grading Guidelines sheet, not to scale; it is generic guidance, not a site-approved drawing for either Tom Street lot.','PDF page 1','Typical dimensions are not measured elevations or approved site-specific values. Verify applicable plan and code edition.')]
    claims=[];exhibits=[];joins=[]
    for cid,eid,rel,claim,loc,limit in records:
        b=(ROOT/rel).read_bytes();h=hashlib.sha256(b).hexdigest()
        claims.append(dict(claim_id=cid,claim=claim,evidentiary_class='OFFICIAL_RECORD',source_exhibit=('EX-23|EX-28' if cid=='CLM-024' else eid),source_file=rel,sha256=h,dated_reference=loc,capture_utc='2026-10-16',limitation=limit,contrary_evidence='Unresolved matters are not findings against the builder or County.',confidence='HIGH for preserved record contents; limited applicability',reviewer='2026-10-16 independent source review'))
        exhibits.append(dict(exhibit_id=eid,caption=claim,source_file=rel,sha256=h,bytes=len(b),official_identifier=loc,what_it_proves=claim,what_it_does_NOT_prove=limit,public_release='PUBLIC_RESEARCH_REFERENCE_NOT_SIGNED_MEETING_EXHIBIT'))
        joins.append(dict(claim_id=cid,property_or_scope='Tom Street shared system' if cid in ('CLM-024','CLM-027') else 'County authority context',source_file=rel,source_sha256=h,source_byte_count=len(b),source_locator=loc,proof_limit=limit,inspection_status='REVIEWED_SOURCE_CONTENT_NOT_SITE_COMPLIANCE'))
    corroborating=OLD+'SRC_GOMAPS_TOM.json'; raw=(ROOT/corroborating).read_bytes()
    exhibits.append(dict(exhibit_id='EX-28',caption='County GoMaps corroboration of County Maintained Tom Street',source_file=corroborating,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),official_identifier='OBJECTID 2036; address range 2100-2299',what_it_proves='County GIS road-maintainer classification',what_it_does_NOT_prove=records[0][-1],public_release='PUBLIC_RESEARCH_REFERENCE_NOT_SIGNED_MEETING_EXHIBIT'))
    addcsv('00_CONTROL/EVIDENCE_LEDGER.csv','claim_id',claims)
    addcsv('00_CONTROL/EXHIBIT_INDEX.csv','exhibit_id',exhibits)
    rel=OLD+'SRC_GOMAPS_TOM.json';b=(ROOT/rel).read_bytes()
    joins.append(dict(claim_id='CLM-024',property_or_scope='Tom Street shared system',source_file=rel,source_sha256=hashlib.sha256(b).hexdigest(),source_byte_count=len(b),source_locator='features: OBJECTID 2036; MAINTAINER; RANGELOW/RANGEHIGH',proof_limit=records[0][-1],inspection_status='REVIEWED_SOURCE_CONTENT_NOT_SITE_COMPLIANCE'))
    fields,rows=readcsv('00_CONTROL/CLAIM_SOURCE_LINKS.csv')
    for row in joins:
        row={f:str(row.get(f,'')) for f in fields};existing=[x for x in rows if x['claim_id']==row['claim_id'] and x['source_file']==row['source_file']]
        if existing:
            if existing!=[row]:raise ValueError('Claim join conflict')
        else:rows.append(row)
    savecsv('00_CONTROL/CLAIM_SOURCE_LINKS.csv',fields,rows)
    fields,rows=readcsv('00_CONTROL/RESPONSIBILITY_MATRIX.csv')
    for r in rows:
        if r['role'] in ('Road / drainage right-of-way custodian','Road-maintainer classification (not asset title)'):
            r.update(role='Road-maintainer classification (not asset title)',entity='Santa Rosa County',basis='Two County GIS road records: County Maintained; segment 2036, range 2100-2299',verified_from=OLD+'SRC_TOM_FID_2006.json',certainty='VERIFIED_COUNTY_GIS_CLASSIFICATION',notes='Road title, individual culvert/inlet/ditch ownership, accepted assets and legal maintenance obligations remain unresolved.')
    savecsv('00_CONTROL/RESPONSIBILITY_MATRIX.csv',fields,rows)
    addcsv('00_CONTROL/CONTRADICTION_LOG.csv','id',[dict(id='CON-13',claim_a='Road maintainer wholly unverified',source_a='Earlier jurisdiction/readiness drafts',claim_b='County GIS classifies the target Tom Street segment County Maintained',source_b=OLD+'SRC_TOM_FID_2006.json',resolution='Road classification resolved by exact agency captures; drainage-asset ownership/maintenance and title remain unresolved.',status='ROAD_GIS_RESOLVED_ASSET_SCOPE_UNRESOLVED')])

def main():
    if len(sys.argv)!=2:raise SystemExit('Usage: reconcile_question_findings.py reviewed-artifact.zip')
    import_reviewed(Path(sys.argv[1]));write(REPORT,(ROOT/'tools/reviewed_question_report.md').read_bytes());documents();registers()
    print('Changed reviewed paths:\n'+'\n'.join(sorted(CHANGED)))
if __name__=='__main__':main()
