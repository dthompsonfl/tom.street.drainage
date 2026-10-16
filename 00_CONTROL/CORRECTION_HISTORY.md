> **HISTORICAL ERRATUM (2026-10-15):** The correction log below itself made statements that 2266 never existed and that the archived Clerk results conclusively proved a deed's parcel association. Historical MGO permit records use 2266. The saved Clerk item is a search grid, not the native deed image. Original quoted excerpts do not establish verbatim preservation of all older source notes. See current reconciled documents.

# CORRECTION HISTORY — LEGACY RESEARCH CLAIMS

This file preserves, verbatim, every factual claim made by the earlier research
pass **before** verification against official government records. It is kept so
that the audit trail of "what was previously asserted" survives even though the
note files themselves have been overwritten with verified data.

Verification date: 2026-10-15
Verified against: Santa Rosa County Property Appraiser official roll
(`search.srcpa.gov`), Santa Rosa County Clerk AcclaimWeb official records.

---

## CLAIM 1 — parcel numbers (from MLS listing research)

Original assertion, preserved verbatim:

> - 2268 Tom Street (Site A): 21-2S-26-0780-0QQ00-1060 (confirmed from MLS/web search)
> - 2265 Tom Street (existing): 21-2S-26-0780-0QQ00-1180 (confirmed from RealtyHop/web search)
> - 2264 Tom Street: Reported as 21-2S-26-0780-0QQ00-1490 (needs verification)

Also recorded previously as:

> Subdivision: Crescent Shores area; MLS notes "NO RECORDED SUBDIVISION"
> Legal description reference: Begins in ORB 3492 PG 700 (from MLS)

**VERIFICATION RESULT — parcel numbers were transposed.**

| Address | Previously asserted | Officially verified | Verdict |
|---|---|---|---|
| 2264 Tom St | `21-2S-26-0780-0QQ00-1490` | **`21-2S-26-0780-0QQ00-1020`** | WRONG |
| 2268 Tom St | `21-2S-26-0780-0QQ00-1060` | **`21-2S-26-0780-0QQ00-1490`** | WRONG |
| 2265 Tom St | `21-2S-26-0780-0QQ00-1180` | **`21-2S-26-0780-0QQ00-1180`** | CORRECT |
| 2266 Tom St | unresolved | **no such address exists** | RESOLVED |

`21-2S-26-0780-0QQ00-1060` is in fact **2274 Tom St**, owner MATIG-A CEPRIANO P JR.

## CLAIM 2 — official records book/page reference

Original assertion:

> Previous research identified Official Records Book 3492, page 700 as a lead.

**VERIFICATION RESULT — the lead is real but was misattributed.**
ORB 3492 PG 700 is instrument **201603296**, recorded 2016-01-28, a DEED from
MATIGA CIPRIANO A SR to MATIGA CEPRIANO P JR for $500.00, legal description
"**21-2S-26 POPE SUBD LOT 22 UNREC**". That transaction corresponds to
**2274 Tom St**, not to 2268 Tom St. The MLS listing text was carrying an
unrelated book/page reference.

## CLAIM 3 — "NO RECORDED SUBDIVISION"

Original assertion:

> MLS notes "NO RECORDED SUBDIVISION"

**VERIFICATION RESULT — not yet resolved either way.** The Santa Rosa County
Property Appraiser officially files both target parcels under
"CRESCENT SHORES (00780)". Whether a *recorded plat* exists for that filing has
not been determined: the Clerk's Legal Search endpoint
(`/search/SearchTypeLegalSearch`) returns HTTP 404 and the party-name index
exceeds the result limit. This remains an open question — see
`00_CONTROL/PERMIT_DOCUMENT_INVENTORY.csv` entry `DOC-SHARED-9004`.

## CLAIM 4 — verification status of legacy evidence files

Original assertions, preserved verbatim:

> `sha256_hash: SHA256_PENDING` on all three source-register entries
> `file_size_bytes: 0` on all three source-register entries
> SRC-001 status: `VERIFIED_FROM_WEBSEARCH`
> SRC-002 status: `NOT_VERIFIED`
> SRC-003 status: `NOT_VERIFIED`

**VERIFICATION RESULT — these were never official records.**
The three source entries pointed at hand-typed web-search note files, not at
downloaded government documents. The status `VERIFIED_FROM_WEBSEARCH` was
misleading and has been replaced with `SUPERSEDED_NOT_OFFICIAL`. No file in
this project is now marked verified unless it exists on disk, is non-empty,
has an identified file type, and has a computed SHA-256 recorded in
`00_CONTROL/EVIDENCE_MANIFEST.csv`.

## CLAIM 5 — developer identity

Original assertion:

> 2264 Tom St ... New construction (Holiday Builders?)

**VERIFICATION RESULT — confirmed from an official source.**
The Santa Rosa County Property Appraiser official roll lists
**HOLIDAY BUILDERS INC** as the **owner of record** of both
21-2S-26-0780-0QQ00-1020 (2264 Tom St) and 21-2S-26-0780-0QQ00-1490
(2268 Tom St), with mailing address 2293 W Eau Gallie Blvd, Melbourne, FL 32935.

This establishes builder/owner identity. It does **not** yet establish who the
permit applicant or the licensed contractor of record is; that requires the
MGO permit records, which are account-gated.

## CLAIM 6 — development name

**VERIFICATION RESULT — a second development name has surfaced.**
The only Environmental Resource Permit within 2,000 ft of either target parcel
is **NWFWMD ERP Official Permit ID 9220-2**, project "**Hadleigh Hills, Phase 2
Ext. to P9220-1**", applicant **Hadleigh Hills Development Group**, ERP
Individual, 8.1 acres, Santa Rosa County, decided 2016-11-21.

This indicates "Hadleigh Hills" is likely the **development of record** while
"Crescent Shores (00780)" is the **Property Appraiser filing/plat name**.
All future county, clerk and water-management-district searches should be run
under **both** names.