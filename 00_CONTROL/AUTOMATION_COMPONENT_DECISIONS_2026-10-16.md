# Autonomous research components | Explicit execution decisions

**Control status: October 16, 2026 | Technical planning, not an evidence-acquisition claim.**

The historical [`AUTONOMOUS_PIPELINE_COMPLETENESS_REPORT.md`](AUTONOMOUS_PIPELINE_COMPLETENESS_REPORT.md) describes five helper modules not present in the installed tools and claims an end-to-end system that current source does not prove. They are **not** replaced with empty scripts merely to make a green `--dry-run` report. The current pipeline must report them missing wherever referenced and refuse execution without an explicit operator acknowledgment.

| Historically named module | Current decision | Grounded boundary and what would permit implementation |
| --- | --- | --- |
| `analyze_lidar_terrain_change.py` | **DEFERRED, UNVERIFIED** | 2006 point-cloud and 2017 terrain datasets have been preserved, but actual ground-class extraction, datum/unit harmonization, comparable survey control and current 2026 observations are not established. A quantitative tool needs actual input/data coverage and independent professional acceptance criteria before claims about slope change. Historical terrain cannot prove current drainage. |
| `acquire_noaa_precipitation_and_storms.py` | **OPTIONAL RESEARCH, DEFERRED** | NOAA station captures and regional precipitation context exist; a storm-event correlation pipeline needs identified site events, verified station times/zones, rainfall products, service coverage, retrieval manifests and tests. Do not equate airport totals with a site rain gauge. |
| `audit_private_photo_vault.py` | **LIMITED FUNCTION REPLACED** | [`tools/private_evidence_audit.py`](../tools/private_evidence_audit.py) provides a **read-only off-repository** hash and duplicate inventory, using private manifests only with explicit storage. It does not authenticate camera-native capture dates or grant public-sharing permission. The historical filename remains absent intentionally. |
| `ingest_records_request_response.py` | **PARTIALLY REPLACED; AUTO-PUBLIC-INGEST DEFERRED** | [`tools/record_submission_receipt.py`](../tools/record_submission_receipt.py) supports **human-verified, explicitly authorized** receipt status entry with optimistic register checksum. It does not send a request or publish incoming records. Automatic ingestion requires safe quarantine, signature/filetype inspection, human privacy and parcel/source review, and safe source-register merging with rollback; do not create a "submit" record by inference. |
| `patch_legacy_checks_for_autonomy.py` | **RETIRED BY DESIGN** | Automatic rewriting of canonical consistency and release checks to make new evidence pass would undermine audit integrity. Instead, six historical fixed-data builders have been disabled and CI tests guard their entrypoints. New source/claim evidence must be reviewed and integrated explicitly. |

## Supported tools today

- `python tools/check_administration.py --strict`: validates current public registers, current-document links and toolkit file restrictions without network or writes.
- `python tools/report_current_status.py`: displays **current** counts directly from public CSVs without altering them. `--format json` is available for inspection/export via shell redirection to a controlled destination.
- `python tools/autonomous_evidence_pipeline.py --mode full --dry-run`: lists the configured phases and actual missing module names, with no acquisition or writes. A successful diagnostic is **not** a successful full investigation.
- `python tools/private_evidence_audit.py --vault /controlled/private/path`: local private-only hash/duplicate inventory.
- `python tools/record_submission_receipt.py ...`: operator-validated proof and dated receipt status; no outgoing mail is sent.

## Acceptance criteria before enabling full autonomous acquisition

1. Enumerate each network service and license/permission requirement; use an explicit request allowlist and bounded rate/retry policy. No unreviewed authenticated capture may enter public Git.
2. Prove archived evidence is append-only, checksum-verified, uniquely identified and cannot overwrite canonical raw records or live source registers.
3. Require dated originals, source coverage, CRS and vertical datum/units for terrain and precipitation comparisons. Label observations and derived estimates.
4. Quarantine every returned document until both source and privacy review, even when a government system supplied it.
5. Exercise independent negative tests for bogus responses, timeouts, wrong-project permit identifiers, redirect HTML, truncated PDFs, duplicate IDs and unavailable services.
6. Validate a complete dry-run and an isolated synthetic end-to-end test; then run only owner-approved bounded acquisition tasks and inspect all generated diffs before promotion.
7. Obtain any necessary expert review before using results for an engineering conclusion or public statement.

**Closure decision:** The supported administration/documentation gates have been implemented and tested. End-to-end autonomous acquisition and site-specific engineering determination are **not complete** and should not be marked complete by a mere file-presence test. Source gaps remain in [`MISSING_RECORDS_AND_ACTIONS.csv`](MISSING_RECORDS_AND_ACTIONS.csv).
