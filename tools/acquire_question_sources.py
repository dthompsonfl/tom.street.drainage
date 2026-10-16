#!/usr/bin/env python3
"""Capture bounded public agency JSON without credentials or applicability claims.

Response bytes and provenance are preserved separately. Empty/truncated searches
are never a no-records determination. Existing captures are never overwritten.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
STREETS = 'https://services.arcgis.com/Eg4L1xEv2R3abuQd/arcgis/rest/services/StreetsOpenData/FeatureServer/0'
GOMAPS = 'https://cloud.santarosa.fl.gov/arcgis/rest/services/santarosa/GoMaps4_0/MapServer'
PORTAL = 'https://santarosagis.maps.arcgis.com/sharing/rest/content/items/'
NWFWMD = 'https://permitting.sjrwmd.com/arcgis02/rest/services/NWFWMD/EPermit_ERP/MapServer/0'
ALLOWED = {'services.arcgis.com', 'cloud.santarosa.fl.gov', 'santarosagis.maps.arcgis.com', 'permitting.sjrwmd.com'}
MAX_BYTES = 8 * 1024 * 1024

def check_url(url: str) -> str:
    p = urlsplit(url)
    if p.scheme != 'https' or p.hostname not in ALLOWED or p.username or p.password or p.port not in (None, 443):
        raise ValueError('Unapproved public acquisition URL')
    return url

class CheckedRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def parse_capture(raw: bytes) -> dict:
    obj = json.loads(raw)
    if not isinstance(obj, dict) or 'error' in obj:
        raise ValueError('Agency API returned an error or unexpected JSON shape')
    return obj

def classify(obj: dict) -> str:
    if obj.get('exceededTransferLimit'):
        return 'PARTIAL_TRANSFER_LIMIT'
    if obj.get('features') == []:
        return 'EMPTY_SEARCH_NOT_ABSENCE_PROOF'
    return 'CAPTURED_NOT_APPLICABILITY_VERIFIED'

def write_once(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        f.write(raw)

def query(base: str, **params) -> str:
    return base + '?' + urlencode({'f': 'pjson', **params})

def fetch(item: tuple[str, str], out: Path) -> dict:
    key, url = item
    row = {'source_id': key, 'requested_url': check_url(url),
           'retrieved_utc': datetime.now(timezone.utc).isoformat(),
           'status': 'NOT_CAPTURED', 'local_path': None}
    try:
        req = Request(url, headers={'User-Agent': 'Tom-Street-Public-Records-Research/1.0', 'Accept': 'application/json'})
        with build_opener(CheckedRedirect()).open(req, timeout=40) as response:
            check_url(response.url)
            raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError('Response exceeds bounded capture size')
            row.update(final_url=response.url, http_status=response.status,
                       content_type=response.headers.get('Content-Type'),
                       last_modified=response.headers.get('Last-Modified'))
        obj = parse_capture(raw)
        target = out / (key + '.json')
        write_once(target, raw)
        row.update(status=classify(obj), local_path=target.relative_to(ROOT).as_posix(),
                   bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        if 'features' in obj:
            row['feature_count'] = len(obj['features'])
            row['review_attributes'] = [f.get('attributes', {}) for f in obj['features'][:20]]
        elif 'layers' in obj:
            row['review_layers'] = [{'id': f['id'], 'name': f['name']} for f in obj['layers']]
        elif 'fields' in obj:
            row['review_fields'] = [f['name'] for f in obj['fields']]
    except Exception as exc:
        row['failure'] = type(exc).__name__ + ': ' + str(exc)[:300]
    return row

def main() -> None:
    out = ROOT / '17_CURRENT_RESEARCH' / 'captures' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out.mkdir(parents=True, exist_ok=False)
    items = [
        ('SRC_STREET_APP', query(PORTAL + 'a7fd63b5d7b241af943d8bcc617d1096')),
        ('SRC_STREET_APP_DATA', query(PORTAL + 'a7fd63b5d7b241af943d8bcc617d1096/data')),
        ('SRC_STREET_WEBMAP', query(PORTAL + 'b48f751210f14be5aae454f627f6a095/data')),
        ('SRC_STREET_METADATA', query(STREETS)),
        ('SRC_TOM_STREET', query(STREETS + '/query', where="STREETNAME = 'TOM ST'", outFields='*', returnGeometry='true', outSR=4326)),
        ('SRC_TOM_FID_2006', query(STREETS + '/query', objectIds=2006, outFields='*', returnGeometry='true', outSR=4326)),
        ('SRC_STREET_SPATIAL', query(STREETS + '/query', geometry='-86.8147,30.4155', geometryType='esriGeometryPoint', inSR=4326, spatialRel='esriSpatialRelIntersects', distance=100, units='esriSRUnit_Meter', outFields='*', returnGeometry='true', outSR=4326)),
        ('SRC_GOMAPS_METADATA', query(GOMAPS)),
        ('SRC_GOMAPS_TOM', query(GOMAPS + '/5/query', where="STREETNAME = 'TOM ST'", outFields='*', returnGeometry='true', outSR=4326)),
        ('NWFWMD_ERP_METADATA', query(NWFWMD)),
        ('NWFWMD_ERP_SPATIAL', query(NWFWMD + '/query', geometry='-86.8147,30.4155', geometryType='esriGeometryPoint', inSR=4326, spatialRel='esriSpatialRelIntersects', distance=2000, units='esriSRUnit_Foot', outFields='*', returnGeometry='true', outSR=4326)),
    ]
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(lambda i: fetch(i, out), items))
    manifest = {'captured_utc': datetime.now(timezone.utc).isoformat(),
                'scope': 'Public agency GIS retrieval only; not a certification of legal ownership, engineering plans, elevation measurements or environmental permit applicability.',
                'sources': rows}
    write_once(out / 'ACQUISITION_MANIFEST.json', (json.dumps(manifest, indent=2) + '\n').encode())
    print(json.dumps(manifest, indent=2))
    if not any(r['local_path'] for r in rows):
        raise SystemExit('No agency JSON captured; inspect failure manifest')

if __name__ == '__main__':
    main()
