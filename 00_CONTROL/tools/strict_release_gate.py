#!/usr/bin/env python3
"""Fail-closed checks for immutable agency-record references and public drafts.

Run with no arguments for read-only checks. Non-zero means release NOT approved.
This checks file integrity, logical linkage and publishing rules, not site
engineering adequacy or a legal conclusion. Human privacy review still required.
"""
from __future__ import annotations
import csv,hashlib,json,re,sys,zipfile,subprocess
from pathlib import Path
from paths import ROOT
from classify_for_release import classify

ERRORS=[]
def fail(message):ERRORS.append(message);print('FAIL',message)
def ok(label):print('PASS',label)
def readcsv(name):return list(csv.DictReader((ROOT/name).open(newline='')))
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def check_claim_links():
 entries=readcsv('00_CONTROL/CLAIM_SOURCE_LINKS.csv')
 ledger={x['claim_id']:x for x in readcsv('00_CONTROL/EVIDENCE_LEDGER.csv')}
 assert ledger
 grouped={}
 for r in entries:
  cid=r['claim_id'];grouped.setdefault(cid,[]).append(r)
  p=ROOT/r['source_file']
  if not p.is_file() or h(p)!=r['source_sha256'] or len(p.read_bytes())!=int(r['source_byte_count']):fail('claim source checksum/path: '+cid+' '+r['source_file'])
 for cid,row in ledger.items():
  if row['evidentiary_class'] in ('OFFICIAL_RECORD','OBSERVATION') and not grouped.get(cid):fail('claim missing primary-source joins: '+cid)
 if set(ledger) - set(grouped) - {'CLM-019','CLM-020'}:
  fail('unmapped official claims: '+', '.join(sorted(set(ledger)-set(grouped)-{'CLM-019','CLM-020'})))
 for cid,expected in {'CLM-006':{'2264','2268'},'CLM-010':{'2264','2268'},'CLM-011':{'2264','2268'},'CLM-012':{'2264','2268'},'CLM-016':{'2260','2270'}}.items():
  scopes={v['property_or_scope'] for v in grouped.get(cid,[])}
  if scopes!=expected:fail('missing cross-site corroboration: '+cid)
 for addr,number in [('2264','1621'),('2268','1612')]:
  folder=ROOT/f'03_PERMITS_AND_INSPECTIONS/{addr}_Tom_St'
  project=json.loads((folder/f'BP-2026-{number}_project_by_uid.json').read_text())['data']
  assert project.get('status')=='Active',('unexpected archived status',addr)
  refresh=json.loads((ROOT/f'03_PERMITS_AND_INSPECTIONS/STATUS_REFRESH/BP-2026-{number}_status_refresh.json').read_text())
  if refresh['status_at_refresh']!=project['status'] or 'archived' not in refresh.get('status_verification_scope','').lower():fail('misrepresented archived permit status: '+addr)
  req=json.loads((folder/f'BP-2026-{number}_requirements.json').read_text())
  if not any(x.get('Requirement')=='Certified Drainage as Built' and x.get('Status')=='Assigned' for x in req):fail('as-built task no longer corroborated: '+addr)
  uploaded=json.loads((folder/f'BP-2026-{number}_project_files.json').read_text())
  if uploaded.get('data')!=[]:fail('portal attachments have changed: '+addr)
 if not ERRORS:ok('claim-to-source pointers and site-pair primary-record joins')

def check_evidence_manifest():
 items=readcsv('00_CONTROL/EVIDENCE_MANIFEST.csv')
 names=set()
 for r in items:
  name=r['relative_path']
  if name in names:fail('duplicate evidence manifest path: '+name)
  names.add(name)
  p=ROOT/name
  if not p.exists() or h(p)!=r['sha256'] or str(p.stat().st_size)!=r['bytes']:
   fail('stale or absent evidence-manifest entry: '+name)
  if name=='00_CONTROL/EVIDENCE_MANIFEST.csv':fail('manifest must not self-hash')
 if not ERRORS:ok('evidence manifest source hashes')

def check_privacy_and_release():
 classifier=ROOT/'00_CONTROL/tools/classify_for_release.py'
 code=classifier.read_bytes()
 # Ban self-exempting real-world credential patterns; synthetic fixtures only.
 if b'ACCOUNT_MARKERS =' in code or b'7568CBA6' in code or b'__Host-' in code:fail('account-specific legacy marker remains in classifier')
 # A pyc created during local checks is ignored by .gitignore, but a
 # previously *tracked* pyc is unsafe; query the Git index when available.
 if (ROOT/'.git').exists():
  q=subprocess.run(['git','ls-files','--cached','--','*.pyc'],cwd=ROOT,capture_output=True,text=True)
  if q.returncode or q.stdout.strip():fail('bytecode remains tracked in Git index')
 else:
  # Source ZIP has no Git index; remote tree must also be checked at publish.
  pass
 docs=ROOT/'15_RECONCILED_DRAFTS'
 assert docs.is_dir()
 for p in docs.rglob('*.md'):
  content=p.read_text()
  bad=re.findall(r'(?i)(?:the sealed engineer.s drainage certification does not exist|drains into structures on the 2260|every inspection passed)',content)
  if bad:fail('unsupported assertion in canonical draft: '+str(p.relative_to(ROOT)))
  cl,why=classify(str(p.relative_to(ROOT)),p.read_bytes())
  if cl!='PUBLIC_CANDIDATE':fail('canonical public draft requires review: '+str(p.relative_to(ROOT)))
 for p in [ROOT/'14_MEETING_PACKET/RELEASE_README.md',ROOT/'README.md']:
  if 'supersed' not in p.read_text().lower() and 'withdrawn' not in p.read_text().lower():fail('historical release not marked superseded: '+p.name)
 for p in (ROOT/'releases').rglob('*.zip'):
  # Legacy release must never be silently upgraded to cleared publication.
  with zipfile.ZipFile(p) as z:
   if z.testzip() is not None:fail('corrupt archive '+str(p))
   if any('..' in n.split('/') or n.startswith('/') for n in z.namelist()):fail('zip path traversal '+str(p))
 if not ERRORS:ok('historical release withdrawn, public-draft privacy and archive integrity')

def check_requests():
 rows=readcsv('00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv')
 for x in rows:
  if x['submitted'].upper()=='TRUE' and not x['receipt_id'].strip():fail('records request marked sent without receipt: '+x['gap_id'])
 for p in ['13_PUBLIC_RECORDS_REQUESTS/FDEP_CONSTRUCTION_STORMWATER_CGP_RECORDS_DRAFT.md','13_PUBLIC_RECORDS_REQUESTS/COUNTY_PUBLIC_WORKS_DRAINAGE_WORK_REQUEST_DRAFT.md']:
  if not (ROOT/p).exists():fail('missing additional official records/work order draft: '+p)
 if not ERRORS:ok('agency requests not falsely represented as submitted')

if __name__=='__main__':
 for fn in (check_claim_links,check_evidence_manifest,check_privacy_and_release,check_requests):
  try:fn()
  except Exception as exc:fail(f'{fn.__name__}: {type(exc).__name__}: {exc}')
 print(f'STRICT GATE: {len(ERRORS)} error(s); no human privacy approval implied')
 raise SystemExit(1 if ERRORS else 0)
