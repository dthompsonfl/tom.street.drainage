> **SUPERSEDED ACQUISITION SNAPSHOT:** Contains some early overconfident assertions about 2266 historical address use, 2000-era mobile-home attribution, what grading fees prove, and whether assigned as-builts exist. The underlying saved raw agency results are preserved; use `15_RECONCILED_DRAFTS/04_CROSS_SOURCE_RECONCILIATION.md` for governing interpretation.

# Acquisition Results — Tom Street Drainage Investigation

**Status: ACQUISITION IN PROGRESS**
Report date: 2026-10-16 (UTC)
Scope: 2264 Tom Street and 2268 Tom Street, Navarre, FL 32566, Santa Rosa County

---

## 1. Verified property identifiers

All values below come from the **Santa Rosa County Property Appraiser official
roll**, retrieved directly from the agency's own search application.

| Address | **Verified parcel ID** | MGO parcel | Owner of record | Zoning | Filing | Lot |
|---|---|---|---|---|---|---|
| **2264 Tom St** | **`21-2S-26-0780-0QQ00-1020`** | `212S2607800QQ001020` | HOLIDAY BUILDERS INC | R2M | Crescent Shores (00780) | 1020 |
| **2268 Tom St** | **`21-2S-26-0780-0QQ00-1490`** | `212S2607800QQ001490` | HOLIDAY BUILDERS INC | R2M | Crescent Shores (00780) | 1490 |
| 2265 Tom St (existing) | `21-2S-26-0780-0QQ00-1180` | `212S2607800QQ001180` | BOGART CHRISTOPHER DAVID & | R2M | Crescent Shores (00780) | 1180 |
| 2266 Tom St | *no current parcel* | — | — | — | — | — |

**Discrepancies resolved:**

1. The prior research **transposed** the two target parcels. It had recorded
   2264 as `...-1490` and 2268 as `...-1060`. Both were wrong.
2. `...-1060` is actually **2274 Tom St** (MATIG-A CEPRIANO P JR).
3. **2266 Tom St has no current parcel**, but it *was* a real historical address:
   five closed Mobile-Home-era permits exist from 1996–1998. The address was
   No County renumbering or parcel merger instrument has been obtained; this history is unresolved.
4. The MLS claim that 2268 Tom St begins at **ORB 3492 PG 700** is wrong — that
   instrument (deed 201603296, "21-2S-26 POPE SUBD LOT 22 UNREC") belongs to
   **2274 Tom St**.

**Unresolved:** recorded legal description for lots 1020 and 1490; whether a
recorded plat exists for Crescent Shores (00780).

## 2. Permit inventory

All permits below were retrieved from **MGO Connect (Santa Rosa County)** using
an authenticated customer session.

### Target sites

| Address | Permit | Type | Status | Created | Issued | Updated | Applicant |
|---|---|---|---|---|---|---|---|
| **2264 Tom St** | **`BP-2026-1621`** | New Single Family (R) | **Active** | 2026-02-11 | 2026-03-23 | 2026-10-01 | Amy Riddle, Holiday Builders INC |
| **2268 Tom St** | **`BP-2026-1612`** | New Single Family (R) | **Active** | 2026-02-11 | 2026-03-23 | 2026-10-06 | Amy Riddle, Holiday Builders INC |

- 2264 Tom St: 2,704 sq ft, project UID `DBFA3383-592A-4486-A392-F88065C90F95`, ID 17513349, **15 inspections**
- 2268 Tom St: 2,312 sq ft, project UID `677D3AE3-F348-4B97-A37C-8B0BC05CEAF7`, ID 17513025, **11 inspections**

### Prior permits on the same parcels (historical grading relevance)

`1996-2765-000-B-0 / -E-0 / -M-0 / -P-0` (2264 Tom St, 1996) and
`2000-4250-000-B-0 / -E-0 / -G-0 / -P-0` (2268 Tom St, 2000) — these historical permits are address-indexed, and parcel continuity (especially 2268) has not been verified.

### Adjacent frontage (drainage tie-in points named in county records)

| Permit | Address | Type | Outcome |
|---|---|---|---|
| `2019-7490-000-B-2` | 2260 Tom St | Driveway Connection | Closed — **2 failed inspections** |
| `2021-2524-000-B-1` | 2270 Tom St | Driveway Connection | Closed — **3 failed inspections** |
| `2015-1043-000-B-9` | 2265 Tom St | Site (R) | Closed |
| `2019-7490-000-B-9` | 2260 Tom St | Site (R) | Closed |
| `BP-2023-5719` | 2198 Tom St | Demolition (R) | Closed |

## 3. Original documents acquired

All files are official county records retrieved programmatically and validated.
Sizes and SHA-256 values below are generated from the files themselves by
`00_CONTROL/tools/validate_evidence.py` and cross-checked against
`00_CONTROL/SOURCE_REGISTER.csv` (**0 checksum mismatches**).

| Property | Permit | Document | Agency | Local file | Bytes | SHA-256 | Result |
|---|---|---|---|---|---|---|---|
| both | — | Official parcel record export, 2264 | SRC Property Appraiser | `02_PROPERTY_AND_PARCELS/2264_Tom_St/srcpa_property_record_21-2S-26-0780-0QQ00-1020.json` | see manifest | see manifest | PASS |
| both | — | Official parcel record export, 2268 | SRC Property Appraiser | `02_PROPERTY_AND_PARCELS/2268_Tom_St/srcpa_property_record_21-2S-26-0780-0QQ00-1490.json` | see manifest | see manifest | PASS |
| both | — | Full Tom Street roll, 123 records | SRC Property Appraiser | `02_PROPERTY_AND_PARCELS/RAW_HTTP/srcpa_property_query_street_TOM_NAVARRE.json` | see manifest | see manifest | PASS |
| — | — | ORB 3492/700 search result set | SRC Clerk (AcclaimWeb) | `00_CONTROL/SYSTEM_RAW/acclaim_bookpage_3492_700_20261015T235902Z.html` | 43776 | `01791b2f…b11515` | PASS |
| 2264 | `BP-2026-1621` | Permit record (full detail) | SRC Development Services | `03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_project_by_uid.json` | see manifest | see manifest | PASS |
| 2264 | `BP-2026-1621` | Inspection history, 15 records | SRC Development Services | `03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_inspections.json` | see manifest | see manifest | PASS |
| 2264 | `BP-2026-1621` | Task/requirement list | SRC Development Services | `03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_requirements.json` | 53307 | see manifest | PASS |
| 2268 | `BP-2026-1612` | Permit record (full detail) | SRC Development Services | `03_PERMITS_AND_INSPECTIONS/2268_Tom_St/BP-2026-1612_project_by_uid.json` | see manifest | see manifest | PASS |
| 2268 | `BP-2026-1612` | Inspection history, 11 records | SRC Development Services | `03_PERMITS_AND_INSPECTIONS/2268_Tom_St/BP-2026-1612_inspections.json` | see manifest | see manifest | PASS |
| 2268 | `BP-2026-1612` | Task/requirement list | SRC Development Services | `03_PERMITS_AND_INSPECTIONS/2268_Tom_St/BP-2026-1612_requirements.json` | 51805 | see manifest | PASS |
| both | — | ERP record, Hadleigh Hills Phase 2 | NWFWMD | `09_ENVIRONMENTAL_PERMITS/SYSTEM_RAW/erp_nearest_permits_tom_street.json` | 3318 | `383baf5f…78567` | PASS |
| — | — | Tom Street permit sweep, 885 projects | SRC Development Services | `03_PERMITS_AND_INSPECTIONS/SYSTEM_RAW/mgo_sweep_results.json` | see manifest | see manifest | PASS |
| — | `2019-7490-000-B-2`, `2021-2524-000-B-1`, … | Neighbouring driveway/site permits | SRC Development Services | `04_ENGINEERING_AND_DRAINAGE/Tom_Street_Shared_System/*.json` | see manifest | see manifest | PASS |

Complete byte-exact sizes and full SHA-256 digests for every one of the **89**
validated files: `00_CONTROL/EVIDENCE_MANIFEST.csv`.

## 4. Missing documents

**Definitively established: the MGO Connect customer portal exposes ZERO
document attachments for either permit.** The endpoint
`/api/v3/cp/ProjectFiles/get-customer-files-by-project-id/{id}` returns
`{"data":[]}` for both. Three candidate inspection-report endpoints returned
HTTP 404. This is not an authentication problem — it is the portal's design.

| Missing document | Property | Status | Action |
|---|---|---|---|
| Approved site plan / plot plan | both | `NOT_OFFERED_IN_PORTAL` | Chapter 119 request |
| Approved grading plan + all revisions | both | `NOT_OFFERED_IN_PORTAL` | Chapter 119 request |
| Existing-conditions / topographic survey | both | `NOT_OFFERED_IN_PORTAL` | Chapter 119 request |
| Erosion & sediment control plan | both | `NOT_OFFERED_IN_PORTAL` | Chapter 119 request — the permit carries an erosion/site grade fee; a fee cannot establish that any particular plan was filed or approved |
| Driveway plan and culvert details | both | `NOT_OFFERED_IN_PORTAL` | Chapter 119 request |
| **Certified Drainage as Built** | both | `AUTHENTICATION_REQUIRED` | County requirement still `Assigned` on both permits — document not yet submitted |
| Certificate of Occupancy | both | `NOT_FOUND_IN_SEARCHED_SYSTEM` | `Issue CO` still `Assigned`; both permits `Active` |
| Recorded legal description | both | `NOT_FOUND_IN_SEARCHED_SYSTEM` | Clerk Legal Search HTTP 404 |
| Recorded plat / drainage easement | both | `NOT_FOUND_IN_SEARCHED_SYSTEM` | Plat book range unknown |
| Subdivision drainage master plan, ROW/culvert drawings | shared | `AUTHENTICATION_REQUIRED` | Chapter 119 request to Engineering/Public Works |
| NWFWMD ERP 9220-2 permit file | shared | `REQUEST_DRAFTED` | NWFWMD request |

Full detail: `00_CONTROL/PERMIT_DOCUMENT_INVENTORY.csv` (43 rows).

## 5. Government systems searched

| System | Search terms | Date | Outcome | Limitation |
|---|---|---|---|---|
| SRC Property Appraiser | `street=TOM city=NAVARRE`; `parcelId=` ×3 | 2026-10-15 | **123 records; both parcels exported** | Export lacks legal description, building card, sales history |
| SRC Property Appraiser | `/property`, `/property/print/selected` | 2026-10-15 | No parcel-detail route exists; print returns a label only | — |
| SRC Clerk (AcclaimWeb) | Book/Page **3492 / 700** | 2026-10-15 | **28 documents; instrument 201603296 retrieved** | — |
| SRC Clerk (AcclaimWeb) | Name: `HOLIDAY BUILDERS`, `Builders, Holiday` | 2026-10-15 | "results exceeded maximum limit"; date narrowing suppressed grid | Party-name index unusable at this scope |
| SRC Clerk (AcclaimWeb) | Legal Search route | 2026-10-15 | **HTTP 404** | Endpoint broken |
| MGO Connect | 6 public routes as Guest | 2026-10-15 | All redirect to `/cp/login` | **Resolved** by user authentication |
| MGO Connect (authenticated) | `2264 TOM ST`, `2268 TOM ST`, `2266 TOM ST`, `2265/2267/2270/2274 TOM ST`, parcels ×4, `BUSINESSNAME` ×3, `SUBDIVISION=CRESCENT SHORES` | 2026-10-15/16 | **885 unique projects enumerated; both target permits located and fully extracted** | Portal exposes no document files |
| FDEP + 5 WMD ERP ArcGIS REST | spatial query 150/500/1000/2000 ft ×3 parcels | 2026-10-15 | **0 ERPs ≤150 ft; 1 ERP ≤2000 ft (NWFWMD 9220-2)** | Permit documents not public |
| NWFWMD ERP | `SITE_NM LIKE '%Hadleigh%'/'%Tom%'/'%Navarre%'/'%Crescent%'` | 2026-10-15 | 1 Hadleigh Hills record; **0 "Crescent"** | — |
| County StoryMaps 2020–2026 | "Crescent Shores", "Hadleigh Hills", "Tom St", "Pope" | 2026-10-15 | **Zero hits in all 7 maps** | — |

## 6. Records requests prepared

All are **`DRAFTED_NOT_SUBMITTED`** — nothing has been sent.

1. `13_PUBLIC_RECORDS_REQUESTS/2264_TOM_ST_COMPLETE_PERMIT_FILE.md`
2. `13_PUBLIC_RECORDS_REQUESTS/2268_TOM_ST_COMPLETE_PERMIT_FILE.md`
3. `13_PUBLIC_RECORDS_REQUESTS/SHARED_TOM_STREET_ROW_AND_DRAINAGE_PLANS.md`
4. `13_PUBLIC_RECORDS_REQUESTS/CLERK_DEEDS_PLATS_EASEMENTS.md`
5. `13_PUBLIC_RECORDS_REQUESTS/NWFWMD_ERP_9220-2_FILE.md`

## 7. Validation results

```
python3 00_CONTROL/tools/validate_evidence.py
  files=89  pass=89  fail=0

SOURCE_REGISTER.csv checksum reconciliation:
  34 paths checked, 0 mismatches
```

Every file exists, is non-empty, has an identified MIME type, and — for
HTML/JSON — has been parsed and content-checked. No entry is marked verified
that is not backed by a real file on disk with a computed SHA-256.

## 8. Outstanding action — highest priority

**Obtain the approved grading plans, topographic surveys and — above all — the
"Certified Drainage as Built" documents for `BP-2026-1621` (2264 Tom St) and
`BP-2026-1612` (2268 Tom St).**

This is the single highest-value missing item because the county's own task list
shows the **"Certified Drainage as Built" requirement is still `Assigned` on
both permits** — meaning neither lot has an accepted as-built drainage record,
and both "Site Grading / Drainage (mid- and final-construction)" inspections
remain **Not Complete**. These documents are held by Development Services and
are not released through any public portal.

### Remaining acquisition queue

1. Submit the five drafted Chapter 119 requests (needs your approval).
2. Clerk: retry plat/deed retrieval using plat book ranges and date windows
   rather than the unusable party-name index.
3. Retrieve the NWFWMD ERP 9220-2 file (Hadleigh Hills Phase 2) — the only ERP
   within 2,000 ft and the most likely source of the original drainage design.
4. Retrieve Tom Street roadway profiles, crown/shoulder elevations and swale
   sections from Public Works.

---

### What is deliberately *not* claimed

No claim is made that all county-held records have been obtained. The portal
work is exhausted — six anonymous routes plus a full authenticated sweep, with
the county's own document endpoint returning empty for both permits. The
remaining items require agency production under Chapter 119.