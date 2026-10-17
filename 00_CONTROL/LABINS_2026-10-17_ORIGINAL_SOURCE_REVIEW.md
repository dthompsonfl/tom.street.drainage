# Tom Street | LABINS original aerial-image and grid verification

**Source acquisition date:** October 17, 2026 UTC  
**Primary custodian:** Florida Department of Environmental Protection / LABINS, hosted in cooperation with Florida State University FREAC  
**Evidence status:** Actual historic images archived and checksummed; present-day construction drainage and permitted grading remain unverified.

## Verified geographic targeting

The official FSU FREAC LABINS State Plane North imagery-grid MapServer layer **14** returns one polygon with **`spn_id = 648138`**, **OBJECTID 11183**, at each of four representative locations: 2264, 2265, 2268 Tom Street and a corridor center point. The official source layer, attributes, source response URLs, original JSON and SHA-256 capture hashes are preserved at [LABINS Santa Rosa source archive](../11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-17/LABINS_SANTA_ROSA/). This is a reproducible **grid-cell lookup** and **not** a boundary survey or aerial acquisition timestamp.

The County-level grid reference is preserved unchanged as [ORIGINAL_LABINS_SANTA_ROSA_HIRES_GRID_MAP.pdf](../11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-17/LABINS_SANTA_ROSA/ORIGINAL_LABINS_SANTA_ROSA_HIRES_GRID_MAP.pdf), 1,412,537 bytes, SHA-256 `ef95acfb412961dc129ff4aabf285a72fdb748ef767c701626c684ce32961d8f`. The image derivative is clearly separated and cannot replace the original.

## Original public imagery located and downloaded

Using the actual publicly published [LABINS high-resolution image download search](https://www.labins.org/mapping_data/aerials/hi-resolution_images.cfm), entering verified grid `648138` yielded 20 source URLs; the unchanged [official search results](../11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-17/LABINS_SANTA_ROSA/ORIGINAL_LABINS_CELL_648138_SEARCH_RESULT.html) are preserved.

| Published collection | Original MrSID images acquired | Acquired ancillary originals | Verified download result |
| --- | --- | --- | --- |
| **2007** | Normal-color and color-infrared originals | Two `.sdw`, two `.aux` | 6 of 6 |
| **2010** | Normal-color | `.sdw`, `.aux` | 3 of 3 |
| **2013** | Normal-color | `.sdw`, `.aux` | 3 of 3 |
| **2016** | Normal-color | `.sdw`, `.xml` | **3 of 4**; original `OP2016_NC_648138_24.aux` returned HTTP 404 |
| **2019** | Normal-color | `.sdw`, `.aux`, `.xml` | 4 of 4 |
| **Total** | **6 original MrSID images** | **13 original companion files** | **19 of 20 original public links saved** |

Original untouched bytes and per-year `ACQUISITION_MANIFEST_<year>.json` SHA-256 records are retained under [ORIGINAL_IMAGERY_CELL_648138](../11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-17/LABINS_SANTA_ROSA/ORIGINAL_IMAGERY_CELL_648138/), never overwritten by derived JPEG or modified GIS. Source integrity was verified using per-file SHA-256, file size, real MrSID header bytes, six-value world files, and XML parser where applicable. The missing 2016 `.aux` is a genuine publicly broken URL, not a substitute-created file.

### Original metadata confirms wider flight periods

- **2016 Accuplus:** original FGDC XML lists project-wide aerial collection **December 7, 2015 through February 6, 2016** and publication date **June 7, 2016**.
- **2019 Accuplus:** original FGDC XML lists project-wide collection **January 25 through March 6, 2019** and publication date **January 24, 2020**.

These intervals describe the *projects*, **not exact exposure times of the specific 648138 frame**. Aerial photographs are planimetric visual evidence; they do **not** establish topographic height differences, driveway/culvert invert elevations, hydraulic positive outfall, or that Holiday Builders caused any drainage condition.

## Independent validation and evidence reconciliation

The source files, official responses and negative controls are individually registered under **`SRC-PRE-013` through `SRC-PRE-041`** in [SOURCE_REGISTER.csv](SOURCE_REGISTER.csv), separately numbered **`EX-52` through `EX-80`** in [EXHIBIT_INDEX.csv](EXHIBIT_INDEX.csv), and bounded under **`CLM-044` through `CLM-052`** with one or more original-file hash links per material claim in [EVIDENCE_LEDGER.csv](EVIDENCE_LEDGER.csv) and [CLAIM_SOURCE_LINKS.csv](CLAIM_SOURCE_LINKS.csv).

The independent read-only test `python tools/check_labins_primary_sources.py` verifies 29 source files (including the original map, GIS query results, public source-search files and Property Appraiser negative control), 19 downloaded originals, metadata and original file headers, the lone 2016 auxiliary gap, registry SHA-256 and all claim/source mappings. The [GitHub validation workflow](https://github.com/dthompsonfl/tom.street.drainage/actions/workflows/verify-labins-evidence.yml) has a read-only `contents: read` permission and is not an automatic publication workflow. **A successful checksum audit certifies custody of bytes, not the sufficiency of evidence for a drainage conclusion.**

### Related finding that must not contaminate the packet

A separate Property Appraiser `/plat/query` search with `phase=00780` returned **SENTINEL RIDGE PHASE 1**, code `04933`, rather than Crescent Shores. The original [unrelated result](../02_PROPERTY_AND_PARCELS/CLERK_LOT_QQ_DISCOVERY_2026-10-17/ORIGINAL_SRCPA_PLAT_QUERY_00780.json) is retained as a *negative control*. It does **not** identify the subject subdivision and does not contradict the official recorded Clerk Crescent Shores Plat A/70. The subdivision code in the parcel roll cannot safely be substituted for an undocumented `phase` search parameter.

## Material open records and next steps

1. **FDOT APLUS 2022 and 2025 original Santa Rosa image frames, orthophotos, exact Tom Street coverage and flight dates:** the [FDOT official catalogue](https://fdotwww.blob.core.windows.net/sitefinity/docs/default-source/co-gis/aplus/aerial-photography-listecc67b89-a9cc-4abe-9516-b7e8a977c432.pdf) lists these years for Santa Rosa County, but does not guarantee this specific street. Their *actual site-covering images* remain missing. LABINS grid ID `648138` is useful context but may differ from FDOT's indexing system.
2. **2016 LABINS missing `.aux` file:** request an alternative County/FREAC file if georeferencing tools need it; original image, `.sdw` and FGDC XML exist, so do not describe the year as entirely missing.
3. **Later Lot QQ title instruments and recorded drainage/road easements:** original Clerk Plat A/70 and 2017 multi-parcel deed lead do not reconstruct current lots.
4. **County approved grading/site plans and certified as-builts for BP-2026-1621 and BP-2026-1612:** still unavailable; no refreshed authenticated MGO permit status.
5. **Roadway swale, stormwater structure and outfall measurements:** obtain engineering field survey in a consistent vertical datum before attributing a drainage deficit.
6. **On-site homeowner originals, metadata and consent:** only private, lawful intake with copies and provenance; never deposit unreviewed resident images into the public repository.

**No public-records request or site inspection is represented as sent or performed by this source-acquisition work.** The corresponding request drafts remain unsigned and unsent. Six temporary self-publishing data-acquisition workflow files were removed after an existing governance test revealed that automatic direct-main writes violated repository safeguards; only the already reviewed/preserved originals and safe local scripts remain. Ongoing verification workflows are read-only.
