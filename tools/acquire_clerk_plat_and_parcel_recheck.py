#!/usr/bin/env python3
"""Public Clerk plat search and dated official Property Appraiser cross-check.

No authenticated portal state, cookie, raw HTML with personal details, or
unverified private deed is committed. A plat PDF is saved only when the Clerk
guest index positively identifies the document as a plat relevant to Crescent
Shores. Otherwise report the exact source-access gap.
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from pypdf import PdfReader
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"02_PROPERTY_AND_PARCELS/PRE_REQUEST_OCT16_PRIMARY_LOOKUPS"
OUT.mkdir(parents=True,exist_ok=True)
SYS=ROOT/"00_CONTROL/tools"
sys.path.insert(0,str(SYS))
from acclaim_search import boot, open_search, set_val, submit, controls  # noqa:E402

PARCELS={
"2264_TOM_ST":"21-2S-26-0780-0QQ00-1020",
"2268_TOM_ST":"21-2S-26-0780-0QQ00-1490",
"2265_TOM_ST":"21-2S-26-0780-0QQ00-1180",
"2274_TOM_ST_DISPUTED":"21-2S-26-0780-0QQ00-1060"
}
EXPECTED_STREETS={"2264_TOM_ST":"2264","2268_TOM_ST":"2268","2265_TOM_ST":"2265","2274_TOM_ST_DISPUTED":"2274"}
PA="https://search.srcpa.gov"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"

def store(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_bytes()!=data:
        raise RuntimeError("No silent overwriting of official baseline: "+str(path))
    if not path.exists():path.write_bytes(data)
    return {"path":path.relative_to(ROOT).as_posix(),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}

def pa_query(session,pid):
    base={
        "quickSearchParam":"","useQuickSearch":"false","parameterMatch":"intersect",
        "name":"","street":"","unit":"","city":"","zip":"","useRange":"false",
        "parcelId":pid,"phase":"","parcelGroup":"","xfCode":"","landUse":"",
        "zoning":"","acreageFrom":"","acreageTo":"","buildingUse":"",
        "structuralElement":"","yearBuiltFrom":"","yearBuiltTo":"",
        "heatedSquareFootageFrom":"","heatedSquareFootageTo":"","action":"Search"
    }
    response=session.post(PA+"/property/query",data=base,timeout=50)
    response.raise_for_status()
    obj=response.json()
    if not isinstance(obj,dict) or "results" not in obj:
        raise RuntimeError("Property query did not return result object")
    return response.content,obj

def property_appraiser():
    report={"authority":"Santa Rosa County Property Appraiser","status":"NOT_OBTAINED","results":[]}
    session=requests.Session(); session.headers.update({"User-Agent":UA})
    try:session.get(PA+"/property",timeout=40).raise_for_status()
    except Exception as exc:report["session_note"]=type(exc).__name__+": "+str(exc)[:150]
    for slug,pid in PARCELS.items():
        entry={"requested_parcel":pid,"label":slug,"status":"NOT_OBTAINED"}
        try:
            b,obj=pa_query(session,pid)
            matches=[x for x in obj["results"] if (x.get("parcelNumber") or x.get("parcelID") or x.get("parcelId"))==pid]
            if not matches:
                # The original API indexed parcelKey instead; print safe schema only.
                entry["status"]="PARCEL_NOT_UNIQUELY_MATCHED_IN_RETURNED_INDEX"
                entry["result_count"]=len(obj["results"])
                entry["returned_field_names"]=[list(x.keys()) for x in obj["results"][:1]]
            else:
                key=matches[0].get("parcelKey")
                if key is None:raise RuntimeError("Validated parcel lacks export key")
                index=store(OUT/f"ORIGINAL_SRCPA_QUERY_{slug}.json",b)
                export=session.post(PA+"/property/export/selected",
                                    data=[("parcel",str(key)),("format","json")],timeout=50)
                export.raise_for_status()
                records=export.json()
                if not isinstance(records,list) or len(records)!=1 or records[0].get("parcelNumber")!=pid:
                    raise RuntimeError("Official export does not match requested parcel")
                situs=(records[0].get("situsAddress1") or "").upper()
                if not situs.startswith(EXPECTED_STREETS[slug]+" TOM"):
                    entry["status"]="NEW_OFFICIAL_SITUS_DIFFERS_REQUIRES_REVIEW"
                else:entry["status"]="OFFICIAL_PARCEL_AND_SITUS_MATCH_AT_CAPTURE"
                entry.update({"query":index,
                              "export":store(OUT/f"ORIGINAL_SRCPA_EXPORT_{slug}.json",export.content),
                              "situs":situs,"owner_role": "Agency owner name is in saved original; no inferred relationship"})
        except Exception as exc:
            entry["status"]="PUBLIC_ENDPOINT_ACCESS_OR_VALIDATION_FAILED"
            entry["failure"]=type(exc).__name__+": "+str(exc)[:260]
        report["results"].append(entry)
    report["status"]="PARCEL_REFRESH_PARTIAL" if any("MATCH_AT_CAPTURE" in x["status"] for x in report["results"]) else "PARCEL_REFRESH_UNAVAILABLE"
    return report

def srcpa_plat_probe():
    record={"status":"NOT_OBTAINED","source":PA+"/plat","search_phrase":"CRESCENT SHORES"}
    s=requests.Session();s.headers["User-Agent"]=UA
    try:
        r=s.get(PA+"/plat",timeout=40);r.raise_for_status()
        from bs4 import BeautifulSoup
        doc=BeautifulSoup(r.text,"html.parser")
        forms=doc.select("form")
        record["page_status"]="HTML_ACCESSIBLE"
        record["candidate_forms"]=[{
            "action":f.get("action"),"method":f.get("method"),
            "input_names":sorted({e.get("name") for e in f.select("input,select") if e.get("name")})
        } for f in forms]
        record["status"]="FORM_SCHEMA_CAPTURED_EXACT_PLAT_QUERY_NOT_CONFIRMED"
        # Avoid making unsupported POST assumptions about a proprietary search route.
    except Exception as exc:
        record["status"]="PUBLIC_PLAT_FORM_UNAVAILABLE"
        record["failure"]=type(exc).__name__+": "+str(exc)[:260]
    return record

def safe_excerpt(s):
    # Only expose the official catalog hits and path hints; never archive a
    # raw Clerk page containing unrelated residents' names.
    s=re.sub(r"\s+"," ",s)
    out=[]
    for term in ["CRESCENT SHORES","Plat Book","DocumentPdfAllPages","PLAT"]:
        match=re.search(re.escape(term),s,re.I)
        if match:
            out.append({"term":term,"found":True})
    return out

def clerk_search():
    report={"authority":"Santa Rosa County Clerk AcclaimWeb","status":"NOT_OBTAINED","queries":[]}
    with sync_playwright() as pw:
        b,ctx,page=boot(pw)
        try:
            for page_no in ("70","70A"):
                record={"book_type_requested":"PLAT","book_number_requested":"A","page_requested":page_no,"status":"NOT_OBTAINED"}
                try:
                    actual=open_search(page,"search/SearchTypeBookPage")
                    record["landed_url"]=actual.split("?")[0]
                    fields=controls(page)
                    record["form_field_names"]=[{"id":i.get("id"),"name":i.get("name"),"tag":i.get("tag")} for i in fields]
                    select_status=[]
                    for e in page.query_selector_all("select"):
                        try:
                            opts=[(o.get_attribute("value") or "", (o.inner_text() or "").strip()) for o in e.query_selector_all("option")]
                            candidates=[(v,t) for v,t in opts if "plat" in t.lower() or t.strip().upper()=="P"]
                            if candidates:
                                e.select_option(value=candidates[0][0])
                                select_status.append({"selected":"PLAT", "field_id":e.get_attribute("id")})
                        except Exception as exc: select_status.append({"error":type(exc).__name__})
                    if not select_status:
                        try:
                            page.locator("button[onclick*='ShowTypes']").click()
                            check=page.locator("#BookTypeDiv input[name='BookTypeInfoCheckBox'][value='3']").first
                            check.check(force=True)
                            page.locator("#BookTypeDiv input[value='Done']").first.click(force=True)
                            select_status.append({"selected":"PLAT - Plats/Maps",
                                                  "field":"BookTypeInfoCheckBox", "value":"3",
                                                  "display":page.locator("#BookTypesDisplay").input_value()})
                        except Exception as exc:
                            record["book_type_widget_error"]=type(exc).__name__+": "+str(exc)[:180]
                    record["selected_book_type_options"]=select_status
                    record["book_field_accepted"]=set_val(page,"BookNumber","A")
                    record["page_field_accepted"]=set_val(page,"PageNumber",page_no)
                    if not record["book_field_accepted"] or not record["page_field_accepted"]:
                        record["status"]="GUEST_FORM_FIELDS_UNSUPPORTED"
                    elif not select_status:
                        record["status"]="PLAT_BOOK_TYPE_CONTROL_NOT_VERIFIED"
                    else:
                        submit(page);page.wait_for_timeout(4000)
                        html=page.content(); text=page.inner_text("body")
                        record["result_book_terms"]=safe_excerpt(text)
                        rows=[]
                        for tr in page.query_selector_all(".t-grid-content tbody tr"):
                            tds=tr.query_selector_all("td")
                            if len(tds)<10:continue
                            cells=[(v.inner_text() or "").strip() for v in tds]
                            check=tr.query_selector("input[name='checkedRecords']")
                            candidate_id=(check.get_attribute("value") or "") if check else ""
                            if not candidate_id.isdigit():continue
                            rows.append({"book_type":cells[7],"book_page":cells[8],
                                         "document_type":cells[10] if len(cells)>10 else "",
                                         "legal_region":cells[-1],"document_id":candidate_id})
                        record["safe_index_rows"]=rows[:45]
                        record["safe_index_count_visible"]=len(rows)
                        matching=[r for r in rows if r["book_type"].upper()=="PLAT"
                                  and r["book_page"].upper().replace(" ","")==f"A/{page_no}".upper()
                                  and ("PLAT" in r["document_type"].upper() or
                                       "MAP" in r["document_type"].upper())]
                        record["exact_plat_index_matches"]=matching
                        for match in matching[:2]:
                            doc_id=match["document_id"]
                            url=f"https://acclaim.srccol.com/AcclaimWeb/Image/DocumentPdfAllPages/{doc_id}"
                            try:
                                res=requests.get(url,timeout=60,headers={"User-Agent":UA})
                                res.raise_for_status()
                                if not res.content.startswith(b"%PDF-") or len(res.content)>24_000_000:
                                    raise RuntimeError("Result was not a bounded official PDF")
                                pdf=PdfReader(BytesIO(res.content))
                                if not 1<=len(pdf.pages)<=25:
                                    raise RuntimeError("Unexpected document page count")
                                content="\n".join((p.extract_text() or "") for p in pdf.pages)
                                if re.search(r"\b\d{3}[- ]\d{2}[- ]\d{4}\b|social security number|bank account|date of birth",content,re.I):
                                    raise RuntimeError("Document has sensitive information: withhold from public repo")
                                # Plat is a published land survey/record, not a private resident photograph or deed.
                                filename=f"ORIGINAL_CLERK_PLAT_BOOK_A_PAGE_{page_no}.pdf"
                                match["original"]=store(OUT/filename,res.content)
                                match["original"].update({"url":url,"pages":len(pdf.pages),
                                  "release":"PUBLIC_CLERK_PLAT_SUBJECT_TO_HUMAN_EXHIBIT_REVIEW"})
                                match["original_acquisition_status"]="SOURCE_PDF_ARCHIVED_EXACT_PLAT_INDEX_MATCH"
                            except Exception as exc:
                                match["original_acquisition_status"]="PDF_DOWNLOAD_OR_PRIVACY_GATE_FAILED"
                                match["original_failure"]=type(exc).__name__+": "+str(exc)[:190]
                        record["status"]=("EXACT_PLAT_INDEX_MATCH_FOUND" if matching
                                         else "NO_EXACT_PLAT_RECORD_FOUND_IN_GUEST_VISIBLE_PAGE")
                except Exception as exc:
                    record["status"]="CLERK_GUEST_SEARCH_FAILED"
                    record["failure"]=type(exc).__name__+": "+str(exc)[:260]
                report["queries"].append(record)
        finally:
            ctx.close();b.close()
    report["status"]="GUEST_PLAT_SEARCH_PERFORMED"
    return report

def known_official_document_probe():
    """Hash/summarize the known Clerk-hosted instruments without republishing
    third-party signatures/identity-bearing deed images on this public repo."""
    report=[]
    for label,id_ in [("OR_BOOK_3653_PAGE_976",3266090),("OR_BOOK_718_PAGE_289",7838)]:
        url=f"https://acclaim.srccol.com/AcclaimWeb/Image/DocumentPdfAllPages/{id_}"
        row={"source":url,"record":label,"status":"NOT_OBTAINED"}
        try:
            r=requests.get(url,timeout=55,headers={"User-Agent":UA})
            r.raise_for_status()
            if not r.content.startswith(b"%PDF-") or len(r.content)>18_000_000:
                raise RuntimeError("Not an official PDF document within size cap")
            pdf=PdfReader(BytesIO(r.content))
            if not 1<=len(pdf.pages)<=30:raise RuntimeError("Implausible recorded instrument page count")
            row.update({"status":"OFFICIAL_PDF_BYTES_RETRIEVED_PRIVACY_REVIEW_REQUIRED",
                        "source_bytes":len(r.content),"sha256":hashlib.sha256(r.content).hexdigest(),
                        "page_count":len(pdf.pages),"contains_image_based_pages":any(
                         not (p.extract_text() or "").strip() for p in pdf.pages)})
            # do not add original sensitive signatures, addresses or deed document
            # to the public repository until a human release review approves it
        except Exception as exc:
            row["status"]="CLERK_PDF_NOT_RETRIEVABLE_AT_PUBLIC_ENDPOINT"
            row["failure"]=type(exc).__name__+": "+str(exc)[:240]
        report.append(row)
    return report

def main():
    results={
        "captured_utc":datetime.now(timezone.utc).isoformat(),
        "purpose":"Limited pre-request official public parcel/plat and original Clerk URL retrieval",
        "privacy":"Clerk deed originals not committed to public repository without signature/third-party privacy review",
    }
    for label,method in [
        ("srcpa_parcels",property_appraiser),
        ("srcpa_plat_search",srcpa_plat_probe),
        ("clerk_known_document_probes",known_official_document_probe),
        ("clerk_plat_search",clerk_search),
    ]:
        try:results[label]=method()
        except Exception as exc:results[label]={"status":"BLOCKED","failure":type(exc).__name__+": "+str(exc)[:260]}
    path=OUT/"ACQUISITION_REPORT.json"
    path.write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"report":str(path.relative_to(ROOT)),
      "pa":results["srcpa_parcels"].get("status"),"plat":results["clerk_plat_search"].get("status"),
      "clerk_pdf":[r["status"] for r in results["clerk_known_document_probes"]]},indent=2))

if __name__=="__main__":
    main()
