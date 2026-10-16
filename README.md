# Tom Street Drainage Investigation

> **Research status (updated October 16, 2026 UTC): DRAFT EVIDENCE PACKET; NOT AN ENGINEERING OR LEGAL FINDING.** Start with the [current assertion consistency register](00_CONTROL/ACTIVE_ASSERTION_CONSISTENCY_2026-10-15.md) and [reading-order guide distinguishing historical snapshots](00_CONTROL/READING_ORDER_AND_SNAPSHOT_STATUS.md). The [frozen prior audit](00_CONTROL/FINAL_REVIEW_READINESS_2026-10-15.md) and [file-by-file inventory](00_CONTROL/FINAL_FILE_SCOPE_INVENTORY_2026-10-15.csv) describe earlier revisions, not today's tracked-file count. This GitHub repository is **public**. The approved plans and measurements needed to determine drainage performance have **not** been obtained. Read [the current release guide](15_RECONCILED_DRAFTS/README.md) before using anything in a meeting.


## Historical evidence acquisition and preservation (October 16, 2026)

**Latest verified source and gap register:** [historical evidence completeness and provenance](00_CONTROL/HISTORICAL_EVIDENCE_COMPLETENESS_2026-10-16.md). The [new historic source directory](11_HYDROLOGY_AND_HAZARD/SRC_PUBLIC_GIS_2026-10-16/) contains original 2006 NOAA point cloud, 2017 NOAA bare-earth GeoTIFF, 2017 survey report, official preconstruction aerial exports (1994 through 2023), the 336-page county watershed public draft, East Navarre official study-area image, and county GIS source captures. [File hashes, byte counts and failed acquisition status](00_CONTROL/HISTORICAL_PUBLIC_EVIDENCE_INTEGRITY_AUDIT_2026-10-16.json) are machine-checked. Original 2018 Panhandle LiDAR index is preserved, but that survey does **not** cover the subject sites. Not all archive-year aerial images are downloaded, and site-specific approved engineering plans or current as-built measurements are still missing.

**Private homeowner photographs must not be published to the public repository.** The [privacy-safe photo filename index](00_CONTROL/PRIVATE_RESIDENT_PHOTO_INVENTORY_PUBLIC_SAFE_2026-10-16.csv) records 37 reported file instances / 35 unique contents. Only owner-authorized files, with metadata and permission review, can be added to separately access-controlled private evidence storage. A public list is not the same as preserving the private originals.

## Controlling jurisdiction: Santa Rosa County only

**Local authority is Santa Rosa County, Florida**, not any neighboring county. Use the [jurisdiction, agency and legal-edition register](00_CONTROL/JURISDICTION_AND_AUTHORITY_SCOPE_2026-10-15.md) to distinguish County Engineering, Building Inspections, Public Works, Property Appraiser and Clerk roles from Florida DEP/NWFWMD requirements and federal FEMA/NOAA/EPA background. **County GIS now identifies the relevant Tom Street segment as County Maintained** (FID 2006 / segment 2036, range 2100-2299). Individual drainage-asset ownership, acceptance and easements remain unresolved. See the [five-question findings](17_CURRENT_RESEARCH/FIVE_QUESTION_FINDINGS_2026-10-16.md). The November 2025 LDC PDF must be read alongside effective 2026 ordinances, conditional lot-grading exemptions (§ 4.04.01.D.4), and the separate **all-lots certified-as-built** provision (§ 4.04.01.E). None establishes a site violation without actual plans and measurements.

## Current property and permit register

These identifiers come from saved Santa Rosa County Property Appraiser and MGO permit records, **not a live status guarantee**. The source timestamps are in the original files.

| Role | Address | Parcel ID | Saved permit and status |
| --- | --- | --- | --- |
| Construction site | **2264 Tom Street, Navarre** | `21-2S-26-0780-0QQ00-1020` | `BP-2026-1621`, Active at capture |
| Construction site | **2268 Tom Street, Navarre** | `21-2S-26-0780-0QQ00-1490` | `BP-2026-1612`, Active at capture |
| Neighboring established property | **2265 Tom Street** | `21-2S-26-0780-0QQ00-1180` | Historical site context; not one of the two construction permits |

Both construction parcels listed **Holiday Builders Inc.** as owner of record on the captured appraiser roll. Owner, permit applicant, licensed builder and engineer-of-record roles must not be conflated. Historical MGO permits referred to **2266 Tom Street**, although no current appraiser situs record for that address appeared in the saved search; there is **no verified address-renumbering or parcel-merger instrument**.

## Use these meeting materials, not the older release

| Current document | Purpose |
| --- | --- |
| [Five-page reconciled meeting PDF](15_RECONCILED_DRAFTS/pdf/Tom_Street_Reconciled_Public_Meeting_Draft.pdf) | Homeowner brief, commissioner cover letter, records letter, proxy notes and follow-up sheet |
| [Commissioner letter](15_RECONCILED_DRAFTS/06_COMMISSIONER_COVER_LETTER_DRAFT.md) | Request a named engineering contact, site review and written response |
| [County Chapter 119 letter](15_RECONCILED_DRAFTS/02_COUNTY_LETTER_DRAFT.md) | Records request and engineering clarification |
| [Current draft-source folder](15_RECONCILED_DRAFTS/) | The five editable source documents, manifest and checksums |
| [Controlled PDF/ZIP release manifest](15_RECONCILED_DRAFTS/pdf/RELEASE_MANIFEST.json) | Specifies exactly what entered the **draft** package |

**Superseded historic materials:** `14_MEETING_PACKET/` and `releases/2026-10-15/` contain an earlier packet and must **not** be distributed as current. Those originals remain only for chronology and audit trails. The word “final” in an older ZIP filename is not evidence of factual review or signing. The new five-page packet likewise remains **DRAFT_NOT_APPROVED_FOR_EXTERNAL_DISTRIBUTION** until a homeowner verifies its contents, signs any letter, and approves what is shared.

## What the saved inspection records actually show

- **2264, August 6, 2026:** a driveway inspector recorded **instructions** for roughly 100 feet of 12-inch perforated pipe and inlets, referring to structures near 2260 and 2270. This is **not** proof of construction, easement rights, invert elevation or capacity.
- **2268, August 31, 2026:** an inspection comment referred to keeping a roadway/stormwater ditch free of construction sediment. On **September 10** another comment directed matching existing roadway grades. Those comments provide no numerical heights, storm design or proof of field adequacy.
- Both permits' saved MGO task lists show **Certified Drainage as Built: Assigned**. This **does not establish** whether an engineer's letter exists, was submitted, is late or has been approved. Both permits had no customer-visible plan attachments in the captured portal endpoint.

## Governing code context (applicability not determined)

The saved [Santa Rosa County Land Development Code](08_LEGAL_AND_REGULATORY/SOURCE/santa_rosa_county_LDC.pdf) is a 509-page PDF whose **cover and revisions table identify November 10, 2025 (Ordinance 2025-25)**. The PDF's January 13, 2026 internal creation timestamp **is not its enactment or effective date**. County [official LDC site](https://www.santarosa.fl.gov/182/Land-Development-Code).

- **§ 4.04.01.D.1:** for the class of residential lot it specifies, the required lot-grading information depends on whether the County has a subdivision grading plan on file. It lists the ERP-letter or Florida PE plan pathway, elevations and positive outfall, plus a conformance certification at the appropriate completion stage.
- **§ 4.04.01.D.4:** lists possible lot-grading-plan exemptions, which cannot be ruled in or out from unsurveyed photographs or lot height alone.
- **§ 4.04.01.E:** addresses certified as-builts before issuance of a certificate of occupancy.

Before alleging noncompliance, verify the lot-specific approval pathway, controlling ordinance edition and amendments on the permit's application/issuance dates, actual plans and applicable exceptions. See [regulatory and case-law matrix](00_CONTROL/REGULATORY_AND_CASELAW_MATRIX.md) and [the scanned corrected *Westland* opinion](08_LEGAL_AND_REGULATORY/SOURCE/PRIMARY_AUTHORITY/Westland_Skating_Center_v_Gus_Machado_Buick_Fla_1989_CORRECTED_OPINION.pdf). Neither code text nor a case-law rule establishes liability without physical facts.

## Evidence catalogue and acquisition status

| Location | What it contains |
| --- | --- |
| [`00_CONTROL/SOURCE_REGISTER.csv`](00_CONTROL/SOURCE_REGISTER.csv) | Local source identities and preserved SHA-256 hashes |
| [`00_CONTROL/EVIDENCE_LEDGER.csv`](00_CONTROL/EVIDENCE_LEDGER.csv) | Claim classification, exhibit, limitations and contrary evidence |
| [`00_CONTROL/PERMIT_DOCUMENT_INVENTORY.csv`](00_CONTROL/PERMIT_DOCUMENT_INVENTORY.csv) | Obtained documents and precisely named missing files |
| [`00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv`](00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv) | Custodians, draft requests and response tracking |
| [`00_CONTROL/CHRONOLOGY.csv`](00_CONTROL/CHRONOLOGY.csv) | Dated events and uncertain historical attribution |
| [`08_LEGAL_AND_REGULATORY/SOURCE/PRIMARY_AUTHORITY/`](08_LEGAL_AND_REGULATORY/SOURCE/PRIMARY_AUTHORITY/) | Corrected Florida Supreme Court opinion plus two **DEP index reports**; signed DEP consent orders **not** obtained |
| [`16_ARCHIVE_RECONCILIATION/`](16_ARCHIVE_RECONCILIATION/) | Boundaries of archive verification and candidate photographic exhibits (without the images) |

**Known major gaps:** originals of approved/revised grading and drainage plans; original surveys; finished grades; pipe and outfall geometry; shared roadside design and maintenance/ROW/easements; actual deed/plat images; certified completion/CO status; ERP permit-file geographic scope; storm-event field chronology; and qualified, measured effects on neighboring homes.

**Five foundational Chapter 119 requests plus two supplemental drafts** in [`13_PUBLIC_RECORDS_REQUESTS/`](13_PUBLIC_RECORDS_REQUESTS/) have **no verified submission receipts**. Do not mark them sent.

## Private evidence and public-repository warning

A separate protected resident package contains **15 JPEG copies that matched their archived hashes**. Native camera originals, capture timestamps, precise site attribution and public-release permission are **not validated**. Do not commit photographs/EXIF, private ZIPs, authenticated login captures or residents' identities into this public repository.

Prior authenticated portal material containing requester identity **was committed in older Git history**. Deleting current tracked copies does **not** remove historical exposure. A history rewrite would require coordinated approval, not an automatic force-push.

## Regenerating and checking the current draft

```bash
python3 -m pip install -r requirements-release.txt
python3 tools/build_reconciled_packet.py
python3 tools/verify_reconciled_release.py
python3 00_CONTROL/tools/test_evidence.py
```

The [GitHub Actions workflow](.github/workflows/reconciled-public-packet.yml) builds the exact public-scope drafts, verifies the original record hashes and controls the ZIP contents. Passing tests means **file integrity and internal consistency**, **not engineering adequacy, legal applicability or complete records acquisition**.

**Highest-value next action:** request the full County engineering/permit files for both lots and the Tom Street roadside system; obtain the official design, responsible professional and surveyed before/after condition before making a causation or violation claim.
