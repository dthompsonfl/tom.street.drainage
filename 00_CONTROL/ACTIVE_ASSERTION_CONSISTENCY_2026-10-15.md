# Active assertion consistency | Tom Street

**Review scope:** Current `main` narratives, claim/exhibit/source crosswalks, permit and property registers, recorded events and the controlled homeowner packet. Earlier uncorrected documents in `14_MEETING_PACKET/`, `releases/` and the 2026-10-15 acquisition/baseline logs are **historical evidence of research decisions**, not controlling assertions. Source bytes and prior Git revisions are preserved.

**Decision criterion:** Zero known unqualified **mutually conflicting assertions** across the *current* evidence register and public draft documents after source-specific reconciliation and automated tests. This is **not** a claim that all facts are known, all historically incorrect text has been erased, every photo is authenticated, or any engineering/legal conclusion has been proved.

## Canonical statements (must not be contradicted in current materials)

| Topic | Controlled statement | Evidence scope |
| --- | --- | --- |
| 2264 Tom Street | PA parcel `21-2S-26-0780-0QQ00-1020`; MGO `BP-2026-1621`, Active **in the archived October 2026 snapshot** | Separate PA export and MGO project JSON |
| 2268 Tom Street | PA parcel `21-2S-26-0780-0QQ00-1490`; MGO `BP-2026-1612`, Active **in the archived October 2026 snapshot** | Separate PA export and MGO project JSON |
| 2265 Tom Street | Existing nearby property, PA parcel `21-2S-26-0780-0QQ00-1180`; **not a subject construction permit** | PA export |
| 2266 Tom Street | Absent from the saved present-day PA street-roll query; historic MGO permits use 2266. **No proven renumbering, merger or later disposition** | Different dates/systems, not a factual contradiction |
| 1996/2000 permit leads | Historical permit entries exist; attribution to legally identical current lots not established by old street labels alone; 2000 leads cite a parcel now mapped to 2274 | Require Clerk legal descriptions/address history |
| 2264 driveway pipe | August 6 inspector **instructed** proposed work at nearby addresses; **no approved design, installed pipe or drainage capacity demonstrated** | MGO comment only |
| 2268 ditch/roadway | Archived inspector comments **refer** to ditch and matching grade; no actual slope, level or downstream capacity measured | MGO comment only |
| MGO drainage certificates | Both saved requirement snapshots: `Certified Drainage as Built = Assigned`; whether submitted, filed, accepted, required immediately, late or missing is **unverified** | Administrative task ≠ original signed letter |
| MGO attachments | Authenticated **customer-visible endpoints** returned zero files for each site; **County-held original drawings cannot be inferred absent** | Two separate preserved API results |
| FEMA | Query points near target properties returned Zone X; **no whole-parcel flood designation or drainage-adequacy conclusion established** | Sampled NFHL queries |
| ERP 9220-2 | Nearby NWFWMD **spatial search lead**; scope, project boundary, hydraulic basin and target-site authorization unverified | Limited radius result only |
| Land Development Code | County PDF identifies November 10, 2025 / Ord. 2025-25; January 13, 2026 is internal file metadata. **Controlling permit-date amendment and exemptions remain fact dependent** | County code; code-reformat proposal not enacted as of Oct 15 |
| Clerk ORB 3492/700 | Saved Clerk **results grid** contains a candidate instrument; **recorded deed image and association to a specific modern parcel remain unverified** | Not a title opinion |
| DEP Holiday Builders filings | Two official quarterly **index** entries archived; **signed consent orders and Tom Street relevance not established** | No site-specific misconduct finding |
| Homeowner photographs | Fifteen archived JPEG **copies** internally hash-matched; native device files, dates, exact parcel assignments and permission not authenticated | No public original-photo exhibit |
| Records requests | **Five foundational and three supplemental draft files (eight files containing nine request/service templates).** **Zero verified sending receipts.** | Never mark as submitted until proof retained |
| Engineering effects | Approved site designs, true surveyed pre/post grades, outfall/inverts, runoff modeling, ownership and responsibility **not established** | No violation, negligence or causation conclusion |

## Research contradictions versus outstanding questions

For interpretation of stale statuses and formerly incorrect claims, see [historical snapshot and reading-order control](READING_ORDER_AND_SNAPSHOT_STATUS.md).

The original `00_CONTROL/CONTRADICTION_LOG.csv` intentionally documents **earlier conflicting assertions**, including wrong parcel attributions and overstatements about nonexistent plans, ERP scope, task states and photograph provenance. Keeping that ledger is correct evidence practice. The live statements above accept **only supported propositions**, and assign genuinely unresolved questions a single status of **UNVERIFIED/NOT_OBTAINED**, not competing assertions.

The remaining engineering plans, surveys, signed permits and photo originals are **external verification gaps**, not contradictions to be resolved by rewriting. The legal opinion and DEP index PDFs are general/reference sources, not proof of a Tom Street drainage defect.

## Enforcement

`python3 tools/check_repository_consistency.py` validates PA/MGO primary pairs, capture-date limitations, permit inventory site bindings, the 1996/2000 historical distinctions, current five-page PDF draft status, eight unsent draft files, permit-access snapshot scope, limitations of FEMA/ERP/photographs, and that old reports are conspicuously historical. `tools/check_document_claims.py` separately validates precise claim→exhibit→primary-source parity, including **both** lots and both neighboring driveway histories.

**Audit limitation:** Neither text patterns nor repository source hashes can certify that every statement in every old archive is factually correct. The tests are a bounded set of reproducible invariants. They cannot substitute for actual County engineering-file production, independent measurements, legal-effective-date verification, permission to release photos or homeowner review.

## October 16: verified road classification and remaining questions

**October 16 follow-up:** the target road is **County Maintained** in County GIS; asset ownership/maintenance remains unresolved. Actual Ordinances 2025-25 and 2026-03 and the generic grading guideline are now preserved. Clerk-certified electronic transmission dates are not separate Department of State filing receipts. No lot-specific approved plan, exemption, surveyed invert/outfall, or matched ERP/CGP authorization was obtained. See [17_CURRENT_RESEARCH/FIVE_QUESTION_FINDINGS_2026-10-16.md](../17_CURRENT_RESEARCH/FIVE_QUESTION_FINDINGS_2026-10-16.md) and its source links.
