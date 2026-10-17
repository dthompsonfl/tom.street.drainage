# Private original intake and portable evidence identity contract

**Interim operating procedure.** No login system, database service or hosted application is created here. This repository is public; completed resident materials and custody logs are not. Human appointments, actual submissions and transfer receipts are pending until performed.

## Receive an item without changing the original

1. The original evidence owner keeps their **untouched camera-native, email or document file** in household-controlled storage. Agree privately with the coordinator on a transfer method whose access is restricted, and the purpose, scope, retention and restrictions. Do not use GitHub issues/commits or a public chat upload as private transfer.
2. A coordinator assigns stable identifiers (not GitHub numbers): household reference `HH-<random-opaque-id>` (mapping to real resident held only privately); evidence ID `EVD-<UUID>`; and optional distinct derivative `DER-<UUID>`. Official source IDs retain the existing `SRC-` scheme. Never rename an original file to make its source appear different: preserve original filename and its bytes while assigning an external ID.
3. Record original filename, MIME as detected and asserted, bytes, SHA-256, capture timestamp as supplied (with source/time-zone/uncertainty), first receipt timestamp in UTC, originating custodian and permitted uses. **EXIF is an unverified metadata claim** until compared to original file, source owner and device/time settings.
4. Independently calculate hash of retained original, of transferred copy and upon each custody change; record `FROM`, `TO`, UTC transfer timestamp, method, reference, integrity result and access boundary privately. No public note should expose household identity, exact photo GPS or transfer URL.
5. Store originals with restricted read access and a separately verified encrypted/offline backup. Maintain an access/retention log. The evidence custodian verifies restores and periodic hashes. Roles or permissions are not inferred from tool execution.
6. Create separate derivatives with distinct IDs and checksums, original-ID links, edit/redaction description, date, source/publication limits and reviewer record; never silently replace a source. A source record may be a government publication even when retrieved through ordinary free registration: classify its content and access terms separately from login/session artifacts.
7. To correct, supersede or restrict use, make an append-only private custody/consent event, preserve the prior version, update future distribution approvals and create a public-safe correction ID. Withdrawal of future permission is not a retroactive deletion of public Git history.

## Portable field contract (future authenticated app)

| Entity | Stable required fields | Sensitive storage rule |
| --- | --- | --- |
| Household | `household_ref`, created_utc, owner-consent scope | Real address/name mapping **private only** |
| Evidence original | `evidence_id`, original_filename, `sha256`, byte_count, source_type, source_date, received_utc, custody_ref, household_ref or `source_id` | Original and private location never public by default |
| Derivative | `derivative_id`, `original_evidence_id`, checksum, transformation, editor_role, created_utc, review_status | Release only with version-specific consent/review |
| Custody event | `event_id`, `evidence_id`, UTC timestamp, from/to role, method, hash_check, receipt_ref | Identifiers to real persons private |
| Consent | `consent_id`, owner_ref, covered evidence/version, intended audience, uses, restrictions, evidence_ref, decision, reviewed_utc, supersedes | Proof and personal signatures private; public references opaque |
| Claim | Existing `claim_id`, `source_id`, source SHA, locator, evidentiary type, limits, contradicted_by, version | No unverified inference promoted to fact |
| Records request | Stable request/gap ID, issuing agency, requested source IDs, sent_utc, receipt reference, responses, status | No submitted/sent status without verified private receipt |
| Edition | Edition ID, exact source commit, included file checksums, decision, privacy/source-review references, supersedes | Public only when approved for named audience |

Opaque refs must remain stable across CSV migrations, never depend on row numbers, issue numbers, present directory order or human-readable resident names. Dates use ISO 8601 with timezone; retain original local-time statements separately. Use append-only events to preserve history, not mutable audit fields. Filenames and paths can change without changing evidence IDs.

## Existing validated tools and safeguards

`python tools/private_evidence_audit.py --vault /path/outside/checkout` hashes a controlled folder and detects duplicates. `tools/record_submission_receipt.py` has a preview/acknowledgment flow and optimistic register hash. These do **not** create proof of custody, recipient receipt or consent by themselves. Synthetic tests are provided in `tools/test_private_operations.py`. Never run these against public tests containing actual resident data.

**Corrections:** maintain source/correction/version history; stop new derivative distributions pending review when a resident challenges attribution or consent. Do not delete preserved originals. If a genuine credential leaked, contain and rotate privately without displaying its value or destructively rewriting source history.

**Before first real transfer:** coordinator and resident must agree on a private channel, custodian and backup responsible person, access controls, signed/intelligible intended-use consent and proof retained outside Git. All are presently human dependencies.
