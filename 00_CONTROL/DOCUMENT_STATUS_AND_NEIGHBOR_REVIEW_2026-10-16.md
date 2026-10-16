# Which Tom Street documents are current?

**Independent documentation check: October 16, 2026.** This is a navigation and credibility check for the public repository. It does not certify drainage engineering, legal compliance, privacy clearance of every archived file, or completeness of government productions.

## For neighbors: read these first

| Purpose | Current document | Review status |
| --- | --- | --- |
| What this is about | [Project homepage](../README.md) | Available for neighbor reading and corrections |
| How to help check it | [Neighbor review guide](../NEIGHBOR_REVIEW_GUIDE.md) | Available for feedback; no GitHub account required for reading |
| What each source can prove | [Plain-English evidence guide](../PUBLIC_EVIDENCE_GUIDE.md) | Limited by saved source dates |
| What to bring to a meeting | [Five-page draft packet](../15_RECONCILED_DRAFTS/README.md) | **UNSIGNED DRAFT**, not approved for external submission |
| How to record an observation | [Neighbor toolkit](../18_NEIGHBOR_TOOLKIT/README.md) | Blank templates; keep originals private |
| What is missing | [Open questions](OPEN_QUESTIONS.md) and [community readiness](COMMUNITY_READINESS_2026-10-16.md) | Material County and survey dependencies remain |
| What technical/admin controls are implemented | [Current administrative and technical status](ADMINISTRATION_AND_TECHNICAL_STATUS_2026-10-16.md) | Updated source-linked operational boundaries; not an engineering clearance |

## How to interpret the rest of the repository

**Original agency source files:** saved parcel and permit responses, engineering/GIS downloads, aerial exports, official reports and enacted legal materials. They are preserved as source evidence, not rewritten to sound as if a resident created them. A checksum verifies a copy's bytes, **not** its meaning or current applicability.

**Current working research:** claim/source registers, the preserved County-maintenance classification, date-bounded research, primary-source extracts and open questions. Treat every claim as limited by the source and its retrieval date.

**Historical or superseded analysis:** `00_CONTROL/ACQUISITION_CHECKPOINT.md`, `ACQUISITION_RESULTS.md`, `PROGRESS.md`, `CURRENT_STATE_RECONCILIATION.md`, `FINAL_REVIEW_READINESS_2026-10-15.md`, `MAIN_BRANCH_REMEDIATION_STATUS.md`, `RESEARCH_STATUS_AT_COMMIT.md`, `RESEARCH_PLAN.md`, and the independent baseline audit describe earlier snapshots. Their counts, checklist boxes and tool availability must not be mistaken for present-day status.

**Superseded public packets:** `14_MEETING_PACKET/` and `releases/2026-10-15/` include older writing, some of which made unsupported inferences. **Do not distribute those PDFs or ZIPs as the current packet**, even though they remain in Git history for accountability.

**Proposed or incomplete automation:** [Autonomous pipeline completeness report](AUTONOMOUS_PIPELINE_COMPLETENESS_REPORT.md) is an **unverified historical design assessment**, not proof that all proposed code was delivered. The current runner references unavailable Python modules, and its associated test suite cannot substantiate a stated full pass while those dependencies are absent. Do not use that report to claim a complete automatic evidence acquisition or release system.

## Verification performed during this review

- Inspected the live `main` Git tree and the content of all **75 Markdown files present at the initial snapshot**, checking relative links and stale request-count language. No unresolved local Markdown links were identified in that scan.
- Found and corrected visible literal backslash-newline sequences in the homepage and the evidence guide. Subsequent additions require the same checks.
- Identified five proposed autonomous modules absent from `tools/`: `analyze_lidar_terrain_change.py`, `audit_private_photo_vault.py`, `acquire_noaa_precipitation_and_storms.py`, `ingest_records_request_response.py`, and `patch_legacy_checks_for_autonomy.py`.
- GitHub Actions has reported success for the controlled **draft** packet build, including source/document/jurisdiction and neighbor-publication checks. That is **not** a human sign-off or professional engineering verification.
- The privacy classification records many source files as `REVIEW_REQUIRED`. Sensitive data may also remain in older Git history. **Do not assume the entire public repository is cleared for unrestricted redistribution.**

## What we still cannot claim

We have not recovered the stamped grading plans, parcel-specific approved changes, a common-datum current survey, measured culvert inverts/outfall, County acceptance/maintenance records for each structure, or signed applicable environmental permissions. No letter should imply that public-records requests have been submitted without receipts. No evidence presented establishes that the new construction caused a code violation or flooding.

**Decision:** The new front-door guides are appropriate for neighbors to review and correct; the source archive is available with scope/privacy cautions; the official letters remain drafts pending personal approval, independent print/privacy review and the missing agency evidence.

**Responsibility for the next official submission:** The resident who signs or submits it must check their own observations and the exact version, and retain their actual outgoing copy, acknowledgment and response privately.
