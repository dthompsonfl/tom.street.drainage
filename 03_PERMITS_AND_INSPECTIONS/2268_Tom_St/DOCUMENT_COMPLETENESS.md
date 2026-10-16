# Document Completeness Audit — 2268 Tom Street, Navarre, FL 32566

**Parcel (verified, Santa Rosa County Property Appraiser):** `21-2S-26-0780-0QQ00-1490`
**Parcel as stored in MGO:** `212S2607800QQ001490`
**Owner of record:** HOLIDAY BUILDERS INC
**Audit date:** 2026-10-15

Status key:
`DOWNLOADED_VERIFIED` · `HISTORICAL_LEAD_UNLINKED` · `NOT_OBTAINED_FOR_SITE` · `NOT_OFFERED_IN_PORTAL` · `NOT_FOUND_IN_SEARCHED_SYSTEM` ·
`AUTHENTICATION_REQUIRED` · `REQUEST_DRAFTED`

---

## 1. Record-by-record status

| # | Record | Status | Evidence / explanation |
|---|---|---|---|
| 1 | **Official parcel record** | `DOWNLOADED_VERIFIED` | `02_PROPERTY_AND_PARCELS/2268_Tom_St/srcpa_property_record_21-2S-26-0780-0QQ00-1490.json` |
| 2 | **Recorded legal description** | `NOT_FOUND_IN_SEARCHED_SYSTEM` | Clerk Legal Search endpoint returns HTTP 404; Property Appraiser export does not carry legal description. See `PERMIT_DOCUMENT_INVENTORY.csv` / `DOC-SHARED-9004`. |
| 3 | **Related deeds / plat records** | `NOT_FOUND_IN_SEARCHED_SYSTEM` | **Correction recorded:** the MLS claim that this lot begins at ORB 3492 PG 700 is wrong. ORB 3492/700 = instrument **201603296**, deed dated 2016-01-28, legal "**21-2S-26 POPE SUBD LOT 22 UNREC**" — that is **2274 Tom St**. |
| 4 | **Building permit** | `DOWNLOADED_VERIFIED` | **`BP-2026-1612`** — New Single Family (R) — **Active** — created 2026-02-11. Project UID `677D3AE3-F348-4B97-A37C-8B0BC05CEAF7`, MGO project ID `17513025`. |
| 4b | Possible historical permits with conflicting identity | `HISTORICAL_LEAD_UNLINKED` | Four 2000-era MGO records are **unlinked address/parcel-history leads**; the archived parcel identifier for those records currently maps to **2274 Tom St**, not confirmed to 2268. Attribution needs original applications and parcel history. |
| 5 | **Original site plan** | `NOT_OFFERED_IN_PORTAL` | `ProjectFiles/get-customer-files-by-project-id/17513025` → **0 files**. |
| 6 | **Original approved grading plan** | `NOT_OFFERED_IN_PORTAL` | Same as #5. An Erosion Control/Site Grade Flat Fee appears on the permit. This does **not** establish approval or existence of a particular drawing. |
| 7 | **Approved engineering revisions** | `NOT_OFFERED_IN_PORTAL` | Not exposed. |
| 8 | **Existing-conditions survey** | `NOT_OFFERED_IN_PORTAL` | Not exposed. |
| 9 | **Approved stormwater / drainage drawings** | `NOT_OFFERED_IN_PORTAL` | See §2 — the inspector refers to a **roadway and stormwater ditch**, without supplying a surveyed location or approved engineering plan. |
| 10 | **Erosion-control plan** | `NOT_OFFERED_IN_PORTAL` | Fee line does not prove a particular plan exists in the County file. |
| 11 | **Separate driveway permit and approved plans** | `NOT_OBTAINED_FOR_SITE` | See §2. No separate standalone driveway permit project was returned by address, parcel, business-name or subdivision search. |
| 12 | **Culvert / ROW drawings** | `NOT_OFFERED_IN_PORTAL` | Inspector's roadway-grade consultation does not contain an approved culvert/ROW design. No drawing retrieved. |
| 13 | **Inspection history** | `DOWNLOADED_VERIFIED` | **11 inspections** — `BP-2026-1612_INSPECTION_HISTORY.md`. |
| 14 | **Code enforcement and correction records** | `NOT_OBTAINED_FOR_SITE` | The **11 captured permit inspection entries** are marked Passed; that does **not** establish that no other agency inspection, notice or enforcement matter exists. No authoritative no-records response received. |
| 15 | **Final grading documentation** | `NOT_OFFERED_IN_PORTAL` | Not exposed. |
| 16 | **Certified as-built** | `NOT_OFFERED_IN_PORTAL` | Not exposed. |
| 17 | **Certificate of Occupancy** | `NOT_FOUND_IN_SEARCHED_SYSTEM` | Project status is still **Active**; no CO in the project or type records. |
| 18 | **Site-applicable environmental filings and authorization** | `NOT_OBTAINED_FOR_SITE` | Nearby NWFWMD ERP 9220-2 is an **unlinked lead**; no approved parcel intersection or permit-file coverage was demonstrated. Negative radius searches do not establish absence of permit coverage. |

## 2. Official drainage findings already recovered

From `/api/v3/cp/work-orders/17513025/inspections`:

| Date | Inspection | Result | Official comment |
|---|---|---|---|
| 2026-08-31 | **Site Grading / Drainage (pre-construction)** | Passed | "**Site passes.** Ensure that **roadway and stormwater ditch** remain free of construction sediment." |
| 2026-09-10 | **Driveway Line & Grade / Consultation** | Passed | "**Flat; Match Existing roadway Grades**; Call for pre-pour Inspection when ready" |

Two findings of direct relevance:

1. The county's own inspector identified an existing **roadway and stormwater
   ditch** along the Tom Street frontage as the feature that must be kept free
   of construction sediment. This confirms only that the inspector **referred to** a roadway/stormwater ditch. The ditch's exact location, responsibility and capacity remain unverified.
2. The inspector directed matching roadway grades; no numeric elevation, freeboard or hydraulic capacity can be inferred.

For comparison, the archived 2264 Tom St driveway **inspector's instruction** calls for 12-inch ADS pipe and an inlet near structures identified by the 2260 and 2270 addresses. This is not confirmation of an approved design or completed connection; shared drainage, ownership, capacity and performance require the actual plans and surveys.

## 3. Why the remaining documents cannot be obtained from the portal

MGO Connect's public customer portal returns **zero** files for this project
(`/api/v3/cp/ProjectFiles/get-customer-files-by-project-id/17513025` →
`{"data": []}`). The tested customer attachment endpoint did not expose plans, surveys or as-builts. **Their existence and availability from the actual County custodian are unresolved.**
Three candidate inspection-report endpoints were tried and all returned HTTP 404.

## 4. Outstanding action for this property

`13_PUBLIC_RECORDS_REQUESTS/2268_TOM_ST_COMPLETE_PERMIT_FILE.md` — status
**DRAFTED_NOT_SUBMITTED**. Items 5–8, 10, 12, 15–16 of §1 above must be requested.

**Denominator note:** this audit uses the captured MGO permit at 2268 and 2000-era **unlinked leads whose parcel identifiers currently map elsewhere**, and
against the county's own document endpoint for the active permit. No claim of
completeness is made beyond what those records enumerate.