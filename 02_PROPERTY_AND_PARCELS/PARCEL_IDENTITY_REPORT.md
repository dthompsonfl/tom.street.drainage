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

## 2266 Tom Street — current status versus historical evidence

No 2266 situs appears on the archived current Property Appraiser roll. However, 1996–1998 MGO records use **2266 Tom Street**. Do not claim this historical address never existed. Its later addressing/parcel disposition is unverified; request county address-change and recorded parcel history.


## Developer / builder identity

**HOLIDAY BUILDERS INC** is the **owner of record** on both target parcels,
mailing address 2293 W Eau Gallie Blvd, Melbourne, FL 32935-3184.

Note carefully: owner of record, applicant, licensed contractor and engineer of record are different roles. The saved MGO records identify the **permit applicant/business** but do not alone establish the responsible licensed contractor or engineer of record.

## Development of record — two names

| Name | Where it appears | Status |
|---|---|---|
| **Crescent Shores (00780)** | Property Appraiser filing label (not a retrieved recorded plat) | Filing label verified; recorded plat unverified |
| **Hadleigh Hills, Phase 2** | Nearby NWFWMD ERP 9220-2, separate applicant *Hadleigh Hills Development Group* | Nearby indexed permit exists; no verified lot coverage |

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
5. **Outstanding permit attachments, not all permit records:** building-permit identities, current-at-capture statuses and many inspections **were acquired** from MGO, under `03_PERMITS_AND_INSPECTIONS/`. Approved original/revised grading and drainage plans, surveys, driveway/culvert drawings, engineering calculations, certified as-builts and actual CO documents are still unobtained. The earlier acquisition checkpoint was superseded.