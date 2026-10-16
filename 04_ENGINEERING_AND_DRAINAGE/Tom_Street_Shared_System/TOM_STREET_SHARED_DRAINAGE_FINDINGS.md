# Tom Street Shared Drainage System — Official Records Recovered

Compiled: 2026-10-16 · All statements below are drawn from county permit records
retrieved from MGO Connect (Santa Rosa County) unless marked otherwise.

## The corridor

Tom Street, Navarre, Santa Rosa County, FL 32566, within subdivision
**Crescent Shores (00780)** (Section 21 · Township 2S · Range 26).

| Address | Parcel (PA verified) | Permit history |
|---|---|---|
| 2198 Tom St | `...-0QQ88-0000` | Mobile home demolished 2023 (`BP-2023-5719`), replaced `BP-2023-8141` |
| 2260 Tom St | `...-0QQ00-1030` | New single family 2019 — **incl. Driveway Connection permit** |
| **2264 Tom St** | **`...-0QQ00-1020`** | **Target A — `BP-2026-1621`, Active** |
| 2265 Tom St | `...-0QQ00-1180` | New single family 2015 — the existing affected residence |
| 2266 Tom St | *historically existed* | Mobile home permits 1996 & 1998; **no longer a separate parcel** |
| 2267 Tom St | `...-0QQ00-1320` | New single family 2015 |
| **2268 Tom St** | **`...-0QQ00-1490`** | **Target B — `BP-2026-1612`, Active** |
| 2270 Tom St | `...-0QQ00-1030` | New single family 2021 — **incl. Driveway Connection permit** |
| 2274 Tom St | `...-0QQ00-1060` | Deed 201603296, ORB 3492/700, "POPE SUBD LOT 22 UNREC" |

This corridor is being converted from individual mobile-home lots to
conventional single-family housing. Both target lots previously carried a
mobile home (2264: permits of 1996; 2268: permits of 2000).

## Finding 1 — the county has officially identified a roadside storm drainage system

**2268 Tom St, `BP-2026-1612`, Site Grading / Drainage (pre-construction)
Inspection, 2026-08-31 — Passed:**

> "Site passes. Ensure that **roadway and stormwater ditch** remain free of
> construction sediment."

The county's own inspector identified an existing **roadway and stormwater
ditch** along the Tom Street frontage as the feature that must be protected
during construction.

## Finding 2 — 2264's driveway was designed to tie into the neighbouring lots' drainage

**2264 Tom St, `BP-2026-1621`, Driveway Line & Grade / Consultation Inspection,
2026-08-06 — Passed:**

> "Use 100 ft of **12 inch ADS perforated pipe with sock**; Tear out existing
> concrete end @ address **2260** and tie into with new pipe; Install **1st inlet
> box** @ roughly halfway; Tear out existing concrete end @ address **2270** and
> install an inlet box; call for Pre-pour inspection when ready"

The driveway drainage design for 2264 is **not** a self-contained rear-yard
system. It runs along the street frontage and connects to pre-existing concrete
storm structures on **both** adjacent parcels (2260 and 2270 Tom Street) via
12-inch ADS perforated pipe, with at least one inlet box mid-block.

## Finding 3 — 2268's driveway was set to match the existing road surface

**2268 Tom St, `BP-2026-1612`, Driveway Line & Grade / Consultation Inspection,
2026-09-10 — Passed:**

> "Flat; **Match Existing roadway Grades**; Call for pre-pour Inspection when ready"

The driveway and lot elevation at 2268 were directed to be matched to the
existing roadway grade, described as "Flat" — i.e. no freeboard was designed
into the driveway relative to the road surface.

## Finding 4 — the neighbouring driveway connections failed inspection repeatedly

Official inspection history of the two "Driveway Connection" permits that
2264's design ties into:

| Permit | Address | Failed inspections | Final |
|---|---|---|---|
| `2019-7490-000-B-2` Driveway Connection | **2260 Tom St** | 2019-12-20, 2020-02-19 (**2 failures**) | Passed 2020-03-13 / 2020-03-17 |
| `2021-2524-000-B-1` Driveway Connection | **2270 Tom St** | 2021-08-03, 2021-08-05, 2021-08-20 (**3 failures**) | Passed 2021-08-23 |

Both were eventually closed complete, but both required multiple failed
inspections and rework before approval. The county's failure-reason field
records only the inspector's name, so the specific non-compliance is not
disclosed through the portal.

## Finding 5 — the certified drainage as-builts do not yet exist on either target lot

Both permits carry an open county requirement:

> **"Certified Drainage as Built"** — status **`Assigned`**

on both `BP-2026-1621` (2264 Tom St) and `BP-2026-1612` (2268 Tom St).

Also outstanding on both:

- `Site Grading / Drainage (mid-construction) Inspection` — **Not Complete**
- `Site Grading / Drainage (final construction) Inspection` — **Not Complete**
- `Driveway Final Inspection` — **Not Complete**
- `Issue CO` — **Assigned** (no certificate of occupancy issued)
- Permit status remains **Active** for both.

On 2268 Tom St, `Driveway Pre-Pour Inspection` is still **Not Complete**
(as of the county's task list), even though the line-and-grade consultation
passed on 2026-09-10.

## Finding 6 — the only Environmental Resource Permit nearby

| Field | Value |
|---|---|
| ERP Official Permit ID | **9220-2** |
| Project | Hadleigh Hills, Phase 2 Ext. to P9220-1 |
| Applicant | **Hadleigh Hills Development Group** |
| Rule / type | 62-330 · ERP Individual |
| County | Santa Rosa |
| Acres | 8.1 |
| Decision | 2016-11-21 |

This is the only ERP record returned by the District's own public map service
within 2,000 ft of either target parcel. No FDEP-issued ERP exists within that
radius. It is the most likely public source of the original drainage design for
this corridor.

## What is NOT available from any public source

- No approved site plan, grading plan, topographic survey, culvert drawing,
  swale section or as-built is exposed through the MGO customer portal for
  either permit (`ProjectFiles` endpoint returns an empty list).
- No recorded plat or drainage easement has been located. The Clerk's
  Legal Search endpoint returns HTTP 404 and the party-name index exceeds the
  result limit.
- Neither "Crescent Shores" nor "Hadleigh Hills" appears in any of the county's
  seven annual Approved Subdivisions StoryMaps (2020–2026).

## Requests drafted to close these gaps

- `13_PUBLIC_RECORDS_REQUESTS/2264_TOM_ST_COMPLETE_PERMIT_FILE.md`
- `13_PUBLIC_RECORDS_REQUESTS/2268_TOM_ST_COMPLETE_PERMIT_FILE.md`
- `13_PUBLIC_RECORDS_REQUESTS/SHARED_TOM_STREET_ROW_AND_DRAINAGE_PLANS.md`
- `13_PUBLIC_RECORDS_REQUESTS/CLERK_DEEDS_PLATS_EASEMENTS.md`
- `13_PUBLIC_RECORDS_REQUESTS/NWFWMD_ERP_9220-2_FILE.md`

All five are **`DRAFTED_NOT_SUBMITTED`**.