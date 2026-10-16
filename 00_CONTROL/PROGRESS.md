# PROGRESS — Tom Street Drainage Investigation

**Status: ACQUISITION IN PROGRESS**
Last updated: 2026-10-16 (UTC session, continuous)

---

## What has actually been acquired this session

| System | Result |
|---|---|
| Santa Rosa County Property Appraiser | **FULL ACCESS.** Both target parcels identified and officially exported. |
| Santa Rosa County Clerk (AcclaimWeb) | Guest access; Book/Page search working. ORB 3492/700 retrieved and shown to be misattributed. |
| **MGO Connect (Santa Rosa County permits)** | **AUTHENTICATED.** Both building permits located, opened and fully extracted — metadata, inspections, requirements, fees, contacts, payments. |
| FDEP + 5 water management districts ERP | Queried directly. NWFWMD ERP 9220-2 located as the only ERP within 2,000 ft. |
| County approved-subdivision StoryMaps | All 7 annual maps searched — **zero** hits for "Crescent Shores" or "Hadleigh Hills". |
| NWFWMD ERP 9220-2 permit file | Not publicly downloadable; request drafted. |

## Key corrections to prior research

1. **The two target parcels had been transposed.** 2264 Tom St is
   `21-2S-26-0780-0QQ00-1020`; 2268 Tom St is `21-2S-26-0780-0QQ00-1490`.
2. **`...-1060` is not 2268 Tom St** — it is **2274 Tom St** (MATIG-A CEPRIANO P JR).
3. **2266 Tom Street does not exist.** The address sequence skips it.
4. **ORB 3492 PG 700 is not a 2268 Tom Street instrument.** It is deed 201603296
   for "21-2S-26 POPE SUBD LOT 22 UNREC" = 2274 Tom Street.
5. **A second development name has surfaced:** "Hadleigh Hills" is the NWFWMD ERP
   project name; "Crescent Shores (00780)" is the Property Appraiser filing name.

## Permits located

| Address | Parcel | Permit | Type | Status | Issued | Applicant |
|---|---|---|---|---|---|---|
| 2264 Tom St | `21-2S-26-0780-0QQ00-1020` | **BP-2026-1621** | New Single Family (R) | **Active** | 2026-03-23 | Amy Riddle, Holiday Builders INC |
| 2268 Tom St | `21-2S-26-0780-0QQ00-1490` | **BP-2026-1612** | New Single Family (R) | **Active** | 2026-03-23 | Amy Riddle, Holiday Builders INC |

Plus 4 legacy permits on each lot (1996 mobile home at 2264; 2000 mobile home at 2268).

## Highest-value drainage findings recovered

- **2264** driveway line-and-grade inspection (2026-08-06): *"Use 100 ft of 12 inch
  ADS perforated pipe with sock; Tear out existing concrete end @ address 2260 and
  tie into with new pipe; Install 1st inlet box @ roughly halfway; Tear out existing
  concrete end @ address 2270 and install an inlet box."*
- **2268** site grading/drainage pre-construction inspection (2026-08-31): *"Site
  passes. Ensure that roadway and stormwater ditch remain free of construction sediment."*
- **2268** driveway line-and-grade inspection (2026-09-10): *"Flat; Match Existing
  roadway Grades."*
- **Both permits: the county requirement "Certified Drainage as Built" is still
  `Assigned` — it has not been submitted or approved on either lot.**

## Immediate next operations

1. Complete the Tom Street address sweep (running) to confirm no separate grading,
   ROW or land-development permit exists for the block.
2. Re-run the Clerk search using a different method (plat book range + date windows)
   to locate the Crescent Shores / Pope Subdivision plat and the deeds for lots
   1020 and 1490.
3. Obtain user approval to submit the four drafted Chapter 119 requests.
4. Request the NWFWMD ERP 9220-2 file and the County's drainage/ROW plans.

## Resumability

All acquisition tools live in `00_CONTROL/tools/` and are re-runnable:
`srcpa_acquire.py`, `validate_evidence.py`, `build_registers*.py`,
`clerk_search.py`, `clerk_name.py`, `mgo_pull.py`, `mgo_bulksearch.py`,
`mgo_inspections.py`, `erp_nearest.py`, `search_storymaps.py`.

The MGO session state lives **outside** the repository at
`/tmp/opencode/mgo_auth.json`. No credential or token is stored in this project.
If it has expired, re-authenticate with `00_CONTROL/tools/mgo_login_helper.py`.