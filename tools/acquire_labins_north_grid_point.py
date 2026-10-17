#!/usr/bin/env python3
"""Locate Tom Street in the official LABINS/FREAC 5000-foot imagery grid.

LABINS' own FREAC mapping source specifies the State Plane North grid as
MapServer layer 14 with attribute [spn_id]. Spatially query four site sample
coordinates. Preserve the original layer metadata and query JSON.
The grid ID is an index coordinate, not a photograph or proof of available
years. Do not alter underlying source records in the public repository.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode,urlsplit
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-17/LABINS_SANTA_ROSA"
BASE="https://maps.freac.fsu.edu/arcgis/rest/services/LABINS/LABINS_Data_ccr_relate/MapServer"
MAX=6_000_000
POINTS={
  "2264_TOM_ST_SAMPLE":(-86.81466,30.41519),
  "2268_TOM_ST_SAMPLE":(-86.81466,30.41534),
  "2265_TOM_ST_SAMPLE":(-86.81521,30.41515),
  "CORRIDOR_CENTER_SAMPLE":(-86.81475,30.41524),
}
def fetch(url):
    v=urlsplit(url)
    if v.scheme!="https" or v.hostname!="maps.freac.fsu.edu":
        raise ValueError("Not official FREAC public ArcGIS hostname")
    r=Request(url,headers={"User-Agent":"TomStreetPublicEvidence/2.0","Accept":"application/json"})
    with urlopen(r,timeout=75) as conn:
        if conn.status!=200 or urlsplit(conn.url).hostname!=v.hostname:raise RuntimeError("Unexpected response source")
        raw=conn.read(MAX+1)
    if not 80<len(raw)<=MAX:raise RuntimeError("Unexpected response length")
    parsed=json.loads(raw)
    if not isinstance(parsed,dict) or parsed.get("error"):raise RuntimeError("ArcGIS error or unstructured JSON")
    return raw,parsed
def save(path,content):
    OUT.mkdir(parents=True,exist_ok=True)
    dest=OUT/path
    if dest.exists() and dest.read_bytes()!=content:
        raise RuntimeError("Previously saved original changed: do not replace")
    if not dest.exists():dest.write_bytes(content)
    return {"path":dest.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(content).hexdigest(),"bytes":len(content)}

def main():
    results={"captured_utc":datetime.now(timezone.utc).isoformat(),
         "official_source":BASE,
         "mapping_app_source":"https://github.com/FREAC/LABINS/blob/master/script.js",
         "declared_layer":14,"declared_attribute":"spn_id",
         "jurisdiction":"LABINS Florida State Plane North high resolution imagery 5,000-foot grid",
         "captures":[],"point_intersections":[],"errors":[],
         "limitations":["Published imagery grid is not an aerial photograph or guarantee of 2022/2025 local coverage.",
             "Representative parcel points are based on saved county GIS and are not surveyed property boundary markers.",
             "FREAC/LABINS source geometry and attributes may be authoritative for its own tiling scheme but do not establish permit conditions.",
             "No date of imagery acquisition follows from grid identifiers."]}
    probes=[
       ("ORIGINAL_FREAC_LABINS_MAPSERVICE_METADATA.json",BASE+"?f=pjson"),
       ("ORIGINAL_FREAC_STATE_PLANE_NORTH_GRID_LAYER14_METADATA.json",BASE+"/14?f=pjson"),
    ]
    for label, (lon,lat) in POINTS.items():
        uri=BASE+"/14/query?"+urlencode({"geometry":f"{lon},{lat}","geometryType":"esriGeometryPoint",
             "inSR":4326,"spatialRel":"esriSpatialRelIntersects",
             "outFields":"*","returnGeometry":"true","outSR":4326,"f":"pjson"})
        probes.append((f"ORIGINAL_FREAC_LABINS_NORTH_GRID_{label}.json",uri))
    for filename,url in probes:
        result={"official_url":url,"name":filename,"status":"NOT_ACQUIRED"}
        try:
            blob,parsed=fetch(url)
            if "METADATA" in filename:
                name=parsed.get("name","") or parsed.get("mapName","")
                result["reported_name"]=name
                if filename.endswith("LAYER14_METADATA.json") and "Grid" not in name and not any("spn_id" in f.get("name","").lower() for f in parsed.get("fields",[])):
                    raise RuntimeError("LABINS north layer id 14 not validated against expected image grid")
            else:
                features=parsed.get("features")
                if not isinstance(features,list):raise RuntimeError("ArcGIS response has no features array")
                result["feature_count"]=len(features)
                result["grid_identifiers"]=[f.get("attributes",{}).get("spn_id") or f.get("attributes",{}).get("SPN_ID") for f in features[:10]]
                results["point_intersections"].append({"sample":filename,"grid_ids":result["grid_identifiers"],
                                                        "features":result["feature_count"],
                                                        "interpretation":"Approximate site point only; no imagery coverage assumption"})
            result.update(save(filename,blob))
            result["status"]="OFFICIAL_FREAC_SOURCE_ARCHIVED_AND_HASHED"
        except Exception as exc:
            result["status"]="SOURCE_UNAVAILABLE_OR_VALIDATION_FAILED"
            result["error"]=type(exc).__name__+": "+str(exc)[:250]
            results["errors"].append({"name":filename,"error":result["error"]})
        results["captures"].append(result)
    results["status"]="PARTIAL_SOURCE_CAPTURE" if results["errors"] else "ALL_SOURCE_PROBES_CAPTURED"
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"LABINS_NORTH_GRID_POINT_LOOKUP_MANIFEST.json").write_text(json.dumps(results,indent=2)+"\n")
    print(json.dumps({"status":results["status"],"point_intersections":results["point_intersections"],
                        "errors":results["errors"]},indent=2))
if __name__=="__main__":main()
