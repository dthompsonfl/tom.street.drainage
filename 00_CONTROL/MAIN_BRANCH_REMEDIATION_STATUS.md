# Main branch remediation and outstanding evidence gates

**As of:** October 15, 2026 (U.S. Central) / October 16, 2026 (UTC)  
**Branch:** `main`  
**Release state:** **DRAFT / ENGINEERING RECORDS OUTSTANDING**

This report distinguishes verified code/document-control corrections from engineering evidence that cannot be obtained or proven merely by editing the repository.

## Implemented directly on `main`

| Control | Remediation | Revision |
|---|---|---|
| Shared drainage interpretations | Corrected 2260/2270 parcel mapping; removed claims that an inspection instruction proves installed pipe, outfall capacity, lack of freeboard, or that an assigned certification task proves a signed document does not exist | `d9a212e` |
| Action inventory | Replaced the stale unstarted-search checklist with permit-specific acquisition blockers and exact needed records | `6d1b46b` |
| County law source | Registered the existing 509-page official Land Development Code PDF by source path, public URL, byte size and verified SHA-256; governing edition/effective amendments require separate verification | `fa5516d` |
| Evidence-manifest reliability | Changed `validate_evidence.py` to index only primary-source evidence, excluding mutable registers, generated release files, private vault contents and its own checksum; rebuilt the 60-file source manifest | `eb47b15` |
| Evidence tests | Manifest tests now require exact source-file coverage, correct file sizes/hashes and unique IDs including the permit document inventory. Release ZIP parity test now uses the actual path in `RELEASE_MANIFEST.json` | `eb47b15` |
| Legacy-tool safety | Disabled obsolete `build_registers.py` and `build_registers2.py` entrypoints that could overwrite current registers with superseded assumptions | `4890bf3`, `133fd88` |
| Continuous verification | Added main-branch CI evidence invariant checks to the PDF draft workflow | `acff132` |

Other commits made by the concurrent project agent already corrected the duplicated `DOC-2264-0001` and `DOC-2268-0001` records, preserved Florida opinion/DEP index PDFs, and produced the newer `15_RECONCILED_DRAFTS/` materials. Do not replace that work with an earlier ZIP.

**Validation:** GitHub Actions build `38849972154` completed successfully after the main-branch evidence validator and CI changes. Passing CI establishes the specified source/file/release consistency checks, **not** drainage adequacy, county compliance, or complete possession of agency records.

## Open material requirements, not solved by a Git commit

1. **BP-2026-1621 / 2264 Tom St:** Original approved and revised lot-grading/site plans; surveys; positive outfall, roadway pipe/inlet drawings and invert elevations; complete engineering review; installed-as-built and CO documents if issued.
2. **BP-2026-1612 / 2268 Tom St:** Same original design, review, grade/capacity, drainage/ROW and certification records.
3. **Shared Tom Street system:** Subdivision master grading and drainage plans, surveyed swales/culverts and downstream outlet, maintenance and easement documents, complaint history and field condition.
4. **Clerk records:** Actual recorded deed/plat/easement images and verified title/parent-parcel history. A search-results grid is not a recorded instrument.
5. **Environmental authority:** Scope and applicability of ERP 9220-2 and any other ERP/CGP coverage or exemptions. Mere proximity does not establish a permit connection.
6. **Engineering verification:** Pre-development and current site elevations, documented storm event data and measured outfall/invert values; potential alternative explanations must be evaluated.
7. **Original photos:** Full originals/metadata and owner publication permissions are still necessary for evidentiary exhibits; preserve privately before creating approved public derivatives.
8. **Agency requests:** Five draft Chapter 119 requests remain **DRAFTED_NOT_SUBMITTED**; do not report requests as sent without actual transmission and receipts.
9. **Legal record:** Confirm the historically controlling ordinance versions and any relevant effective amendments; opinions and case summaries do not prove site-specific wrongdoing.
10. **Public privacy/history:** The repository is public; historical authenticated captures were previously committed. Untracking them does not remove old Git-history exposure. Any history rewrite or publication of restricted documents requires explicit, coordinated approval.

## Publication rule

Use `15_RECONCILED_DRAFTS/` as the current text baseline. Preserve the superseded `14_MEETING_PACKET/` and `releases/2026-10-15/` as archival versions, **not final distributable proof**.

Request and validate the actual agency drawings and certifications first. Maintain real file hashes and source IDs; keep missing documents as explicit gaps. Publish only reviewed, appropriately redacted, dated and citation-checked versions.

**Next highest-value action:** Produce and obtain the county's complete grading, drainage, driveway/ROW and engineer-certification file for each permit, then commission or request an independent, measured comparison with the surrounding roadway drainage system.

## October 16: verified road classification and remaining questions

**October 16 follow-up:** the target road is **County Maintained** in County GIS; asset ownership/maintenance remains unresolved. Actual Ordinances 2025-25 and 2026-03 and the generic grading guideline are now preserved. Clerk-certified electronic transmission dates are not separate Department of State filing receipts. No lot-specific approved plan, exemption, surveyed invert/outfall, or matched ERP/CGP authorization was obtained. See [17_CURRENT_RESEARCH/FIVE_QUESTION_FINDINGS_2026-10-16.md](../17_CURRENT_RESEARCH/FIVE_QUESTION_FINDINGS_2026-10-16.md) and its source links.
