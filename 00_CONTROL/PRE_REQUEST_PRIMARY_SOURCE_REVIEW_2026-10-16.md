# Pre-request primary source results | Tom Street

**October 16, 2026; Santa Rosa County, Florida.** This is an evidence-custody report, **not** a title opinion, engineering survey or finding of Holiday Builders misconduct.

## Acquired official original documents

**1. Crescent Shores recorded subdivision plat:** Santa Rosa Clerk `PLAT A/70`, document `875693`, **2 original scanned sheets**; the second sheet is marked **70 A**. [View original PDF](../02_PROPERTY_AND_PARCELS/PRE_REQUEST_OCT16_PRIMARY_LOOKUPS/ORIGINAL_CLERK_PLAT_BOOK_A_PAGE_70.pdf) or [Clerk official source](https://acclaim.srccol.com/AcclaimWeb/Image/DocumentPdfAllPages/875693). SHA-256 `37b48f9c727e42163bbca3f407c9e827b3baf7cd106b86f457d38e9c6ac36d1`; 3,377,943 bytes. The 1946 source includes original dedication language concerning streets and roads on that plat. This **does not prove County acceptance or drainage facility ownership**, nor identify the modern target lot dimensions. Display-only rendered images and a separate SHA-256 render manifest are under [plat display derivatives](../02_PROPERTY_AND_PARCELS/PRE_REQUEST_OCT16_PRIMARY_LOOKUPS/PLAT_A_70_DISPLAY_DERIVATIVES/).

**2. Fresh County Property Appraiser exports:** four exact-address/parcel source records confirm **2264 `...-1020`, 2268 `...-1490`, 2265 `...-1180`, 2274 `...-1060`** at the October 16 capture. [Original agency JSON](../02_PROPERTY_AND_PARCELS/PRE_REQUEST_OCT16_PRIMARY_LOOKUPS/) is archived with hashes. This establishes current tax situs identity, not title, surveys or elevations.

**3. Historic County stormwater mapping:** fresh [hosted GIS original geometry and metadata](../11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/COUNTY_STORMWATER_HOSTED_FEATURE/) includes feature **2068**, with the previously recorded GlobalID and source **Road & Bridge Maps Marked Up by Foreman**. It corroborates source presence at a representative point, not the original mapping date, flood severity, builder causation or hydrologic capacity.

Each original source has an ID in [SOURCE_REGISTER.csv](SOURCE_REGISTER.csv), supporting exhibit in [EXHIBIT_INDEX.csv](EXHIBIT_INDEX.csv), evidence-limited claims in [EVIDENCE_LEDGER.csv](EVIDENCE_LEDGER.csv) and preserved source-file links in [CLAIM_SOURCE_LINKS.csv](CLAIM_SOURCE_LINKS.csv).

## Retrieved but not publicly republished

[Clerk OR Book 3653, Page 976](https://acclaim.srccol.com/AcclaimWeb/Image/DocumentPdfAllPages/3266090) (3 pages) and [OR Book 718, Page 289](https://acclaim.srccol.com/AcclaimWeb/Image/DocumentPdfAllPages/7838) (4 pages) were accessed and their source hashes/page counts recorded, but signed/third-party images are **not in this public Git repository**, awaiting privacy and lot-attribution review. The recorded source descriptions reference Lot QQ / Pope Subdivision; these are not verified links to either current property deed.

## DEP and NWFWMD public point-source checks

Four original [FDEP/NWFWMD public GIS responses](../09_ENVIRONMENTAL_PERMITS/PRE_REQUEST_PUBLIC_PERMIT_REFRESH_2026-10-16/) were archived with SHA-256 hashes. FDEP stormwater map queries returned **zero facility points within 500 m** of the selected location, and **one point within 2 km named Soundside Hollow / FLR10WY27** with no demonstrated connection to either Tom Street construction parcel. NWFWMD ERP ID 9220 returned one Hadleigh Hills Phase 2 **sequence 2 point feature**.

These limited public map returns do **not** establish a no-record determination, whether CGP or ERP authorization covers either lot, or any permitting violation. Actual agency documents, boundaries, operator and common-plan status remain unverified. Source and claim ledgers now include `SRC-PRE-009`–`SRC-PRE-012` and `CLM-042`–`CLM-043`.

## Acquisition attempts that remain open

- **2022 County aerial originals:** live County MapServer metadata did not yield usable source information; direct tile requests at four zoom levels returned HTTP 404. [The official attempted acquisition manifest](../11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/COUNTY_2022_CACHED_ORTHOPHOTO/ACQUISITION_MANIFEST.json) lists failures. This is **not a County no-records determination**. FDOT APLUS original site-covering imagery, exact flight dates and an alternative County-held dataset are needed.
- **Later Lot QQ parcels/easements:** despite original 1946 Plat A/70 being saved, all subsequent subdivision/conveyance instruments connecting current `-1020` and `-1490`, road acceptances, maintenance and drainage easements remain unverified.
- **Building permits:** fresh County appraiser **property** data do not refresh County MGO building permit status. No authenticated current MGO session, approved lot grading/site plans, certified current as-builts, roadway pipe invert measurements, positive outfall or new engineer inspection obtained.
- **ERP and DEP CGP:** nearby NWFWMD `9220-2` point record not matched to actual polygon or parcels; DEP construction stormwater coverage/NOI/common plan unverified.
- **Private homeowner photographs:** original file contents, timestamps, GPS metadata and authorization cannot be verified from the public-safe index; capture originals only with residents' consent and in restricted storage. **No on-site visit or current photographs are represented as completed.**

## Before submission

Preserve the actual Clerk/PA/GIS source files already downloaded; narrow the Clerk request to missing **later** Lot QQ deeds and easements. Send independent County Engineering and building-records requests for the two permits and shared roadside infrastructure. Separately seek FDOT 2022 imagery, NWFWMD/DEP permit instruments, and Public Works service inspection, with homeowner authorization and transmission receipts. Original subdivision plat recovery is useful, but approved engineering plans and a measured receiving outfall remain the decisive gap.

**No records request was sent during this work.** The [Clerk source](https://santarosaclerk.com/links/online-forms/records/) identifies `PublicRecordRequest@santarosaclerk.com`. The [County source](https://santarosa.fl.gov/485/Public-Records-FOIA-Requests) distinguishes County departmental and Clerk custodians.
