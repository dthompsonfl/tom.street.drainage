# Tom Street Drainage Investigation

> **CURRENT RELEASE CONTROL (2026-10-15):** The PDF and ZIP publications under `14_MEETING_PACKET/` and `releases/2026-10-15/` are **superseded historical exports**, not approved final evidence. The latest fact-checked text and reconciliation status are to be maintained in `15_RECONCILED_DRAFTS/`. This is a **public** repository: do not upload unredacted authenticated-portal captures, homeowner photo originals/EXIF, or raw multi-source workspace archives without privacy and permission review.


An evidence-based public-records investigation into drainage at two residential
lots under construction in Navarre, Santa Rosa County, Florida:

| Site | Parcel (verified) | Permit | Status at 2026-10-16 |
|---|---|---|---|
| **2264 Tom Street** | `21-2S-26-0780-0QQ00-1020` | `BP-2026-1621` | **Active** |
| **2268 Tom Street** | `21-2S-26-0780-0QQ00-1490` | `BP-2026-1612` | **Active** |

Existing affected residence: **2265 Tom Street**, parcel `21-2S-26-0780-0QQ00-1180`.

---

## ⚠️ Read this first

**This repository does not conclude that anything is wrong.**

It contains official county records and an honest account of what those records
do and do not establish. Specifically:

- **No code violation has been established.**
- **No drainage-adequacy determination has been made.** No approved grading plan,
  survey, as-built, invert elevation or field measurement exists here.
- **No hydraulic capacity calculation has been performed**, and none can be
  without real geometry and a Florida licensed Professional Engineer.
- The county's open tasks ("Certified Drainage as Built: Assigned") are
  **consistent with a normal unfinished build**, not evidence of breach.

Legal/engineering determination status: **NOT_READY**.
See [`00_CONTROL/DESIGN_VS_FIELD_MATRIX.csv`](00_CONTROL/DESIGN_VS_FIELD_MATRIX.csv)
— 9 of 10 rows are `NOT_TESTABLE`.

---

## What we verified

From the **Santa Rosa County Property Appraiser official roll**:

- Holiday Builders, Inc. owns both target lots.
- Zoning **R2M**; Property Appraiser filing **Crescent Shores (00780)**, lots 1020 and 1490.

From **MGO Connect** (Santa Rosa County Development Services), authenticated:

- `BP-2026-1621` and `BP-2026-1612`, both Active, both issued **2026-03-23**.
- Applicant on both: **Amy Riddle, Holiday Builders INC**.
- **26 inspection records** with county inspector comments, including the
  driveway-drainage direction at 2264 and the stormwater-ditch remark at 2268.
- The open task **"Certified Drainage as Built" is still `Assigned` on both.**

From the **Santa Rosa County Land Development Code** (official PDF, 509 pp,
cover dated November 10, 2025; PDF CreationDate January 13, 2026 is metadata, not enactment) — § 4.04.01.D.1 requires, for a sub-one-acre lot without a
subdivision lot grading plan on file with County Engineering, a sealed Florida PE
lot grading plan or an NWFWMD Individual ERP letter, **and** a sealed engineer's
conformance letter **before Certificate of Occupancy**.

From **FEMA NFHL**: archived **geocoded sample points** returned Zone X on FIRM panel 12113C0587H. Whole-parcel flood-zone coverage has not been verified by a parcel-polygon overlay, and the mapping does not measure local street flooding. From **NOAA NCEI**: rainfall context for the construction window.

---

## What we do **not** have

| Gap | Custodian | Status |
|---|---|---|
| Approved grading plans, both lots | Development Services | `REQUEST_DRAFTED` |
| **Does a subdivision lot grading plan exist on file? (pivotal)** | Engineering | `REQUEST_DRAFTED` |
| Sealed engineer's drainage certification | Development Services | `REQUEST_DRAFTED` |
| Surveys, driveway inverts, roadway profile | Dev Services / Public Works | `REQUEST_DRAFTED` |
| Recorded plat, deeds, drainage easements | Clerk of Court | `REQUEST_DRAFTED` |
| NWFWMD ERP 9220-2 file | NWFWMD | `REQUEST_DRAFTED` |
| **Homeowner photos** | Private archive contains 15 hash-matched JPEG copies; original capture provenance and permission unverified | `PRIVATE_COPIES_VERIFIED_ONLY` |
| Surveyor / PE field measurements | to be engaged | `NOT_OBTAINED` |

**All five public-records requests are `DRAFTED_NOT_SUBMITTED`.** No submission
receipt exists for any of them. Status is tracked in
[`00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv`](00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv).

---

## Repository map

| Path | Contents |
|---|---|
| `00_CONTROL/` | Registers, audit, corrections, legal matrix, tests, tools |
| `02_PROPERTY_AND_PARCELS/` | Official parcel records per property |
| `03_PERMITS_AND_INSPECTIONS/` | Permit records, inspection histories, status refresh |
| `04_ENGINEERING_AND_DRAINAGE/` | Shared Tom Street drainage findings |
| `08_LEGAL_AND_REGULATORY/` | Verified LDC source PDF |
| `09_ENVIRONMENTAL_PERMITS/` | ERP records and proximity analysis |
| `11_HYDROLOGY_AND_HAZARD/` | FEMA flood zone + NOAA rainfall |
| `13_PUBLIC_RECORDS_REQUESTS/` | Five submission-ready Chapter 119 requests |
| `14_MEETING_PACKET/` | Public-safe packet: brief, letter, proxy notes, tracker, PDFs |
| `releases/` | Signed-off public packet ZIP + SHA256SUMS |

### Key documents

| File | What it is |
|---|---|
| [`00_CONTROL/CURRENT_STATE_RECONCILIATION.md`](00_CONTROL/CURRENT_STATE_RECONCILIATION.md) | Baseline audit, defects found, remediation log |
| [`00_CONTROL/ACQUISITION_RESULTS.md`](00_CONTROL/ACQUISITION_RESULTS.md) | What was searched, retrieved and what remains |
| [`00_CONTROL/CORRECTION_HISTORY.md`](00_CONTROL/CORRECTION_HISTORY.md) | Every prior claim that was wrong, and why |
| [`00_CONTROL/REGULATORY_AND_CASELAW_MATRIX.md`](00_CONTROL/REGULATORY_AND_CASELAW_MATRIX.md) | Verified authority, applicability, and what is unverified |
| [`00_CONTROL/EVIDENCE_LEDGER.csv`](00_CONTROL/EVIDENCE_LEDGER.csv) | 20 claims with exhibit, hash, limitation and contrary evidence |
| [`00_CONTROL/CONTRADICTION_LOG.csv`](00_CONTROL/CONTRADICTION_LOG.csv) | Conflicts and how each was resolved |
| [`00_CONTROL/EXHIBIT_INDEX.csv`](00_CONTROL/EXHIBIT_INDEX.csv) | Each exhibit: what it proves **and what it does not** |
| [`00_CONTROL/TEST_RESULTS.txt`](00_CONTROL/TEST_RESULTS.txt) | Latest test run |

---

## Reproduce

```bash
# validate every evidence file, rebuild the manifest
python3 00_CONTROL/tools/validate_evidence.py

# rebuild canonical registers from the actual evidence files
python3 00_CONTROL/tools/build_canonical_registers.py

# privacy classification + restricted-file handling
python3 00_CONTROL/tools/classify_for_release.py --write

# run the test suite
python3 00_CONTROL/tools/test_evidence.py

# build the release ZIP (validate -> test -> package)
python3 00_CONTROL/tools/build_release.py
```

Network-dependent tools (`mgo_*.py`, `clerk_*.py`, `srcpa_acquire.py`) require a
live MGO/Clerk session or public network access. They are **not** self-configuring.

---

## Privacy

The repository remote is **PUBLIC**.

- Authenticated portal captures containing the account holder's identity are
  **not** tracked. They live in `.evidence_vault/` (git-ignored) and are indexed
  by hash in [`00_CONTROL/RESTRICTED_EVIDENCE_INDEX.csv`](00_CONTROL/RESTRICTED_EVIDENCE_INDEX.csv).
- No password, token or session cookie is stored in this repository.
- Screenshots used publicly are **redacted derivatives**, labelled as such.

**Disclosed:** those files remain in published Git **history** at commit
`5ddbac9`. Removing them going forward does not erase prior commits. Purging
history would require a rewrite, which is outside this project's authorisation.

---

## Method limitations

1. Inspector comments are **directions recorded during construction**, not
   approved drawings and not proof of what was installed.
2. An empty portal attachment list **does not prove** the County holds no plans.
3. Proximity of **ERP 9220-2** does **not** prove it covers these lots — no
   polygon intersection was performed.
4. Regional rainfall from Pensacola airport is **not** on-site measurement.
5. **Westland Skating Center v. Gus Machado Buick** (Fla. 1989) — the corrected Florida Supreme Court opinion was retrieved and read from FSU College of Law's digital docket. Its reasonable-use rule is verified; subsequent legal treatment and application to these specific lots remain unresolved. See the updated legal matrix.
6. Party-name search on the Clerk's portal exceeds its result limit; Legal
   Search returns HTTP 404. Recorded as gaps, not as "no records".

---

*Evidence retrieved 15–16 October 2026. Prepared by an AI research assistant.
Not legal advice; not an engineering assessment.*