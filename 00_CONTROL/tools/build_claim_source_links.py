#!/usr/bin/env python3
"""HISTORICAL SOURCE-LINK GENERATOR DISABLED: current ledger has later claims.

Build an auditable claim -> primary-source table from preserved archive bytes.

Do not infer a second-property source automatically from a first-property capture.
This generator only inserts explicitly enumerated, locally corroborated links.
"""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
from paths import ROOT

LINKS={
 'CLM-001': [('2264','02_PROPERTY_AND_PARCELS/2264_Tom_St/srcpa_property_record_21-2S-26-0780-0QQ00-1020.json','$[0].parcelNumber','$[0].situsAddress1')],
 'CLM-002': [('2268','02_PROPERTY_AND_PARCELS/2268_Tom_St/srcpa_property_record_21-2S-26-0780-0QQ00-1490.json','$[0].parcelNumber','$[0].situsAddress1')],
 'CLM-003': [('street-roll','02_PROPERTY_AND_PARCELS/RAW_HTTP/srcpa_property_query_street_TOM_NAVARRE.json','query: street=TOM city=NAVARRE','no current 2266 entry; historical address not negated')],
 'CLM-004': [('2264','03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_project_by_uid.json','data.status, data.dateIssued','archived October 2026')],
 'CLM-005': [('2268','03_PERMITS_AND_INSPECTIONS/2268_Tom_St/BP-2026-1612_project_by_uid.json','data.status, data.dateIssued','archived October 2026')],
 'CLM-006': [('2264','03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_project_by_uid.json','data.applicantBusinessName','business only; no contact details'),('2268','03_PERMITS_AND_INSPECTIONS/2268_Tom_St/BP-2026-1612_project_by_uid.json','data.applicantBusinessName','business only; no contact details')],
 'CLM-007': [('2264','03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_inspections.json','data[*].inspectionDateTime; comments','instruction != as-built')],
 'CLM-008': [('2268','03_PERMITS_AND_INSPECTIONS/2268_Tom_St/BP-2026-1612_inspections.json','data[*].inspectionDateTime; comments','observed ditch; no quantitative drainage proof')],
 'CLM-009': [('2268','03_PERMITS_AND_INSPECTIONS/2268_Tom_St/BP-2026-1612_inspections.json','data[*].inspectionDateTime; comments','qualitative roadway grade only')],
 'CLM-010': [('2264','03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_requirements.json','$[*].Requirement == Certified Drainage as Built; Status','Assigned != submitted/late'),('2268','03_PERMITS_AND_INSPECTIONS/2268_Tom_St/BP-2026-1612_requirements.json','$[*].Requirement == Certified Drainage as Built; Status','Assigned != submitted/late')],
 'CLM-011': [('2264','03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_requirements.json','relevant drainage/final/CO requirements','does not establish CO issuance'),('2268','03_PERMITS_AND_INSPECTIONS/2268_Tom_St/BP-2026-1612_requirements.json','relevant drainage/final/CO requirements','does not establish CO issuance')],
 'CLM-012': [('2264','03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_project_files.json','data == []','portal only; not county file inventory'),('2268','03_PERMITS_AND_INSPECTIONS/2268_Tom_St/BP-2026-1612_project_files.json','data == []','portal only; not county file inventory')],
 'CLM-013': [('ERP proximity','09_ENVIRONMENTAL_PERMITS/SYSTEM_RAW/erp_nearest_permits_tom_street.json','sites.*.attributes.OFFCL_PRMT_ID','proximity result only; overlap/applicability unverified')],
 'CLM-014': [('FEMA point samples','11_HYDROLOGY_AND_HAZARD/fema_nfhl_flood_hazard_zones.json','results.*','sampled points only; not certified parcel-wide zone')],
 'CLM-015': [('County StoryMaps searched','04_ENGINEERING_AND_DRAINAGE/Tom_Street_Shared_System/approved_subdivision_storymaps_search.json','search queries/results','negative interface search is not evidence no plan exists')],
 'CLM-016': [('2260','04_ENGINEERING_AND_DRAINAGE/Tom_Street_Shared_System/2019-7490-000-B-2.json','search_row, inspections','historical neighbor record, no present harm'),('2270','04_ENGINEERING_AND_DRAINAGE/Tom_Street_Shared_System/2021-2524-000-B-1.json','search_row, inspections','historical neighbor record, no present harm')],
 'CLM-017': [('County LDC','08_LEGAL_AND_REGULATORY/SOURCE/santa_rosa_county_LDC.pdf','section 4.04.01.D.1, D.4, E','conditional applicability; 2025-11-10 cover')],
 'CLM-018': [('County LDC','08_LEGAL_AND_REGULATORY/SOURCE/santa_rosa_county_LDC.pdf','section 3.04.04, 3.04.05','site impact not established')],
 'CLM-021': [('Florida Supreme Court corrected opinion','08_LEGAL_AND_REGULATORY/SOURCE/PRIMARY_AUTHORITY/Westland_Skating_Center_v_Gus_Machado_Buick_Fla_1989_CORRECTED_OPINION.pdf','Florida Supreme Court opinion, 1989-03-30','general legal principle; no Tom Street finding')],
 'CLM-022': [('FDEP 2023 index','08_LEGAL_AND_REGULATORY/SOURCE/PRIMARY_AUTHORITY/FDEP_FINAL_ORDER_INDEX_2023_Q1.pdf','OGC 22-2720 / DEP23-0087','index only; order not obtained; no Tom Street link')],
 'CLM-023': [('FDEP 2024 index','08_LEGAL_AND_REGULATORY/SOURCE/PRIMARY_AUTHORITY/FDEP_FINAL_ORDER_INDEX_2024_Q1.pdf','OGC 23-1387 / DEP24-0006','index only; order not obtained; no Tom Street link')],
}
FIELDS=['claim_id','property_or_scope','source_file','source_sha256','source_byte_count','source_locator','proof_limit','inspection_status']

def run():
 ledger={r['claim_id']:r for r in csv.DictReader((ROOT/'00_CONTROL/EVIDENCE_LEDGER.csv').open())}
 missing=set(ledger)-set(LINKS)-{'CLM-019','CLM-020'}
 if missing:raise ValueError('Claims without declared source mapping: '+', '.join(sorted(missing)))
 rows=[]
 for cid in sorted(LINKS):
  if cid not in ledger:raise ValueError('Unknown claim '+cid)
  for scope,file,locator,limit in LINKS[cid]:
   p=ROOT/file
   if not p.is_file():raise FileNotFoundError(file)
   data=p.read_bytes()
   rows.append(dict(claim_id=cid,property_or_scope=scope,source_file=file,source_sha256=hashlib.sha256(data).hexdigest(),source_byte_count=len(data),source_locator=locator,proof_limit=limit,inspection_status='LOCAL_SOURCE_HASH_VERIFIED; SEMANTIC_INTERPRETATION_REVIEW_REQUIRED'))
 out=ROOT/'00_CONTROL/CLAIM_SOURCE_LINKS.csv'
 with out.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
 return len(rows)
if __name__=='__main__':
    raise SystemExit("RETIRED HISTORICAL SOURCE-LINK BUILDER: cannot overwrite later claim/source joins. Use active reviewed register updates.")
    print('link rows',run())
