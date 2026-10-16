# Parcel Identity Report — Tom Street, Navarre, Santa Rosa County, Florida

**Status: VERIFIED against official records, 2026-10-15.**
Supersedes the earlier draft of this file, whose parcel numbers came from MLS
listing research and were wrong. Original claims preserved verbatim in
`00_CONTROL/CORRECTION_HISTORY.md`.

## Primary construction sites

| # | Address | **Verified parcel ID** | Parcel key | Owner of record |
|---|---|---|---|---|
| A | 2264 Tom Street, Navarre FL 32566 | **21-2S-26-0780-0QQ00-1020** | 10082028 | HOLIDAY BUILDERS INC |
| B | 2268 Tom Street, Navarre FL 32566 | **21-2S-26-0780-0QQ00-1490** | 10082068 | HOLIDAY BUILDERS INC |

Both are improved (`vacantImproved = I`), zoned **R2M**, and filed by the
Property Appraiser under **CRESCENT SHORES (00780)** — lot 1020 and lot 1490
respectively, Section 21, Township 2S, Range 26, Block 0QQ00.

## Existing affected residence

| Address | Verified parcel ID | Parcel key | Owner of record |
|---|---|---|---|
| 2265 Tom Street | 21-2S-26-0780-0QQ00-1180 | 10082042 | BOGART CHRISTOPHER DAVID & |

Also R2M / Crescent Shores (00780), lot 1180.

## 2266 Tom Street — resolved

**There is no 2266 Tom Street.** The official Tom Street roll contains no
parcel with that situs address; the numbering sequence simply skips it
(2263 → 2264 → 2265 → 2267 → 2268 → 2269). 2266 must not be substituted for
either target site.

## Developer / builder identity

**HOLIDAY BUILDERS INC** is the **owner of record** on both target parcels,
mailing address 2293 W Eau Gallie Blvd, Melbourne, FL 32935-3184.

Note carefully: owner of record ≠ permit applicant ≠ licensed contractor. Those
roles are only established by the MGO permit records, which are account-gated.

## Development of record — two names

| Name | Where it appears | Status |
|---|---|---|
| **Crescent Shores (00780)** | Santa Rosa County Property Appraiser filing/plat name | Verified |
| **Hadleigh Hills, Phase 2** | NWFWMD Environmental Resource Permit 9220-2, applicant *Hadleigh Hills Development Group*, 8.1 ac, decided 2016-11-21 | Verified ERP record within 2,000 ft |

Both names must be used in further county, clerk and water-management-district
searches.

## Method

`search.srcpa.gov` is a Remix application. The public search form POSTs to
`/property/query`, which returns JSON. Field names were taken from the live
HTML form. Per-parcel official record exports were retrieved with
`POST /property/export/selected` using the internal parcel key. No login,
captcha or access control was involved.

Reproduce with:

```
python3 00_CONTROL/tools/srcpa_acquire.py
```

## Still not established from an official source

1. Recorded legal description for lots 1020 and 1490.
2. Recorded subdivision plat for Crescent Shores (00780), and whether any
   recorded plat exists at all.
3. Deeds in the chain of title for the two target lots.
4. Building card, improvement history and sales history.
5. **All permit records** — building permits, approved grading plans,
   drainage drawings, surveys, driveway/culvert permits, inspections,
   certified as-builts and certificates of occupancy. MGO Connect requires an
   account; see `00_CONTROL/ACQUISITION_CHECKPOINT.md` §9.