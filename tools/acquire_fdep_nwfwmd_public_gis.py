#!/usr/bin/env python3
"""Capture bounded Florida DEP construction-stormwater GIS and NWFWMD permit data.

GIS features are indexed point locations, not permit boundaries. No result
does NOT establish missing CGP coverage, operator liability or violation.
Never collect account cookies, personal resident data or plan-submittal tokens.
"""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"09_ENVIRONMENTAL_PERMITS/PRE_REQUEST_PUBLIC_PERMIT_REFRESH_2026-10-16"
FDEP="https://ca.dep.state.fl.us/arcgis/rest/services/OpenData/WAFR/MapServer/0"
NWFWMD="https://permitting.sjrwmd.com/arcgis02/rest/services/NWFWMD/EPermit_ERP/MapServer/0"
POINT="-86.81466,30.41519"
MAX=3_000_000
SOURCES={
    "ORIGINAL_FDEP_NPDES_STORMWATER_LAYER_METADATA.json":FDEP+"?f=pjson",
    "ORIGINAL_FDEP_NPDES_STORMWATER_WITHIN_500M.json":FDEP+"/query?"+urlencode({
        "geometry":POINT,"geometryType":"esriGeometryPoint","inSR":4326,
        "spatialRel":"esriSpatialRelIntersects","distance":500,"units":"esriSRUnit_Meter",
        "outFields":"*","returnGeometry":"true","outSR":4326,"f":"pjson"}),
    "ORIGINAL_FDEP_NPDES_STORMWATER_WITHIN_2000M.json":FDEP+"/query?"+urlencode({
        "geometry":POINT,"geometryType":"esriGeometryPoint","inSR":4326,
        "spatialRel":"esriSpatialRelIntersects","distance":2000,"units":"esriSRUnit_Meter",
        "outFields":"*","returnGeometry":"true","outSR":4326,"f":"pjson"}),
    "ORIGINAL_NWFWMD_ERP_9220_ALL_SEQUENCES.json":NWFWMD+"/query?"+urlencode({
        "where":"OFFCL_PRMT_ID=9220","outFields":"*","returnGeometry":"true",
        "outSR":4326,"f":"pjson"})
}

def query(url):
    p=urlparse(url)
    if p.scheme!="https" or p.hostname not in {"ca.dep.state.fl.us","permitting.sjrwmd.com"}:
        raise ValueError("Unapproved public agency hostname")
    req=Request(url,headers={"User-Agent":"TomStreetResearchPublicEvidence/2.0","Accept":"application/json"})
    with urlopen(req,timeout=70) as response:
        if response.status!=200 or urlparse(response.url).hostname!=p.hostname:
            raise RuntimeError("Response status or host changed")
        raw=response.read(MAX+1)
    if not (50<len(raw)<=MAX):raise RuntimeError("Invalid or oversized response")
    obj=json.loads(raw)
    if not isinstance(obj,dict) or obj.get("error"):
        raise RuntimeError("Not a valid official ArcGIS JSON response")
    return raw,obj

def archive(dest,raw):
    h=sha256(raw).hexdigest()
    if dest.exists() and dest.read_bytes()!=raw:
        raise RuntimeError("Official source bytes changed; preserve a separate dated version before replacing")
    if not dest.exists():dest.write_bytes(raw)
    return {"path":dest.relative_to(ROOT).as_posix(),"sha256":h,"bytes":len(raw)}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    result={
      "captured_utc":datetime.now(timezone.utc).isoformat(),
      "jurisdiction":"Florida DEP and NWFWMD original public ArcGIS sources",
      "requested_point_wgs84":POINT,"sources":[],"failed_queries":[],
      "conclusion_limitations":[
        "A bounded search of public GIS is neither a complete permit-register search nor a legal no-record certification.",
        "The FDEP NPDES stormwater feature is a permit point, NOT mapped construction plan, footprint or qualifying discharge.",
        "Nearness of NWFWMD ERP point 9220 (Hadleigh Hills) does not associate the project with these particular Tom Street parcels.",
        "An empty public GIS result does not prove an absent NOI or violation; some FDEP permit records require agency/OCULUS lookup.",
        "Local grading compliance and hydraulic adequacy require actual County engineering plans and field measurements.",
      ]}
    for name,url in SOURCES.items():
        one={"source_name":name,"official_url":url,"status":"NOT_ACQUIRED"}
        try:
            raw,obj=query(url)
            if name.endswith("METADATA.json"):
                if "Stormwater" not in obj.get("name","") and obj.get("id")!=0:
                    raise RuntimeError("Public layer identity mismatch")
                one["layer_name"]=obj.get("name")
            else:
                features=obj.get("features")
                if not isinstance(features,list):raise RuntimeError("Not feature query response")
                one["features_returned"]=len(features)
                one["feature_ids"]=[v.get("attributes",{}).get("OBJECTID") for v in features[:100]]
                if "ERP_9220" in name:
                    if any(v.get("attributes",{}).get("OFFCL_PRMT_ID")!=9220 for v in features):
                        raise RuntimeError("Wrong NWFWMD permit returned")
                    one["observed_seqs"]=[v["attributes"].get("SEQ_NO") for v in features]
                if "WITHIN_500M" in name or "WITHIN_2000M" in name:
                    one["distances_are_meter_bounded_queries"]=True
            one.update(archive(OUT/name,raw))
            one["status"]="ORIGINAL_OFFICIAL_ARCGIS_RESPONSE_ARCHIVED"
        except Exception as exc:
            one["status"]="NOT_OBTAINED_PUBLIC_QUERY_FAILED"
            one["error"]=type(exc).__name__+": "+str(exc)[:250]
            result["failed_queries"].append(name)
        result["sources"].append(one)
    result["source_coverage_status"]="PARTIAL" if result["failed_queries"] else "ALL_FOUR_QUERIES_CAPTURED_SOURCE_SCOPE_LIMITED"
    (OUT/"ACQUISITION_MANIFEST.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"scope":result["source_coverage_status"],"queries":[{"name":x["source_name"],"status":x["status"],"features":x.get("features_returned")} for x in result["sources"]]},indent=2))
if __name__=="__main__":main()
