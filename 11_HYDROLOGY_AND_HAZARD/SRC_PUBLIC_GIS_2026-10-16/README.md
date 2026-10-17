# Tom Street public GIS, LiDAR and historic-source acquisition (2026-10-16)

**Evidence status:** Original NOAA historical terrain sources and primary county GIS feature responses are preserved. **This is NOT proof of construction-related drainage damage, a legal code violation, or a certified survey.** Acquired files and their child manifests are authoritative for acquisition statuses. Any subsequently retrieved official plan or dated survey may change these interpretations.

## Identity and scope

| Site | Source-verified parcel ID | Role |
|---|---|---|
| 2264 Tom Street | `21-2S-26-0780-0QQ00-1020` | 2026 construction, `BP-2026-1621` |
| 2268 Tom Street | `21-2S-26-0780-0QQ00-1490` | 2026 construction, `BP-2026-1612` |
| 2265 Tom Street | `21-2S-26-0780-0QQ00-1180` | Established neighboring home |

Situs and current-tax-parcel GIS layers are **not legal boundary surveys**. Data at representative within-parcel points are not an exhaustive lot survey.

## Original historical topography (preserved binary data)

| Date | Original public file | Extent / quality verification | Integrity |
|---|---|---|---|
| 2006-02-28 source date in NOAA file name | [`ORIGINAL_NOAA_2006/20060228_sr1369_ld_p17.copc.laz`](ORIGINAL_NOAA_2006/20060228_sr1369_ld_p17.copc.laz) | Original compressed LAS 1.4 cloud; LAS header and bounds checked; source coverage at all three point coordinates independently verified using the original 2,404-feature NOAA index | SHA256 `d5e83be7740af296db227af9c29e253ccc9c0279ee062c32c1091bb2f4376faa`; 17,352,858 bytes |
| 2017-03-31 to 2017-04-08 collection interval | [`ORIGINAL_NOAA_2017/16reu175645.tif`](ORIGINAL_NOAA_2017/16reu175645.tif) | NOAA/NWFWMD original 1-meter hydro-flattened bare-earth GeoTIFF, 1500×1500 pixels; EPSG:6345 horizontal; 3 parcel sample locations fall inside data-bearing raster | SHA256 `449070da44acbdc23a289bdbfb436ef0eeb75b2cdc5cdee1fda154b263e507e0`; 6,589,870 bytes |

NOAA 2017 metadata: https://www.fisheries.noaa.gov/inport/item/55909. **The 2017 GeoTIFF uses a 1-meter XY grid (meters horizontally), but NAVD88/GEOID12B elevations are in U.S. survey feet (vertical CRS EPSG:6360).** The NOAA lineage documents that the original vertical meter heights were converted to U.S. survey feet. Never confuse horizontal raster resolution with vertical elevation units.

At the three arbitrarily selected representative locations, this 2017 NOAA raster returns:

- 2264: **31.4549 US survey feet** (~9.5875 m) NAVD88/GEOID12B
- 2265: **32.1479 US survey feet** (~9.7987 m)
- 2268: **31.6617 US survey feet** (~9.6505 m)

These are **not finished-floor elevations, parcel means, fill measurements, legal survey figures, culvert inverts or construction-year grades**. Underlying measurement uncertainty, land-cover classification and surface representation matter. NOAA reported project-wide bare-earth DEM non-vegetated vertical accuracy of +/-9.6 cm at 95% confidence and vegetated vertical accuracy of +/-14.9 cm at 95th percentile; those are **project-wide tests**, not certified local accuracy.

The original NOAA 2006 public product is in the GEOID18 catalogue, and its historic site ground-class data have **not been extracted or analyzed**. Never directly subtract 2006 and 2017 source heights without reconciling the different published horizontal/vertical datums, units, survey dates, classifications and grid/point-cloud processing.

[2006 source catalogue](https://www.fisheries.noaa.gov/inport/item/48209); [2006 preserved original tile index and intersection proof](ORIGINAL_NOAA_2006/tileindex_2006_FL_Panhandle_m57.acquisition.json); [2006 original file and checks](ORIGINAL_NOAA_2006/2006_tom_street_copc_acquisition.json); [2017 TIFF acquisition manifest](ORIGINAL_NOAA_2017/16reu175645.acquisition.json).

`USGS_3DEP_2017_DEM_15_POINT_SAMPLES.json` independently preserves 15 USGS EPQS elevation point responses, whose source raster metadata reports a 2017-05-05 acquisition date. The NOAA 2017 tile documents a March/April 2017 survey window: **do not claim these are exactly the same product or that the date discrepancy has been resolved**, even if values appear similar.

## Official Santa Rosa County GIS features acquired and independently intersected

Read [the full saved GIS parcel/road/problem-area geometries](SANTA_ROSA_COUNTY_PRIMARY_GEOMETRIES.json), [18 thematic point intersection responses](SANTA_ROSA_COUNTY_3_PARCEL_LAYER_INTERSECTIONS.json) and [bounded local contour/structure queries](SANTA_ROSA_COUNTY_CONTROLS_AND_NEARBY_FEATURES.json). The original query URLs are retained with each response.

1. Santa Rosa County Streets GIS layer 5: Tom Street GIS segment object `2036`, address range `2100-2299`, maintainer `County Maintained`, status `OPEN`. Segment `2300-2330` is also county maintained. **This does not resolve title/maintenance of individual culverts, pipes, swales, inlets or outfalls.**
2. Santa Rosa County Stormwater Problem Area layer 79: official OBJECTID `2068`, source `Road & Bridge Maps Marked Up by Foreman`, intersects the three site sample points; the full **historic mapped polygon** was captured. County layer history discusses historic staff observations and 2006 storm problems. **Neither the polygon nor historical mapping proves a 2026 builder violation, current design insufficiency or builder causation.** Obtain the original marked-up foreman maps and the decision history for object 2068.
3. Soils layer 35: sampled points within mapped soil OBJECTID `14438`, map unit `34`, `Pactolus loamy sand, 0-5% slopes`. General map unit, not a parcel soil test or infiltration rate.
4. Drainage basins layer 100: basin OBJECTID `93`, mapped label `DIRECT RUNOFF TO BAY`. A large-basin description **does not prove positive hydraulic outfall from the constructed driveways**.
5. Wetland layer 36: no returned feature **at the selected points only**, not a no-wetlands determination.
6. County FEMA layer 45: point samples in Zone X. This does not rule out local nuisance flooding.
7. Contour layer 50: one 35-ft line within an expanded neighborhood search rectangle; no contour intersects the narrow sample rectangle. **Five-foot contour intervals cannot establish lot grades or site-drainage slope.**
8. Structures layer 2: nearby addressing points include 2260, 2264, 2265, 2268 and 2270 Tom Street; `Elev` field returned null, not a measured elevation.

[Santa Rosa County GoMaps service](https://cloud.santarosa.fl.gov/arcgis/rest/services/santarosa/GoMaps4_0/MapServer). [Official County GIS disclaimer](https://www.santarosa.fl.gov/470/Mapping-GIS). County hosted layers require distribution/accuracy disclaimers to accompany redistributions.

## Historic County aerial-photo retrieval: NOT OBTAINED

[Independent eight-year acquisition manifest](COUNTY_HISTORICAL_AERIAL_EXPORTS/ACQUISITION_MANIFEST.json). County map-service endpoints for 2001, 2005, 2006, 2010, 2012, 2016, 2019 and 2022 were enumerated; all eight ArcGIS export requests on October 16, 2026 returned **HTTP 500**. A direct JSON diagnostic for selected years states the service is **not started**. These are **catalogue leads, not saved imagery**. Request County GIS/Property Appraiser aerial TIFFs and acquisition metadata, or use another public archive such as Florida DOT APLUS. Do not pretend source is unavailable merely because this specific service is stopped.

## Critical evidence *still* missing

- **County-held approved grading/lot-drainage drawings** and revisions for permits `BP-2026-1621` and `BP-2026-1612`; certified drainage as-builts; owner/engineer-of-record and any subdivision grading plan or exemption.
- **Existing and certified measured** preconstruction and postconstruction elevations, roadway profiles, culvert inverts, inlet dimensions, and verified receiving outfall.
- **True Tom Street roadside stormwater asset ownership, easements, drainage maintenance/acceptance records**, plus source history behind County problem-area object 2068.
- The original **East Navarre drainage watershed study engineering model, survey inputs and report**, and the parcel-specific coverage of any environmental resource permit.
- Source orthophotos and accurate capture dates for each year; native 2026 resident original photos/permissions and event logs.

These require official agency records production or qualified field survey. The public customer-facing permit portal did not supply the approved sealed plans. Do not mark any Chapter 119 request submitted without a transmission and receipt. Existing draft requests are in `13_PUBLIC_RECORDS_REQUESTS/`. This acquisition does not supplant the project's canonical evidence ledger or authorize external circulation of private source evidence.

## Additional original and aerial evidence archived October 16

See the [canonical historical evidence coverage register](../../00_CONTROL/HISTORICAL_EVIDENCE_COMPLETENESS_2026-10-16.md), [machine-verified original hashes](../../00_CONTROL/HISTORICAL_PUBLIC_EVIDENCE_INTEGRITY_AUDIT_2026-10-16.json) and [private resident photograph index](../../00_CONTROL/PRIVATE_RESIDENT_PHOTO_INVENTORY_PUBLIC_SAFE_2026-10-16.csv). The initial sections above describe the original first acquisition scope; the linked control register supersedes older incomplete source counts.

- **Historical orthophotos:** `FLORIDA_DEP_HISTORICAL_AERIALS/` contains nine source-verified public GIS JPEG exports for 1994, 1999, 2004, 2007, 2010 (NAIP and FDOT), 2013, 2016 and 2019, plus mosaic source/coverage queries and 11 explicitly recorded failed/blank year attempts. These are **derived images** and need source flight dates and original frames before they can be treated as complete.
- **2023 federal imagery:** `USDA_NAIP_2023/` contains a federally hosted 2023 orthophoto export, source mosaic catalogue intersection record and byte checksum; the source cover is 0.3-meter imagery, while the exported JPEG is derived.
- **2021 federal imagery:** `USDA_NAIP_2021/` records an attempted retrieval and blank response, with only a generalized catalogue item. **Do not include 2021 in acquired site imagery.**
- **Historical FDOT collections:** `FDOT_AERIAL_ARCHIVE_INDEX/` preserves the original agency 2026 list and recent status PDF. Santa Rosa County year collections on that list: **1966, 1978, 1988, 1997, 2005, 2006, 2010, 2013, 2016, 2019, 2022**. The actual 1966/1978/1988/1997/2022 photo frames or source orthomosaics have **not** been acquired from FDOT APLUS.
- **Regional surveys and published reports:** `NOAA_SURVEY_REPORTS/` preserves the 91-page report documenting the 2017 survey that actually covers Tom Street, plus four 2018 regional reports for a different footprint. `ORIGINAL_NOAA_2018/` has the 16,801-feature original regional index proving **no 2018 NOAA Panhandle DEM tile intersects these parcels**; its nearest feature is about **38 km** away.
- **County watershed data:** `WATERSHED_DOCUMENTS/` contains the 336-page public draft Watershed Master Plan, plus the published East Navarre study-area original JPEG. **The approved detailed model, technical report, field survey, and lot-specific grading plans remain missing.**

## Additional original high-resolution LABINS aerials (acquired October 17)

The [new LABINS public-source archive](../SRC_PUBLIC_GIS_2026-10-17/LABINS_SANTA_ROSA/) contains the official Santa Rosa imagery grid PDF, original FSU FREAC State Plane North grid-geometry responses, the original cell **648138** image availability search, and [all nineteen actual original imagery/companion files](../SRC_PUBLIC_GIS_2026-10-17/LABINS_SANTA_ROSA/ORIGINAL_IMAGERY_CELL_648138/) downloaded for 2007 through 2019. Original photos: 2007 color + infrared, and 2010, 2013, 2016, 2019 normal color. Only the listed 2016 auxiliary `.aux` file returned 404. The source lookup is based on the actual official polygon intersection, not guessed cell numbers.

Original 2016 and 2019 metadata provide collection-wide flight-date ranges, not exact exposure times per image. The records are aerial imagery, **not** vertical surface surveys, permit grades or hydraulic analyses. See [the auditable file ledger and outstanding source requests](../../00_CONTROL/LABINS_2026-10-17_ORIGINAL_SOURCE_REVIEW.md). The 2022 and 2025 site-covering FDOT originals remain outstanding.

**Privacy:** The public Git tree intentionally excludes unapproved resident original JPEG/HEIC files, EXIF GPS and other private camera metadata. The original earlier photo report documents 37 file instances/35 distinct photographic contents, not 37 verified original camera captures. Restricted photographs must be managed outside the public Git repo, with explicit owner permission and independent hash/custody verification.
