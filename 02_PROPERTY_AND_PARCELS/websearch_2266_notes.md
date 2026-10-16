# 2266 Tom St — RESOLVED: NO CURRENT PARCEL, BUT A HISTORICAL ADDRESS EXISTED

**Status: OVERWRITTEN 2026-10-15/16 with verified official data.**

## Finding 1 — no current parcel

An exhaustive query of the Santa Rosa County Property Appraiser official roll
(`street=TOM, city=NAVARRE` → 123 parcels) returns **no parcel with situs
address 2266 Tom St**. The current address sequence skips it:

```
2263  2264  2265  [2266 absent]  2267  2268  2269  2270
```

## Finding 2 — but 2266 Tom Street WAS a real address historically

Santa Rosa County permit records (MGO Connect) contain **five** projects at
"2266 TOM ST", all long closed:

| Permit | Type | Date | MGO parcel |
|---|---|---|---|
| `1996-2741-000-B-0` | Mobile Home (R) | 1996-07-16 | `212S2607800QQ890000` |
| `1996-2741-000-E-0` | Electrical (R) | 1996-07-16 | `212S2607800QQ890000` |
| `1996-2741-000-G-0` | Gas Permit (R) | 1996-07-16 | `212S2607800QQ890000` |
| `1996-2741-000-P-0` | Plumbing (R) | 1996-07-16 | `212S2607800QQ890000` |
| `1998-323-000-G-0` | Gas Permit (R) | 1998-02-04 | `212S2607800QQ001030` |

All are Mobile-Home-era permits. The 2266 address appears to have been
**absorbed by renumbering** into the lots now numbered 2260 / 2270 (MGO maps
both 2260 and the historic 2266 permits to `...QQ890000`, which indicates the
block was replatted or renumbered at some point).

## Consequence for the investigation

2266 must **not** be substituted for either target site: there is no current
parcel, building or permit record at 2266 that relates to 2264 or 2268.

It is retained here as background because it confirms the block's mobile-home
history and the renumbering that produced the current lot layout — both
relevant to interpreting historic grading.

## Evidence

- `RAW_HTTP/srcpa_property_query_street_TOM_NAVARRE.json` (123 official records)
- `../03_PERMITS_AND_INSPECTIONS/SYSTEM_RAW/mgo_sweep_results.json` (permit records)
