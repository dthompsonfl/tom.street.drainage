#!/usr/bin/env python3
"""Bounded public-index investigation of Crescent Shores Lot QQ title leads.

This collects public Clerk *index metadata*, not raw documents, signatures,
owners' mailing addresses, portal HTML, cookies or credentials. Indexed deeds
are candidates only until their legal description and chain are verified.
The separate SRCPA plat search probes the real published POST form.
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import requests
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"00_CONTROL/tools"))
from acclaim_search import boot, open_search, set_val, submit
OUT=ROOT/"02_PROPERTY_AND_PARCELS/CLERK_LOT_QQ_DISCOVERY_2026-10-17"
BASE="https://acclaim.srccol.com/AcclaimWeb/"
REPORT=OUT/"INDEX_DISCOVERY_REPORT.json"
HINTS=("CRESCENT SHORES","POPE SUBD","LOT QQ","TOM ST","21-2S-26","0QQ00","0QQ55")
SEARCHES=[
 ("legal", "CRESCENT SHORES"),
 ("legal", "POPE SUBD"),
 ("legal", "LOT QQ"),
 ("legal", "21-2S-26"),
 ("name", "HOLIDAY BUILDERS INC"),
]
MAX_PAGES=4

def utc():return datetime.now(timezone.utc).isoformat()

def safe(v):
    return re.sub(r"\s+"," ",str(v or "")).strip()[:200]

def match_hint(text):
    t=safe(text).upper()
    return any(h in t for h in HINTS)

def get_rows(pg):
    out=[]
    for tr in pg.query_selector_all(".t-grid-content tbody tr"):
        cells=[safe(c.inner_text()) for c in tr.query_selector_all("td")]
        if len(cells)<11:continue
        cb=tr.query_selector("input[name='checkedRecords']")
        docid=(cb.get_attribute("value") or "") if cb else ""
        if not docid.isdigit():continue
        # Store only land-description and document metadata, not party identities.
        legal=cells[-1]
        out.append({
            "clerk_index_document_id":docid,
            "recorded_date":cells[6],
            "record_book_type":cells[7],
            "book_page":cells[8],
            "instrument_number":cells[9],
            "document_type":cells[10],
            "legal_index_excerpt":legal,
            "has_target_related_legal_terms":match_hint(legal),
        })
    return out

def book_index(pg, kind, phrase):
    url="search/SearchTypeComments" if kind=="legal" else "search/SearchTypeName"
    r={"kind":kind,"query":phrase,"started_utc":utc(),"status":"NOT_SEARCHED","relevant_index_rows":[]}
    try:
        landing=open_search(pg,url)
        r["landed_url"]=landing.split("?")[0]
        fields=[]
        schema=[]
        for element in pg.query_selector_all("form input, form textarea"):
            try:
                typ=(element.get_attribute("type") or "text").lower()
                ident={"id":element.get_attribute("id"),
                       "name":element.get_attribute("name"),"type":typ,
                       "visible":element.is_visible(),"readonly":element.is_read_only()}
                if typ in ("text","search","textarea"):
                    schema.append(ident)
                    if ident["visible"] and not element.is_disabled() and not ident["readonly"]:
                        fields.append({"id":ident["id"],"name":ident["name"]})
            except Exception:pass
        r["search_form_schema"]=schema[:30]
        r["visible_text_form_fields"]=fields
        name_fields=("SearchOnName","SearchComments","SearchOnComment","SearchOnComments","Comments","SearchTerm","LegalDescription")
        identified=next((s for s in name_fields if any(s==v.get("name") or s==v.get("id") for v in fields)),None)
        # An official form can have only one visible enabled search field. Do
        # not fill an unrecognized multi-field form by guessing.
        if identified:
            if not set_val(pg,identified,phrase):
                raise RuntimeError("Unable to fill identified legal/name form control")
            r["filled_form_control"]=identified
        elif len(fields)==1:
            candidates=pg.locator("form input[type='text'], form input[type='search'], form textarea")
            for i in range(candidates.count()):
                el=candidates.nth(i)
                if el.is_visible() and not el.is_disabled() and not el.is_read_only():
                    el.fill(phrase)
                    break
            r["filled_form_control"]=fields[0].get("name") or fields[0].get("id")
        else:
            r["status"]="FORM_FIELDS_UNMAPPED_NEEDS_REVIEW"
            return r
        submit(pg)
        pg.wait_for_timeout(4000)
        body=pg.inner_text("body")
        if re.search(r"results exceeded.*maximum limit",body,re.I):
            r["status"]="RESULTS_TOO_MANY_NO_COMPLETENESS"
        elif re.search(r"no records|no results|0 results",body,re.I):
            r["status"]="ZERO_PUBLIC_SEARCH_ROWS_NOT_TITLE_ABSENCE"
        else:
            r["status"]="INDEX_SEARCH_PERFORMED_SCOPE_LIMITED"
        total=re.search(r"Displaying items\s+([\d,\-]+)\s+of\s+([\d,]+)",body)
        r["reported_results"]=int(total.group(2).replace(",","")) if total else None
        r["displayed_range"]=total.group(1) if total else None
        seen=set()
        for page in range(MAX_PAGES):
            for item in get_rows(pg):
                key=item["clerk_index_document_id"]
                if key in seen:continue
                seen.add(key)
                if item["has_target_related_legal_terms"]:
                    r["relevant_index_rows"].append(item)
            if page==MAX_PAGES-1:break
            nxt=pg.locator(".t-grid-pager a:has(.t-arrow-next), .t-grid-pager a:has-text('next')")
            try:
                if nxt.count()==0 or not nxt.first.is_visible() or "t-state-disabled" in (nxt.first.get_attribute("class") or ""):
                    break
                nxt.first.click(timeout=6000)
                pg.wait_for_timeout(1200)
            except Exception:break
        r["unique_displayed_document_count"]=len(seen)
        r["pages_cap"]=MAX_PAGES
        if r["reported_results"] is not None and r["reported_results"]>len(seen):
            r["incomplete_public_pagination"]=True
        r["finished_utc"]=utc()
    except Exception as exc:
        r["status"]="PUBLIC_PORTAL_SEARCH_ERROR"
        r["error"]=type(exc).__name__+": "+str(exc)[:220]
    return r

def plat_lookup():
    res={"source_url":"https://search.srcpa.gov/plat","status":"NOT_SEARCHED","queries":[]}
    sess=requests.Session()
    sess.headers["User-Agent"]="TomStreetPublicEvidence/2.0"
    try:
        page=sess.get("https://search.srcpa.gov/plat",timeout=45)
        page.raise_for_status()
        from bs4 import BeautifulSoup
        doc=BeautifulSoup(page.text,"html.parser")
        form=doc.select_one("form[action='/plat/query']")
        if not form or not form.select_one("[name='phase']"):
            res["status"]="FORM_NOT_VERIFIED"
            return res
        for phrase in ("CRESCENT SHORES","00780"):
            q={"query":phrase,"endpoint":"https://search.srcpa.gov/plat/query","status":"NOT_SEARCHED"}
            try:
                response=sess.post(q["endpoint"],data={"phase":phrase},timeout=45,
                                   headers={"Referer":"https://search.srcpa.gov/plat"})
                response.raise_for_status()
                q["content_type"]=response.headers.get("Content-Type","")[:70]
                data=response.json()
                if not isinstance(data,dict):raise RuntimeError("not JSON object")
                q["response_field_names"]=sorted(data.keys())
                body=json.dumps(data,ensure_ascii=True)
                q["mentions_target"]=("CRESCENT SHORES" in body.upper() or "00780" in body)
                q["results_count"]=len(data.get("results",[])) if isinstance(data.get("results"),list) else None
                if q["results_count"]==1 and phrase=="00780":
                    # Official filtered subdivision-code query; only a single
                    # target response is preserved as primary source bytes.
                    entry=data["results"][0]
                    q["result_field_names"]=sorted(entry.keys()) if isinstance(entry,dict) else []
                    original=OUT/"ORIGINAL_SRCPA_PLAT_QUERY_00780.json"
                    body=resp.content
                    if original.exists() and original.read_bytes()!=body:
                        raise RuntimeError("Previous subdivision source changed; use dated snapshot")
                    if not original.exists():original.write_bytes(body)
                    q["original_source"]={"path":original.relative_to(ROOT).as_posix(),
                        "bytes":len(body),"sha256":hashlib.sha256(body).hexdigest(),
                        "official_url":q["endpoint"]}
                    q["status"]="OFFICIAL_TARGET_SUBDIVISION_INDEX_SAVED_NEEDS_IDENTITY_REVIEW"
                else:
                    q["status"]="PUBLIC_PLAT_INDEX_RESPONSE_RETRIEVED_NEEDS_SEMANTIC_REVIEW"
            except Exception as exc:
                q["status"]="PUBLIC_PLAT_QUERY_FAILED"
                q["error"]=type(exc).__name__+": "+str(exc)[:160]
            res["queries"].append(q)
        res["status"]="TWO_TARGETED_PA_PLAT_QUERIES_ATTEMPTED"
    except Exception as exc:
        res["status"]="PA_PLAT_FORM_FAILED"
        res["error"]=type(exc).__name__+": "+str(exc)[:220]
    return res

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    result={"captured_utc":utc(),"scope":"public Clerk guest search index / Property Appraiser subdivision-index probes",
            "privacy":"No deed original, owner personal info, raw portal HTML, cookie or resident media in this derived index",
            "completeness":"BOUNDED_DISCOVERY_NOT_COMPLETE_RECORDS_CUSTODIAN_SEARCH",
            "searches":[]}
    with sync_playwright() as pw:
        browser,context,page=boot(pw)
        try:
            for kind,query in SEARCHES:
                result["searches"].append(book_index(page,kind,query))
                time.sleep(0.5)
        finally:
            context.close();browser.close()
    result["srpa_plat"]=plat_lookup()
    serialized=(json.dumps(result,indent=2,ensure_ascii=True)+"\n").encode()
    if REPORT.exists() and REPORT.read_bytes()!=serialized:
        stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path=OUT/("INDEX_DISCOVERY_REPORT_"+stamp+".json")
    else:path=REPORT
    path.write_bytes(serialized)
    print(json.dumps({"report":str(path.relative_to(ROOT)),
       "queries":[{"phrase":r["query"],"status":r["status"],
         "relevant_rows":len(r["relevant_index_rows"]),
         "reported_results":r.get("reported_results"),
         "form_fields":r.get("visible_text_form_fields",[])} for r in result["searches"]],
       "plat_query_status":result["srpa_plat"]["status"]},indent=2))

if __name__=="__main__":main()
