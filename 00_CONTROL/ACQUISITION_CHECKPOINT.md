> **SUPERSEDED HISTORICAL ACQUISITION CHECKPOINT (2026-10-15).** The access results and early ERP ranking below describe their original limited searches, not the current state. Subsequent authenticated MGO records were acquired; ERP proximity is not permit applicability. See `15_RECONCILED_DRAFTS/` and `00_CONTROL/SOURCE_REGISTER.csv` for current research conclusions.

# EVIDENCE ACQUISITION CHECKPOINT

Generated: 2026-10-15 (UTC session, continuous)
Original local working directory: `[private workstation path withheld]`

## 1. Project directory inspected

Existing project reused in place. 13 pre-existing control/notes files were
audited and **not** deleted; superseded entries are preserved and marked
`SUPERSEDED_NOT_OFFICIAL` in `SOURCE_REGISTER.csv`.
Git history preserved (branch `main`, no commits existed yet).

## 2. OpenCode tools verified

| Capability | Result |
|---|---|
| Terminal / filesystem | yes |
| `curl`, `wget`, `file`, `sha256sum`, `pdftotext`, `pdfinfo` | yes |
| Python 3.14.4 + `requests` | yes |
| Installed this session: `pypdf`, `beautifulsoup4`, `lxml`, `playwright` | yes |
| Playwright Chromium (headless shell 156.0.8078.4) | **verified working** |
| PIL | yes |
| Web search / URL fetch | yes |

No Docker used. No CAPTCHA, paywall or access control bypassed.

## 3. Official county systems successfully accessed

- **Santa Rosa County Property Appraiser** — `search.srcpa.gov` fully accessed.
  Public Remix app; undocumented JSON endpoints discovered by reading the live
  form and JS bundle. Public guest access, no login.
- **Santa Rosa County Clerk (AcclaimWeb)** — public **Guest** session
  established after disclaimer acceptance. Book/Page search works.
- **FDEP + all 5 Water Management Districts ERP map services** — public ArcGIS
  REST, queried directly.
- **Florida Water Permits Portal** — public, address search executed.
- **MGO Connect** — portal reached, jurisdiction set to Santa Rosa County
  (JID=276), **but permit search is login-gated**.

## 4. Official parcel searches executed

`street=TOM, city=NAVARRE` → **123 parcels**; `parcelId=` exact query per
target; per-parcel official record export for all three addresses.

### CRITICAL CORRECTION — prior parcel identifiers were wrong

| Address | Prior claim (MLS) | **Verified official parcel** | Verified owner |
|---|---|---|---|
| 2264 Tom St | `...0QQ00-1490` ❌ | **`21-2S-26-0780-0QQ00-1020`** | HOLIDAY BUILDERS INC |
| 2268 Tom St | `...0QQ00-1060` ❌ | **`21-2S-26-0780-0QQ00-1490`** | HOLIDAY BUILDERS INC |
| 2265 Tom St | `...0QQ00-1180` ✅ | **`21-2S-26-0780-0QQ00-1180`** | BOGART CHRISTOPHER DAVID & |
| 2266 Tom St | unknown | **NOT FOUND ON CURRENT ROLL** (historical MGO permits use 2266) | — |

The prior agent had **transposed** the two target parcels. `...-1060` is
actually **2274 Tom St** (MATIG-A CEPRIANO P JR). The 2266 ambiguity is now
unresolved: current situs roll omits 2266; historic permit records include it.

## 5–6. Permit records located

**NONE.** MGO Connect was tested on six public routes with a real browser.
Every route redirects to `/cp/login` for Guest users. MGO does not offer
anonymous permit search for this jurisdiction. See §9.

## 7. Government documents downloaded and validated

7 evidence files across 3 official systems. `python3 00_CONTROL/tools/validate_evidence.py`
reports **35 files, 35 pass, 0 fail**.

## 8. Paths and SHA-256 of acquired files

```
02_PROPERTY_AND_PARCELS/RAW_HTTP/srcpa_property_query_street_TOM_NAVARRE.json
02_PROPERTY_AND_PARCELS/2264_Tom_St/srcpa_property_record_21-2S-26-0780-0QQ00-1020.json
02_PROPERTY_AND_PARCELS/2268_Tom_St/srcpa_property_record_21-2S-26-0780-0QQ00-1490.json
02_PROPERTY_AND_PARCELS/2265_Tom_St/srcpa_property_record_21-2S-26-0780-0QQ00-1180.json
00_CONTROL/SYSTEM_RAW/acclaim_bookpage_3492_700_20261015T235902Z.html
09_ENVIRONMENTAL_PERMITS/SYSTEM_RAW/erp_nearest_permits_tom_street.json
09_ENVIRONMENTAL_PERMITS/SYSTEM_RAW/flwaterpermits_erp_2268_Tom_Street_Navarre_FL_32566.html
```

Exact sizes and full SHA-256 values are in `00_CONTROL/EVIDENCE_MANIFEST.csv`
and `00_CONTROL/SOURCE_REGISTER.csv` (generated from the files themselves;
a self-check confirmed **0 checksum mismatches**).

Official identifiers acquired:
- Parcel keys `10082028` (2264), `10082068` (2268), `10082042` (2265)
- Recorded instrument `201603296` — **ORB 3492 PG 700**, DEED, 2016-01-28
- ERP `9220-2` — "Hadleigh Hills, Phase 2", NWFWMD, Santa Rosa County, 8.1 ac,
  applicant **Hadleigh Hills Development Group**, decided 2016-11-21

## 9. Known attachments not accessible

All permit-side records for both sites. 22 catalogued entries in
`00_CONTROL/PERMIT_DOCUMENT_INVENTORY.csv` covering: permit applications,
site/plot plans, approved grading plans and finished-floor elevations,
existing-conditions and boundary/topographic surveys, erosion-control plans,
driveway permits and culvert details, inspection history and correction
notices, final approvals, certificates of occupancy, certified as-builts, and
the shared Tom Street ROW / subdivision drainage master plan.

**Exact barrier:** MGO Connect `/cp/search?jid=276&pid=3` redirects every
anonymous request to `/cp/login`. Verified on 6 routes.

## 10. Next immediate retrieval actions

1. **Unblock MGO** (needs user): register/login to `mgoconnect.org/cp/portal`,
   jurisdiction Santa Rosa County. Then search `2264 Tom St`, `2268 Tom St`,
   `2264 Tom St`, parcel `...-1020`, parcel `...-1490`, and applicant
   `Holiday Builders`. Open every permit and download every attachment.
2. Change Clerk method: stop using party-name search; use Book Type = PLAT and
   date-windowed Book/Page searches around 2015–2016 to find the Crescent
   Shores / Pope Subdivision plat and the deeds for lots 1020 and 1490.
3. Retrieve the NWFWMD ERP 9220-2 file (Hadleigh Hills Phase 2) — this is the
   only ERP permit within 2,000 ft of either parcel and is the most likely
   source of the original drainage design.
4. Retrieve the county "Subdivisions Approved 2026 / 2025" StoryMaps to pin
   the development approval record for Hadleigh Hills / Crescent Shores.

**Status: ACQUISITION IN PROGRESS.**
Not yet: PUBLIC-SOURCE ACQUISITION COMPLETE; AGENCY PRODUCTION OUTSTANDING.