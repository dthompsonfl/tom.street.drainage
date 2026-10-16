# Document Completeness Audit — 2264 Tom Street, Navarre, FL 32566

**Parcel (verified, Santa Rosa County Property Appraiser):** `21-2S-26-0780-0QQ00-1020`
**Parcel as stored in MGO:** `212S2607800QQ001020`
**Owner of record:** HOLIDAY BUILDERS INC
**Audit date:** 2026-10-15

Status key:
`DOWNLOADED_VERIFIED` · `AUTHENTICATION_REQUIRED` · `NOT_FOUND_IN_SEARCHED_SYSTEM` ·
`NOT_OFFERED_IN_PORTAL` · `REQUEST_DRAFTED` · `OFFICIAL_NO_RECORDS_RESPONSE`

---

## 1. Record-by-record status

| # | Record | Status | Evidence / explanation |
|---|---|---|---|
| 1 | **Official parcel record** | `DOWNLOADED_VERIFIED` | `02_PROPERTY_AND_PARCELS/2264_Tom_St/srcpa_property_record_21-2S-26-0780-0QQ00-1020.json` |
| 2 | **Recorded legal description** | `NOT_FOUND_IN_SEARCHED_SYSTEM` | Clerk Legal Search endpoint returns HTTP 404. Property Appraiser export does not carry legal description. Referenced in `PERMIT_DOCUMENT_INVENTORY.csv` / `DOC-SHARED-9004`. |
| 3 | **Related deeds / plat records** | `NOT_FOUND_IN_SEARCHED_SYSTEM` | Party-name search exceeds the Acclaim result limit; plat book/page range not yet determined. A **related** instrument *was* retrieved: ORB 3492/700 = 201603296 (deed, Pope Subd Lot 22 unrec) — but it belongs to **2274 Tom St**, not this lot. |
| 4 | **Building permit** | `DOWNLOADED_VERIFIED` | **`BP-2026-1621`** — New Single Family (R) — **Active** — created 2026-02-11, updated 2026-10-01. Project UID `DBFA3383-592A-4486-A392-F88065C90F95`, MGO project ID `17513349`. Files: `BP-2026-1621_project_by_uid.json`, `_inspections.json`, `_types.json`, `_contacts.json`, `_INSPECTION_HISTORY.md`. |
| 4b | Prior-permit history on this lot | `DOWNLOADED_VERIFIED` | 4 older projects, all 1996: `1996-2765-000-B-0` Mobile Home, `-E-0` Electrical, `-M-0` Mechanical, `-P-0` Plumbing. **This lot previously carried a mobile home** — relevant to historic grading. |
| 5 | **Original site plan** | `NOT_OFFERED_IN_PORTAL` | MGO endpoint `ProjectFiles/get-customer-files-by-project-id/17513349` returns **0 files**. The county's customer portal exposes **no plan attachments** for this permit. |
| 6 | **Original approved grading plan** | `NOT_OFFERED_IN_PORTAL` | Same as #5. An Erosion Control/Site Grade Flat Fee was assessed. A fee alone does **not** prove any particular approved grading or erosion plan exists. |
| 7 | **Approved engineering revisions** | `NOT_OFFERED_IN_PORTAL` | No revision metadata exposed to portal users. |
| 8 | **Existing-conditions survey** | `NOT_OFFERED_IN_PORTAL` | Not exposed. |
| 9 | **Stormwater / drainage documentation** | `NOT_OFFERED_IN_PORTAL` | Not exposed as a document. **However, a county inspector described proposed work in the inspection record (not a sealed engineering determination)** — see §2. |
| 10 | **Erosion-control plan** | `NOT_OFFERED_IN_PORTAL` | Fee line does not prove a particular erosion-control plan is held. |
| 11 | **Driveway permit** | `DOWNLOADED_VERIFIED` (as inspection record) | See §2 — driveway line & grade and pre-pour inspections are officially recorded with **substantive engineering comments**. No separate standalone driveway permit project was returned by address, parcel, business-name or subdivision search. |
| 12 | **Culvert / ROW drawings** | `NOT_OFFERED_IN_PORTAL` | The inspection comments describe the culvert design verbally; no drawing is released. |
| 13 | **Inspection history** | `DOWNLOADED_VERIFIED` | **15 inspections** — `BP-2026-1621_INSPECTION_HISTORY.md`. |
| 14 | **Correction / enforcement records** | `DOWNLOADED_VERIFIED` | One **Partial Pass** on 2026-08-14 (windload / truss bearing), with correction text recorded. No stop-work or code-enforcement record returned. |
| 15 | **Final grading documentation** | `NOT_OFFERED_IN_PORTAL` | Not exposed. |
| 16 | **Certified as-built** | `NOT_OFFERED_IN_PORTAL` | Not exposed. |
| 17 | **Certificate of Occupancy** | `NOT_FOUND_IN_SEARCHED_SYSTEM` | Project status is still **Active** as of 2026-10-01; no CO appears in the project or type records. |
| 18 | **Associated environmental filings** | `DOWNLOADED_VERIFIED` | Nearby NWFWMD ERP 9220-2 is an **unlinked lead**; no approved parcel intersection or permit-file coverage was demonstrated. Negative radius searches do not establish absence of permit coverage. |

## 2. Official drainage findings already recovered

From `/api/v3/cp/work-orders/17513349/inspections`:

| Date | Inspection | Result | Official comment |
|---|---|---|---|
| 2026-07-22 | **Site Grading / Drainage (pre-construction)** | Passed | *(no comment)* |
| 2026-08-06 | **Driveway Line & Grade / Consultation** | Passed | "Use 100 ft of **12 inch ADS perforated pipe with sock**; Tear out existing concrete end @ address **2260** and tie into with new pipe; Install **1st inlet box** @ roughly halfway; Tear out existing concrete end @ address **2270** and install an inlet box; call for Pre-pour inspection when ready" |
| 2026-10-01 | **Driveway Pre-Pour** | Passed | *(no comment)* |

The 2026-08-06 comment is direct official evidence that the driveway drainage
design ties into existing storm structures at **2260 and 2270 Tom Street** with
a 12-inch ADS perforated pipe and at least one inlet box — i.e. the inspector contemplated roadside pipe work, not a proven installed and surveyed system. Legal rights, alignment and capacity are unresolved.

## 3. Why the remaining documents cannot be obtained from the portal

MGO Connect's public customer portal returns **zero** files for this project
(`/api/v3/cp/ProjectFiles/get-customer-files-by-project-id/17513349` →
`{"data": []}`). Plans, surveys and as-builts are held in the county's internal
permit system and are not exposed to portal users at any privilege level tested.
Three candidate inspection-report endpoints were tried and all returned HTTP 404.

## 4. Outstanding action for this property

`13_PUBLIC_RECORDS_REQUESTS/2264_TOM_ST_COMPLETE_PERMIT_FILE.md` — status
**DRAFTED_NOT_SUBMITTED**. Items 5–12 and 15–16 of §1 above must be requested.

**Denominator note:** this audit is reconciled against the authoritative
MGO project record for this address (5 projects: 1 active BP + 4 from 1996) and
against the county's own document endpoint for the active permit. No claim of
completeness is made beyond what those records enumerate.