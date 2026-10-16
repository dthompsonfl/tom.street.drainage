#!/usr/bin/env python3
"""Acquire original 2022 cached Santa Rosa imagery tiles and public stormwater GIS.

Separate authoritative raw County bytes from derivatives. No source bytes are
fabricated or overwritten; partial downloads remain explicitly partial.
This does not establish individual lot boundaries or 2026 drainage causation.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
import math
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16"
DEST = BASE / "COUNTY_2022_CACHED_ORTHOPHOTO"
GIS = BASE / "COUNTY_STORMWATER_HOSTED_FEATURE"
MAP = "https://cloud.santarosa.fl.gov/arcgis/rest/services/santarosa/Aerials2022/MapServer"
LAYER = "https://cloud.santarosa.fl.gov/arcgis/rest/services/Hosted/OpenData_StormwaterProblemAreas/FeatureServer/0"
BBOX = (-86.8162, 30.4144, -86.8134, 30.4160)
MAX_BYTES = 2_500_000
NOTES = [
    "These are official cached map-render tiles and a stitched derivative, not raw camera frames or the original flight survey.",
    "County Aerials2022 service title is not proof of the exact acquisition day; obtain catalogue/flight metadata from FDOT.",
    "Map tile spatial resolution is not a vertical elevation or survey-quality map.",
    "Original tile SHA-256, service metadata, spatial extent and image format preserved; no parcel boundary lines are certified.",
    "OpenData stormwater polygon is a historic planning indicator; it does not prove current flooding, severity, cause or a violation.",
    "Reusers must include the County GIS source metadata and distribution-liability/usage statement."
]

def fetch(url, limit=MAX_BYTES):
    parts = urlparse(url)
    if parts.scheme != "https" or parts.hostname != "cloud.santarosa.fl.gov":
        raise ValueError("Unsupported source host")
    req = Request(url, headers={"User-Agent":"TomStreetPublicEvidence/2.0","Accept":"application/json,image/jpeg,image/png,*/*"})
    with urlopen(req, timeout=65) as r:
        if r.status != 200 or urlparse(r.url).hostname != parts.hostname:
            raise RuntimeError("Non-200 or cross-origin redirect")
        raw = r.read(limit+1)
        mime = r.headers.get("Content-Type", "")
    if not (100 <= len(raw) <= limit): raise RuntimeError("Invalid response size")
    return raw, mime

def saved(dest, raw):
    dest.parent.mkdir(parents=True, exist_ok=True)
    digest=sha256(raw).hexdigest()
    if dest.exists():
        if dest.read_bytes() != raw:
            raise RuntimeError(f"Upstream changed previously preserved original {dest}")
    else:
        dest.write_bytes(raw)
    return {"path":dest.relative_to(ROOT).as_posix(),"bytes":len(raw),"sha256":digest}

def jcapture(url, path, require=None):
    raw,mime=fetch(url)
    obj=json.loads(raw)
    if not isinstance(obj,dict) or obj.get("error"):
        raise RuntimeError(f"Invalid County GIS response for {path.name}")
    if require and not require(obj):
        raise RuntimeError("County response did not satisfy source identity check")
    return obj, saved(path,raw) | {"url":url,"mime":mime}

def project(lon,lat):
    lat=max(-85.05112878,min(85.05112878,lat))
    r=6378137.0
    return (r*math.radians(lon), r*math.log(math.tan(math.pi/4+math.radians(lat)/2)))

def probe_standard_site_center_tiles():
    """Last-resort public cache probe when County metadata returns a 500.

    ArcGIS traditional 3857 tile origin is a documented hypothesis here, not
    an agency-supplied tiling/flight-date confirmation. No composite is made.
    """
    r=6378137.0; origin=20037508.342789244
    lon,lat=-86.81466,30.41519
    x=r*math.radians(lon)
    y=r*math.log(math.tan(math.pi/4+math.radians(lat)/2))
    rows=[]
    for z in (19,18,17,16):
        resolution=156543.03392804097/(2**z)
        col=math.floor((x+origin)/(256*resolution))
        row=math.floor((origin-y)/(256*resolution))
        url=f"{MAP}/tile/{z}/{row}/{col}"
        hit={"url":url,"level":z,"row":row,"column":col,
             "georeference":"HYPOTHESIS_STANDARD_ARCGIS_3857_TILE_GRID"}
        try:
            blob,mime=fetch(url,limit=2_500_000)
            ext="jpg" if blob.startswith(b"\xff\xd8\xff") else "png" if blob.startswith(b"\x89PNG\r\n\x1a\n") else None
            if not ext:raise ValueError("not JPEG or PNG cache tile")
            img=Image.open(BytesIO(blob));img.load()
            if img.size!=(256,256) or max(ImageStat.Stat(img.convert("RGB")).var)<4:
                raise ValueError("tile is blank or wrong dimensions")
            out=DEST/"FALLBACK_TILE_PROBES"/f"z{z}_r{row}_c{col}.{ext}"
            hit.update(saved(out,blob));hit["status"]="RAW_PUBLIC_CACHE_TILE_DOWNLOADED_BUT_GRID_NOT_VERIFIED"
        except Exception as exc:
            hit["status"]="PUBLIC_TILE_NOT_AVAILABLE";hit["failure"]=type(exc).__name__+": "+str(exc)[:180]
        rows.append(hit)
    return rows


def imagery():
    rawmeta={"source":MAP,"bbox_lonlat":BBOX,"tiles":[],"failures":[],"status":"NOT_OBTAINED"}
    try:
        meta, capture = jcapture(MAP+"?f=pjson",DEST/"ORIGINAL_AERIALS2022_MAPSERVER_METADATA.json",
                                lambda j:j.get("singleFusedMapCache") is True and isinstance(j.get("tileInfo"),dict))
        rawmeta["service_metadata"]=capture
        info=meta["tileInfo"]
        size=info["cols"]
        if size != info["rows"] or size not in (256,512):
            raise RuntimeError("Unexpected cache tile geometry")
        origin=info["origin"]
        lods=info.get("lods",[])
        corners=[project(BBOX[0],BBOX[1]),project(BBOX[2],BBOX[3])]
        west,south=corners[0];east,north=corners[1]
        candidates=[]
        for lod in lods:
            res=float(lod["resolution"]); level=int(lod["level"])
            if not(0.1 <= res <= 1.5):continue
            cmin=math.floor((west-origin["x"])/(res*size))
            cmax=math.floor((east-origin["x"])/(res*size))
            rmin=math.floor((origin["y"]-north)/(res*size))
            rmax=math.floor((origin["y"]-south)/(res*size))
            count=(cmax-cmin+1)*(rmax-rmin+1)
            if 1<=count<=32:candidates.append((res,level,cmin,cmax,rmin,rmax,count))
        if not candidates:raise RuntimeError("No bounded County 2022 cached resolution available")
        res,level,cmin,cmax,rmin,rmax,count=sorted(candidates)[0]
        rawmeta.update(level=level,resolution_m_per_pixel=res,cache_tile_size_px=size,
                       expected_tile_count=count,cache_columns=[cmin,cmax],cache_rows=[rmin,rmax],
                       origin_3857=origin,source_crs="EPSG:3857")
        images={}
        for row in range(rmin,rmax+1):
            for col in range(cmin,cmax+1):
                url=f"{MAP}/tile/{level}/{row}/{col}"
                try:
                    b,mime=fetch(url,limit=2_500_000)
                    if b[:3]==b"\xff\xd8\xff": ext="jpg"
                    elif b[:8]==b"\x89PNG\r\n\x1a\n":ext="png"
                    else:raise ValueError("not original cached image bytes")
                    im=Image.open(BytesIO(b));im.load()
                    if im.size!=(size,size):raise ValueError(f"unexpected tile size {im.size}")
                    if max(ImageStat.Stat(im.convert("RGB")).var)<4.0:raise ValueError("empty or blank tile")
                    file=DEST/"ORIGINAL_TILES"/f"z{level}_r{row}_c{col}.{ext}"
                    record=saved(file,b)|{"url":url,"row":row,"column":col,"type":"OFFICIAL_CACHE_TILE"}
                    rawmeta["tiles"].append(record); images[(row,col)]=im.convert("RGB")
                except Exception as exc:
                    rawmeta["failures"].append({"row":row,"column":col,"error":str(exc)[:200]})
        if len(images)==count:
            mosaic=Image.new("RGB", ((cmax-cmin+1)*size, (rmax-rmin+1)*size))
            for (row,col),img in images.items():
                mosaic.paste(img,((col-cmin)*size,(row-rmin)*size))
            target=DEST/"DERIVED_TOM_STREET_2022_TILE_MOSAIC.png"
            buffer=BytesIO();mosaic.save(buffer,format="PNG")
            rawmeta["derived_mosaic"]=saved(target,buffer.getvalue())|{"source":"original cached tiles listed in this manifest"}
            world=(res,0.0,0.0,-res,origin["x"]+cmin*res*size+res/2,origin["y"]-rmin*res*size-res/2)
            saved(DEST/"DERIVED_TOM_STREET_2022_TILE_MOSAIC.pgw",
                  ("\n".join(f"{v:.12f}" for v in world)+"\n").encode())
            rawmeta["status"]="ALL_EXPECTED_ORIGINAL_2022_TILES_ACQUIRED"
        elif images:rawmeta["status"]="PARTIAL_2022_TILE_ACQUISITION_NOT_SUFFICIENT_TO_MAP_WHOLE_BBOX"
        else:rawmeta["status"]="NO_VALID_2022_TILES_RETRIEVED"
    except Exception as exc:
        rawmeta["status"]="2022_CACHE_ACQUISITION_FAILED"
        rawmeta["failure"]=type(exc).__name__+": "+str(exc)[:300]
        rawmeta["fallback_tile_probes"]=probe_standard_site_center_tiles()
        if any(z["status"].startswith("RAW_PUBLIC") for z in rawmeta["fallback_tile_probes"]):
            rawmeta["status"]="PUBLIC_CENTER_CACHE_TILE_ONLY_METADATA_AND_FULL_COVERAGE_UNVERIFIED"
            rawmeta["tiles"]=[z for z in rawmeta["fallback_tile_probes"] if z["status"].startswith("RAW_PUBLIC")]
    rawmeta["note"]=NOTES
    return rawmeta

def stormwater():
    details={"source":LAYER,"status":"NOT_OBTAINED","captures":[]}
    candidates=[
        (LAYER+"?f=pjson",GIS/"ORIGINAL_HOSTED_LAYER_METADATA.json",
         lambda d:d.get("name")=="OpenData_StormwaterProblemAreas"),
        ("https://cloud.santarosa.fl.gov/arcgis/rest/services/Hosted/OpenData_StormwaterProblemAreas/FeatureServer/info/iteminfo?f=pjson",
         GIS/"ORIGINAL_HOSTED_SERVICE_ITEMINFO.json",
         lambda d: "licenseInfo" in d or "description" in d),
        (LAYER+"/query?"+urlencode({"geometry":"-86.81466,30.41519","geometryType":"esriGeometryPoint",
          "inSR":"4326","spatialRel":"esriSpatialRelIntersects","outFields":"*",
          "returnGeometry":"true","outSR":"4326","f":"pjson"}),
         GIS/"ORIGINAL_HOSTED_FEATURES_AT_2264_POINT.json",
         lambda d:isinstance(d.get("features"),list))
    ]
    for url,path,test in candidates:
        try:
            j,r= jcapture(url,path,test)
            details["captures"].append(r | {"feature_count":len(j.get("features",[])) if "features" in j else None})
            if "features" in j:details["intersecting_features"]=[
               {"fid":f.get("attributes",{}).get("fid"),
                "datasource":f.get("attributes",{}).get("datasource"),
                "globalid":f.get("attributes",{}).get("globalid")} for f in j["features"]]
        except Exception as exc:
            details.setdefault("failures",[]).append({"url":url,"error":str(exc)[:220]})
    details["status"]="CAPTURED" if len(details["captures"])==len(candidates) else "PARTIAL_SOURCE_CAPTURES"
    details["interpretation"]="Hosted FIDs may differ from GoMaps OBJECTID 2068. Match GlobalID or geometry before equating entries."
    return details

def main():
    DEST.mkdir(parents=True,exist_ok=True);GIS.mkdir(parents=True,exist_ok=True)
    result={"acquisition_utc":datetime.now(timezone.utc).isoformat(),
            "method":"public Santa Rosa County published ArcGIS service and cache",
            "imagery":imagery(),"stormwater":stormwater()}
    (DEST/"ACQUISITION_MANIFEST.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"imagery_status":result["imagery"]["status"],
      "tile_count":len(result["imagery"]["tiles"]),
      "tile_failures":len(result["imagery"]["failures"]),
      "stormwater_status":result["stormwater"]["status"]},indent=2))
    if result["imagery"]["status"]=="2022_CACHE_ACQUISITION_FAILED":
        print("County 2022 archive unavailable at this access level; no imagery claim is established.")

if __name__=="__main__":
    main()
