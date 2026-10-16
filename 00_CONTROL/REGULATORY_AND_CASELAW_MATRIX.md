# Regulatory and Case-Law Matrix

Compiled: 2026-10-16. Every row records what was **actually verified against a
primary source**, what remains unverified, and whether the authority is binding,
conditional, inapplicable or unresolved.

**Standing caveat:** the preparer of this matrix is not a licensed attorney and
not a licensed Professional Engineer. Nothing here is legal advice or an
engineering determination. Rows classify applicability; they do not assert
compliance or violation.

Status vocabulary: `VERIFIED_APPLICABLE` · `CONDITIONALLY_APPLICABLE` ·
`NOT_APPLICABLE` · `UNRESOLVED`

---

## A. Sources actually retrieved and verified

| Source | Where retrieved | Verification |
|---|---|---|
| Fla. Stat. § 119.07 (2026) | `flsenate.gov/Laws/Statutes/2026/119.07` | Full statutory text read |
| Santa Rosa County LDC (official PDF, 509 pp) | `santarosa.fl.gov/DocumentCenter/View/5820/…` | Downloaded; `%PDF-1.6`; 7,225,217 bytes; SHA-256 `12f0ec8d024c95fa15af73f1cde340867068bb51d51bb9fcb6f1ca3e6e69ebae`; PDF cover/ordinance text dated 2025-11-10 (Ord. 2025-25); PDF CreationDate 2026-01-13 is *file metadata*, not legal effective date |
| Fla. Stat. § 373.042 (2026) | `flsenate.gov/Laws/Statutes/2026/373.042` | Full statutory text read |
| **Westland Skating Center, Inc. v. Gus Machado Buick, Inc., 542 So. 2d 959 (Fla. 1989)** | [FSU College of Law corrected Supreme Court opinion](https://library.law.fsu.edu/Digital-Collections/flsupct/dockets/72492/op-72492.pdf) | **PRIMARY OPINION LOCATED AND READ**; subsequent treatment not comprehensively reviewed — see §E |

---

## B. Land Development Code — verified text

All page references are to the official PDF at
`08_LEGAL_AND_REGULATORY/SOURCE/santa_rosa_county_LDC.pdf`. The LDC prints its
own page numbers in the footer; both are given because they differ.

### B1 — § 3.04.04, Obstruction of Drainageways
*Printed page 139 = PDF page 157.*

> "To the extent practicable, all development shall conform to the natural
> contours of the land with natural or man-made drainageways left unobstructed.
> **The obstruction of natural or man-made drainageways is strictly prohibited.**"

- **Status: CONDITIONALLY_APPLICABLE.**
- **Proposition proved:** the jurisdiction has an express prohibition on
  obstructing natural or man-made drainageways.
- **Applicability prerequisites:** identification of *the* drainageway, its
  alignment, and whether any obstruction exists. None of those is established
  here — no plan, no profile, no as-built, no survey.
- **Explicitly NOT concluded:** that any obstruction occurred at 2264 or 2268.
  The 2264 inspector direction to "tear out existing concrete end" and "install
  an inlet box" is a work instruction; it is not itself proof of obstruction.

### B2 — § 3.04.05, Erosion and Sedimentation Control
*Printed pages 139–140 = PDF page 157ff.* Sub-section A.1.a (Single Family):

> "Any overall site regulated by the SWPPP shall maintain erosion control
> measures so as to prevent sediment or debris from leaving the development
> parcel. Any sediment or debris that leaves the development site shall be
> properly recovered by the building permit holder. Failure to comply … shall
> constitute a violation … and shall cause suspension of a building permit …
> and code enforcement action."

- **Status: CONDITIONALLY_APPLICABLE.**
- **Conflict noted:** § 3.04.03 states that "in no instances shall any
  development be exempt from section 3.04.04 … and section 3.04.05." SWPPP
  applicability itself is not established.
- **NOT concluded:** that sediment left the parcel, or that the permit is
  suspended. The 2268 inspector's remark about keeping the ditch free of
  construction sediment is a routine precaution, not a finding of breach.

### B3 — § 4.04.01, Drainage and Stormwater Management Plan
*Printed pages 249–250 = PDF pages 267–268.*

**§ 4.04.01.A** — "adequate drainage and stormwater management" means design
and construction that "will not cause flood damage to the property involved or
surrounding properties," meeting Chapter 62-330 F.A.C. and the Code's criteria.

**§ 4.04.01.B** — a plan "signed and sealed by a Professional Engineer
registered in the State of Florida" is required *prior to* a development order
or building permit, and the permit "shall be conditioned upon full compliance
with that plan."

**§ 4.04.01.D.1 — lots under one acre without a subdivision lot grading plan on
file with County Engineering.** Requires, *prior to issuance of a building
permit*:
1. **(a)** an **Individual ERP approval letter from NWFWMD** with all
   supporting calculations and construction plans, **OR** an **engineered lot
   grading plan signed/sealed by a Florida PE**;
2. **(b)** finish floor elevation of all structures;
3. **(c)** all site improvements conveying runoff (swales, ditches, culverts,
   pipes, inlets) shown **to a positive outfall**, with **all elevations and/or
   inverts** — and if no positive outfall is available or it would negatively
   impact adjacent properties, a stormwater pond is required;
4. **(d)** spot elevations around the lot perimeter along property lines;
5. **(e)** flow areas indicating direction of flow;
6. **(f)** construction-phase BMPs;
7. **(g)** **"At substantial completion and prior to Certificate of Occupancy,
   the Engineer of Record shall provide a signed/sealed letter to the County
   certifying the approved lot grading plan was built in conformance with the
   plan. Any major deviations … will require an as-built plan."**

- **Status: CONDITIONALLY_APPLICABLE — and this is the pivotal provision.**
- **Why it matters:** sub-paragraph (g) explains, in the county's own words, why
  the MGO task **"Certified Drainage as Built"** exists and why it sits at
  **Assigned** on both permits while **"Issue CO"** is also **Assigned**. The
  county's workflow mirrors this code text.
- **Applicability prerequisites — UNRESOLVED:** the section turns on whether a
  *subdivision lot grading plan is on file with the County Engineering
  Department* for these lots. Both parcels are well under one acre (lot sizes
  recorded as ~0.14–0.16 ac in earlier secondary data, not yet confirmed from
  an official survey). **That on-file status has not been determined.** It is
  tracked as **GAP-11** and is the single highest-value factual question in the
  investigation, because the answer determines whether the compliant path was a
  sealed PE lot grading plan or an NWFWMD Individual ERP letter.
- **NOT concluded:** non-compliance. Both permits remain **Active**. An open
  pre-CO task on an active permit is the expected state of an unfinished
  house, not evidence of breach.

### B4 — § 4.04.01.D.2.b — lots 1–2 acres fronting county roads with <50 ft ROW
*Printed page 250.* "A recorded drainage easement **may** be required prior to
Certificate of Occupancy, when the County Engineer determines … necessary …
**No drainage easement will be greater than 20-feet wide** along the right-of-way."

- **Status: NOT_APPLICABLE on current evidence** — the D.2 band applies to lots
  of one acre or more. If D.1 applies instead, a drainage easement could still
  be relevant, but the text located here does not govern D.1 lots.
- Recorded because the Tom Street frontage is the likely location of any such
  easement and **no easement has been located** (GAP-14).

### B5 — § 4.04.01.D.4, conditional lot-grading-plan exemptions
*Printed page 252 = PDF page 270.*

- **Status: CONDITIONALLY_APPLICABLE / EXEMPTION UNRESOLVED.** The published code provides four alternative paths for exempting a **lot grading plan**, with conditions involving structure/fill configuration, stem-wall lot width, wide lots, or special circumstances at the discretion of the County Engineer/Building Official. It expressly notes construction **BMP requirements remain** despite lot grading exemptions.
- A narrow single-family-lot exemption from a plan must not be read as a blanket exemption from drainage, erosion control, certified as-built, or other applicable requirements.
- **Evidence needed:** the County's written exemption/waiver record or documented classification, and elevations, fill quantity, foundation configuration, lot dimensions and neighboring runoff consequences. Neither photos nor an unverified lot size establish an exemption or its absence.

### B6 — § 4.04.01.E, certified as-built before occupancy
*Printed page 252 = PDF page 270.*

- **Status: VERIFIED CODE TEXT / SITE-SPECIFIC COMPLIANCE UNRESOLVED.** Section E states: **"All lots will require a certified as-built prior to issuance of the Certificate of Occupancy."** This provision is **separate from** the conditional § 4.04.01.D.1.g engineer's conformance-letter pathway.
- The current site task **"Certified Drainage as Built: Assigned"** neither proves that a certified as-built has been produced nor that it is absent, due, overdue, or approved.
- **Evidence needed:** actual MGO document record and county engineering approval/CO gate for each permit, plus the governing ordinance edition.

### B7 — § 4.04.01.G-H and I, roadside geometry and calculations
*Printed pages 253 onward = PDF pages 271 onward.*

- **Status: CONDITIONALLY_APPLICABLE.** The published code includes ditch/swale, right-of-way, minimum-slope and stormwater-design requirements. The exact provisions controlling an existing ditch, a lot-grading exemption or a subdivision-installed system depend on approved plans, asset ownership, design and any approved exception.
- Request documented roadside cross-sections, minimum slopes, swale depth, ditch maintenance acceptance, engineered calculations and the receiving outfall. **Do not derive grade compliance from an inspector's adjective or uncalibrated photographs.**

---

## C. Florida public-records law — verified text

**Fla. Stat. § 119.07 (2026)** — verified against the official text.

| Subdivision | Verified content | Use here |
|---|---|---|
| 119.07(1)(a) | every custodian shall permit inspection and copying "at any reasonable time, under reasonable conditions, and under supervision" | basis for the Chapter 119 requests |
| 119.07(1)(c) | custodian must "acknowledge requests … promptly and respond … in good faith" | sets response expectation |
| 119.07(1)(d) | partial exemption requires **redaction and production of the remainder** | requests ask for release of unexempt portions |
| 119.07(1)(e) | exemption must be stated **with the statutory citation** | requests ask for citations |
| 119.07(2)(a) | remote electronic access is permitted as an additional means | native-format request |
| 119.07(4)(d) | special service charge permitted where extensive IT/clerical effort is required | fee-estimate and rolling-production language in the drafts |

- **Status: VERIFIED_APPLICABLE.** These are the governing procedures for all
  five drafted requests.
- **Note:** the five requests are `DRAFTED_NOT_SUBMITTED`. No submission
  receipt exists, so no response deadline has begun.

### C1 — § 373.042 (2026), Minimum flows and minimum water levels
Verified full text. Establishes minimum flow/water level authority for the
Department and districts. **Status: UNRESOLVED** as applied here — no minimum
flow or minimum water level has been identified for the specific watercourse
receiving the Tom Street frontage, and none has been retrieved. Not a
compliance standard this investigation relies on.

---

## D. Environmental permitting — applicability deliberately unproven

- **ERP 9220-2** ("Hadleigh Hills, Phase 2 Ext. to P9220-1", applicant
  *Hadleigh Hills Development Group*, 8.1 ac, decided 2016-11-21) was returned as a nearby ERP lead by the **limited archived radius search** near the properties; neither exhaustive permit coverage nor parcel intersection was checked.
  **Status: UNRESOLVED.** No polygon intersection against the parcel polygons
  has been performed; no permit document obtained. It is a lead, not an
  attribution (CON-06, GAP-17).
- **No FDEP-issued ERP** was returned by the archived 2,000-ft query. **Status: UNRESOLVED** — and per the directive, a negative search hit does *not*
  prove no authorisation exists (GAP-18).
- **Construction-stormwater NPDES coverage / common-plan-of-development:**
  **UNRESOLVED.** No CGP coverage record, NOI or common-plan determination has
  been obtained. Nothing here asserts that authorisation was or was not required.

---

## E. Case law — primary opinion verified, application unresolved

**Westland Skating Center, Inc. v. Gus Machado Buick, Inc., 542 So. 2d 959 (Fla. 1989)**, Florida Supreme Court, docket 72492, March 30, 1989.

- **Primary document:** [FSU College of Law docket 72492](https://library.law.fsu.edu/Digital-Collections/flsupct/dockets/72492/72492.html), [11-page corrected opinion](https://library.law.fsu.edu/Digital-Collections/flsupct/dockets/72492/op-72492.pdf), retrieved and text-checked on 2026-10-15. The **original PDF is now archived unchanged** at `08_LEGAL_AND_REGULATORY/SOURCE/PRIMARY_AUTHORITY/Westland_Skating_Center_v_Gus_Machado_Buick_Fla_1989_CORRECTED_OPINION.pdf` with independent SHA-256 recorded in the acquisition manifest.
- **Rule adopted by Court:** Florida applies the **reasonable-use rule** to damage from interference with surface water. The court adopts it at opinion PDF page 6 and describes the comparison of improved-property conduct at PDF pages 7-8.
- **Critical distinction:** compliance with a building code may be evidence of reasonable use but is **not reasonableness as a matter of law** (opinion PDF pages 9-10). This undermines both automatic allegations from high fill and automatic absolution from an approved building permit.
- **Status:** primary text verified; subsequent citator/treatment and direct applicability to actual Tom Street engineering facts **not completed**. No liability finding is asserted.

The original opinion is a legal research source, not a homeowner technical exhibit without factual and legal professional review.
---

## F. Summary

| Authority | Verified? | Applies here? | Blocking dependency |
|---|---|---|---|
| LDC § 3.04.04 obstruction of drainageways | yes, primary PDF | conditionally | identification of the drainageway and of any obstruction |
| LDC § 3.04.05 erosion/sediment control | yes, primary PDF | conditionally | SWPPP applicability; evidence of any discharge |
| LDC § 4.04.01.B PE-sealed plan before permit | yes, primary PDF | conditionally | whether such a plan exists for these lots |
| **LDC § 4.04.01.D.1 (sub-1-acre lots)** | yes, primary PDF | **conditionally — pivotal** | **GAP-11: on-file subdivision lot grading plan?** |
| **LDC § 4.04.01.D.4 (lot grading exemptions)** | yes, primary PDF | conditional, not established | written exemption/pathway and site/fill measurements |
| **LDC § 4.04.01.E (all-lots certified as-built)** | yes, primary PDF | general rule, permit-specific compliance unresolved | certified as-built document, county acceptance and CO stage |
| **LDC § 4.04.01.G-H (swale geometry)** | yes, primary PDF | conditional | approved design, right-of-way acceptance, actual measurements |
| LDC § 4.04.01.D.2.b drainage easement | yes, primary PDF | not applicable on current evidence | — |
| Fla. Stat. § 119.07 (2026) | yes, official text | yes | — |
| Fla. Stat. § 373.042 (2026) | yes, official text | unresolved | minimum flow for the receiving watercourse |
| ERP 9220-2 applicability | record yes, applicability no | **unresolved** | GAP-16 / GAP-17 |
| **Westland Skating Center (Fla. 1989)** | primary FSU corrected opinion checked | factual application unresolved | subsequent treatment and surveyed effects |

**Nothing in this matrix supports a statement that any violation occurred.** The
verified text establishes *what the County's rules require*; the absence of
approved plans, surveys, as-builts and field measurements in this repository
means the compliance question cannot yet be reached in either direction.
## G. Edition and amendment control (October 2026)

The county-hosted LDC edition identifies **Ord. 2025-25 (adopted November 10, 2025)** on its cover, with amendments to §§ 3.04.05 and 4.04.01. An internal PDF creation timestamp in January 2026 must not be reported as a new legal enactment. The 2026 Ordinances index shows later LDC-related enactments, some changing zoning/future-land-use maps. Review each ordinance's effective date and text against the actual permits **created February 11, 2026 and issued March 23, 2026** before asserting any amendment applied or did not apply. Sources: https://santarosa.fl.gov/182/Land-Development-Code and https://library.municode.com/fl/santa_rosa_county/ordinances/code_of_ordinances?nodeId=2026 .

**Jurisdiction and post-issuance ordinance control:** The official [Santa Rosa 2026 Ordinances index](https://library.municode.com/fl/santa_rosa_county/ordinances/code_of_ordinances?nodeId=2026) lists **2026-03 (January 22, wellfield protection overlay)** before the March 2026 permits, and **2026-10 (May 21), 2026-14 (June 22), 2026-16 (July 23)** relating to zoning/land-use map revisions after their issuance. Index descriptions alone do not establish Tom Street parcel applicability. Collect final ordinance text, map exhibits and effective-date clauses, then distinguish law controlling initial review from any later revisions. County [Stormwater Requirements](https://santarosa.fl.gov/197/Stormwater-Requirements) identifies Santa Rosa County Engineering as the subdivision plan reviewer. County [Road Issues](https://santarosa.fl.gov/377/Road-Issues) limits maintenance services to county-maintained roads; **Tom Street maintainer and roadside asset acceptance are unresolved** and must be separately established. See [jurisdiction scope register](JURISDICTION_AND_AUTHORITY_SCOPE_2026-10-15.md). Do not use other Florida county ordinances as controlling local law.

## H. DEP historical order-index leads (official PDFs preserved)

- Official 2023 Q1 FDEP Final Order Report (local `SOURCE/PRIMARY_AUTHORITY/FDEP_FINAL_ORDER_INDEX_2023_Q1.pdf`, page 1): lists Holiday Builders, `OGC 22-2720 / DEP23-0087`, dated February 9, 2023. **Only the index PDF has been obtained, NOT the full signed consent order.**
- Official 2024 Q1 FDEP Final Order Report (local `SOURCE/PRIMARY_AUTHORITY/FDEP_FINAL_ORDER_INDEX_2024_Q1.pdf`, page 2): lists Holiday Builders Inc, `OGC 23-1387 / DEP24-0006`, dated January 10, 2024. **Only the index PDF has been obtained, NOT the signed order.**
- **Both are historical unrelated-case research leads**. The index entries do not identify a breach at 2264 or 2268 Tom Street, nor permit any inference that the builder was negligent in 2026. Request actual signed orders and project identifiers from DEP before citing the matters in external meetings. See [`PRIMARY_SOURCES_README.md`](../08_LEGAL_AND_REGULATORY/PRIMARY_SOURCES_README.md) and `SOURCE/PRIMARY_AUTHORITY/ACQUISITION_MANIFEST.json`.

## I. Pending October 2026 administrative LDC reformat (not a substantive amendment)

A [September 29, 2026 official Santa Rosa County notice](https://santarosa.fl.gov/m/newsflash/Home/Detail/2186) announces a proposed repeal-and-replacement **for formatting and section-navigation only**, with no change to development regulations. The Zoning Board hearing was scheduled for October 8 and the County Commission consideration for **October 22, 2026**. As of the October 15 investigation date, this advertised future Commission action must **not** be described as an already enacted law. For durable citations use **section numbers and ordinance effective dates**, not just PDF page numbers. Confirm final adoption and any intervening revisions directly from the County before later use. The older March 2026 permit dates must be compared to the rules legally controlling at those dates.
