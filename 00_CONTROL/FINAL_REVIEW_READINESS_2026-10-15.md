# Tom Street | Final evidence-packet review and release decision

**Review date:** October 15, 2026 (Central) / October 16, 2026 (UTC)  
**Repository:** [dthompsonfl/tom.street.drainage](https://github.com/dthompsonfl/tom.street.drainage), `main`  
**Frozen scope:** 210 Git-tracked files at commit `c76cef942dc23ecaf1dd338804e3212b245490d6`, enumerated individually by path, size and Git object ID in `00_CONTROL/FINAL_FILE_SCOPE_INVENTORY_2026-10-15.csv`. This snapshot is immutable history; subsequent commits are not represented until another inventory is generated.

## Decision

**Public packet status: DRAFT. Engineering/legal evidentiary package: NOT COMPLETE.** The current `15_RECONCILED_DRAFTS/pdf/` packet has five one-page components and checksum-controlled ZIP output and is fit for homeowner editorial review and a factual request for county assistance. It has **not** been approved/signed by the homeowner, visually certified in final print form, or established as proof of permit violation, improper grading or causation.

## Audited scope and what “reviewed” means

| Scope | Determination | Boundary |
| --- | --- | --- |
| Repository inventory and navigation | 210 tracked files catalogued by path/role/object ID; canonical folder separated from superseded historic release | Git file inventory is **not** proof every sentence of archived research or every original camera file was independently authenticated |
| Canonical meeting drafts | Five editable homeowner drafts plus combined five-page PDF/ZIP, signed-off status `DRAFT_NOT_APPROVED_FOR_EXTERNAL_DISTRIBUTION` | Text is not a legal brief or PE certification; final homeowner approval outstanding |
| Source-to-claim and checksum controls | County parcel/permit capture, inspections, source hashes, exhibit statuses, and registry joins tested in existing CI; source-specific cross-check and targeted narrative audit conducted | Integrity controls verify bytes and documented scope, not hydrologic effects or permit lawfulness |
| Property identifiers | 2264 and 2268 address/parcel/permit pairs established in preserved PA and MGO snapshots | 2266 historical address disposition and older 2000 mobile-home link to current 2268 **not proven** |
| Engineering record completeness | **Not complete**: original approved grading/ROW/culvert plans, preconstruction surveys, positive outfall elevations and certified as-builts not acquired | A passed inspection comment or empty customer attachment endpoint is not a sealed design nor proof a document does not exist |
| Environmental authority | Nearby NWFWMD ERP 9220-2 identified as spatial **lead only** | No site polygon or hydraulic-basin overlap shown; CGP/ERP requirements/exemptions not decided |
| Legal research | Santa Rosa County LDC PDF, corrected Florida Supreme Court *Westland* opinion and two Florida DEP quarterly order **indexes** preserved as separate references | LDC ordinance effective-date and any exceptions need permit-date review; actual signed DEP orders and later caselaw treatment not obtained |
| Residents' photographs | Two recent archives and nested packages were independently byte-inventoried (179 entry positions); 15 JPEG **copies** matched archived hashes | Native originals, standard EXIF capture dates, permissions, dated storm-to-photo crosswalk and site attribution unverified; originals **not published** |
| Public records requests | Five custodian-specific Chapter 119 drafts in `13_PUBLIC_RECORDS_REQUESTS/` plus additional targeted requests | No mailing/sending/acknowledgment/production receipts; status must remain drafted |
| Public repository privacy | Historic authenticated captures previously disclosed; current distribution excludes raw resident photos | Removing tracked files did not remove exposure in earlier Git history; separate authorized cleanup decision needed |

## Material corrections completed during this review

1. **Single current packet:** root README now points to `15_RECONCILED_DRAFTS` and warns that `14_MEETING_PACKET` and `releases/2026-10-15` are superseded. The obsolete legacy packet generator is disabled.
2. **Permit-file claim classification:** 2264 and 2268 completeness sheets distinguish customer-visible inspection remarks from an approved driveway permit, engineering drawings, a site-linked environmental authorization or the full enforcement file. Historical addresses and permit leads no longer prove completed replatting or fill change.
3. **Title/parcel cautions:** original deed image for ORB 3492/700 not obtained. A Clerk results grid is insufficient to tie the instrument conclusively to a different current lot. 2266 historical MGO address exists but alleged renumbering remains unverified.
4. **Legal-version control:** LDC cover reflects Ordinance 2025-25 (November 10, 2025), not a January 2026 enactment merely because PDF metadata says January. The County's September 29, 2026 [announcement](https://santarosa.fl.gov/m/newsflash/Home/Detail/2186) advertised an October 22 consideration of **format-only** LDC reorganization; do not call it enacted as of October 15. Use section numbers plus effective dates.
5. **Original legal exhibits:** corrected 1989 `Westland` opinion and the 2023/2024 DEP quarterly indexes now have separate exhibit identifiers. The DEP **signed orders** are not among the acquired primary documents.
6. **No automatic compliance findings:** open `Certified Drainage as Built: Assigned` tasks do not prove certification non-submission, lateness or violation. The pipe/inlet instructions are not an installation/as-built record.

## Highest-priority blocking documents and people

1. **County Engineering / Development Services:** Complete approved original/revised signed/sealed site, lot-grading and stormwater plans and calculations for `BP-2026-1621` and `BP-2026-1612`; document-index and governing review conditions, engineer of record, and exact status of any grading/as-built and CO files.
2. **County Public Works:** Roadside right-of-way, pipe, inlets, swale/outfall layout, invert/grade records, acceptance, easements, maintenance history and documented current condition at the Tom Street frontage. Confirm any responsibility of builder versus County versus owner/HOA; do not assume.
3. **Clerk and County addressing:** Recorded deeds, real plat(s), ROW/easements, lot legal descriptions, historical 2266 disposition and disputed 2000 permit parcel association.
4. **NWFWMD/FDEP:** Site boundaries, actual ERP approval or exemption and any CGP/NOI records; obtain signed DEP consent orders only if historical matters are intended for separate research.
5. **Homeowner evidence and qualified inspection:** Native photos, reliable capture times and permission; contemporary baseline and post-fill surveys, rainfall context and an independent Florida surveyor/PE to evaluate design-versus-field and plausible alternative runoff causes.
6. **Process:** Get homeowner approval, send records requests, preserve receipt IDs, log every production, have County commit to a site-review/response schedule.

## Release control and honest conclusion

- **Suitable now:** calm, nonaccusatory letter to commissioner and County and a bounded list of engineering questions, clearly marked draft, after resident confirms names/addresses and signs.
- **Not suitable now:** an exhibit package alleging unlawful filling, defective drainage, negligence, unpermitted shared pipe or a builder-specific regulatory history connected to Tom Street.
- **Evidence preservation:** do not rename/recompress originals or delete previous source captures; maintain checksum and retrieval date. Review private-data history exposure before any broad sharing.
- **Testing:** GitHub CI checks structure/byte integrity and selected claim invariants. A successful automated run **does not equal final factual/legal/engineering certification**; the latest run and head must be confirmed after the last edit.

**Audit limitation:** all 210 tracked files were inventoried by Git path/object metadata and substantive high-risk narratives, registers and primary-capture links were reviewed; not all historical source documents, camera-native files, and archived third-party workspaces were independently re-authenticated or read line-by-line in this pass. Completeness cannot be certified without County records and the remaining archives.
