# Neighborhood governance, workflow controls and continuity

**Status: technical governance procedure; not a signed appointment or publication authorization.** Recorded 2026-10-16. Verify the current GitHub branch configuration before relying on any statement in this dated entry.

## Roles and separation of authority

| Function | Duty | Designation status |
| --- | --- | --- |
| Organizer/coordinator | Maintain the source register, share a single current-version pointer, collect correction requests, schedule review, and track open records requests | Repository owner is current organizer; separate publication power not inferred |
| Backup coordinator | Keep current directions, emergency offline copies, and restore continuity if organizer unavailable | **VACANT; individual must accept** |
| Evidence custodian | Secure originals, hashes, transfer receipts, custody events, access boundaries, restrictions and approved derivatives | **PENDING formal designation** |
| Source reviewer | Match each material claim to source bytes, exact text/date, contrary evidence and limitations | **PENDING independent appointment** |
| Privacy reviewer | Examine account/session content, household information, public availability and reusable rights independently | **PENDING independent appointment** |
| Publication approver | Accept or reject one named package/version for the stated audience and distribution channel | **PENDING real approval; may not be simulated by CI** |
| Resident/source owner | Authenticate own first-person words, authorize specific sharing and transfer, withdraw or restrict prospective reuse | **Individual consent required each time** |

One person can temporarily handle administrative tasks, but the repository may not claim independent review when the same person performed every role. Do not invent named backups, digital signatures or decisions.

## GitHub state and safeguards

At baseline `257c712d232f2d5e5495e26b6a6e9572dc452c22`, main was unprotected and the ruleset list was empty. The active GitHub connection could read branch status but the protection endpoint returned **403 Resource not accessible by integration**. This tool connection cannot configure branch protection. Never record protection as enabled without an authorized independent check.

The previous 27 workflows included automatic direct-main acquisition and PDF commits. The governance change converts source acquisition and preservation jobs to **manual launch plus read-only token**, and keeps PDF generation and checks while retaining unapproved builds as short-lived CI artifacts instead of changing `main`. All review/acceptance decisions remain manual. No more `git push origin HEAD:main` in workflows; the included regression test enforces this policy.

**Recommended branch protection (PENDING platform action):** require pull requests targeting main, at least one independent approved review, dismissal of stale approvals on new changes, all required evidence-administration and document-validation checks, protection of `main` against deletion/force updates, no unreviewed bypass actors, and restricted direct pushes. Before enabling, verify the necessary required check names on actual successful runs and that editor/maintainer access is available. Test both an approved merge and a rejected unauthorized bypass. Owner-direct emergency change is **not a standing bypass**.

**Read-only neighborhood access:** share a specific approved edition only. GitHub read access must not be mistaken for permission to upload private files or edit the canonical evidence; no neighbor write access is conferred here.

## Acquired source delivery after disabling unattended pushes

All **21 deliberately started** official-record acquisition, source-preservation, provenance and historical-plat rendering jobs retain their bounded, source-specific output files as **review-only GitHub Actions artifacts for seven days**, after a local restricted-content pattern screen. These are *temporary staging artifacts*, not a checked-in official original, not a public neighborhood edition and not proof of rights to redistribute. Their capture path lists come from the previously committed allowlists; they exclude raw SYSTEM_RAW portal captures, project/record page HTML and .env files. The runner has read-only repository permissions and cannot push.

**Coordinator process:** select a specific completed manual Actions run, download its named unapproved-source-capture artifact before expiry, independently inspect original bytes, SHA-256 manifests, access method, original source and any personal/session artifacts. Retain accepted, unchanged originals in the appropriate source directory using an authorized reviewed commit/merge to main. Update SOURCE_REGISTER, evidence and claim links only after verification. Record any rejected, failed or incomplete capture honestly in the gaps log. If the artifact contains private data, hold it in controlled storage, do not add it to Git, and consider the authenticated/public separation. CI content scanning is not adequate human privacy clearance. **No automatic GitHub release or neighborhood distribution occurs.**

## Operational recovery and interrupted runs

1. In a disrupted handoff, stop new publications and identify last successfully reviewed source commit, known edition ID, current manifest SHA and outstanding human gates. Re-fetch `origin/main`, inspect status and CI; never reset others' commits to align a narrative.
2. Preserve independent offline, access-controlled backups of original household evidence and its manifests. A repository backup preserves public research, **not** the private originals. Backup custodian/rotation verification is pending human designation.
3. Retrieve historic editions from `releases/` or the dated approved edition index. Candidate review artifacts can expire; archive a validated candidate privately until approved. Never overwrite a named published edition.
4. If automated acquisition fails, keep its manifest and logs, classify the failure, and rerun only the specifically authorized manual job. A successful research query does not turn into approved public evidence.
5. Incoming corrections create a new dated note with prior version and source; disputed factual claims are marked open, not silently deleted. A resident restriction stops **new prospective distributions** until reviewed; historical public Git copies may remain accessible and require separate response.
6. Future app migration must import immutable evidence identifiers and lineage from [the portable metadata contract](PRIVATE_INTAKE_AND_PORTABLE_METADATA_CONTRACT.md); do not couple IDs to Git issue numbers.

## Decision gates

The draft letter author must approve exact words. Each private evidence owner must approve exact use. The source/privacy reviewers document conclusions separately. The publication approver must authorize a pinned package. Two actual independent nontechnical-neighbor tests and required fixes must be recorded before the final neighborhood handoff. None of these actions is completed by creating a blank form or passing CI.
