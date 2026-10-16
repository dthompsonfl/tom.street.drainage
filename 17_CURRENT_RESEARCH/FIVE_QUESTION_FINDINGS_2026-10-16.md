# Tom Street: five-question findings and remaining evidence

**Reviewed October 16, 2026 UTC. Current research, not an engineering or legal determination.** Local jurisdiction: Santa Rosa County, Florida. Original captured records retain their original timestamps; this update does not refresh the live MGO permit status.

## Decision table

| Question | Answer supported by the records | Status |
| --- | --- | --- |
| Which approved plans govern 2264 and 2268? | No actual site-approved plan, plan identifier/revision, subdivision-plan linkage, or approved lot-specific exemption has been obtained. Generic grading guidance and an approved review task are not the plan. | NOT_OBTAINED |
| What are the measured elevations, inverts and positive outfall? | No surveyed values with datum, benchmark, date and responsible professional, or verified continuous receiving-outfall route, have been obtained. | NOT_OBTAINED |
| Is Tom Street County maintained? Who maintains its drainage structures? | The relevant road segment is explicitly **County Maintained** in two County GIS services. Ownership and maintenance of each inlet, ditch, driveway pipe and downstream facility require separate asset/acceptance/easement records. | ROAD_GIS_VERIFIED; ASSET_RESPONSIBILITY_UNRESOLVED |
| Which amendments and exemptions apply? | Actual Ordinances 2025-25 and 2026-03 are now preserved. The first amends drainage-related provisions; the second concerns the East Milton wellfield. Actual lot-specific plan pathway, exemptions, permit conditions and complete temporal applicability remain unresolved. | PRIMARY_ORDINANCES_OBTAINED; LOT_APPLICATION_UNRESOLVED |
| Is there applicable ERP or construction CGP coverage? | The nearby NWFWMD 9220-2 record is a point-location lead, not a project boundary or parcel match. No lot-specific ERP approval/exemption or FDEP CGP acknowledgment/NOI/common-plan determination has been obtained. | COVERAGE_UNRESOLVED |

## 1. Approved plans: what is and is not established

The archived County project records pair **2264 Tom Street / BP-2026-1621 / 21-2S-26-0780-0QQ00-1020** and **2268 Tom Street / BP-2026-1612 / 21-2S-26-0780-0QQ00-1490**. Their creation and issuance fields are February 11 and March 23, 2026. These are saved records, not a new live-status retrieval. Sources: the two `03_PERMITS_AND_INSPECTIONS/*/BP-2026-*_project_by_uid.json` records and task/attachment captures.

An `Engineering Review` approval flag does not identify the approved drawing, revision, engineer, conditions, or actual grading. An empty customer-attachment response does not prove the County has no plans. The saved appraiser filing name **Crescent Shores (00780)** is a search key, not proof that a particular subdivision grading plan governs. **Hadleigh Hills** remains an unlinked environmental-permit lead.

The County's one-page [Typical Yard Grading Guidelines](captures/20261016T060511Z/SRC_TYPICAL_GRADING.pdf) is now preserved. It is explicitly not to scale and is **NOT a site-specific approved plan** for either lot. It describes positive drainage and consulting a subdivision master plan where applicable; its typical numerical dimensions cannot be reported as approved or measured Tom Street values. Original URL: https://www.santarosa.fl.gov/DocumentCenter/View/370/Typical-Lot-Grading-PDF .

**Required closure evidence:** the County-held original and every revised approved drawing, sheet index, approval date/stamp and engineer; the recorded subdivision/parent-approval linkage; the written plan pathway or exemption record for each parcel. Ask the County to identify exactly what its Engineering Review approved. Do not narrow the search solely to Hadleigh Hills or a current street address.

## 2. Measurements and outfalls: no defensible numeric answer yet

The August 6 inspection direction at 2264 specifies proposed 100-foot/12-inch pipe and inlet work near 2260/2270. Those dimensions are an instruction, not a measured installation. The August 31 and September 10 comments at 2268 discuss sediment protection and matching roadway grades, without surveyed elevation values. The original inspection JSON remains the source.

The County road GIS contains `From_Elev=0`, `To_Elev=0`, `Z_Value=0` and `ROWWIDTH=0`. **These are unqualified database values, not evidence of sea-level road elevations, zero-width right-of-way, or surveyed inverts.** Neither FEMA base-flood elevations nor terrain-model heights can substitute for measured underground pipe inverts.

A bounded 150-meter MS4-outfall query returned no features. This is not proof that no lawful outfall exists: inventory coverage, feature type and the query boundary limit the result. A drainage-basin query returned `DIRECT RUNOFF TO BAY`; this basin label does not identify the site's installed outlet or prove a continuous, adequately sized conveyance. Sources: `SRC_MS4_OUTFALL_VICINITY.json` and `SRC_GIS_BASIN_VICINITY.json` in the [second capture](captures/20261016T060511Z/).

The County's stormwater problem-area layer returned **OBJECTID 2068**, with source description **Road & Bridge Maps Marked Up by Foreman**, for the queried vicinity. It is a useful records lead. The record does not establish the date, cause, severity or present condition of any Tom Street flooding. Obtain the underlying marked maps, complaint/work-order history and explanation; this evidence may support pre-existing drainage limitations as an alternative explanation rather than implicating new construction.

**Required closure evidence:** a common-datum survey of finished floors, property corners/perimeters, roadway crown/shoulders, swale bottoms, inlet rims and every pipe's upstream/downstream invert; pipe diameter/material/length/slope; a documented outlet and downstream control/tailwater; dates and preconstruction-to-current comparison. Request existing records under Chapter 119; request a new County field investigation separately as a service, not as an existing-records entitlement.

## 3. Road maintenance: a resolved factual component

The County's Road Issues page directs users to the Street-Maintainer app. Its app data identifies the County street web map and service. The preserved relevant feature is:

| Field | Preserved value |
| --- | --- |
| Street | TOM ST |
| Street ID / segment | 3503 / 2036 |
| Open-data feature | FID 2006 |
| Address range | 2100-2299; even addresses 2100-2298 |
| Status / surface / city | OPEN / Paved / Navarre |
| Maintainer | **County Maintained** |
| County GoMaps corroboration | OBJECTID 2036, same range and maintainer |

Primary evidence: [open-data exact feature](captures/20261016T054716Z/SRC_TOM_FID_2006.json), [County GoMaps street query](captures/20261016T054716Z/SRC_GOMAPS_TOM.json), and the app/web-map/metadata records preserved beside them. Both addresses fall within that segment's address range. These two services are corroborating County publications, not independent surveys.

**What this resolves:** current public County GIS classifies the road as County maintained. Earlier documents calling road-maintainer status wholly unknown are superseded on this point.

**What it does not resolve:** title to the road, exact right-of-way boundary, an easement, acceptance of the new pipe/inlet work, or ownership and maintenance of each drainage structure. A County-maintained road does not automatically make every adjacent private driveway culvert or subdivision facility a County asset.

**Action:** provide segment 2036/FID 2006 to Santa Rosa County Public Works, request an inspection/work-order number, and ask for the accepted drainage-asset inventory, easements and maintenance agreements. The official [Road Issues](https://www.santarosa.fl.gov/377/Road-Issues) page lists Public Works at **850-626-0191**. No service request was submitted by this research.

## 4. Actual ordinance evidence and applicability limits

### Ordinance 2025-25

The [10-page enacted instrument](captures/20261016T060511Z/ORD_2025_25.pdf) is now preserved, not merely its index description. Page 1 identifies changes including erosion/sediment control and drainage/stormwater management. Page 2 records adoption **November 10, 2025**, and the Clerk's certification of recording and electronic **transmission on November 14, 2025**. Section 3 makes effectiveness depend on filing with the Department of State. **The Clerk's transmission certificate is not a separately obtained Department of State receipt.** Do not manufacture a confirmed receipt/effective date from a PDF creation timestamp.

Exhibit A pages 4-5 amend **4.04.01.I.3.i**, including treatment-pond fencing exceptions. The instrument does not present a revision to D.1, D.4 or E. Its references to section 4.04.01 therefore do not establish that every residential grading provision changed in this ordinance.

### Ordinance 2026-03

The [four-page enacted instrument](captures/20261016T060511Z/ORD_2026_03.pdf) records adoption **January 22, 2026** and a Clerk-certified electronic transmission **January 27, 2026**. Its subject and map are the **East Milton Wellfield Protection Overlay**, not an amendment to the Tom Street residential grading standards. The bounded County wellfield GIS query returned no feature near the target coordinates. That is supporting geographic context, not a certified parcel overlay analysis. No evidence found makes this wellfield amendment a Tom Street lot-grading exemption.

### Residential rules and the unresolved permit pathway

The preserved 509-page County LDC shows **4.04.01.D.1** on PDF pages 268-269 and **D.4/E** on PDF page 270 (printed page 252). D.1 is conditional on the specified lot category and no subdivision lot-grading plan being on file; it offers the stated ERP-letter or sealed-PE-plan route. Determining whether a subdivision plan is on file does **not**, by itself, choose between those two alternatives.

D.4 lists grading-plan exemption conditions involving piling/pier construction and fill, stem-wall/side-yard/fill criteria, minimum lot width, or a County Engineer/Building Official special-circumstances determination. BMP requirements remain despite grading-plan exemptions. **No exemption has been established or excluded for either target lot.** Section E separately requires a certified as-built before CO in the published text. An assigned portal task is not proof that the document is absent, overdue or approved.

The Florida Building Commission's [official current page](https://www.floridabuilding.org/c/default.aspx) identifies the **8th Edition (2023)** effective **December 31, 2023**. This is the state-code baseline to check against the February/March 2026 permit records. The root-page HTML captured by the automated downloader is only a redirect; the substantive page was separately read through the browser. Exact permit-declared code edition, supplements, local amendments and any vesting claim still require the approval file.

**Still open:** final County confirmation of the governing edition/amendments for initial approval and later revisions; complete review of other potentially applicable 2026 ordinances (including 2026-10, 2026-14 and 2026-16); actual permit exemptions/waivers. The advertised October 22, 2026 reformat is not treated as already enacted law.

## 5. ERP and FDEP CGP: different authorizations, neither matched yet

The new [NWFWMD record](captures/20261016T054716Z/NWFWMD_ERP_SPATIAL.json) identifies **9220-2**, Hadleigh Hills Phase 2, applicant Hadleigh Hills Development Group, 8.1 acres, decision November 21, 2016. The service is a **point layer**, not project-boundary polygons; `LINK` and `FDEP_ID` are null.

It also reports **expiration 2021-11-21**, alongside `Issued`, `In Compliance` and disclosure `Active`. Preserve these different fields without converting them into a legal conclusion about 2026 authorization. Obtain the actual instrument, extensions, predecessor 9220-1 and project boundary. Neither proximity nor an applicant-name result establishes coverage of either Tom Street parcel. No finding of expired/unpermitted construction follows from the map alone.

FDEP's [Construction Activity guidance](https://floridadep.gov/water/stormwater/content/construction-activity), preserved as `DEP_CGP_CRITERIA.html`, distinguishes construction CGP from ERP/local approval. Coverage turns on qualifying disturbance, including sub-acre work within a larger common plan, and qualifying discharge. Two small lots are not automatically exempt; shared builder identity alone also does not prove a regulated common plan.

**Required closure evidence:** a signed ERP approval or exemption tied to the actual parcel/project footprint; County-held authorization references; FDEP NOI, coverage acknowledgment/ID, operator and common-plan limits, SWPPP where held, transfers and termination records. Public-map or building-permit-string searches are not agency-certified no-records findings.

## Research execution, preservation and next priority

Five independent research agents were dispatched for plans, measurements, maintenance, legal applicability and environmental permitting. The maintenance and environmental jobs completed within their bounded source scope. The other three stopped at the service's credit limit with incomplete results. Their output was treated as leads; it did not establish missing engineering facts. The supervising review independently retrieved the raw GIS records and enacted ordinances described above.

The first acquisition preserved **11 official JSON responses**. The follow-up attempted **22 sources**, captured **21 responses**, and recorded one API failure without inventing a file. A returned HTML page may be only a redirect; a valid download is not proof of substantive relevance. Raw captures are unchanged, with URLs, times, byte sizes and SHA-256 hashes. Sources and new claims are joined in the control registers.

**Highest-priority next action:** use the verified County-maintained road classification to obtain a named Public Works/Engineering case, then obtain the two approved lot-grading files and accepted roadside system plans together. Those documents and a common-datum field survey are the bottleneck to a defensible drainage assessment. Eight draft files containing nine separate request/service templates remain unsubmitted in the available evidence. No violation, causation, negligence or asset-specific maintenance liability is established here.
