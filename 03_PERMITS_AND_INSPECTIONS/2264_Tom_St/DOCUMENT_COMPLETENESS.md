# Document Completeness Audit — 2264 Tom Street, Navarre, FL 32566

**Parcel (verified, Santa Rosa County Property Appraiser):** `21-2S-26-0780-0QQ00-1020`
**Parcel as stored in MGO:** `212S2607800QQ001020`
**Owner of record:** HOLIDAY BUILDERS INC
**Audit baseline date:** 2026-10-15

**October 17 supplementary note:** The original 1946 Crescent Shores recorded subdivision plat, Clerk `PLAT A/70` (document `875693`, two sheets), was subsequently acquired. The historic row below concerning unavailable deeds/plat records is retained as an October 15 snapshot, **not** the current plat acquisition status. See the [primary-source reconciliation](../../00_CONTROL/PRE_REQUEST_PRIMARY_SOURCE_REVIEW_2026-10-16.md). Later deeds linking Lot QQ to parcel `-1020`, recorded easements and site-specific approved drawings remain missing.

Status key:
`DOWNLOADED_VERIFIED` · `HISTORICAL_LEAD_UNLINKED` · `NOT_OBTAINED_FOR_SITE` · `AUTHENTICATION_REQUIRED` · `NOT_FOUND_IN_SEARCHED_SYSTEM` ·
`NOT_OFFERED_IN_PORTAL` · `REQUEST_DRAFTED` · `OFFICIAL_NO_RECORDS_RESPONSE`

---

## 1. Record-by-record status

| # | Record | Status | Evidence / explanation |
|---|---|---|---|
| 1 | **Official parcel record** | `DOWNLOADED_VERIFIED` | `02_PROPERTY_AND_PARCELS/2264_Tom_St/srcpa_property_record_21-2S-26-0780-0QQ00-1020.json` |
| 2 | **Recorded legal description** | `NOT_FOUND_IN_SEARCHED_SYSTEM` | Clerk Legal Search endpoint returns HTTP 404. Property Appraiser export does not carry legal description. Referenced in `PERMIT_DOCUMENT_INVENTORY.csv` / `DOC-SHARED-9004`. |
| 3 | **Related deeds / plat records** | `NOT_FOUND_IN_SEARCHED_SYSTEM` | Party-name search exceeds the Acclaim result limit; plat book/page range not yet determined. A **related** instrument *was* retrieved: ORB 3492/700 = 201603296 (deed, Pope Subd Lot 22 unrec) — but it belongs to **2274 Tom St**, not this lot. |
| 4 | **Building permit** | `DOWNLOADED_VERIFIED` | **`BP-2026-1621`** — New Single Family (R) — **Active** — created 2026-02-11, updated 2026-10-01. Project UID `DBFA3383-592A-4486-A392-F88065C90F95`, MGO project ID `17513349`. Files: `BP-2026-1621_project_by_uid.json`, `_inspections.json`, `_types.json`, `_contacts.json`, `_INSPECTION_HISTORY.md`. |
| 4b | Historical 1996-era permit leads | `HISTORICAL_LEAD_UNLINKED` | Four older MGO project entries bear historical site identifiers: `1996-2765-000-B-0` Mobile Home, `-E-0` Electrical, `-M-0` Mechanical, `-P-0` Plumbing. A prior mobile-home-era history is a relevant lead, but **the original legal descriptions and historical-to-current parcel continuity have not been verified**. Historic grading cannot be inferred from the permit types. |
| 5 | **Original site plan** | `NOT_OFFERED_IN_PORTAL` | MGO endpoint `ProjectFiles/get-customer-files-by-project-id/17513349` returns **0 files**. The county's customer portal exposes **no plan attachments** for this permit. |
| 6 | **Original approved grading plan** | `NOT_OFFERED_IN_PORTAL` | Same as #5. An Erosion Control/Site Grade Flat Fee was assessed. A fee alone does **not** prove any particular approved grading or erosion plan exists. |
| 7 | **Approved engineering revisions** | `NOT_OFFERED_IN_PORTAL` | No revision metadata exposed to portal users. |
| 8 | **Existing-conditions survey** | `NOT_OFFERED_IN_PORTAL` | Not exposed. |
| 9 | **Stormwater / drainage documentation** | `NOT_OFFERED_IN_PORTAL` | Not exposed as a document. **However, a county inspector described proposed work in the inspection record (not a sealed engineering determination)** — see §2. |
| 10 | **Erosion-control plan** | `NOT_OFFERED_IN_PORTAL` | Fee line does not prove a particular erosion-control plan is held. |
| 11 | **Separate driveway permit and approved plans** | `NOT_OBTAINED_FOR_SITE` | See §2 — driveway line & grade and pre-pour inspections are officially recorded with **substantive engineering comments**. No separate standalone driveway permit project was returned by address, parcel, business-name or subdivision search. |
| 12 | **Culvert / ROW drawings** | `NOT_OFFERED_IN_PORTAL` | Inspector comments describe contemplated work, **not an approved or installed culvert design**. No drawing retrieved. |
| 13 | **Inspection history** | `DOWNLOADED_VERIFIED` | **15 inspections** — `BP-2026-1621_INSPECTION_HISTORY.md`. |
| 14 | **Code enforcement, notices and correction file** | `NOT_OBTAINED_FOR_SITE` | A **building inspection** returned a windload/truss-bearing Partial Pass, but that is not the County's complete enforcement or correction file. No agency no-records certification received. |
| 15 | **Final grading documentation** | `NOT_OFFERED_IN_PORTAL` | Not exposed. |
| 16 | **Certified as-built** | `NOT_OFFERED_IN_PORTAL` | Not exposed. |
| 17 | **Certificate of Occupancy** | `NOT_FOUND_IN_SEARCHED_SYSTEM` | Project status is still **Active** as of 2026-10-01; no CO appears in the project or type records. |
| 18 | **Site-applicable environmental filings and authorization** | `NOT_OBTAINED_FOR_SITE` | Nearby NWFWMD ERP 9220-2 is an **unlinked lead**; no approved parcel intersection or permit-file coverage was demonstrated. Negative radius searches do not establish absence of permit coverage. |

## 2. Official drainage findings already recovered

From `/api/v3/cp/work-orders/17513349/inspections`:

| Date | Inspection | Result | Official comment |
|---|---|---|---|
| 2026-07-22 | **Site Grading / Drainage (pre-construction)** | Passed | *(no comment)* |
| 2026-08-06 | **Driveway Line & Grade / Consultation** | Passed | "Use 100 ft of **12 inch ADS perforated pipe with sock**; Tear out existing concrete end @ address **2260** and tie into with new pipe; Install **1st inlet box** @ roughly halfway; Tear out existing concrete end @ address **2270** and install an inlet box; call for Pre-pour inspection when ready" |
| 2026-10-01 | **Driveway Pre-Pour** | Passed | *(no comment)* |

The 2026-08-06 comment is a County inspector's **instruction for proposed roadside pipe and inlet work**, referring to structures by street addresses 2260 and 2270. It is **not** a sealed design, a determination that structures lie on neighboring private parcels, or proof the work was installed. Location, receiving outfall, easements, legal maintenance duties and hydraulic capacity remain unresolved.

## 3. Why the remaining documents cannot be obtained from the portal

MGO Connect's public customer portal returns **zero** files for this project
(`/api/v3/cp/ProjectFiles/get-customer-files-by-project-id/17513349` →
`{"data": []}`). The portal did not expose such attachments in the tested authenticated customer view. **Their existence, precise custodian, approval status and release path remain unverified.** A negative customer API response is not an agency no-records determination.
Three candidate inspection-report endpoints were tried and all returned HTTP 404.

## 4. Outstanding action for this property

`13_PUBLIC_RECORDS_REQUESTS/2264_TOM_ST_COMPLETE_PERMIT_FILE.md` — status
**DRAFTED_NOT_SUBMITTED**. Items 5–12 and 15–16 of §1 above must be requested.

**Denominator note:** this audit is based on the captured MGO site search (the active building permit and four 1996-era historical leads with unconfirmed parcel continuity) and
against the county's own document endpoint for the active permit. No claim of
completeness is made beyond what those records enumerate.