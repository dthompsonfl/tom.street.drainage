# Document Completeness Audit — 2268 Tom Street, Navarre, FL 32566

**Parcel (verified, Santa Rosa County Property Appraiser):** `21-2S-26-0780-0QQ00-1490`
**Parcel as stored in MGO:** `212S2607800QQ001490`
**Owner of record:** HOLIDAY BUILDERS INC
**Audit date:** 2026-10-15

Status key:
`DOWNLOADED_VERIFIED` · `NOT_OFFERED_IN_PORTAL` · `NOT_FOUND_IN_SEARCHED_SYSTEM` ·
`AUTHENTICATION_REQUIRED` · `REQUEST_DRAFTED`

---

## 1. Record-by-record status

| # | Record | Status | Evidence / explanation |
|---|---|---|---|
| 1 | **Official parcel record** | `DOWNLOADED_VERIFIED` | `02_PROPERTY_AND_PARCELS/2268_Tom_St/srcpa_property_record_21-2S-26-0780-0QQ00-1490.json` |
| 2 | **Recorded legal description** | `NOT_FOUND_IN_SEARCHED_SYSTEM` | Clerk Legal Search endpoint returns HTTP 404; Property Appraiser export does not carry legal description. See `PERMIT_DOCUMENT_INVENTORY.csv` / `DOC-SHARED-9004`. |
| 3 | **Related deeds / plat records** | `NOT_FOUND_IN_SEARCHED_SYSTEM` | **Correction recorded:** the MLS claim that this lot begins at ORB 3492 PG 700 is wrong. ORB 3492/700 = instrument **201603296**, deed dated 2016-01-28, legal "**21-2S-26 POPE SUBD LOT 22 UNREC**" — that is **2274 Tom St**. |
| 4 | **Building permit** | `DOWNLOADED_VERIFIED` | **`BP-2026-1612`** — New Single Family (R) — **Active** — created 2026-02-11. Project UID `677D3AE3-F348-4B97-A37C-8B0BC05CEAF7`, MGO project ID `17513025`. |
| 4b | Prior-permit history on this lot | `DOWNLOADED_VERIFIED` | Four 2000-era mobile-home-related MGO records are **historical leads**; the archived parcel identifier for those records currently maps to **2274 Tom St**, not confirmed to 2268. Attribution needs original applications and parcel history. |
| 5 | **Original site plan** | `NOT_OFFERED_IN_PORTAL` | `ProjectFiles/get-customer-files-by-project-id/17513025` → **0 files**. |
| 6 | **Original approved grading plan** | `NOT_OFFERED_IN_PORTAL` | Same as #5. An Erosion Control/Site Grade Flat Fee appears on the permit. This does **not** establish approval or existence of a particular drawing. |
| 7 | **Approved engineering revisions** | `NOT_OFFERED_IN_PORTAL` | Not exposed. |
| 8 | **Existing-conditions survey** | `NOT_OFFERED_IN_PORTAL` | Not exposed. |
| 9 | **Stormwater / drainage documentation** | `DOWNLOADED_VERIFIED` (as inspection record) | See §2 — the inspector refers to a **roadway and stormwater ditch**, without supplying a surveyed location or approved engineering plan. |
| 10 | **Erosion-control plan** | `NOT_OFFERED_IN_PORTAL` | Fee line does not prove a particular plan exists in the County file. |
| 11 | **Driveway permit** | `DOWNLOADED_VERIFIED` (as inspection record) | See §2. No separate standalone driveway permit project was returned by address, parcel, business-name or subdivision search. |
| 12 | **Culvert / ROW drawings** | `NOT_OFFERED_IN_PORTAL` | Drainage design is described verbally in the inspection record; no drawing released. |
| 13 | **Inspection history** | `DOWNLOADED_VERIFIED` | **11 inspections** — `BP-2026-1612_INSPECTION_HISTORY.md`. |
| 14 | **Correction / enforcement records** | `DOWNLOADED_VERIFIED` | **No failed or partial inspections on this permit.** Every inspection passed. No code-enforcement or stop-work record was returned by these searches; this is not an official no-records finding. |
| 15 | **Final grading documentation** | `NOT_OFFERED_IN_PORTAL` | Not exposed. |
| 16 | **Certified as-built** | `NOT_OFFERED_IN_PORTAL` | Not exposed. |
| 17 | **Certificate of Occupancy** | `NOT_FOUND_IN_SEARCHED_SYSTEM` | Project status is still **Active**; no CO in the project or type records. |
| 18 | **Associated environmental filings** | `DOWNLOADED_VERIFIED` | Nearby NWFWMD ERP 9220-2 is an **unlinked lead**; no approved parcel intersection or permit-file coverage was demonstrated. Negative radius searches do not establish absence of permit coverage. |

## 2. Official drainage findings already recovered

From `/api/v3/cp/work-orders/17513025/inspections`:

| Date | Inspection | Result | Official comment |
|---|---|---|---|
| 2026-08-31 | **Site Grading / Drainage (pre-construction)** | Passed | "**Site passes.** Ensure that **roadway and stormwater ditch** remain free of construction sediment." |
| 2026-09-10 | **Driveway Line & Grade / Consultation** | Passed | "**Flat; Match Existing roadway Grades**; Call for pre-pour Inspection when ready" |

Two findings of direct relevance:

1. The county's own inspector identified an existing **roadway and stormwater
   ditch** along the Tom Street frontage as the feature that must be kept free
   of construction sediment. That is official confirmation of a roadside
   conveyance adjacent to this lot.
2. The inspector directed matching roadway grades; no numeric elevation, freeboard or hydraulic capacity can be inferred.

Compare the neighbouring 2264 Tom St lot (BP-2026-1621), whose driveway design
ties into existing storm structures at **2260 and 2270 Tom Street** with
12-inch ADS perforated pipe and an inlet box. The presence and capacity of any shared connection require plans, installed-works records and surveys.

## 3. Why the remaining documents cannot be obtained from the portal

MGO Connect's public customer portal returns **zero** files for this project
(`/api/v3/cp/ProjectFiles/get-customer-files-by-project-id/17513025` →
`{"data": []}`). Plans, surveys and as-builts are not exposed to portal users.
Three candidate inspection-report endpoints were tried and all returned HTTP 404.

## 4. Outstanding action for this property

`13_PUBLIC_RECORDS_REQUESTS/2268_TOM_ST_COMPLETE_PERMIT_FILE.md` — status
**DRAFTED_NOT_SUBMITTED**. Items 5–8, 10, 12, 15–16 of §1 above must be requested.

**Denominator note:** this audit is reconciled against the authoritative
MGO project record for this address (5 projects: 1 active BP + 4 from 2000) and
against the county's own document endpoint for the active permit. No claim of
completeness is made beyond what those records enumerate.