#!/usr/bin/env python3
"""Bounded, read-only primary-source captures. No automatic fact acceptance."""
from __future__ import annotations
import hashlib,json,re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode,urlsplit
from urllib.request import Request,build_opener,HTTPRedirectHandler

ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'www.santarosa.fl.gov','santarosa.fl.gov','cloud.santarosa.fl.gov','santarosagis.maps.arcgis.com','services.arcgis.com','www.arcgis.com','mcclibraryfunctions.azurewebsites.us','www.floridabuilding.org','floridabuilding.org','floridadep.gov','nwfwater.com','permitting.sjrwmd.com'}
MAX_BYTES=16*1024*1024
GIS='https://cloud.santarosa.fl.gov/arcgis/rest/services/santarosa/GoMaps4_0/MapServer'
AGOL='https://santarosagis.maps.arcgis.com/sharing/rest/content/items/'
MS4='https://services.arcgis.com/Eg4L1xEv2R3abuQd/arcgis/rest/services/MS4Audit_gdb/FeatureServer/0'
def query(url,**kw):return url+'?'+urlencode({'f':'pjson',**kw})
def spatial(url):return query(url,geometry='-86.8147,30.4155',geometryType='esriGeometryPoint',inSR=4326,spatialRel='esriSpatialRelIntersects',distance=150,units='esriSRUnit_Meter',outFields='*',returnGeometry='true',outSR=4326)
ITEMS=[
 ('ORD_2025_25','https://mcclibraryfunctions.azurewebsites.us/api/ordinanceDownload/12483/1396775/pdf?forceDownload=true','pdf'),
 ('ORD_2026_03','https://mcclibraryfunctions.azurewebsites.us/api/ordinanceDownload/12483/1415471/pdf','pdf'),
 ('SRC_TYPICAL_GRADING','https://www.santarosa.fl.gov/DocumentCenter/View/370/Typical-Lot-Grading-PDF','pdf'),
 ('SRC_SUBDIVISION_APP',query(AGOL+'d133cc1e306b48f584b54389e99b37d8/data'),'json'),
 ('SRC_STORMWATER_MAP',query(AGOL+'d031e663a2f5453ca9ca6782f0f42b1e/data'),'json'),
 ('DEP_STORMWATER_MAP',query('https://www.arcgis.com/sharing/rest/content/items/9b7d4bdb68d84bd0b890e4ab83b29550/data'),'json'),
 ('SRC_GIS_PARCEL_METADATA',query(GIS+'/8'),'json'),
 ('SRC_GIS_WELLFIELD_METADATA',query(GIS+'/94'),'json'),
 ('SRC_GIS_WELLFIELD_VICINITY',spatial(GIS+'/94/query'),'json'),
 ('SRC_GIS_BASIN_VICINITY',spatial(GIS+'/100/query'),'json'),
 ('SRC_GIS_PROBLEM_AREA_79',spatial(GIS+'/79/query'),'json'),
 ('SRC_GIS_PROBLEM_AREA_92',spatial(GIS+'/92/query'),'json'),
 ('SRC_MS4_METADATA',query(MS4),'json'),
 ('SRC_MS4_OUTFALL_VICINITY',spatial(MS4+'/query'),'json'),
 ('SRC_SUBDIVISION_PAGE','https://www.santarosa.fl.gov/198/Subdivisions','html'),
 ('SRC_LDC_PAGE','https://www.santarosa.fl.gov/182/Land-Development-Code','html'),
 ('SRC_ROAD_ISSUES','https://www.santarosa.fl.gov/377/Road-Issues','html'),
 ('FBC_CURRENT_EDITION','https://www.floridabuilding.org/','html'),
 ('DEP_CGP_CRITERIA','https://floridadep.gov/water/stormwater/content/construction-activity','html'),
 ('DEP_CGP_LOOKUP','https://floridadep.gov/water/stormwater/content/find-permit','html'),
 ('NWFWMD_ERP_CRITERIA','https://nwfwater.com/permits/environmental-resource-permits/','html'),
 ('NWFWMD_PUBLIC_PORTAL','https://permitting.sjrwmd.com/nwep/','html'),
]
def check_url(url):
 p=urlsplit(url)
 if p.scheme!='https' or p.hostname not in ALLOWED or p.username or p.password or p.port not in (None,443):raise ValueError('Unapproved URL')
 return url
class Redirect(HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  check_url(newurl);return super().redirect_request(req,fp,code,msg,headers,newurl)
def validate_payload(raw,kind):
 if not raw:raise ValueError('Empty response')
 if kind=='pdf':
  if not raw.startswith(b'%PDF-'):raise ValueError('Not PDF bytes')
  return 'PDF_BYTES_NOT_YET_REVIEWED'
 if kind=='json':
  obj=json.loads(raw)
  if not isinstance(obj,dict) or 'error' in obj:raise ValueError('API error or unexpected JSON')
  if obj.get('exceededTransferLimit'):return 'PARTIAL_TRANSFER_LIMIT'
  if obj.get('features')==[]:return 'EMPTY_SEARCH_NOT_ABSENCE_PROOF'
  return 'JSON_CAPTURE_NOT_APPLICABILITY_VERIFIED'
 if kind!='html':raise ValueError('Unsupported response kind')
 return 'HTML_CAPTURE_NOT_PLAN_VERIFICATION'
def fetch(item,out):
 key,url,kind=item; row={'source_id':key,'requested_url':check_url(url),'retrieved_utc':datetime.now(timezone.utc).isoformat(),'status':'NOT_CAPTURED'}
 try:
  with build_opener(Redirect()).open(Request(url,headers={'User-Agent':'Tom-Street-Public-Records-Research/1.0'}),timeout=45) as r:
   check_url(r.url);raw=r.read(MAX_BYTES+1)
   if len(raw)>MAX_BYTES:raise ValueError('Response too large')
   row.update(final_url=r.url,http_status=r.status,content_type=r.headers.get('Content-Type'))
  status=validate_payload(raw,kind);target=out/(key+'.'+kind)
  with target.open('xb') as f:f.write(raw)
  row.update(status=status,local_path=target.relative_to(ROOT).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
 except Exception as exc:row['failure']=type(exc).__name__+': '+str(exc)[:300]
 return row
def main():
 out=ROOT/'17_CURRENT_RESEARCH'/'captures'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');out.mkdir(parents=True,exist_ok=False)
 with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(lambda x:fetch(x,out),ITEMS))
 manifest={'scope':'Fixed public records and guidance; not signed site-plan, survey, positive-outfall or coverage verification. Empty GIS searches do not prove absence.','sources':rows}
 with (out/'ACQUISITION_MANIFEST.json').open('x') as f:json.dump(manifest,f,indent=2)
 print(json.dumps(manifest,indent=2))
 if not any('local_path' in r for r in rows):raise SystemExit('No source captured')
if __name__=='__main__':main()
