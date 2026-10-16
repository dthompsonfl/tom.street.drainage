# 2266 Tom St — RESOLVED: NO CURRENT PARCEL, BUT A HISTORICAL ADDRESS EXISTED

**Status: HISTORICAL RESEARCH LEAD, NOT A RECORDED ADDRESS-CHANGE FINDING.** Existing 1996–1998 MGO files establish historical usage, but disposition is not verified.

## Finding 1 — no current parcel

A captured street-address query of the Santa Rosa County Property Appraiser roll
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

These historical records give no certified address-change or parcel-merger history. The old MGO parcel keys overlap other present-day records, but that alone does **not** establish that 2266 was renumbered to 2260 or 2270, or that any merger/replat occurred. Request the original permit legal descriptions, County addressing history, and Clerk title/plat instruments.

## Consequence for the investigation

2266 must **not** be substituted for either target site: there is no current
parcel, building or permit record at 2266 that relates to 2264 or 2268.

It is retained as evidence of historical MGO address usage and possible mobile-home-era improvements. Changes in addressing, parcel boundaries and grading remain **unverified**, not established.

## Evidence

- `RAW_HTTP/srcpa_property_query_street_TOM_NAVARRE.json` (123 official records)
- `../03_PERMITS_AND_INSPECTIONS/SYSTEM_RAW/mgo_sweep_results.json` (permit records)
