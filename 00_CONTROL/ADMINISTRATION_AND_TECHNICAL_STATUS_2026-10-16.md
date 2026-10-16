# Current administrative and technical completion register

**Controlled status entry | October 16, 2026 | Public-safe administrative summary**

This is the active entry point for determining **which repository procedures are implemented and which evidence-based questions remain unresolved**. It does not replace the archived 51-item independent audit or declare that the drainage investigation is complete. Do not treat historical statuses as today's open-defect count.

## Current records and controls

| Workstream | Verified/implemented baseline | Remaining requirement | Closure gate |
| --- | --- | --- | --- |
| Property identities | Saved Santa Rosa Property Appraiser records tie 2264 to `...-1020`, 2268 to `...-1490` | Later land divisions, full title chain and historical address anomalies | Actual recorded instruments, dated source references and qualified interpretation where necessary |
| Historic subdivision plat | Official original Crescent Shores `PLAT A/70`, two scanned sheets, preserved in `02_PROPERTY_AND_PARCELS/PRE_REQUEST_OCT16_PRIMARY_LOOKUPS/` | Later Lot QQ deeds, easements, right-of-way acceptance and modern lot geometry | Specific recorded instruments/source IDs; do not extrapolate from a 1946 dedication |
| Building permits | Archived County MGO captures identify BP-2026-1621 and BP-2026-1612 | Original approved/revised lot-grading, site, stormwater, driveway, inspection and signed as-built documents; current permit/CO status | Complete County production or dated custodian explanation of which records are held/withheld/not retained |
| Roadway and drainage | County GIS lists Tom Street segment 2036 as County Maintained | Each culvert/inlet/swale/outlet's design, acceptance, measured invert, and responsible maintainer | Accepted asset plans, easements, work orders, County explanation and common-datum measurements |
| Environmental authorization | Nearby ERP lead and bounded public map queries are saved | Site-specific ERP and construction CGP coverage/exemption, approved footprint and records | Actual authorizations or agency response linked to the parcels/project; not point proximity |
| Historical evidence | Official aerials, original terrain sources and relevant GIS response files preserved with limits | Site-specific aerial frame dates, original photo custody, professionally comparable grade context | Original records plus dated/limited analysis; historical LiDAR is not current survey |
| Public toolkit | Complete blank 18-page packet, separate worksheets, editable registers, automated PDF generator and publication checks on `main` | Resident usability feedback and permission-controlled adoption | Real neighbor prints/uses forms and controls own originals |
| Current meeting letters | Source-limited, unsigned drafts and reproducible PDFs | Individual sender wording approval, signature, sending and tracking | Human-verified outgoing copy and actual transmittal receipt; no false submission claims |
| Public privacy | Generic automated classification, separate restricted-material policy, and an optional off-repository duplicate/hash auditor | Human inspection of native originals, third-party permissions and previous public Git history | Private risk review and documented authorized remediation; a hash cannot prove authenticity |
| Autonomous research runner | Existing runner has a dry-run diagnostic, missing-module preflight and explicit operator acknowledgement before **any** non-dry-run mode | Five historically promised helper modules not all present; network/acquisition operations not audited end-to-end | Bounded isolated testing, network scopes, immutable archival writes and verified result before claiming ready |

## Administrative changes and acceptance

1. `tools/check_administration.py` is a **read-only** gate for active summary crosslinks, unique register identifiers, honest records-request receipt fields, verified source scope, known blank-toolkit media, recovered plat status, and the generated packet's five-input count. `tools/test_administration.py` uses synthetic records to prove regressions are rejected.
2. `.github/workflows/administration-quality.yml` runs the checker and synthetic regression tests on changes, with read-only GitHub permissions. It statically compiles tracked Python sources and compares the automation runner's declared missing modules against files that actually exist. It **does not execute** online acquisitions or issue records requests.
3. `00_CONTROL/RECORDS_INTAKE_AND_STATUS_SOP.md` documents private original handling, receipt verification, partial productions, ledger updates, public review and draft/publication boundaries. `tools/private_evidence_audit.py` and `tools/record_submission_receipt.py` are optional operator-controlled helpers with synthetic regression tests. They do not send requests, export resident data or perform an agency lookup.
4. The original 51 findings remain in [`INDEPENDENT_REMEDIATION_REGISTER.csv`](INDEPENDENT_REMEDIATION_REGISTER.csv), a historical audit with statuses **OPEN** or **REMEDIATION_STARTED_REVIEW_REQUIRED** from its baseline. Those flags are not an up-to-date assessment of current `main`. Reassess each against current code/source and record actual closure evidence; do not mechanically relabel all 51 as closed.
5. External evidence gaps remain in [`MISSING_RECORDS_AND_ACTIONS.csv`](MISSING_RECORDS_AND_ACTIONS.csv), while next owner actions remain in [`NEXT_ACTIONS.md`](NEXT_ACTIONS.md). These are different sets and must not be summed as a single defect count.

## Safety and maintenance decisions

- The current repository is **public**. Do not push resident photographs, device metadata, raw personal communications, credentials or authenticated captures into GitHub. Do not attempt a Git history rewrite without explicit authorization, full impact analysis, key rotation where needed and recovery plan.
- Preserve source originals and historic analysis as evidence of the research trail. Update active navigation and notes rather than modifying signed official records or retroactively editing earlier captures.
- Keep `15_RECONCILED_DRAFTS` as unsigned drafts pending an individual's editorial/permission decision. Avoid citing superseded packets in `14_MEETING_PACKET` or `releases/2026-10-15` as current materials.
- Report per-check statuses, tested commit SHA and dates. Neither passing CI nor a file checksum establishes an engineering finding, approved plan adequacy, causation or a violation.

**Next operational priority:** Obtain and track dated agency receipts for the two complete construction permit files and the shared roadway drainage/asset request; arrange a qualified measurement comparison only once the actual approved controls are identified or clearly unavailable.
